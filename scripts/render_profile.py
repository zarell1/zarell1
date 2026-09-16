"""Build profile cards and links from profile.json. Python standard library only."""
import hashlib
import html
import json
import re
import textwrap
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ICONS = [('python', 'Python'), ('csharp', 'C#'), ('cplusplus', 'C++'), ('lua', 'Lua'), ('java', 'Java'), ('html5', 'HTML5'), ('css3', 'CSS3'), ('javascript', 'JavaScript'), ('git', 'Git'), ('powershell', 'PowerShell')]
ESC = lambda s: html.escape(str(s), quote=True)


def validate(config):
    for key, limit in [('project_name', 60), ('description', 360)]:
        value = config.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f'{key}: enter 1–{limit} characters')
        if any(ord(c) < 32 for c in value):
            raise ValueError(f'{key}: use a single line of text')
    for key in ['project_url', 'releases_url']:
        value = config.get(key)
        if not isinstance(value, str):
            raise ValueError(f'{key}: enter an HTTPS URL')
        url = urlsplit(value)
        if url.scheme != 'https' or not url.hostname or url.username or url.password or any(c.isspace() for c in value):
            raise ValueError(f'{key}: enter an HTTPS URL without credentials or spaces')


def text(x, y, value, size=15, color='#e2c58b', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{ESC(value)}</text>'


def panel(w, h, body, frame='full'):
    corners = ''
    if frame != 'bottom':
        corners += f'<path id="frame-top" d="M3 16V3H16M{w-16} 3H{w-3}V16"/>'
    if frame != 'top':
        corners += f'<path id="frame-bottom" d="M3 {h-16}V{h-3}H16M{w-16} {h-3}H{w-3}V{h-16}"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><pattern id="pixels" width="48" height="32" patternUnits="userSpaceOnUse"><path d="M1 1h20v12H1zM24 1h22v12H24zM1 16h11v13H1zM15 16h31v13H15z" fill="#252b2d" fill-opacity=".18"/><path d="M2 13h18M25 13h20M16 29h29" stroke="#d99b28" stroke-opacity=".045"/></pattern><radialGradient id="amber" cx=".1" cy="0" r="1"><stop stop-color="#e8a925" stop-opacity=".055"/><stop offset="1" stop-color="#e8a925" stop-opacity="0"/></radialGradient></defs>
<style>.cursor{{animation:blink 1.6s steps(1) infinite}}.pulse{{animation:pulse 4s ease-in-out infinite}}@keyframes blink{{50%{{opacity:0}}}}@keyframes pulse{{50%{{opacity:.25}}}}@media(prefers-reduced-motion:reduce){{.cursor,.pulse{{animation:none}}}}</style>
<rect width="{w}" height="{h}" fill="#0d1117"/>
<rect x="4" y="4" width="{w-8}" height="{h-8}" fill="url(#pixels)"/><rect width="{w}" height="{h}" fill="url(#amber)"/>
<path d="M3 16V{h-16}M{w-3} 16V{h-16}" stroke="#725420" stroke-opacity=".3" fill="none"/>
<g stroke="#ffbf36" stroke-width="2" fill="none" shape-rendering="crispEdges">{corners}</g>
<g font-family="Consolas,DejaVu Sans Mono,monospace">{body}</g></svg>\n'''


def project_card(config, mobile=False):
    w, pad, title_size, size, chars = (200, 14, 29, 15, 18) if mobile else (480, 24, 34, 18, 37)
    title_lines = textwrap.wrap(config['project_name'], 9 if mobile else 20)
    desc_lines = textwrap.wrap(config['description'], chars)
    body = text(pad, 29, 'LIFETIME PROJECT', 13, '#d9a342')
    y = 74
    for line in title_lines:
        title_width = len(line) * title_size * .6
        body += text(pad, y, line, title_size, '#ffbf36', f'font-weight="bold" textLength="{title_width}" lengthAdjust="spacingAndGlyphs"')
        y += title_size + 8
    cursor_x = min(w-pad-8, pad+title_width+8)
    cursor_y = y-title_size-8-title_size*.76
    body += f'<rect class="cursor" x="{cursor_x}" y="{cursor_y}" width="8" height="{title_size*.8}" fill="#ffbf36"/>'
    y += 10
    for line in desc_lines:
        body += text(pad, y, line, size)
        y += size + 7
    return panel(w, max(182, y + 14), body, frame='top')


def tools_card(icons, mobile=False):
    w, cols, dx, y0 = (200, 2, 88, 82) if mobile else (400, 5, 74, 83)
    body = text(w/2, 27, 'ЯЗЫКИ И ИНСТРУМЕНТЫ' if not mobile else 'ЯЗЫКИ / ИНСТРУМЕНТЫ', 12 if mobile else 14, '#d9a342', 'text-anchor="middle"')
    body += text(w/2, 47, 'CODE · WEB · AUTOMATION', 9 if mobile else 11, '#998155', 'text-anchor="middle"')
    for i, (name, label) in enumerate(ICONS):
        cx = (w - cols*dx)/2 + dx*(i % cols + .5)
        y = y0 + (i//cols)*79
        source = re.sub(r'<\?xml[^>]*\?>', '', icons[name]).strip()
        source = source.replace('<svg ', f'<svg x="{cx-18}" y="{y-22}" width="36" height="36" ', 1)
        body += f'<rect x="{cx-26}" y="{y-28}" width="52" height="52" fill="#0d1117" stroke="#45371c"/>{source}'
        body += text(cx, y+40, label, 10, '#c8ab71', 'text-anchor="middle"')
    h = y0 + ((len(ICONS)-1)//cols)*79 + 57
    return panel(w, h, body)


def build(config, icons, readme):
    validate(config)
    out = {}
    for mobile in [False, True]:
        suffix = '-mobile' if mobile else ''
        w = 200 if mobile else 480
        out[f'assets/current-project{suffix}.svg'] = project_card(config, mobile)
        release_body = f'<path d="M{14 if mobile else 24} 1H{w-24}" stroke="#74541d" stroke-opacity=".6"/>' + text(14 if mobile else 24, 26, 'РЕЛИЗЫ ↗', 14, '#ffbf36')
        out[f'assets/project-releases{suffix}.svg'] = panel(w, 42, release_body, frame='bottom')
        out[f'assets/tools-panel{suffix}.svg'] = tools_card(icons, mobile)
    version = hashlib.sha256(''.join(out.values()).encode()).hexdigest()[:12]
    out = {name.replace('.svg', f'-{version}.svg'): content for name, content in out.items()}
    base = 'https://raw.githubusercontent.com/zarell1/zarell1/main/assets/'
    def picture(name, width, alt):
        return f'<picture><source media="(max-width: 600px)" srcset="{base}{name}-mobile-{version}.svg"><img src="{base}{name}-{version}.svg" width="{width}" alt="{ESC(alt)}"></picture>'
    section = f'''<!-- PROFILE:START -->
<!-- Generated from profile.json by scripts/render_profile.py. -->
<table>
<tr>
<td width="440" valign="top">
<a href="{ESC(config['project_url'])}">{picture('current-project',480,config['project_name']+' — '+config['description'])}</a><br>
<a href="{ESC(config['releases_url'])}">{picture('project-releases',480,'Релизы '+config['project_name'])}</a>
</td>
<td width="400" valign="top">{picture('tools-panel',400,'Языки и инструменты: '+', '.join(label for _,label in ICONS))}</td>
</tr>
</table>
<!-- PROFILE:END -->'''
    if readme.count('<!-- PROFILE:START -->') != 1 or readme.count('<!-- PROFILE:END -->') != 1:
        raise ValueError('README must contain exactly one PROFILE marker pair')
    out['README.md'] = re.sub(r'<!-- PROFILE:START -->.*?<!-- PROFILE:END -->', lambda _: section, readme, flags=re.S)
    return out


if __name__ == '__main__':
    config = json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
    icons = {name: (ROOT/f'assets/icons/{name}.svg').read_text(encoding='utf-8') for name, _ in ICONS}
    result = build(config, icons, (ROOT/'README.md').read_text(encoding='utf-8'))
    # Replace only our obsolete content-addressed outputs; original assets stay intact.
    assets = (ROOT/'assets').resolve()
    for previous in assets.glob('*.svg'):
        if re.fullmatch(r'(current-project|project-releases|tools-panel)(-mobile)?-[0-9a-f]{12}\.svg', previous.name):
            if previous.resolve().parent == assets and f'assets/{previous.name}' not in result:
                previous.unlink()
    for filename, content in result.items():
        (ROOT/filename).write_text(content, encoding='utf-8', newline='\n')
    print(f'Rendered {len(result)} files')
