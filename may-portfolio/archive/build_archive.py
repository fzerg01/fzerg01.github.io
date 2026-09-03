from pathlib import Path
from datetime import datetime, timezone
import html
import json
import shutil
import time

from playwright.sync_api import sync_playwright

WORKS = [
    {"category":"室內設計作品電訪","title":"融匯現代精粹 樹立精緻奢華新標竿","url":"https://hhh.com.tw/cases/detail/d/12925"},
    {"category":"室內設計作品電訪","title":"光蘊流轉 淬鍊自然人文華韻","url":"https://hhh.com.tw/cases/detail/d/12128"},
    {"category":"室內設計作品電訪","title":"重現冰雪絕景 打造尊爵玩美體驗！","url":"https://hhh.com.tw/cases/detail/d/11517"},
    {"category":"室內設計作品電訪","title":"精工巧藝砌築雅緻工岩苑｜現代風｜20坪","url":"https://hhh.com.tw/cases/detail/d/17999"},
    {"category":"專訪","title":"〖人物專訪〗朱英凱室內設計事務所 設計總監－用空間說故事的設計師 允文允武的斜槓生活家！","url":"https://hhh.com.tw/columns/detail/6190"},
    {"category":"專訪","title":"〖開箱〗整理師的15坪魔術空間，告訴你一輩子與髒亂絕緣的重要觀念！","url":"https://hhh.com.tw/columns/detail/4835"},
    {"category":"專訪","title":"構築健康、自然、有溫度的家！光舍丰計榮獲2023年日本Good Design Award","url":"https://hhh.com.tw/columns/detail/7582"},
    {"category":"室內設計作品專欄報導","title":"〖好宅特輯〗從大自然汲取靈感 捏塑柔美侘寂風穴居","url":"https://hhh.com.tw/columns/detail/8053"},
    {"category":"室內設計作品專欄報導","title":"〖好宅特輯〗與自然和諧共舞！四季如詩的逸墅","url":"https://hhh.com.tw/columns/detail/8389"},
    {"category":"室內設計作品專欄報導","title":"〖好宅專輯〗減法哲學織就美式詩境","url":"https://hhh.com.tw/columns/detail/6019"},
    {"category":"室內設計主題報導","title":"小坪數裝修全攻略！從設計規劃著手放大空間坪效","url":"https://hhh.com.tw/columns/detail/5926"},
    {"category":"室內設計主題報導","title":"隔而不斷！5種設計手法放大家的視野","url":"https://hhh.com.tw/columns/detail/8194"},
    {"category":"室內設計主題報導","title":"無須重新裝潢、買家電！8大神器無痛幫居家「開智慧」","url":"https://hhh.com.tw/columns/detail/8717"},
    {"category":"室內設計主題報導","title":"減法美學 開啟「輕」生活","url":"https://hhh.com.tw/columns/detail/8674"},
    {"category":"開箱文","title":"〖好宅開箱分享〗住宅神醫奇蹟拯救老屋！找回家的溫暖幸福","url":"https://hhh.com.tw/columns/detail/6082"},
    {"category":"開箱文","title":"〖開箱〗買下高樓景觀宅，每天俯瞰山水、城市美景好舒壓！","url":"https://hhh.com.tw/columns/detail/7656"},
    {"category":"開箱文","title":"〖好宅開箱〗擺脫租屋時的框架限制！我的35坪現代親子宅超舒適","url":"https://hhh.com.tw/columns/detail/5551"},
    {"category":"廣編文","title":"高端住宅新趨勢！嵌入式廚電正夯，One Bosch一次到位","url":"https://hhh.com.tw/columns/detail/8869"},
    {"category":"廣編文","title":"老屋必修課！6大不可忽視的翻新關鍵｜SD 空間設計 × Panasonic","url":"https://hhh.com.tw/columns/detail/8809"},
    {"category":"廣編文","title":"邂逅精工廚電 演繹精品級廚房美學｜德國百年頂級廚電TEKA X 三宅一秀室內設計","url":"https://hhh.com.tw/columns/detail/8557"},
    {"category":"廣編文","title":"從空間設計到睡眠品質，有品味的室內設計師為什麼都選席伊麗床墊？","url":"https://hhh.com.tw/columns/detail/8299"},
    {"category":"廣編文","title":"設計師的小宅放大術，挑對沙發讓居家空間多2坪","url":"https://hhh.com.tw/columns/detail/7609"},
    {"category":"廣編文","title":"半開放式高效率歐式廚房 延長幸福「食」光 svago廚房家電x合砌設計","url":"https://hhh.com.tw/columns/detail/6930"},
    {"category":"廣編文","title":"〖開箱〗用過就回不去的好物＋１!美型淨水器隨開即飲不用等","url":"https://hhh.com.tw/columns/detail/7241"},
    {"category":"廣編文","title":"3大達人心法！讓你家空氣鮮活起來","url":"https://hhh.com.tw/columns/detail/4143"},
    {"category":"轉載文章","title":"容易不小心入手的8種NG收納用品","url":"https://hhh.com.tw/columns/detail/4339"},
    {"category":"轉載文章","title":"露臺能否加蓋遮雨棚？","url":"https://hhh.com.tw/columns/detail/5848"},
    {"category":"轉載文章","title":"吳淡如：年輕人想買房自住，請記得兩個「千萬不要」！","url":"https://hhh.com.tw/columns/detail/6241"},
    {"category":"建築設計文章","title":"宛若通往天空的階梯！隈研吾於日本鳥取砂丘打造的Takahama Cafe高濱咖啡廳","url":"https://hhh.com.tw/columns/detail/7054"},
    {"category":"建築設計文章","title":"熱播韓劇也到這裡取景！讓你大開眼界的5個絕美書香世界","url":"https://hhh.com.tw/columns/detail/4045"},
    {"category":"建築設計文章","title":"Zaha Hadid遺作The Opus融冰大樓落成！","url":"https://hhh.com.tw/columns/detail/4034"},
]

BOOKS = [
    {"title":"給友達的禮物：表達心意的100分包裝","url":"https://www.books.com.tw/products/0010618991"},
    {"title":"玩最感動、吃最在地、買最實在，最Hot！觀光工廠","url":"https://www.books.com.tw/products/0010615052"},
    {"title":"台南美好小旅行：老城市。新靈魂。慢時光","url":"https://www.books.com.tw/products/0010642045"},
    {"title":"倫敦地鐵購物遊：5大區人氣商圈x300家精選好店","url":"https://www.books.com.tw/products/0010703444"},
    {"title":"咖啡拉花：51款大師級藝術拉花（附DVD）","url":"https://www.eslite.com/product/1001273622413912"},
    {"title":"蔣偉文的幸福廚記：72道超人氣家常料理，享受美味好食光","url":"https://www.books.com.tw/products/0010647939"},
    {"title":"法國甜點聖經：巴黎金牌糕點主廚207堂甜點課（限量典藏版）","url":"https://www.books.com.tw/products/0010686500"},
    {"title":"神奇的檸檬：250種日常妙用，教你擁有全方位健康","url":"https://www.books.com.tw/products/0010632077"},
    {"title":"營養師設計的82道洗腎保健食譜：洗腎也能享受美食零負擔","url":"https://www.books.com.tw/products/0010622087"},
    {"title":"造型兒童餐：88種超萌料理，讓孩子天天都想帶便當！","url":"https://www.books.com.tw/products/0010655039"},
]

ROOT = Path("may-portfolio-archive")
WORK_DIR = ROOT / "works"
THUMB_DIR = ROOT / "thumbs"
SOURCE_DIR = ROOT / "portfolio-source"

for d in (ROOT, WORK_DIR, THUMB_DIR, SOURCE_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Keep a copy of the current portfolio source itself.
for name in ("index.html", "styles.css", "data.js", "app.js"):
    src = Path("may-portfolio") / name
    if src.exists():
        shutil.copy2(src, SOURCE_DIR / name)

archived_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
manifest = {
    "name": "許雅眉 May 完整作品封存",
    "archived_at": archived_at,
    "works": [],
    "books": BOOKS,
}


def lazy_load_everything(page):
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass
    page.wait_for_timeout(1200)
    try:
        height = page.evaluate("Math.min(document.documentElement.scrollHeight, 120000)")
        y = 0
        while y < height:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(120)
            y += 900
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        page.wait_for_timeout(1200)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(700)
    except Exception:
        pass


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1440, "height": 1000},
        locale="zh-TW",
        ignore_https_errors=True,
    )

    for idx, item in enumerate(WORKS, start=1):
        num = f"{idx:02d}"
        result = {
            **item,
            "pdf": f"works/{num}.pdf",
            "mhtml": f"works/{num}.mhtml",
            "thumbnail": f"thumbs/{num}.jpg",
            "status": "pending",
        }
        page = context.new_page()
        try:
            print(f"[{num}/{len(WORKS)}] {item['url']}", flush=True)
            response = page.goto(item["url"], wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(2500)
            lazy_load_everything(page)

            status = response.status if response else None
            result["http_status"] = status
            result["captured_title"] = page.title()

            page.screenshot(
                path=str(THUMB_DIR / f"{num}.jpg"),
                type="jpeg",
                quality=78,
                full_page=False,
            )

            page.pdf(
                path=str(WORK_DIR / f"{num}.pdf"),
                format="A4",
                print_background=True,
                margin={"top":"10mm","right":"8mm","bottom":"10mm","left":"8mm"},
            )

            cdp = context.new_cdp_session(page)
            snapshot = cdp.send("Page.captureSnapshot", {"format": "mhtml"})["data"]
            (WORK_DIR / f"{num}.mhtml").write_text(snapshot, encoding="utf-8")
            cdp.detach()

            result["status"] = "ok" if not status or status < 400 else f"http-{status}"
        except Exception as exc:
            result["status"] = "failed"
            result["error"] = str(exc)
            (WORK_DIR / f"{num}.error.txt").write_text(str(exc), encoding="utf-8")
            print(f"  ERROR: {exc}", flush=True)
        finally:
            manifest["works"].append(result)
            page.close()
            time.sleep(0.2)

    browser.close()

(Path(ROOT) / "manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
)

cards = []
for idx, w in enumerate(manifest["works"], start=1):
    num = f"{idx:02d}"
    status = "已封存" if w["status"] == "ok" else f"封存狀態：{w['status']}"
    thumb = f"thumbs/{num}.jpg"
    pdf = f"works/{num}.pdf"
    mhtml = f"works/{num}.mhtml"
    links = []
    if (ROOT / pdf).exists():
        links.append(f'<a href="{pdf}">PDF</a>')
    if (ROOT / mhtml).exists():
        links.append(f'<a href="{mhtml}">MHTML 離線頁</a>')
    links.append(f'<a href="{html.escape(w["url"], quote=True)}">原始來源</a>')
    thumb_html = f'<img src="{thumb}" alt="">' if (ROOT / thumb).exists() else '<div class="noimg">NO PREVIEW</div>'
    cards.append(f'''<article class="card">{thumb_html}<div class="copy"><small>{idx:02d} · {html.escape(w['category'])}</small><h2>{html.escape(w['title'])}</h2><p>{status}</p><div class="links">{' · '.join(links)}</div></div></article>''')

book_items = "".join(
    f'<li><strong>{html.escape(b["title"])}</strong><br><a href="{html.escape(b["url"], quote=True)}">原始書籍頁</a></li>'
    for b in BOOKS
)

index_html = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>許雅眉 May｜完整作品封存</title>
<style>
:root{{--paper:#f3f0e9;--ink:#20231e;--muted:#74786f;--line:#cbc9c0;--moss:#66705f;--serif:"Noto Serif TC","PMingLiU",serif;--sans:"Noto Sans TC","Microsoft JhengHei",sans-serif}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.7}}main{{width:min(1180px,calc(100% - 36px));margin:auto;padding:60px 0 90px}}h1{{font:500 clamp(40px,6vw,78px)/1.1 var(--serif);margin:8px 0 18px}}.lead{{max-width:760px;color:var(--muted)}}.meta{{font-size:12px;color:var(--moss);letter-spacing:.08em}}.grid{{margin-top:48px;border-top:1px solid var(--line)}}.card{{display:grid;grid-template-columns:220px 1fr;gap:28px;padding:22px 0;border-bottom:1px solid var(--line)}}.card img,.noimg{{width:220px;aspect-ratio:16/10;object-fit:cover;background:#ddd8ce}}.noimg{{display:grid;place-items:center;font-size:11px;color:#777}}small{{color:var(--moss);letter-spacing:.08em}}h2{{font:500 24px/1.45 var(--serif);margin:6px 0}}p{{margin:6px 0;color:var(--muted)}}a{{color:inherit}}.links{{font-size:13px}}.books{{margin-top:70px}}.books li{{margin:0 0 14px}}@media(max-width:680px){{main{{padding-top:34px}}.card{{grid-template-columns:1fr}}.card img,.noimg{{width:100%}}}}
</style></head><body><main>
<div class="meta">OFFLINE ARCHIVE · {html.escape(archived_at)}</div>
<h1>許雅眉 May<br>完整作品封存</h1>
<p class="lead">此封存包保存 31 篇線上作品。每篇優先提供 PDF 與 MHTML；MHTML 是包含當次載入文字、圖片與頁面資源的單檔離線快照，可用 Chrome / Edge 開啟。原始來源網址僅供出處紀錄，即使來源日後失效，已成功產生的 PDF / MHTML 仍可離線閱讀。</p>
<section class="grid">{''.join(cards)}</section>
<section class="books"><h1 style="font-size:42px">出版編輯作品 · 10</h1><ol>{book_items}</ol></section>
</main></body></html>'''
(ROOT / "index.html").write_text(index_html, encoding="utf-8")

readme = f'''許雅眉 May 完整作品封存\n\n封存時間：{archived_at}\n\n使用方式：\n1. 先開啟 index.html。\n2. PDF 可直接離線閱讀。\n3. MHTML 建議使用 Chrome 或 Microsoft Edge 開啟；它保存了當次載入的頁面文字、圖片與樣式資源。\n4. portfolio-source/ 保存製作封存當下的作品集網站原始檔。\n5. manifest.json 記錄每篇來源網址與封存狀態。\n\n注意：若某篇在封存當下原網站已無法存取，manifest.json 會標示 failed / HTTP 狀態。\n'''
(ROOT / "README.txt").write_text(readme, encoding="utf-8")

archive_path = shutil.make_archive("may-portfolio-full-archive", "zip", ROOT)
print(f"Created {archive_path}")
