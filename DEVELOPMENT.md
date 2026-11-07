# Local README preview

This profile contains an English introduction and two linked project cards.
The full square GitHub avatar sits at the top-right edge of the hero, with its
lower edge preserved. There are no hero buttons, extra projects or activity
sections. Entrance animations and light/dark themes are retained.

```sh
python -m pip install -r requirements.txt
python scripts/build_profile.py
node scripts/preview.mjs
```

Open <http://127.0.0.1:4178> and refresh after editing. The preview uses GitHub's
Markdown API, then serves repository assets locally. Changed Markdown needs one
online render; successful responses are cached in `.preview-cache/`, ignored by
Git. Nothing is committed or published by the preview. Stop its terminal with
Ctrl+C. **Replay entrance** restarts the animations without moving the page.

The local preview removes its own top/right article padding so the avatar meets
the preview frame. Project cards reserve their margins via README image widths.
GitHub itself controls the padding around published README content; an SVG
cannot remove that host-page padding. All portrait pixels fit inside the hero's
880 x 460 viewBox; no negative offset or bottom crop is used.

Edit `scripts/build_profile.py` to change copy and regenerate both themes. Links
and accessible descriptions live in `README.md`. The SVGs contain 900 ms
staggered blur/reveal, 720 ms rise and 1100 ms image fade. Reduced-motion settings
disable animation. Preview controls and cache-busting URLs are local only.

## GitHub theme selection

Each image and its wrapping link have a dark and light variant tagged with
`#gh-dark-mode-only` or `#gh-light-mode-only`. GitHub's CSS matches the wrapping
link's `href` suffix and uses its selected page theme to hide the other
variant. A `picture` media query can instead follow the browser/OS preference,
which may disagree with the user's GitHub appearance setting. These fragments
keep hero text, portrait lines, headings and card surfaces in the same theme.
Project links retain their official website destinations; the theme fragments
do not alter the requested server URL.

The preview uses `data-color-mode` and fragment visibility rules, just like the
GitHub page, rather than overriding media queries. Replay URLs preserve the
theme fragments. Verify that exactly four images are visible, all in the
selected theme, including after replay; also check GitHub with a manually
selected dark theme while the OS/browser prefers light.

## Avatar refresh

The avatar belongs to the GitHub profile owner (`nongyehong`), not to each reader
who opens the page. It is retrieved from the public GitHub user API and rendered
into self-contained, animated pointillist SVGs:

```sh
python scripts/build_profile.py --refresh-avatar --username nongyehong
```

Without `--refresh-avatar`, generation works offline using `assets/avatar.png`.
A failed fetch leaves the previous avatar untouched. Identical pixels do not
rewrite the avatar. No token or password is needed for the public image.

`.github/workflows/refresh-avatar.yml` checks hourly and can also be run manually.
On the default branch with GitHub Actions enabled, it commits only changed
avatar/hero files. It does not create an empty commit for an
unchanged avatar. This is scheduled refresh, not per-visitor real-time rendering;
GitHub scheduling and image caching can delay what readers see.

## Project cards and sources

- HuLa opens <https://hulaspark.com>, the website linked by its official repository
  <https://github.com/HuLaSpark/HuLa>. The cover is the project's official client
  screenshot, resized to `assets/hula-desktop.webp`; text inside that existing
  screenshot is part of the source image, not the profile's English copy.
- Kyormar opens <https://kyormar.ai>. Its cover embeds the actual English homepage
  first viewport, captured on 2026-11-07 at 1280 x 720 after selecting essential
  cookies only. The original is `assets/kyormar-home-en.jpg`; it replaces the
  previous concept illustration. Website screenshots are static assets.

Visual reference: <https://github.com/yappologistic/yappologistic>. The avatar
style, Geist typography, card geometry and entrance motion retain that direction.
Fonts use the SIL Open Font License in `assets/fonts/OFL.txt` and are embedded
inside each generated SVG. No third-party image-card or font service is required.

The old WakaTime and 3D contribution workflows remain removed. Historical
`profile-3d-contrib/` artifacts remain in Git but are not shown or updated here.
