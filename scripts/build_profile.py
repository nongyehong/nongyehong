"""Generate Dawn's GitHub-compatible SVG profile assets. Python 3.10+."""
from pathlib import Path
from html import escape
import base64
import argparse
import io
import json
import re
from urllib.request import Request, urlopen

from PIL import Image
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT_NAMES = {"sans": "Geist-Regular.woff2", "medium": "Geist-Medium.woff2", "mono": "GeistMono-Regular.woff2"}
FONTS = {k: TTFont(ASSETS / "fonts" / v) for k, v in FONT_NAMES.items()}
FACES = "".join(f"@font-face{{font-family:{key};src:url(data:font/woff2;base64,{base64.b64encode((ASSETS/'fonts'/value).read_bytes()).decode()}) format('woff2')}}" for key, value in FONT_NAMES.items())
THEMES = {
    "light": dict(bg="#ffffff", panel="#ffffff", fg="#0b0b0b", secondary="#585858", muted="#767676", border="#e3e3e3", soft="#f8f8f8", red="#c9302d"),
    "dark": dict(bg="#121212", panel="#181818", fg="#f2f2f2", secondary="#b4b4b4", muted="#8c8c8c", border="#2b2b2b", soft="#1f1f1f", red="#e0525b"),
}

# Embedded SVG media queries inherit the host element's actual color-scheme.
# This also covers GitHub auto mode with both day and night themes set to dark.
THEME_CSS = ":root{" + ";".join(f"--{key}:{value}" for key,value in THEMES["light"].items()) + "}"
THEME_CSS += "@media(prefers-color-scheme:dark){:root{" + ";".join(f"--{key}:{value}" for key,value in THEMES["dark"].items()) + "}}"
COLORS = {key:f"var(--{key})" for key in THEMES["light"]}

def width(value, size, font="sans", spacing=0):
    total = 0
    for ch in value:
        face = FONTS[font]
        glyph = face.getBestCmap().get(ord(ch))
        if glyph is None:
            raise ValueError(f"Font subset is missing {ch!r}")
        total += face["hmtx"][glyph][0] * size / face["head"].unitsPerEm
    return total + max(0, len(value)-1) * spacing

def txt(value, x, y, size, color, font="sans", align="start", spacing=0, cls="", delay=0):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{font},Arial,sans-serif" font-size="{size}" fill="{color}" text-anchor="{align}" letter-spacing="{spacing}" class="{cls}" style="animation-delay:{delay:.2f}s">{escape(str(value))}</text>'

def motion(body, kind="rise", delay=0):
    return f'<g class="enter-{kind}" style="animation-delay:{delay:.2f}s">{body}</g>'

def animated_segments(segments, x, y, size, color, delay=0):
    parts = []
    for index, segment in enumerate(segments):
        parts.append(txt(segment, x, y, size, color, "medium", cls="enter-word", delay=delay+index*.07))
        x += width(segment, size, "medium")
    return "".join(parts)

def box(x,y,w,h,fill,stroke="none",r=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'

def save(name,w,h,label,body,defs=""):
    css=FACES+THEME_CSS+"""
    .enter-rise{animation:profile-rise 720ms cubic-bezier(.22,1,.36,1) both}
    @keyframes profile-rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
    .enter-word{animation:profile-word 900ms cubic-bezier(.22,1,.36,1) both}
    @keyframes profile-word{from{opacity:0;transform:translateY(.32em);filter:blur(10px)}to{opacity:1;transform:translateY(0);filter:blur(0)}}
    .enter-fade{animation:profile-fade 1100ms cubic-bezier(.22,1,.36,1) both}
    @keyframes profile-fade{from{opacity:0}to{opacity:1}}
    @media(prefers-reduced-motion:reduce){*{animation:none!important}}
    """
    output=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label,quote=True)}"><defs><style>{css}</style>{defs}</defs>{body}</svg>\n'
    (ASSETS / name).write_text(output,encoding="utf-8")

def refresh_avatar(username):
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username):
        raise ValueError("Invalid GitHub username")
    headers = {"User-Agent": "nongyehong-profile-avatar", "Accept": "application/vnd.github+json"}
    with urlopen(Request(f"https://api.github.com/users/{username}", headers=headers), timeout=30) as response:
        avatar_url = json.load(response)["avatar_url"]
    if not avatar_url.startswith("https://avatars.githubusercontent.com/"):
        raise ValueError("Unexpected GitHub avatar host")
    separator = "&" if "?" in avatar_url else "?"
    with urlopen(Request(avatar_url+separator+"s=460", headers={"User-Agent": headers["User-Agent"]}), timeout=30) as response:
        downloaded = response.read(10_000_001)
    if len(downloaded) > 10_000_000:
        raise ValueError("Avatar exceeds size limit")
    avatar = Image.open(io.BytesIO(downloaded)).convert("RGBA")
    canvas = Image.new("RGBA", avatar.size, "white")
    canvas.alpha_composite(avatar)
    avatar = canvas.convert("RGB").resize((460, 460), Image.Resampling.LANCZOS)
    target = ASSETS/"avatar.png"
    if target.exists():
        with Image.open(target) as old:
            if old.size == avatar.size and old.convert("RGB").tobytes() == avatar.tobytes():
                print(f"GitHub avatar for {username} is unchanged.")
                return False
    output = io.BytesIO()
    avatar.save(output, format="PNG")
    pending = target.with_suffix(".tmp")
    pending.write_bytes(output.getvalue())
    pending.replace(target)
    print(f"Updated avatar from GitHub for {username}.")
    return True

def portrait(c, x=420,y=0,size=460):
    image=Image.open(ASSETS/"avatar.png").convert("RGB").resize((140,140))
    dots=[]
    step=size/140
    for row in range(140):
        for col in range(140):
            red,green,blue=image.getpixel((col,row))
            ink=(255-(red*.2126+green*.7152+blue*.0722))/255
            if ink<.045: continue
            px,py=x+(col+.5)*step,y+(row+.5)*step
            fade=min(1,max(0,(px-x)/105))
            opacity=min(1,ink*3)*fade
            color=c["red"] if red>green*1.10 and red>blue*1.04 else c["fg"]
            dots.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{step*.38:.2f}" fill="{color}" opacity="{opacity:.2f}"/>')
    return ''.join(dots)

def pill(value,x,y,c,mono=False):
    font="mono" if mono else "medium"
    fs=11 if mono else 13.5
    h=22 if mono else 34
    w=width(value,fs,font)+(18 if mono else 30)
    return box(x,y,w,h,c["panel"],c["border"],h/2)+txt(value,x+w/2,y+h/2+fs*.34,fs,c["muted"] if mono else c["secondary"],font,"middle"),w

PROJECTS = [
    ("hula", "HuLa", ["Cross-platform instant messaging.", "Built with Rust, Tauri and Vue 3."], ["Rust", "Tauri", "Vue 3"]),
    ("kyormar", "Kyormar", ["Native Agent and IM in one workspace.", "Independent modules, connected when needed."], ["Rust", "GPUI", "Desktop"]),
]
INTRO = "Focused on Rust, IM and AI agents. Building and optimizing software across programming languages. Creator of HuLa and Kyormar."

def build(c):
    body = motion(portrait(c), "fade", .1)
    body += animated_segments(["Rust, ", "IM"], 48, 121, 44, c["fg"], .15)
    body += animated_segments(["and ", "AI ", "agents."], 48, 173, 44, c["fg"], .29)
    body += txt("Building and optimizing software", 49, 233, 17.5, c["secondary"], cls="enter-rise", delay=.43)
    body += txt("across programming languages.", 49, 259, 17.5, c["secondary"], cls="enter-rise", delay=.49)
    body += txt("Creator of HuLa and Kyormar.", 49, 313, 20, c["fg"], "medium", cls="enter-rise", delay=.55)
    save("hero.svg", 880, 460, INTRO, body)

    title = "Featured projects"
    body = animated_segments(["Featured ", "projects"], 440-width(title, 30, "medium")/2, 46, 30, c["fg"])
    body += txt("HuLa · Kyormar", 440, 78, 15, c["secondary"], align="middle", cls="enter-rise", delay=.2)
    save("h-featured.svg", 880, 96, title, body)

    for slug, name, desc, chips in PROJECTS:
        filename = "hula-desktop.webp" if slug == "hula" else "kyormar-home-en.jpg"
        media_type = "image/webp" if slug == "hula" else "image/jpeg"
        screenshot = base64.b64encode((ASSETS/filename).read_bytes()).decode()
        illustration = box(8, 8, 416, 234, "#16191c" if slug == "hula" else "#ffffff", r=12)
        illustration += f'<image x="8" y="8" width="416" height="234" preserveAspectRatio="xMidYMid meet" href="data:{media_type};base64,{screenshot}" clip-path="url(#cover-edge)"/>'
        defs = '<clipPath id="cover-edge"><rect x="8" y="8" width="416" height="234" rx="12"/></clipPath>'
        note = " Official project screenshot." if slug == "hula" else " English homepage screenshot from kyormar.ai."
        body = box(.5, .5, 431, 375, c["panel"], c["border"], 17.5)+motion(illustration, "fade")
        body += txt(name, 20, 278, 19, c["fg"], "medium", spacing=-.4, cls="enter-rise")
        body += '<path d="M400 278l10-10m-9 0h9v9" fill="none" stroke="'+c["muted"]+'" stroke-width="1.2"/>'
        body += ''.join(txt(value, 20, 304+i*20, 13.5, c["secondary"], cls="enter-rise", delay=.08) for i, value in enumerate(desc))
        x = 20
        chips_svg = ""
        for chip in chips:
            part, w = pill(chip, x, 342, c, True)
            chips_svg += part
            x += w+6
        body += motion(chips_svg, delay=.14)
        save(f"card-{slug}.svg", 432, 376, name+" — "+' '.join(desc)+note, body, defs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-avatar", action="store_true", help="Fetch the current public GitHub avatar before rendering")
    parser.add_argument("--username", default="nongyehong", help="GitHub profile owner (not the visiting reader)")
    args = parser.parse_args()
    if args.refresh_avatar:
        refresh_avatar(args.username)
    build(COLORS)
    print("Built adaptive hero and HuLa/Kyormar cards.")
