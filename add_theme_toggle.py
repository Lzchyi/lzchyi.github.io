#!/usr/bin/env python3
"""
Add a dark/light mode toggle to lzchyi.github.io — all 20 pages.

Steps per file:
  1. Revert CSS variables and hardcoded colors back to dark defaults
  2. Inject a light-theme CSS block after :root {}
  3. Inject a no-FOUC script in <head> to restore saved preference
  4. Add a ☀️/🌙 toggle button inside .nav-links
  5. Add toggleTheme() + icon-init to the existing <script> block
"""
import os, glob, re

ROOT = os.path.dirname(os.path.abspath(__file__))

# ─── 1. Revert light-mode literals back to dark defaults ──────────────────────
REVERT = [
    ("--bg: #f8f6fb;",              "--bg: #050507;"),
    ("--bg-soft: #ede9f4;",         "--bg-soft: #090b10;"),
    ("--text: #160e22;",            "--text: #f3eff8;"),
    ("--soft: #3d3448;",            "--soft: #cfc6da;"),
    ("--muted: #6a6078;",           "--muted: #867d93;"),
    ("--line: rgba(0,0,0,0.09);",   "--line: rgba(255,255,255,0.08);"),
    ("--card: rgba(0,0,0,0.035);",  "--card: rgba(255,255,255,0.045);"),
    ("--card-hover: rgba(0,0,0,0.065);", "--card-hover: rgba(255,255,255,0.07);"),
    ("--card-border: rgba(0,0,0,0.1);",  "--card-border: rgba(255,255,255,0.1);"),
    ("--card-strong: rgba(0,0,0,0.16);","--card-strong: rgba(255,255,255,0.16);"),
    # nav glass
    ("background: rgba(248,246,251,0.82);", "background: rgba(5,5,7,0.72);"),
    # hero-card gradient
    ("background: linear-gradient(150deg, color-mix(in srgb, var(--accent) 14%, rgba(255,252,255,0.95)) 0%, rgba(248,245,252,0.98) 65%);",
     "background: linear-gradient(150deg, color-mix(in srgb, var(--accent) 18%, rgba(20,12,30,0.92)) 0%, rgba(7,7,11,0.95) 65%);"),
    # brand-mark
    ("background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 38%, #fff), color-mix(in srgb, var(--accent-warm) 28%, #f5f0fa));",
     "background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 32%, #111), color-mix(in srgb, var(--accent-warm) 22%, #0d0d11));"),
    # hero-mark / app-logo
    ("background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 38%, rgba(255,255,255,0.9)), color-mix(in srgb, var(--accent-warm) 28%, rgba(250,248,252,0.85)));",
     "background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 32%, rgba(20,20,24,0.82)), color-mix(in srgb, var(--accent-warm) 22%, rgba(20,20,24,0.72)));"),
    # page-badge
    ("background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 42%, rgba(255,255,255,0.9)), color-mix(in srgb, var(--accent-warm) 28%, rgba(250,248,252,0.85)));",
     "background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 36%, rgba(20,20,24,0.82)), color-mix(in srgb, var(--accent-warm) 22%, rgba(20,20,24,0.72)));"),
    # feature-icon
    ("background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 56%, rgba(255,255,255,0.8)), color-mix(in srgb, var(--accent-warm) 40%, rgba(250,248,252,0.85)));",
     "background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 34%, rgba(25,25,30,0.85)), color-mix(in srgb, var(--accent-warm) 25%, rgba(25,25,30,0.75)));"),
    # meta-row / btn-ghost
    ("background: rgba(0,0,0,0.025);", "background: rgba(255,255,255,0.025);"),
    ("background: rgba(0,0,0,0.02);",  "background: rgba(255,255,255,0.02);"),
    # nav-link hover
    (".nav-links a:hover { color: var(--text); background: rgba(0,0,0,0.06); transform: translateY(-1px); }",
     ".nav-links a:hover { color: var(--text); background: rgba(255,255,255,0.06); transform: translateY(-1px); }"),
    # borders
    ("border: 1px solid rgba(0,0,0,0.12);", "border: 1px solid rgba(255,255,255,0.12);"),
    ("border: 1px solid color-mix(in srgb, var(--accent) 24%, rgba(0,0,0,0.08));",
     "border: 1px solid color-mix(in srgb, var(--accent) 24%, rgba(255,255,255,0.08));"),
    # ambient glow
    ("radial-gradient(ellipse at 50% 100%, rgba(120,88,170,0.04), transparent 46%);",
     "radial-gradient(ellipse at 50% 100%, rgba(120,88,170,0.06), transparent 46%);"),
]

# ─── 2. Light-mode CSS block ──────────────────────────────────────────────────
LIGHT_CSS = """
html[data-theme="light"] {
  --bg: #f8f6fb;
  --bg-soft: #ede9f4;
  --text: #160e22;
  --soft: #3d3448;
  --muted: #6a6078;
  --line: rgba(0,0,0,0.09);
  --card: rgba(0,0,0,0.038);
  --card-hover: rgba(0,0,0,0.07);
  --card-border: rgba(0,0,0,0.1);
  --card-strong: rgba(0,0,0,0.16);
}
html[data-theme="light"] .nav {
  background: rgba(248,246,251,0.85);
}
html[data-theme="light"] .hero-card {
  background: linear-gradient(150deg, color-mix(in srgb, var(--accent) 14%, rgba(255,252,255,0.96)) 0%, rgba(248,245,252,0.98) 65%);
  border-color: color-mix(in srgb, var(--accent) 24%, rgba(0,0,0,0.08));
}
html[data-theme="light"] .brand-mark {
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 38%, #fff), color-mix(in srgb, var(--accent-warm) 28%, #f5f0fa));
  border-color: rgba(0,0,0,0.12);
}
html[data-theme="light"] .hero-mark,
html[data-theme="light"] .app-logo {
  background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 38%, rgba(255,255,255,0.9)), color-mix(in srgb, var(--accent-warm) 28%, rgba(250,248,252,0.85)));
  border-color: rgba(0,0,0,0.12);
  box-shadow: 0 0 24px var(--accent-glow);
}
html[data-theme="light"] .hero-mark {
  box-shadow: 0 16px 38px rgba(0,0,0,0.12), 0 0 34px var(--accent-glow);
}
html[data-theme="light"] .page-badge {
  background: linear-gradient(145deg, color-mix(in srgb, var(--accent) 42%, rgba(255,255,255,0.9)), color-mix(in srgb, var(--accent-warm) 28%, rgba(250,248,252,0.85)));
  border-color: rgba(0,0,0,0.12);
  box-shadow: 0 0 24px var(--accent-glow);
}
html[data-theme="light"] .feature-icon {
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 52%, rgba(255,255,255,0.8)), color-mix(in srgb, var(--accent-warm) 38%, rgba(250,248,252,0.85)));
  border-color: rgba(0,0,0,0.08);
}
html[data-theme="light"] .meta-row { background: rgba(0,0,0,0.025); }
html[data-theme="light"] .btn-ghost { background: rgba(0,0,0,0.02); }
html[data-theme="light"] .nav-links a:hover { background: rgba(0,0,0,0.06); }
#theme-toggle {
  background: none;
  border: 1px solid var(--card-border);
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;
  color: var(--muted);
  font-size: 15px;
  line-height: 1;
  display: flex;
  align-items: center;
  transition: color .22s var(--ease), border-color .22s var(--ease), transform .22s var(--ease);
}
#theme-toggle:hover { color: var(--text); border-color: var(--card-strong); transform: translateY(-1px); }
"""

# ─── 3. No-FOUC head script (runs before paint) ───────────────────────────────
NOFOUC_SCRIPT = '<script>(function(){var t=localStorage.getItem(\'zc-theme\');if(t===\'light\')document.documentElement.setAttribute(\'data-theme\',\'light\');})();</script>'

# ─── 4. Toggle button HTML ────────────────────────────────────────────────────
TOGGLE_BTN = '<button id="theme-toggle" title="Toggle light / dark mode" onclick="toggleTheme()"><span id="theme-icon">🌙</span></button>'

# ─── 5. Toggle JS (appended inside the existing <script> block) ───────────────
TOGGLE_JS = """
// ── Theme toggle ──────────────────────────────────────────────────────────────
function toggleTheme(){
  var light=document.documentElement.getAttribute('data-theme')==='light';
  var next=light?'dark':'light';
  document.documentElement.setAttribute('data-theme',next);
  localStorage.setItem('zc-theme',next);
  var icon=document.getElementById('theme-icon');
  if(icon) icon.textContent=next==='light'?'☀️':'🌙';
}
// Sync button icon after DOM ready
(function(){
  var t=localStorage.getItem('zc-theme')||'dark';
  var icon=document.getElementById('theme-icon');
  if(icon) icon.textContent=t==='light'?'☀️':'🌙';
})();
"""

# ─────────────────────────────────────────────────────────────────────────────

def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    orig = src

    # 1. Revert to dark defaults
    for old, new in REVERT:
        src = src.replace(old, new)

    # 2. Inject light CSS after end of :root block
    #    Marker: "* { box-sizing: border-box; }" always follows :root in every file
    MARKER = '* { box-sizing: border-box; }'
    if LIGHT_CSS not in src and MARKER in src:
        src = src.replace(MARKER, LIGHT_CSS + MARKER, 1)

    # 3. Inject no-FOUC script in <head> (after </style>)
    if NOFOUC_SCRIPT not in src:
        src = src.replace('</style>', '</style>\n' + NOFOUC_SCRIPT, 1)

    # 4. Add toggle button inside .nav-links — look for the closing </div> of nav-links
    #    Pattern: class="nav-links">...several anchors...</div>
    if 'id="theme-toggle"' not in src:
        src = re.sub(
            r'(class="nav-links">(?:.*?))(</div>)',
            lambda m: m.group(1) + TOGGLE_BTN + m.group(2),
            src,
            count=1,
            flags=re.DOTALL,
        )

    # 5. Append toggleTheme JS before </script> of the reveal script block
    if 'function toggleTheme' not in src:
        src = src.replace('</script>', TOGGLE_JS + '</script>', 1)

    if src != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(src)
        print(f'  ✓ {os.path.relpath(path, ROOT)}')
    else:
        print(f'  – {os.path.relpath(path, ROOT)} (unchanged)')


html_files = sorted(set(
    glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True) +
    glob.glob(os.path.join(ROOT, '*.html'))
))

print(f'Processing {len(html_files)} HTML files…\n')
for p in html_files:
    process(p)
print('\nDone.')
