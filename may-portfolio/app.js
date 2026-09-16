const $=s=>document.querySelector(s);const esc=s=>String(s).replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
BOOKS.push({url:'https://www.books.com.tw/products/0010655039',image:'https://www.books.com.tw/img/001/065/50/0010655039.jpg',title:'造型兒童餐：88種超萌料理，讓孩子天天都想帶便當！'});

// Archive fallback：平常使用官網；官網失效時只要改成 true，31 篇作品會全部切到本站封存頁。
const USE_ARCHIVE=true;
// 測試用：網址加 ?archive=1 可預覽封存模式，不影響一般訪客。
const FORCE_ARCHIVE=new URLSearchParams(location.search).get('archive')==='1';
const ARCHIVE_MODE=USE_ARCHIVE||FORCE_ARCHIVE;
WORKS.forEach((w,i)=>{w.officialUrl=w.url;w.archiveUrl=`archive-static/pages/${String(i+1).padStart(2,'0')}.html`;});
const workHref=w=>ARCHIVE_MODE?w.archiveUrl:w.officialUrl;
const workAttrs=()=>ARCHIVE_MODE?'':'target="_blank" rel="noopener"';

$('#heroVisual').innerHTML=`<img src="https://images.pexels.com/photos/32780010/pexels-photo-32780010.jpeg?auto=compress&cs=tinysrgb&w=1600" alt="溫暖木質調居家空間">`;
$('#featured').innerHTML=FEATURED.map(i=>{const w=WORKS[i];return `<a class="feature" href="${workHref(w)}" ${workAttrs()}><img src="${w.image}" alt="${esc(w.title)}" onerror="this.style.display='none'"><div class="feature-copy"><small>${esc(w.category)}</small><strong>${esc(w.title)}</strong></div></a>`}).join('');
$('#bookGrid').innerHTML=BOOKS.map(b=>`<a class="book" href="${b.url}" target="_blank" rel="noopener"><div class="cover"><img src="${b.image}" alt="${esc(b.title)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.style.display='none'"></div><small>編輯作品</small><strong>${esc(b.title)}</strong></a>`).join('');
const cats=['全部',...new Set(WORKS.map(w=>w.category))], filters=$('#filters'), list=$('#workList'), search=$('#search'), count=$('#count');let active='全部';
filters.innerHTML=cats.map((c,i)=>`<button class="filter${i?'':' active'}" data-cat="${esc(c)}">${esc(c)}</button>`).join('');
function render(){const q=search.value.trim().toLowerCase();const rows=WORKS.filter(w=>(active==='全部'||w.category===active)&&(!q||(w.title+' '+w.category).toLowerCase().includes(q)));list.innerHTML=rows.map(w=>`<a class="work" href="${workHref(w)}" ${workAttrs()}><span class="no">${String(WORKS.indexOf(w)+1).padStart(2,'0')}</span><img src="${w.image}" alt="${esc(w.title)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.style.display='none'"><span><small>${esc(w.category)}</small><strong>${esc(w.title)}</strong></span><span class="view">${ARCHIVE_MODE?'ARCHIVE →':'VIEW ↗'}</span></a>`).join('');count.textContent=`顯示 ${rows.length} / ${WORKS.length} 篇作品${ARCHIVE_MODE?' · 封存模式':''}`;}
filters.addEventListener('click',e=>{const b=e.target.closest('.filter');if(!b)return;filters.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');active=b.dataset.cat;render()});search.addEventListener('input',render);render();