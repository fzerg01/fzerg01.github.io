from pathlib import Path
import html
import json
import re
import shutil
import subprocess

SRC = Path('_archive_src')
ROOT = Path('may-portfolio/archive-static')


def compress_pdf(src: Path, dst: Path):
    cmd = [
        'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', '-dPDFSETTINGS=/ebook',
        '-dNOPAUSE', '-dQUIET', '-dBATCH', '-dDetectDuplicateImages=true',
        '-dDownsampleColorImages=true', '-dColorImageResolution=150',
        '-dDownsampleGrayImages=true', '-dGrayImageResolution=150',
        '-sOutputFile=' + str(dst), str(src)
    ]
    subprocess.run(cmd, check=True)
    if dst.stat().st_size > 95 * 1024 * 1024:
        tmp = dst.with_suffix('.small.pdf')
        cmd = [
            'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', '-dPDFSETTINGS=/screen',
            '-dNOPAUSE', '-dQUIET', '-dBATCH', '-sOutputFile=' + str(tmp), str(dst)
        ]
        subprocess.run(cmd, check=True)
        tmp.replace(dst)
    if dst.stat().st_size > 99 * 1024 * 1024:
        raise RuntimeError(f'PDF still exceeds GitHub single-file limit: {dst}')


def main():
    manifest = json.loads((SRC / 'manifest.json').read_text(encoding='utf-8'))
    if len(manifest.get('works', [])) != 31:
        raise RuntimeError('Expected 31 archived works')
    if any(w.get('status') != 'ok' for w in manifest['works']):
        bad = [i + 1 for i, w in enumerate(manifest['works']) if w.get('status') != 'ok']
        raise RuntimeError(f'Archive contains failed works: {bad}')

    if ROOT.exists():
        shutil.rmtree(ROOT)
    (ROOT / 'pages').mkdir(parents=True)
    (ROOT / 'files').mkdir(parents=True)
    (ROOT / 'thumbs').mkdir(parents=True)

    shutil.copy2(SRC / 'manifest.json', ROOT / 'manifest.json')
    if (SRC / 'README.txt').exists():
        shutil.copy2(SRC / 'README.txt', ROOT / 'README.txt')
    for thumb in (SRC / 'thumbs').glob('*.jpg'):
        shutil.copy2(thumb, ROOT / 'thumbs' / thumb.name)

    for i, w in enumerate(manifest['works'], 1):
        n = f'{i:02d}'
        src_pdf = SRC / 'works' / f'{n}.pdf'
        if not src_pdf.exists():
            raise RuntimeError(f'Missing {src_pdf}')
        compress_pdf(src_pdf, ROOT / 'files' / f'{n}.pdf')

    css = '''
:root{--paper:#f3f0e9;--ink:#20231e;--muted:#73776f;--moss:#66705f;--line:#cbc9c0;--dark:#1d211c}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif}a{color:inherit}
header{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;align-items:center;padding:15px 28px;background:rgba(243,240,233,.94);border-bottom:1px solid var(--line);backdrop-filter:blur(10px)}
.brand{text-decoration:none}.brand strong{display:block;font-family:"Noto Serif TC","PMingLiU",serif;font-size:18px}.brand span{font-size:9px;letter-spacing:.15em;color:var(--muted)}
main{width:min(1180px,calc(100% - 32px));margin:auto;padding:42px 0 80px}.meta{font-size:11px;letter-spacing:.12em;color:var(--moss)}h1{font:500 clamp(30px,5vw,58px)/1.25 "Noto Serif TC","PMingLiU",serif;margin:10px 0 16px}.note{color:var(--muted);font-size:13px}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}.btn{display:inline-block;padding:10px 14px;border:1px solid var(--ink);text-decoration:none;font-size:12px}.btn.dark{background:var(--dark);color:white}.viewer{height:78vh;min-height:620px;border:1px solid var(--line);background:#fff}.viewer iframe{width:100%;height:100%;border:0}.mobile-link{display:none}.archive-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:38px}.card{display:block;text-decoration:none;border-top:1px solid var(--line);padding-top:14px}.card img{width:100%;aspect-ratio:16/10;object-fit:cover;background:#ddd}.card small{display:block;color:var(--moss);margin-top:10px}.card strong{display:block;font-family:"Noto Serif TC","PMingLiU",serif;font-size:19px;line-height:1.45;margin-top:4px}@media(max-width:780px){header{padding:12px 16px}.archive-grid{grid-template-columns:1fr}.viewer{height:65vh;min-height:460px}.mobile-link{display:inline-block}}
'''.strip()
    (ROOT / 'archive.css').write_text(css, encoding='utf-8')

    cards = []
    for i, w in enumerate(manifest['works'], 1):
        n = f'{i:02d}'
        title = html.escape(w['title'])
        cat = html.escape(w['category'])
        url = html.escape(w['url'], quote=True)
        page = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}｜許雅眉 May 封存版</title><link rel="stylesheet" href="../archive.css"></head>
<body><header><a class="brand" href="../../index.html"><strong>許雅眉 May</strong><span>ARCHIVED WORK</span></a><a href="../index.html">全部封存作品</a></header>
<main><div class="meta">ARCHIVE · {n} · {cat}</div><h1>{title}</h1><p class="note">這是本站保存的完整頁面快照，全文與圖片已封存於本網站，不依賴幸福空間原站。</p>
<div class="actions"><a class="btn dark" href="../files/{n}.pdf" target="_blank">開啟完整封存 PDF</a><a class="btn" href="{url}" target="_blank" rel="noopener">查看原始來源 ↗</a><a class="btn" href="../../index.html#works">回作品集</a></div>
<div class="viewer"><iframe src="../files/{n}.pdf#view=FitH" title="{title}"></iframe></div><p class="note mobile-link">若手機沒有直接顯示 PDF，請點上方「開啟完整封存 PDF」。</p></main></body></html>'''
        (ROOT / 'pages' / f'{n}.html').write_text(page, encoding='utf-8')
        cards.append(f'<a class="card" href="pages/{n}.html"><img src="thumbs/{n}.jpg" alt=""><small>{n} · {cat}</small><strong>{title}</strong></a>')

    index = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>許雅眉 May｜完整作品封存</title><link rel="stylesheet" href="archive.css"></head>
<body><header><a class="brand" href="../index.html"><strong>許雅眉 May</strong><span>FULL ARCHIVE</span></a><a href="../index.html">回作品集</a></header>
<main><div class="meta">31 ONLINE WORKS · PERMANENT ARCHIVE</div><h1>完整作品封存</h1><p class="note">31 篇作品的全文與圖片已轉為本站保存的 PDF 快照。即使原始網站下線，這裡仍可閱讀。</p><section class="archive-grid">{''.join(cards)}</section></main></body></html>'''
    (ROOT / 'index.html').write_text(index, encoding='utf-8')

    # Make archive pages the default destination.
    app = Path('may-portfolio/app.js')
    s = app.read_text(encoding='utf-8')
    s = s.replace('const USE_ARCHIVE=false;', 'const USE_ARCHIVE=true;')
    s = s.replace("w.archiveUrl=`detail.html?type=work&id=${i}`;", "w.archiveUrl=`archive-static/pages/${String(i+1).padStart(2,'0')}.html`;")
    app.write_text(s, encoding='utf-8')

    idx = Path('may-portfolio/index.html')
    s = idx.read_text(encoding='utf-8')
    s = re.sub(r'data\.js\?v=[^\"]+', 'data.js?v=20260916-archive', s)
    s = re.sub(r'app\.js\?v=[^\"]+', 'app.js?v=20260916-archive', s)
    idx.write_text(s, encoding='utf-8')

    pdfs = list((ROOT / 'files').glob('*.pdf'))
    total = sum(p.stat().st_size for p in pdfs)
    largest = max(p.stat().st_size for p in pdfs)
    print(f'Generated {len(pdfs)} PDFs')
    print(f'PDF total MB: {total/1024/1024:.1f}')
    print(f'Max PDF MB: {largest/1024/1024:.1f}')


if __name__ == '__main__':
    main()
