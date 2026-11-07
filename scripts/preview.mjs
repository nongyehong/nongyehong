import http from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash, randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const cache = path.join(root,'.preview-cache');
const port = Number(process.env.PORT || 4178);
await mkdir(cache,{recursive:true});
const escape = s => s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
async function render() {
  const text = await readFile(path.join(root,'README.md'),'utf8');
  const key = createHash('sha256').update(text).digest('hex');
  const filename = path.join(cache,`${key}.html`);
  try { return await readFile(filename,'utf8'); } catch(error) { if(error.code!=='ENOENT') throw error; }
  const response = await fetch('https://api.github.com/markdown',{
    method:'POST',headers:{'Content-Type':'application/json','User-Agent':'nongyehong-local-readme-preview','Accept':'application/vnd.github+json'},
    body:JSON.stringify({text,mode:'gfm'}),signal:AbortSignal.timeout(20000),
  });
  if(!response.ok) throw new Error(`GitHub Markdown API returned ${response.status}. Check your connection or try again after the API rate limit resets.`);
  const html = await response.text();
  await writeFile(filename,html);
  return html;
}

function page(html,dark,mobile) {
  // A fresh image URL starts a fresh SVG timeline, even if the browser reuses
  // decoded image documents across navigations. This never changes README.md.
  const replayToken = randomUUID();
  html = html.replace(/\b(src|srcset)="(assets\/[^"?#]+\.svg)(#[^"]+)?"/g,(_,attribute,source,fragment)=>`${attribute}="${source}?preview=${replayToken}${fragment || ''}"`);
  const query = (d,m)=>`/?theme=${d?'dark':'light'}&width=${m?'mobile':'desktop'}`;
  return `<!doctype html><html lang="en" data-color-mode="${dark?'dark':'light'}" data-light-theme="light" data-dark-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dawn · Local README preview</title><style>
  :root{color-scheme:${dark?'dark':'light'};--bg:${dark?'#0d1117':'#fff'};--fg:${dark?'#e6edf3':'#1f2328'};--muted:${dark?'#9198a1':'#59636e'};--border:${dark?'#3d444d':'#d1d9e0'};--subtle:${dark?'#151b23':'#f6f8fa'};--link:${dark?'#79c0ff':'#0969da'}}
  *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}
  /* GitHub theme fragments follow the site's selected theme, not the OS. */
  [data-color-mode=light] .markdown-body [href$="#gh-dark-mode-only"],
  [data-color-mode=dark] .markdown-body [href$="#gh-light-mode-only"]{display:none}
  a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}a:focus-visible,summary:focus-visible{outline:2px solid var(--link);outline-offset:4px}
  .toolbar{position:sticky;top:0;z-index:10;background:var(--subtle);border-bottom:1px solid var(--border);padding:12px 20px;display:flex;gap:18px;align-items:center;justify-content:space-between;flex-wrap:wrap;font-size:13px}.toolbar strong{font-size:14px}.toolbar nav{display:flex;gap:8px}.toolbar a{padding:4px 9px;border:1px solid var(--border);border-radius:6px;color:var(--fg)}.toolbar a[aria-current=true]{background:var(--fg);color:var(--bg)}
  .toolbar button{font:inherit;padding:4px 9px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--fg);cursor:pointer}.toolbar button:hover{border-color:var(--fg)}.toolbar button:focus-visible{outline:2px solid var(--link);outline-offset:3px}
  .local-note{max-width:940px;margin:24px auto 14px;padding:0 18px;color:var(--muted);font-size:13px}.frame{width:calc(100% - 32px);max-width:${mobile?'390':'940'}px;margin:0 auto 40px;border:1px solid var(--border);border-radius:6px;overflow:hidden}.filebar{padding:14px 24px;border-bottom:1px solid var(--border);font:12px ui-monospace,Consolas,monospace}.markdown-body{padding:0 0 24px;overflow-wrap:break-word}
  .markdown-body>:first-child{margin-top:0!important}.markdown-body>:last-child{margin-bottom:0!important}.markdown-body img{max-width:100%;height:auto;box-sizing:content-box;vertical-align:middle}.markdown-body p,.markdown-body table,.markdown-body details,.markdown-body pre{margin-top:0;margin-bottom:16px}.markdown-body h2{font-size:24px;font-weight:600;line-height:1.25;margin-top:24px;margin-bottom:16px;padding-bottom:.3em;border-bottom:1px solid var(--border)}.markdown-body .anchor{display:none}.markdown-body table{display:block;width:max-content;max-width:100%;overflow:auto;border-spacing:0;border-collapse:collapse}.markdown-body th,.markdown-body td{padding:6px 13px;border:1px solid var(--border)}.markdown-body tr:nth-child(2n){background:var(--subtle)}.markdown-body pre{padding:16px;background:var(--subtle);border-radius:6px;overflow:auto;font-size:85%;line-height:1.45}.markdown-body code{font-family:ui-monospace,Consolas,monospace}.markdown-body hr{height:1px;border:0;background:var(--border);margin:24px 0}.markdown-body summary{cursor:pointer}.markdown-body sub{font-size:12px}.markdown-body .highlight{margin-bottom:16px}.markdown-body .highlight pre{margin-bottom:0}
  @media(max-width:600px){.markdown-body{padding:0 0 18px}.toolbar{gap:8px;padding:10px 14px}.frame{width:calc(100% - 24px)}.filebar{padding:12px 18px}.local-note{margin-top:16px}.toolbar strong{display:none}}
  </style></head><body><header class="toolbar"><strong>Dawn / README studio</strong><nav aria-label="Theme"><a aria-current="${!dark}" href="${query(false,mobile)}">Light</a><a aria-current="${dark}" href="${query(true,mobile)}">Dark</a></nav><nav aria-label="Width"><a aria-current="${!mobile}" href="${query(dark,false)}">Desktop</a><a aria-current="${mobile}" href="${query(dark,true)}">Mobile</a></nav><button type="button" id="replay-motion">Replay entrance</button></header><p class="local-note">LOCAL PREVIEW · GitHub-rendered Markdown · Nothing published<br><output id="motion-status" aria-live="polite"></output></p><main class="frame"><div class="filebar">nongyehong / <strong>README.md</strong></div><article class="markdown-body">${html}</article></main><script src="/preview-controls.js"></script></body></html>`;
}

const server = http.createServer(async(req,res)=>{
  try {
    if(req.method!=='GET' && req.method!=='HEAD'){res.writeHead(405);res.end();return;}
    const url = new URL(req.url,'http://127.0.0.1');
    if(url.pathname==='/favicon.ico'){res.writeHead(204);res.end();return;}
    if(url.pathname==='/preview-controls.js'){
      res.writeHead(200,{'Content-Type':'text/javascript; charset=utf-8','Cache-Control':'no-store'});
      res.end(req.method==='HEAD'?undefined:await readFile(path.join(root,'scripts','preview-controls.js')));return;
    }
    if(url.pathname==='/'){
      const html=page(await render(),url.searchParams.get('theme')==='dark',url.searchParams.get('width')==='mobile');
      res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});res.end(req.method==='HEAD'?undefined:html);return;
    }
    const relative = decodeURIComponent(url.pathname).slice(1);
    const file = path.resolve(root,relative);
    const inRoot = file.startsWith(root.endsWith(path.sep)?root:root+path.sep);
    if(!inRoot || !/^(assets|profile-3d-contrib)[/\\]/.test(relative) || path.extname(file)!=='.svg') {res.writeHead(404);res.end('Not found');return;}
    const data = await readFile(file);
    res.writeHead(200,{'Content-Type':'image/svg+xml','Cache-Control':'no-store'});res.end(req.method==='HEAD'?undefined:data);
  } catch(error) {
    const missing=error.code==='ENOENT';
    res.writeHead(missing?404:502,{'Content-Type':'text/html; charset=utf-8'});
    res.end(`<h1>Preview unavailable</h1><p>${escape(error.message)}</p><p><a href="/">Retry preview</a></p>`);
  }
});
server.on('error',error=>{console.error(error.message);process.exitCode=1;});
server.listen(port,'127.0.0.1',()=>console.log(`Local README preview: http://127.0.0.1:${port}`));
