"""V1 shared helpers: read-only hashing with receipts. No writes outside V1 evidence + /tmp/v1-*."""
import datetime, hashlib, json, os, subprocess
from pathlib import Path

E = Path(__file__).resolve().parent
REPO = E.parents[2]
SSD = Path('/Volumes/Extreme SSD')
SHARE = Path('/Volumes/share/ssx3')
LIVE = Path('/tmp/e18-mpeg-link/runtime')
CHUNK = 8 * 1024 * 1024

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha_file(path, chunk=CHUNK):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def pin_file(path):
    """One read: stat + full sha256. Caller separates passes in time."""
    p = Path(path)
    t0 = utc()
    s = p.stat()
    digest = sha_file(p)
    t1 = utc()
    return {'bytes': s.st_size, 'mtime': int(s.st_mtime), 'sha256': digest,
            't0': t0, 't1': t1}

def save(name, obj):
    (E / name).write_text(json.dumps(obj, indent=1) + '\n')

def load(name):
    return json.loads((E / name).read_text())

def run(argv, **kw):
    r = subprocess.run(argv, capture_output=True, text=True, **kw)
    return {'argv': argv, 'rc': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}

def git_blob_id(repo, relpath):
    r = run(['git', '-C', str(repo), 'rev-parse', f'HEAD:{relpath}'])
    return r['stdout'].strip() if r['rc'] == 0 else None

def gnu_build_id(path):
    """Read-only GNU BuildID parse from an ELF file. Returns hex or None."""
    try:
        with Path(path).open('rb') as f:
            eh = f.read(64)
            if len(eh) < 64 or eh[:4] != b'\x7fELF':
                return None
            little = eh[5] == 1
            bo = 'little' if little else 'big'
            e_phoff = int.from_bytes(eh[32:40] if eh[4] == 2 else eh[28:32], bo)
            e_phentsize = int.from_bytes(eh[54:56] if eh[4] == 2 else eh[42:44], bo)
            e_phnum = int.from_bytes(eh[56:58] if eh[4] == 2 else eh[44:46], bo)
            is64 = eh[4] == 2
            for i in range(e_phnum):
                f.seek(e_phoff + i * e_phentsize)
                ph = f.read(e_phentsize)
                p_type = int.from_bytes(ph[0:4], bo)
                if p_type != 4:  # PT_NOTE
                    continue
                if is64:
                    p_offset = int.from_bytes(ph[8:16], bo)
                    p_filesz = int.from_bytes(ph[32:40], bo)
                else:
                    p_offset = int.from_bytes(ph[4:8], bo)
                    p_filesz = int.from_bytes(ph[16:20], bo)
                f.seek(p_offset)
                note = f.read(p_filesz)
                o = 0
                while o + 12 <= len(note):
                    namesz = int.from_bytes(note[o:o+4], bo)
                    descsz = int.from_bytes(note[o+4:o+8], bo)
                    ntype = int.from_bytes(note[o+8:o+12], bo)
                    name = note[o+12:o+12+namesz].rstrip(b'\0')
                    desc_off = o + 12 + ((namesz + 3) // 4) * 4
                    desc = note[desc_off:desc_off+descsz]
                    if name == b'GNU' and ntype == 3:
                        return desc.hex()
                    o = desc_off + ((descsz + 3) // 4) * 4
    except (OSError, ValueError, IndexError):
        return None
    return None

def elf_magic(path, n=4):
    try:
        with Path(path).open('rb') as f:
            return f.read(n).hex()
    except OSError:
        return None

def list_plain(d):
    """Non-sidecar entries of a flat dir: (visible_names, sidecar_count)."""
    p = Path(d)
    names = sorted(x.name for x in p.iterdir())
    side = [n for n in names if n.startswith('._')]
    vis = [n for n in names if not n.startswith('._') and (p / n).is_file()]
    return vis, len(side)
