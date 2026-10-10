"""Seal and fail-closed verify archive payloads; never execute archive contents."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile

ZIP = Path('may-portfolio-full-archive.zip')
META = Path('archive-integrity.json')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def inspect():
    with zipfile.ZipFile(ZIP) as archive:
        files = {}
        seen = set()
        for item in archive.infolist():
            name = item.filename
            p = PurePosixPath(name)
            if (name in seen or p.is_absolute() or '..' in p.parts or '\\' in name
                    or ':' in name or str(p) != name.rstrip('/')
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError(f'Unsafe or duplicate ZIP entry: {name}')
            seen.add(name)
            if item.is_dir():
                continue
            h = hashlib.sha256()
            with archive.open(item) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(block)
            files[name] = {'size': item.file_size, 'sha256': h.hexdigest()}
        manifest = json.loads(archive.read('manifest.json'))
        works = manifest.get('works', [])
        if len(works) != 31 or any(w.get('status') != 'ok' for w in works):
            raise ValueError('Expected 31 successful works; partial archives are rejected')
        for i, work in enumerate(works, 1):
            for key, expected in [('pdf', f'works/{i:02d}.pdf'),
                                  ('mhtml', f'works/{i:02d}.mhtml'),
                                  ('thumbnail', f'thumbs/{i:02d}.jpg')]:
                if work.get(key) != expected or not files.get(expected, {}).get('size'):
                    raise ValueError(f'Manifest/content mismatch: {expected}')
        for name in ['README.txt', 'index.html', 'manifest.json']:
            if not files.get(name, {}).get('size'):
                raise ValueError(f'Missing required content: {name}')
        return files

def source(attempt):
    return dict(repository=os.environ['GITHUB_REPOSITORY'],
                run_id=os.environ['GITHUB_RUN_ID'], run_attempt=str(attempt),
                head_sha=os.environ['GITHUB_SHA'], ref=os.environ['GITHUB_REF'])

def main():
    mode = sys.argv[1]
    if mode == 'seal':
        files = inspect()
        data = dict(schema=1, source=source(os.environ['GITHUB_RUN_ATTEMPT']),
                    archive_sha256=digest(ZIP), files=files)
        META.write_text(json.dumps(data, sort_keys=True, indent=2) + '\n')
        with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
            out.write(f"archive_sha256={data['archive_sha256']}\n")
            out.write(f'metadata_sha256={digest(META)}\n')
            out.write(f"source_attempt={os.environ['GITHUB_RUN_ATTEMPT']}\n")
        return
    if mode != 'verify':
        raise ValueError('Expected seal or verify')
    if digest(META) != os.environ['EXPECTED_METADATA_SHA256']:
        raise ValueError('Integrity metadata SHA-256 mismatch')
    data = json.loads(META.read_text())
    attempt = int(os.environ['SOURCE_ATTEMPT'])
    if attempt < 1 or attempt > int(os.environ['GITHUB_RUN_ATTEMPT']):
        raise ValueError('Invalid source attempt')
    if data.get('schema') != 1 or data.get('source') != source(attempt):
        raise ValueError('Source repository/run/attempt/commit/ref mismatch')
    if digest(ZIP) != os.environ['EXPECTED_ARCHIVE_SHA256'] or data['archive_sha256'] != digest(ZIP):
        raise ValueError('Archive SHA-256 mismatch')
    if inspect() != data['files']:
        raise ValueError('File inventory/size/hash mismatch')
    target = Path('_archive_src')
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()
    with zipfile.ZipFile(ZIP) as archive:
        archive.extractall(target)

if __name__ == '__main__':
    main()
