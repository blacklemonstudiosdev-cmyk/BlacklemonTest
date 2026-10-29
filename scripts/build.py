#!/usr/bin/env python3
"""
BlackLemon Studios - content build.

Scans `products/` and `blogs/` and writes `data/data.js`
(read by the site as `window.BLACKLEMON_DATA`).

    python3 scripts/build.py

Download counter (optional, per product): drop a `counter.json` file into
an app's product folder, e.g. products/nexus/counter.json:

    { "baseline": 23 }

The build reads the real download counts of that app's GitHub release
files, anchors them so the number shows `baseline` right now, and grows
it as real downloads come in. Set GITHUB_TOKEN in the environment (the
GitHub Action does this automatically) for a higher API rate limit. If a
fetch fails, the last known number is kept.

No third-party packages required.
"""
import os
import re
import json
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.avif')
FONT_EXT = ('.ttf', '.otf', '.woff2', '.woff')
RESERVED_DIRS = ('download-counter', 'counter', '.counter')
GH_TOKEN = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')


def rel(path):
    return os.path.relpath(path, ROOT).replace('\\', '/')


def read_json_file(path):
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            return {str(k).lower(): v for k, v in raw.items()}
        print('  ! ' + rel(path) + ' is not a JSON object; ignoring.')
    except json.JSONDecodeError as e:
        print('  ! Invalid JSON in ' + rel(path) + ': ' + str(e))
    return {}


def read_first_json(folder):
    for name in sorted(os.listdir(folder)):
        if name.lower().endswith('.json'):
            return read_json_file(os.path.join(folder, name))
    return {}


def read_product_def(folder):
    """Product definition: prefer text.json; never let counter.json shadow it."""
    tj = os.path.join(folder, 'text.json')
    if os.path.isfile(tj):
        return read_json_file(tj)
    for name in sorted(os.listdir(folder)):
        if name.lower().endswith('.json') and name.lower() != 'counter.json':
            return read_json_file(os.path.join(folder, name))
    return {}


def find_image(folder, prefer=None):
    files = [f for f in sorted(os.listdir(folder)) if f.lower().endswith(IMG_EXT)]
    if prefer:
        for f in files:
            if os.path.splitext(f)[0].lower() == prefer:
                return os.path.join(folder, f)
    return os.path.join(folder, files[0]) if files else None


def numbered_images(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith(IMG_EXT)]

    def key(f):
        m = re.search(r'(\d+)', os.path.splitext(f)[0])
        return (0, int(m.group(1))) if m else (1, f.lower())
    return [os.path.join(folder, f) for f in sorted(files, key=key)]


def item_dirs(base):
    p = os.path.join(ROOT, base)
    if not os.path.isdir(p):
        return []
    out = []
    for name in sorted(os.listdir(p)):
        full = os.path.join(p, name)
        if os.path.isdir(full) and not name.startswith(('.', '_')):
            out.append((name, full))
    return out


def to_int(v, default=0):
    try:
        return int(re.sub(r'[^0-9-]', '', str(v)))
    except (TypeError, ValueError):
        return default


# ---------- download counter ----------
def gh_json(url):
    req = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'blacklemon-build',
    })
    if GH_TOKEN:
        req.add_header('Authorization', 'Bearer ' + GH_TOKEN)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def repo_download_total(urls):
    """Sum download_count of every release asset in the repos these GitHub
    release URLs point to. Returns an int, or None if it can't be fetched."""
    repos = []
    for u in urls:
        m = re.match(r'https?://github\.com/([^/]+)/([^/]+)/releases/', u or '')
        if m:
            pair = (m.group(1), m.group(2))
            if pair not in repos:
                repos.append(pair)
    if not repos:
        return None
    total = 0
    try:
        for owner, repo in repos:
            data = gh_json('https://api.github.com/repos/%s/%s/releases?per_page=100' % (owner, repo))
            for release in data:
                for asset in release.get('assets', []):
                    total += int(asset.get('download_count') or 0)
        return total
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TypeError) as e:
        print('  ! download-count fetch failed: ' + str(e))
        return None


def build_counter(cfg, urls, prev):
    baseline = to_int(cfg.get('baseline'), 0)
    prev = prev or {}
    prev_anchor = prev.get('anchor')
    prev_downloads = prev.get('downloads')
    live = repo_download_total([u for u in urls if u])
    if live is not None:
        anchor = prev_anchor if isinstance(prev_anchor, int) else live
        downloads = baseline + max(0, live - anchor)
    else:
        anchor = prev_anchor if isinstance(prev_anchor, int) else None
        downloads = prev_downloads if isinstance(prev_downloads, int) else baseline
    return {'baseline': baseline, 'anchor': anchor, 'downloads': downloads}


def load_prev_counters():
    p = os.path.join(ROOT, 'data', 'data.js')
    if not os.path.isfile(p):
        return {}
    try:
        txt = open(p, encoding='utf-8').read()
        i, j = txt.find('{'), txt.rfind('}')
        data = json.loads(txt[i:j + 1])
        return {pr.get('slug'): pr.get('counter')
                for pr in data.get('products', []) if pr.get('counter')}
    except Exception:
        return {}


# ---------- products ----------
def build_card(folder):
    data = read_first_json(folder)
    img = find_image(folder, prefer='image')
    return {
        'title': data.get('title', ''),
        'body':  data.get('body', ''),
        'image': rel(img) if img else '',
    }


def find_counter_cfg(folder):
    cf = os.path.join(folder, 'counter.json')
    if os.path.isfile(cf):
        return read_json_file(cf)
    for rn in RESERVED_DIRS:
        dd = os.path.join(folder, rn)
        if os.path.isdir(dd):
            return read_first_json(dd)
    return None


def find_font_file(folder, font_value):
    """A dropped-in title font file, if any. Prefers one whose name matches the
    `font` field; otherwise the first font file found."""
    files = [f for f in sorted(os.listdir(folder))
             if f.lower().endswith(FONT_EXT) and os.path.isfile(os.path.join(folder, f))]
    if not files:
        return None
    base = os.path.splitext(str(font_value or ''))[0].strip().lower()
    for f in files:
        if os.path.splitext(f)[0].lower() == base:
            return os.path.join(folder, f)
    return os.path.join(folder, files[0])


def build_product(slug, folder, prev_counters):
    d = read_product_def(folder)
    mockup = find_image(folder, prefer='mockup')
    cards = []
    for name in sorted(os.listdir(folder)):
        if name in RESERVED_DIRS:
            continue
        sub = os.path.join(folder, name)
        if os.path.isdir(sub) and not name.startswith(('.', '_')):
            card = build_card(sub)
            if card.get('image') or card.get('title') or card.get('body'):
                cards.append(card)
    ptype = (d.get('type') or 'website').lower()
    entry = {
        'slug':       slug,
        'type':       ptype,
        'name':       d.get('name') or slug,
        'font':       d.get('font', ''),
        'fontWeight': d.get('fontweight', ''),
        'lede':       d.get('lede', ''),
        'status':     d.get('status', 'Available Now'),
        'order':      to_int(d.get('order'), 999),
        'disclaimer': d.get('disclaimer', ''),
        'mockup':     rel(mockup) if mockup else '',
        'cards':      cards,
    }
    if ptype == 'app':
        mac = d.get('mac') or {}
        entry['mac'] = {
            'silicon': (mac.get('silicon', '') if isinstance(mac, dict) else ''),
            'intel':   (mac.get('intel', '') if isinstance(mac, dict) else ''),
        }
        entry['windows'] = d.get('windows', '')
    else:
        entry['url'] = d.get('url', '')
        entry['button'] = d.get('button') or ('Open ' + entry['name'] + ' \u2192')

    font_file = find_font_file(folder, entry['font'])
    if font_file:
        entry['fontFile'] = rel(font_file)

    counter_cfg = find_counter_cfg(folder)
    if counter_cfg is not None:
        if ptype == 'app':
            urls = [entry['mac'].get('silicon'), entry['mac'].get('intel'), entry.get('windows')]
        else:
            urls = [entry.get('url')]
        entry['counter'] = build_counter(counter_cfg, urls, (prev_counters or {}).get(slug))
    return entry


def build_products():
    prev = load_prev_counters()
    out = [build_product(slug, folder, prev) for slug, folder in item_dirs('products')]
    out.sort(key=lambda p: (p['order'], p['name'].lower()))
    return out


# ---------- blogs ----------
def build_blog(slug, folder):
    d = read_first_json(folder)
    imgs = [rel(p) for p in numbered_images(folder)]
    return {
        'slug':   slug,
        'title':  d.get('title') or 'Untitled',
        'author': d.get('author', ''),
        'date':   d.get('date', ''),
        'year':   d.get('year', ''),
        'cover':  imgs[0] if imgs else '',
        'images': imgs,
        'body':   d.get('body', ''),
    }


def build_blogs():
    base = os.path.join(ROOT, 'blogs')
    if not os.path.isdir(base):
        return []
    out = []
    for name in sorted(os.listdir(base)):
        if name.startswith(('.', '_')):
            continue
        full = os.path.join(base, name)
        if os.path.isdir(full):
            out.append(build_blog(name, full))
        elif name.lower().endswith('.json'):
            d = read_json_file(full)
            out.append({
                'slug': os.path.splitext(name)[0], 'title': d.get('title') or 'Untitled',
                'author': d.get('author', ''), 'date': d.get('date', ''),
                'year': d.get('year', ''), 'cover': '', 'images': [],
                'body': d.get('body', ''),
            })
    return out


def main():
    data = {'products': build_products(), 'blogs': build_blogs()}
    out_dir = os.path.join(ROOT, 'data')
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'data.js'), 'w', encoding='utf-8') as f:
        f.write('window.BLACKLEMON_DATA = ' + json.dumps(data, indent=2, ensure_ascii=False) + ';\n')
    counts = {k: len(v) for k, v in data.items()}
    dl = [(p['slug'], p['counter']['downloads']) for p in data['products'] if p.get('counter')]
    print('Built data/data.js: ' + str(counts) + (' | counters: ' + str(dl) if dl else ''))


if __name__ == '__main__':
    main()
