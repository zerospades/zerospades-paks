#!/usr/bin/env python3
"""Static checks for the paks in this repository.

Checks what can be checked without running the game; PORTING.md explains each
rule. Errors fail the run, warnings are printed for the reviewer.

usage: check_paks.py [--base PATH ...] [PAK ...]

  --base PATH   base game assets, used to resolve references a pak does not
                ship itself. PATH can be a Resources directory, a .pak/.zip
                (paks nested in a zip are read too), or a text file with one
                path per line. Repeatable.
  PAK           paks to check (default: every *.pak next to this script's
                parent directory).

Sound channel checks need ffprobe on PATH; they are skipped with a warning
otherwise.
"""
import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

WEAPON_TAGS = {'SEMI', 'SMG', 'SHOTGUN', 'SPADE', 'GRENADE'}
GUN_TAGS = {'SEMI', 'SMG', 'SHOTGUN'}
TAGS = WEAPON_TAGS | {'FONT', 'SFX', 'VFX'}
NAME_RE = re.compile(r'^([A-Z]+)-([A-Za-z0-9]+)-([A-Za-z0-9]*)\.pak$')
STRING_RE = re.compile(r'"([^"\n]*)"')
ASSET_EXT = ('.kv6', '.png', '.tga', '.jpg', '.opus', '.ogg', '.wav', '.ttf', '.otf', '.as', '.vxl')


def read_zip_names(data_or_path, out):
    with zipfile.ZipFile(data_or_path) as z:
        for n in z.namelist():
            if n.endswith('/'):
                continue
            if n.lower().endswith(('.pak', '.zip')):
                read_zip_names(io.BytesIO(z.read(n)), out)
            else:
                out.add(n)


def load_base(paths):
    names = set()
    for p in paths:
        if os.path.isdir(p):
            for dp, _, fs in os.walk(p):
                for f in fs:
                    full = os.path.join(dp, f)
                    if not os.path.isfile(full):
                        continue  # dangling symlink
                    if f.lower().endswith(('.pak', '.zip')):
                        read_zip_names(full, names)
                    else:
                        names.add(os.path.relpath(full, p).replace(os.sep, '/'))
        elif p.lower().endswith(('.pak', '.zip')):
            read_zip_names(p, names)
        else:
            names.update(l.strip() for l in open(p) if l.strip())
    # a `.weak` file is served under its plain name
    return {n[:-5] if n.endswith('.weak') else n for n in names}


class Report:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def error(self, pak, msg):
        self.errors += 1
        print(f'::error file={pak}::{msg}' if os.environ.get('GITHUB_ACTIONS') else f'ERROR   {pak}: {msg}')

    def warn(self, pak, msg):
        self.warnings += 1
        print(f'::warning file={pak}::{msg}' if os.environ.get('GITHUB_ACTIONS') else f'warning {pak}: {msg}')


def strip_comments(src):
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
    return re.sub(r'//[^\n]*', '', src)


def getter_body(src, name):
    m = re.search(r'Vector3\s+' + name + r'\s*\{', src)
    if not m:
        return None
    depth, i = 0, m.end() - 1
    for j in range(i, len(src)):
        depth += {'{': 1, '}': -1}.get(src[j], 0)
        if depth == 0:
            return src[i:j + 1]
    return src[i:]


def function_body(src, signature):
    m = re.search(signature + r'\s*\([^)]*\)\s*\{', src)
    if not m:
        return None
    depth, i = 0, m.end() - 1
    for j in range(i, len(src)):
        depth += {'{': 1, '}': -1}.get(src[j], 0)
        if depth == 0:
            return src[i:j + 1]
    return src[i:]


def channels(z, name, tmp):
    path = os.path.join(tmp, 'probe' + os.path.splitext(name)[1])
    with open(path, 'wb') as f:
        f.write(z.read(name))
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                          'stream=channels', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout.strip()
    return int(out) if out.isdigit() else None


def check_pak(path, base, report, have_ffprobe, tmp):
    pak = os.path.basename(path)
    m = NAME_RE.match(pak)
    tag = None
    if not m:
        report.error(pak, 'name does not follow TAG-NAME-AUTHOR.pak (see README.md)')
    else:
        tag = m.group(1)
        if tag not in TAGS:
            report.warn(pak, f'unknown tag {tag}')

    z = zipfile.ZipFile(path)
    files = [n for n in z.namelist() if not n.endswith('/')]
    exact = set(files)
    lower = {n.lower(): n for n in files}
    base_lower = {n.lower() for n in base}

    for n in files:
        low = n.lower()
        if low.endswith('.weak'):
            report.error(pak, f'{n}: .weak files lose to any plain file; remove it')
        elif low.endswith('.wav'):
            report.error(pak, f'{n}: convert sounds to .opus')
        elif os.path.basename(n).startswith('.') or '__MACOSX' in n:
            report.error(pak, f'{n}: stray system file')

    scripts = {n: strip_comments(z.read(n).decode('utf-8', 'replace')) for n in files if n.lower().endswith('.as')}

    # every quoted string that looks like an asset path; a string ending in `/`
    # is a directory the script builds paths in at runtime
    refs, prefixes = {}, []
    for name, src in scripts.items():
        for s in STRING_RE.findall(src):
            if '/' not in s or ' ' in s:
                continue
            if s.endswith('/'):
                prefixes.append(s.lower())
            elif s.lower().endswith(ASSET_EXT):
                refs.setdefault(s, set()).add(name)

    for ref, users in sorted(refs.items()):
        where = ', '.join(sorted(users))
        if ref in exact or ref in base:
            continue
        if ref.lower() in lower:
            report.error(pak, f'{where}: "{ref}" only matches "{lower[ref.lower()]}" by ignoring case; use the exact name')
        elif ref.lower() in base_lower:
            report.warn(pak, f'{where}: "{ref}" only matches a base game file by ignoring case')
        else:
            report.error(pak, f'{where}: "{ref}" is not in the pak or the base game')

    if tag in WEAPON_TAGS:
        used = {r.lower() for r in refs}
        for n in files:
            low = n.lower()
            if low.endswith('.as') or low in used or n in base or low in base_lower:
                continue
            if any(low.startswith(p) for p in prefixes):
                continue
            report.error(pak, f'{n}: no script loads it and it does not replace a base game file; remove it')

    # view weapon rules
    for name, src in scripts.items():
        parts = name.split('/')
        if len(parts) != 4 or parts[:2] != ['Scripts', 'Skin'] or parts[3] != 'View.as':
            continue
        weapon = parts[2]
        if weapon not in ('Rifle', 'SMG', 'Shotgun', 'Spade', 'Grenade', 'Block'):
            continue
        matrix = function_body(src, r'Matrix4\s+GetViewWeaponMatrix')
        if matrix is not None:
            if 'cg_viewWeaponSide' not in matrix or not re.search(r'CreateScaleMatrix\s*\(\s*Vector3\s*\(\s*-1', matrix):
                report.error(pak, f'{name}: GetViewWeaponMatrix() is overridden without the left-handed mirror')
            if 'cg_viewWeaponX' not in matrix:
                report.warn(pak, f'{name}: GetViewWeaponMatrix() ignores cg_viewWeaponX/Y/Z')
        elif weapon in ('Spade', 'Grenade', 'Block') and 'cg_viewWeaponSide' not in src and 'BasicViewWeapon' not in src:
            report.error(pak, f'{name}: does not handle cg_viewWeaponSide')
        for getter in ('MuzzlePosition', 'CaseEjectPosition'):
            body = getter_body(src, getter)
            if body and 'eyeMatrix' in body:
                report.error(pak, f'{name}: {getter} must be in eye space; remove eyeMatrix (see PORTING.md)')
        if weapon in ('Rifle', 'SMG', 'Shotgun'):
            if 'cg_weaponCharms' not in src:
                report.error(pak, f'{name}: weapon charms (cg_weaponCharms) are not drawn')
            if getter_body(src, 'MuzzlePosition') is None and matrix is not None:
                report.warn(pak, f'{name}: no MuzzlePosition; tracers start at the stock gun\'s muzzle')
            if 'cg_reflexScope' not in src:
                report.warn(pak, f'{name}: cg_reflexScope is ignored (fine if the gun has its own optic)')
        for s in STRING_RE.findall(src):
            if re.fullmatch(r'Gfx/[^/]+\.(png|tga)', s, re.I) and s not in base and s.lower() not in base_lower:
                report.warn(pak, f'{name}: "{s}" is a generic name in Gfx/; prefer Gfx/Weapons/<Mod>/...')

    # what other players hear must be mono, or it plays at full volume map-wide
    tp_sounds = set()
    for name, src in scripts.items():
        if name.endswith('/ThirdPerson.as'):
            tp_sounds.update(s for s in STRING_RE.findall(src) if s.lower().endswith(('.opus', '.ogg', '.wav')))
    for s in sorted(tp_sounds):
        if 'stereo' in os.path.basename(s).lower() or s not in exact:
            continue
        if not have_ffprobe:
            continue
        ch = channels(z, s, tmp)
        if ch and ch > 1:
            report.error(pak, f'{s}: played to other players in 3D but has {ch} channels; downmix to mono')


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', action='append', default=[])
    ap.add_argument('paks', nargs='*')
    args = ap.parse_args()

    paks = args.paks or sorted(os.path.join(root, f) for f in os.listdir(root) if f.endswith('.pak'))
    base = load_base(args.base)
    if not base:
        print('warning: no --base given; references to base game files will be reported as missing')
    have_ffprobe = shutil.which('ffprobe') is not None
    if not have_ffprobe:
        print('warning: ffprobe not found; skipping sound channel checks')

    report = Report()
    with tempfile.TemporaryDirectory() as tmp:
        for p in paks:
            check_pak(p, base, report, have_ffprobe, tmp)
    print(f'{len(paks)} paks checked: {report.errors} errors, {report.warnings} warnings')
    return 1 if report.errors else 0


if __name__ == '__main__':
    sys.exit(main())
