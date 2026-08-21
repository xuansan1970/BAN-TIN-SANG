# -*- coding: utf-8 -*-
"""site_template.py — Khung HTML/CSS/JS của website đọc tin.

Dùng string.Template ($placeholder) thay vì f-string để dấu ngoặc nhọn của
CSS/JS không xung đột với cú pháp Python.
"""

PAGE = r"""<!DOCTYPE html>
<html lang="vi" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>$TITLE</title>
<meta name="description" content="Bản tin tổng hợp $DATE_DISPLAY — $TOTAL tin chọn lọc từ hơn 40 nguồn báo chính thống.">
<meta name="theme-color" content="#080b14">
<meta property="og:title" content="$TITLE">
<meta property="og:description" content="$TOTAL tin chọn lọc sáng $DATE_DISPLAY">
<meta property="og:type" content="website">
<link rel="manifest" href="${BASE}manifest.webmanifest">
<link rel="icon" href="${BASE}icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="${BASE}icon.png">
<style>
*,*::before,*::after{box-sizing:border-box}
:root{
  --bg:#080b14; --surface:#11162a; --surface2:#1a2138; --line:#252d47;
  --text:#f1f5f9; --muted:#94a3b8; --faint:#64748b;
  --brand:#4f8cff; --brand2:#a78bfa;
  --shadow:0 10px 30px rgba(0,0,0,.45);
  --radius:16px;
  --font:-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif;
}
html[data-theme=light]{
  --bg:#f6f7fb; --surface:#ffffff; --surface2:#eef1f8; --line:#dfe4f0;
  --text:#0f172a; --muted:#51607a; --faint:#7c8aa3;
  --shadow:0 10px 28px rgba(15,23,42,.10);
}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);
  line-height:1.55;-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer;border:0;background:none;color:inherit}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px}

/* ── Thanh trên cùng ─────────────────────────────────────── */
.topbar{position:sticky;top:0;z-index:50;backdrop-filter:saturate(160%) blur(14px);
  -webkit-backdrop-filter:saturate(160%) blur(14px);
  background:color-mix(in srgb,var(--bg) 82%,transparent);
  border-bottom:1px solid var(--line)}
.rainbow{height:3px;background:linear-gradient(90deg,#ff5470,#fbbf24,#34d399,#22d3ee,#a78bfa)}
.tb-in{display:flex;align-items:center;gap:14px;padding:12px 0;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;flex:0 0 auto}
.logo{width:34px;height:34px;border-radius:10px;flex:0 0 auto;
  background:linear-gradient(135deg,var(--brand),var(--brand2));
  display:grid;place-items:center;font-size:17px}
.brand h1{margin:0;font-size:15.5px;font-weight:800;letter-spacing:-.2px;white-space:nowrap}
.brand small{display:block;font-size:11px;font-weight:500;color:var(--faint);letter-spacing:.2px}
.search{flex:1 1 240px;min-width:170px;position:relative}
.search input{width:100%;padding:10px 14px 10px 38px;border-radius:99px;
  background:var(--surface2);border:1px solid var(--line);color:var(--text);
  font-size:14px;outline:none;transition:border-color .18s,box-shadow .18s}
.search input:focus{border-color:var(--brand);box-shadow:0 0 0 3px color-mix(in srgb,var(--brand) 22%,transparent)}
.search svg{position:absolute;left:13px;top:50%;transform:translateY(-50%);opacity:.5}
.tools{display:flex;gap:7px;flex:0 0 auto}
.icobtn{width:38px;height:38px;border-radius:11px;background:var(--surface2);
  border:1px solid var(--line);display:grid;place-items:center;font-size:15px;
  transition:transform .16s,background .16s,border-color .16s}
.icobtn:hover{transform:translateY(-2px);border-color:var(--brand)}
.icobtn[aria-pressed=true]{background:linear-gradient(135deg,var(--brand),var(--brand2));
  border-color:transparent;color:#fff}

/* ── Chip lọc ────────────────────────────────────────────── */
.chips{display:flex;gap:8px;padding:2px 0 12px;overflow-x:auto;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{white-space:nowrap;padding:8px 14px;border-radius:99px;font-size:13px;font-weight:600;
  background:var(--surface2);border:1px solid var(--line);color:var(--muted);
  transition:transform .16s,color .16s,border-color .16s}
.chip:hover{transform:translateY(-1px);color:var(--text)}
.chip[aria-pressed=true]{color:#07101f;border-color:transparent;
  background:var(--c,var(--brand))}
html[data-theme=light] .chip[aria-pressed=true]{color:#fff}

/* ── Hero ────────────────────────────────────────────────── */
.hero{padding:26px 0 6px}
.hero h2{margin:0;font-size:clamp(26px,5vw,40px);font-weight:800;letter-spacing:-1px;line-height:1.1}
.hero .sub{margin-top:9px;color:var(--faint);font-size:14px}
.stats{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.stat{padding:7px 13px;border-radius:99px;background:var(--surface2);
  border:1px solid var(--line);font-size:12px;font-weight:600}
.weather{margin-top:18px;display:flex;gap:16px;align-items:center;flex-wrap:wrap;
  padding:16px 18px;border-radius:var(--radius);background:var(--surface);
  border:1px solid var(--line)}
.wtemp{font-size:32px;font-weight:800;background:linear-gradient(135deg,#7dd3fc,#a78bfa);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.wtips{display:flex;gap:8px;flex-wrap:wrap;font-size:12.5px;color:var(--muted)}
.wtips span{padding:5px 10px;border-radius:8px;background:var(--surface2)}

/* ── Điểm tin 60 giây ────────────────────────────────────── */
.digest{margin:26px 0 8px;padding:20px;border-radius:var(--radius);
  background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow)}
.digest h3{margin:0 0 4px;font-size:15px;font-weight:800;letter-spacing:.4px}
.digest p{margin:0 0 14px;font-size:12.5px;color:var(--faint)}
.dlist{display:grid;gap:2px}
.ditem{display:flex;gap:12px;padding:11px 0;border-top:1px solid var(--line);align-items:flex-start}
.ditem:first-child{border-top:0}
.dnum{flex:0 0 auto;width:23px;height:23px;border-radius:7px;font-size:12px;font-weight:800;
  display:grid;place-items:center;color:#07101f;background:var(--c,var(--brand))}
.ditem .t{font-size:14.5px;font-weight:600;line-height:1.45}
.ditem .s{margin-top:3px;font-size:11.5px;font-weight:600;color:var(--c,var(--brand))}

/* ── Lưới tin ────────────────────────────────────────────── */
.secthead{display:flex;align-items:center;gap:12px;margin:34px 0 16px}
.secthead .bar{width:4px;height:22px;border-radius:99px;background:var(--c,var(--brand))}
.secthead h3{margin:0;font-size:19px;font-weight:800;letter-spacing:-.3px}
.secthead .n{margin-left:auto;font-size:12px;font-weight:700;color:var(--c,var(--brand))}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(290px,1fr))}
.card{position:relative;display:flex;flex-direction:column;border-radius:var(--radius);
  background:var(--surface);border:1px solid var(--line);overflow:hidden;
  transition:transform .2s cubic-bezier(.2,.8,.3,1),border-color .2s,box-shadow .2s}
.card:hover{transform:translateY(-4px);border-color:color-mix(in srgb,var(--c,var(--brand)) 55%,var(--line));
  box-shadow:var(--shadow)}
.thumb{position:relative;aspect-ratio:16/9;background:var(--surface2);overflow:hidden}
.thumb img{width:100%;height:100%;object-fit:cover;display:block;
  transition:transform .45s cubic-bezier(.2,.8,.3,1)}
.card:hover .thumb img{transform:scale(1.05)}
.ph{width:100%;height:100%;display:grid;place-items:center;text-align:center;color:#fff}
.ph b{display:block;font-size:26px;font-weight:800;letter-spacing:1px;opacity:.94}
.ph span{display:block;margin-top:3px;font-size:11px;font-weight:600;opacity:.62}
.badge{position:absolute;left:10px;top:10px;padding:5px 10px;border-radius:99px;
  font-size:11px;font-weight:700;color:#07101f;background:var(--c,var(--brand))}
.cbody{padding:14px 15px 12px;display:flex;flex-direction:column;flex:1}
.cbody h4{margin:0;font-size:15px;font-weight:650;line-height:1.42}
.cbody .sum{margin-top:8px;font-size:13px;color:var(--muted);line-height:1.55;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.meta{margin-top:auto;padding-top:12px;display:flex;align-items:center;gap:8px;
  font-size:11.5px;font-weight:600;color:var(--c,var(--brand))}
.meta .dot{color:var(--faint);font-weight:400}
.acts{display:flex;gap:4px;margin-left:auto}
.act{width:29px;height:29px;border-radius:8px;display:grid;place-items:center;
  font-size:13px;color:var(--faint);background:var(--surface2);
  transition:color .16s,transform .16s}
.act:hover{transform:translateY(-2px);color:var(--text)}
.act[aria-pressed=true]{color:#fbbf24}
.act.speaking{color:#34d399}

/* ── Chế độ 5 phút ───────────────────────────────────────── */
body.quick .grid,body.quick .secthead{display:none}
body.quick .digest{margin-top:20px}
body.quick .quickonly{display:block}
.quickonly{display:none}
.quickmsg{margin:20px 0;padding:16px 18px;border-radius:var(--radius);
  background:var(--surface);border:1px dashed var(--line);color:var(--muted);font-size:13.5px}

.empty{padding:60px 20px;text-align:center;color:var(--faint)}
.empty b{display:block;font-size:17px;color:var(--text);margin-bottom:6px}

/* ── Ngăn kéo lưu trữ ────────────────────────────────────── */
.drawer{position:fixed;inset:0;z-index:80;display:none}
.drawer[open]{display:block}
.drawer .scrim{position:absolute;inset:0;background:rgba(4,7,15,.6);backdrop-filter:blur(3px)}
.drawer .panel{position:absolute;right:0;top:0;bottom:0;width:min(340px,86vw);
  background:var(--surface);border-left:1px solid var(--line);padding:22px;overflow-y:auto;
  animation:slide .24s cubic-bezier(.2,.8,.3,1)}
@keyframes slide{from{transform:translateX(24px);opacity:.4}to{transform:none;opacity:1}}
.drawer h3{margin:0 0 14px;font-size:16px;font-weight:800}
.dayrow{display:flex;justify-content:space-between;align-items:center;padding:11px 12px;
  border-radius:11px;background:var(--surface2);margin-bottom:8px;font-size:13.5px;font-weight:600}
.dayrow:hover{outline:1px solid var(--brand)}
.dayrow em{font-style:normal;color:var(--faint);font-weight:500;font-size:12px}

footer{margin:48px 0 40px;padding-top:22px;border-top:1px solid var(--line);
  text-align:center;color:var(--faint);font-size:12.5px}
footer b{color:var(--muted)}

.toast{position:fixed;left:50%;bottom:26px;transform:translate(-50%,20px);opacity:0;
  padding:11px 20px;border-radius:99px;background:var(--text);color:var(--bg);
  font-size:13px;font-weight:650;z-index:99;pointer-events:none;
  transition:opacity .22s,transform .22s}
.toast.on{opacity:1;transform:translate(-50%,0)}

@media (max-width:640px){
  .brand small{display:none}
  .hero{padding-top:18px}
  .grid{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<div class="topbar">
  <div class="rainbow"></div>
  <div class="wrap">
    <div class="tb-in">
      <a class="brand" href="${BASE}index.html">
        <span class="logo">📰</span>
        <span><h1>$BRAND</h1><small>$DATE_DISPLAY</small></span>
      </a>
      <div class="search">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
          <circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/></svg>
        <input id="q" type="search" placeholder="Tìm trong $TOTAL tin hôm nay…" autocomplete="off">
      </div>
      <div class="tools">
        <button class="icobtn" id="quick" aria-pressed="false" title="Chế độ đọc nhanh 5 phút">⚡</button>
        <button class="icobtn" id="saved" aria-pressed="false" title="Tin đã lưu">🔖</button>
        <button class="icobtn" id="arch" title="Xem lại các ngày trước">🗓</button>
        <button class="icobtn" id="theme" title="Sáng / Tối">🌙</button>
      </div>
    </div>
    <div class="chips" id="chips"></div>
  </div>
</div>

<main class="wrap">
  <section class="hero">
    <h2>$HERO_TITLE</h2>
    <div class="sub">$DATE_DISPLAY · Tổng hợp tự động từ hơn 40 nguồn báo chính thống</div>
    <div class="stats">
      <span class="stat">📊 $TOTAL tin chọn lọc</span>
      <span class="stat">✅ Link đã kiểm tra</span>
      <span class="stat">🖼 $THUMB_PCT% có ảnh minh hoạ</span>
      <span class="stat">🇻🇳 Ưu tiên Việt Nam</span>
    </div>
    <div id="weather"></div>
  </section>

  <section class="digest" id="digest"></section>
  <div class="quickmsg quickonly">Đang ở <b>chế độ đọc nhanh</b> — chỉ hiện điểm tin quan trọng nhất. Bấm ⚡ lần nữa để xem đầy đủ.</div>

  <div id="sections"></div>
  <div class="empty" id="empty" hidden><b>Không tìm thấy tin nào</b>Thử từ khoá khác hoặc bỏ bớt bộ lọc.</div>
</main>

<footer class="wrap">
  <div><b>$BRAND</b> · cập nhật $UPDATED</div>
  <div style="margin-top:6px">Tự động tổng hợp mỗi sáng · Mọi liên kết đều đã được kiểm tra trước khi đăng</div>
</footer>

<div class="drawer" id="drawer">
  <div class="scrim" data-close></div>
  <div class="panel">
    <h3>🗓 Xem lại các ngày trước</h3>
    <div id="days"></div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const DATA = $DATA_JSON;
const WEATHER = $WEATHER_JSON;
const ARCHIVE = $ARCHIVE_JSON;
const BASE = "$BASE";

const el = (s,r)=> (r||document).querySelector(s);
const els = (s,r)=> [...(r||document).querySelectorAll(s)];
const esc = s => String(s==null?"":s).replace(/[&<>"']/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

let state = { cat:"all", q:"", savedOnly:false, quick:false };
const store = {
  get(k,d){ try{ return JSON.parse(localStorage.getItem(k)) ?? d }catch(e){ return d } },
  set(k,v){ try{ localStorage.setItem(k,JSON.stringify(v)) }catch(e){} }
};
let marks = new Set(store.get("bn_marks",[]));

function toast(msg){
  const t = el("#toast"); t.textContent = msg; t.classList.add("on");
  clearTimeout(t._x); t._x = setTimeout(()=>t.classList.remove("on"), 1900);
}

/* ── Giao diện sáng/tối ─────────────────────────────────── */
(function(){
  const saved = store.get("bn_theme", null);
  const sys = matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  document.documentElement.dataset.theme = saved || sys;
})();
el("#theme").onclick = () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  store.set("bn_theme", next);
  el("#theme").textContent = next === "dark" ? "🌙" : "☀️";
};
el("#theme").textContent = document.documentElement.dataset.theme === "dark" ? "🌙" : "☀️";

/* ── Thời tiết ──────────────────────────────────────────── */
if (WEATHER && WEATHER.ok) {
  el("#weather").innerHTML =
    '<div class="weather"><div><div style="font-weight:700;font-size:15px">'+esc(WEATHER.city)+
    '</div><div style="font-size:12.5px;color:var(--faint)">'+esc(WEATHER.desc)+
    ' · Cảm giác '+esc(WEATHER.feels_like)+'° · Mưa '+esc(WEATHER.rain_prob)+'%</div></div>'+
    '<div class="wtemp">'+esc(WEATHER.temp)+'°</div>'+
    '<div class="wtips">'+(WEATHER.tips||[]).map(t=>'<span>'+esc(t)+'</span>').join("")+'</div></div>';
}

/* ── Chip lọc ───────────────────────────────────────────── */
function buildChips(){
  const c = el("#chips");
  const all = '<button class="chip" data-cat="all" aria-pressed="true">🗞 Tất cả</button>';
  c.innerHTML = all + DATA.map(s =>
    '<button class="chip" data-cat="'+esc(s.key)+'" aria-pressed="false" style="--c:'+esc(s.accent)+'">'+
    s.emoji+" "+esc(s.short)+'</button>').join("");
  els(".chip", c).forEach(b => b.onclick = () => {
    state.cat = b.dataset.cat;
    els(".chip", c).forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    render();
  });
}

/* ── Ô ảnh ──────────────────────────────────────────────── */
function thumbHTML(a){
  if (a.thumbnail) {
    return '<img src="'+esc(a.thumbnail)+'" alt="" loading="lazy" decoding="async" '+
           'onerror="this.parentNode.innerHTML=window.__ph(this.dataset.i)" data-i="'+a.i+'">';
  }
  return window.__ph(a.i);
}
window.__PH = {};
window.__ph = i => {
  const p = window.__PH[i] || {c1:"#2b3a67",c2:"#4a5fc1",ini:"TT",src:""};
  return '<div class="ph" style="background:linear-gradient(135deg,'+p.c1+','+p.c2+')">'+
         '<div><b>'+esc(p.ini)+'</b><span>'+esc(p.src)+'</span></div></div>';
};

/* ── Thẻ tin ────────────────────────────────────────────── */
function cardHTML(a, accent){
  const on = marks.has(a.id);
  return '<article class="card" style="--c:'+esc(accent)+'" data-id="'+esc(a.id)+'">'+
    '<a class="thumb" href="'+esc(a.link)+'" target="_blank" rel="noopener">'+thumbHTML(a)+
      (a.hot ? '<span class="badge">HOT</span>' : '')+'</a>'+
    '<div class="cbody">'+
      '<a href="'+esc(a.link)+'" target="_blank" rel="noopener"><h4>'+esc(a.title)+'</h4></a>'+
      (a.summary ? '<div class="sum">'+esc(a.summary)+'</div>' : '')+
      '<div class="meta"><span>'+esc(a.source)+'</span><span class="dot">·</span><span class="dot">'+esc(a.time)+'</span>'+
        '<span class="acts">'+
          '<button class="act mark" aria-pressed="'+on+'" title="Lưu để đọc sau">🔖</button>'+
          '<button class="act tts" title="Nghe đọc">🔊</button>'+
          '<button class="act share" title="Chia sẻ">↗</button>'+
        '</span>'+
      '</div>'+
    '</div></article>';
}

/* ── Điểm tin 60 giây ───────────────────────────────────── */
function buildDigest(){
  const picks = [];
  DATA.forEach(s => s.articles.slice(0,2).forEach(a => picks.push([a, s])));
  const top = picks.slice(0, 8);
  el("#digest").innerHTML =
    '<h3>⚡ ĐIỂM TIN 60 GIÂY</h3><p>Bận thì đọc đúng phần này là đủ nắm ngày hôm nay</p>'+
    '<div class="dlist">'+ top.map(([a,s],i) =>
      '<div class="ditem" style="--c:'+esc(s.accent)+'"><span class="dnum">'+(i+1)+'</span>'+
      '<div><a href="'+esc(a.link)+'" target="_blank" rel="noopener"><div class="t">'+esc(a.title)+'</div></a>'+
      '<div class="s">'+s.emoji+" "+esc(a.source)+'</div></div></div>').join("")+
    '</div>'+
    '<button class="stat" id="readall" style="margin-top:14px">🔊 Nghe toàn bộ điểm tin</button>';
  el("#readall").onclick = () => speak(top.map(([a]) => a.title).join(". "), el("#readall"));
}

/* ── Render chính ───────────────────────────────────────── */
function match(a){
  if (state.savedOnly && !marks.has(a.id)) return false;
  if (!state.q) return true;
  const q = state.q.toLowerCase();
  return (a.title+" "+(a.summary||"")+" "+a.source).toLowerCase().includes(q);
}
function render(){
  let shown = 0;
  const out = DATA.filter(s => state.cat === "all" || s.key === state.cat).map(s => {
    const list = s.articles.filter(match);
    if (!list.length) return "";
    shown += list.length;
    return '<section class="secthead" style="--c:'+esc(s.accent)+'">'+
             '<span class="bar"></span><h3>'+s.emoji+" "+esc(s.name)+'</h3>'+
             '<span class="n">'+list.length+' tin</span></section>'+
           '<div class="grid">'+list.map(a => cardHTML(a, s.accent)).join("")+'</div>';
  }).join("");
  el("#sections").innerHTML = out;
  el("#empty").hidden = shown > 0;
  wireCards();
}

function wireCards(){
  els(".card").forEach(card => {
    const id = card.dataset.id;
    const a = INDEX[id];
    el(".mark", card).onclick = e => {
      e.preventDefault();
      marks.has(id) ? marks.delete(id) : marks.add(id);
      store.set("bn_marks", [...marks]);
      e.currentTarget.setAttribute("aria-pressed", String(marks.has(id)));
      toast(marks.has(id) ? "Đã lưu tin" : "Đã bỏ lưu");
    };
    el(".share", card).onclick = async e => {
      e.preventDefault();
      const payload = { title: a.title, url: a.link };
      if (navigator.share) { try { await navigator.share(payload) } catch(_){} }
      else { try { await navigator.clipboard.writeText(a.link); toast("Đã copy link") } catch(_){ toast("Không copy được") } }
    };
    el(".tts", card).onclick = e => {
      e.preventDefault();
      speak(a.title + ". " + (a.summary || ""), e.currentTarget);
    };
  });
}

/* ── Đọc to ─────────────────────────────────────────────── */
let speakingBtn = null;
function speak(text, btn){
  if (!("speechSynthesis" in window)) { toast("Trình duyệt không hỗ trợ đọc to"); return }
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
    if (speakingBtn) speakingBtn.classList.remove("speaking");
    if (speakingBtn === btn) { speakingBtn = null; return }
  }
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "vi-VN"; u.rate = 1.02;
  u.onend = () => { btn.classList.remove("speaking"); speakingBtn = null };
  btn.classList.add("speaking"); speakingBtn = btn;
  speechSynthesis.speak(u);
}

/* ── Điều khiển ─────────────────────────────────────────── */
let deb;
el("#q").oninput = e => { clearTimeout(deb); deb = setTimeout(() => { state.q = e.target.value.trim(); render() }, 160) };
el("#quick").onclick = e => {
  state.quick = !state.quick;
  document.body.classList.toggle("quick", state.quick);
  e.currentTarget.setAttribute("aria-pressed", String(state.quick));
};
el("#saved").onclick = e => {
  state.savedOnly = !state.savedOnly;
  e.currentTarget.setAttribute("aria-pressed", String(state.savedOnly));
  if (state.savedOnly && !marks.size) toast("Chưa lưu tin nào — bấm 🔖 trên thẻ tin");
  render();
};
el("#arch").onclick = () => {
  el("#days").innerHTML = ARCHIVE.length
    ? ARCHIVE.map(d => '<a class="dayrow" href="'+BASE+'d/'+esc(d.date)+'.html"><span>'+
        esc(d.label)+'</span><em>'+d.total+' tin</em></a>').join("")
    : '<div style="color:var(--faint);font-size:13px">Chưa có bản lưu trữ nào.</div>';
  el("#drawer").setAttribute("open","");
};
els("[data-close]").forEach(x => x.onclick = () => el("#drawer").removeAttribute("open"));
addEventListener("keydown", e => {
  if (e.key === "Escape") el("#drawer").removeAttribute("open");
  if (e.key === "/" && document.activeElement !== el("#q")) { e.preventDefault(); el("#q").focus() }
});

/* ── Khởi động ──────────────────────────────────────────── */
const INDEX = {};
DATA.forEach(s => s.articles.forEach(a => {
  INDEX[a.id] = a;
  window.__PH[a.i] = a.ph;
}));
buildChips(); buildDigest(); render();

if ("serviceWorker" in navigator) {
  addEventListener("load", () => navigator.serviceWorker.register(BASE + "sw.js").catch(()=>{}));
}
</script>
</body>
</html>
"""
