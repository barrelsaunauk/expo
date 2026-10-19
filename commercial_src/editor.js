// Drag and resize editor for the BSUK trifold. Saves to this browser, Copy layout gives Nikki the JSON.
(function(){
  const KEY='bsuk_commercial_layout_v1';
  let layout=Object.assign({}, window.BASE_LAYOUT||{}); try{ const s=JSON.parse(localStorage.getItem(KEY)||'null'); if(s) layout=s; }catch(e){}
  const {blocks}=BSUKLayout.freeze(layout);
  const mm=()=>BSUKLayout.pxPerMm();
  const sel={el:null};

  // toolbar
  const bar=document.createElement('div'); bar.id='edbar';
  bar.innerHTML=`<b>Layout editor</b>
    <span class="hint">Drag a block to move it. Drag the honey corner to resize. Shift drag an image card to change its picture height. Arrow keys nudge 0.5mm.</span>
    <button id="copy">Copy layout</button><button id="dl">Download layout</button><button id="reset">Reset all</button>
    <span id="pos"></span>`;
  document.body.prepend(bar);
  const st=document.createElement('style'); st.textContent=`
    #edbar{position:fixed;top:0;left:0;right:0;z-index:50;background:#16261C;color:#fff;font:13px/1.4 Poppins,Arial,sans-serif;padding:10px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
    #edbar .hint{opacity:.8;font-size:12px;max-width:620px}
    #edbar button{background:#C08B41;border:0;color:#fff;font-weight:700;border-radius:999px;padding:6px 14px;cursor:pointer;font-family:inherit}
    #edbar #reset{background:transparent;border:1px solid rgba(255,255,255,.4)}
    #edbar #pos{margin-left:auto;font-family:ui-monospace,monospace;font-size:12px;opacity:.85}
    .panel [data-k]{cursor:move;outline:1px dashed transparent;transition:outline-color .1s}
    .panel [data-k]:hover{outline-color:rgba(214,168,104,.7)}
    .panel [data-k].sel{outline:2px solid #C08B41;outline-offset:1px}
    .rz{position:absolute;right:-6px;bottom:-6px;width:12px;height:12px;background:#C08B41;border:2px solid #fff;border-radius:3px;cursor:nwse-resize;z-index:9;display:none}
    [data-k].sel .rz{display:block}
    body{padding-top:70px}
    .sheet{margin:16px auto}
  `; document.head.appendChild(st);

  function save(){ localStorage.setItem(KEY, JSON.stringify(layout)); }
  function rec(el){
    const b={el,panel:el.closest('.panel')}; const m=BSUKLayout.measure(b);
    const o={l:+m.l.toFixed(2),t:+m.t.toFixed(2),w:+m.w.toFixed(2),h:+m.h.toFixed(2)};
    const im=el.classList.contains('lab')?el.querySelector('img'):null;
    if(im) o.ih=+(im.getBoundingClientRect().height/mm()).toFixed(2);
    layout[el.dataset.k]=o; save(); show(el);
  }
  function show(el){ const o=layout[el.dataset.k]||BSUKLayout.measure({el,panel:el.closest('.panel')}); document.getElementById('pos').textContent=`${el.dataset.k}  left ${(+o.l).toFixed(1)}  top ${(+o.t).toFixed(1)}  w ${(+o.w).toFixed(1)}  h ${(+o.h).toFixed(1)} mm`; }

  blocks.forEach(({el})=>{
    const rz=document.createElement('i'); rz.className='rz'; el.appendChild(rz);
    el.addEventListener('mousedown',e=>{
      if(e.target===rz) return;
      e.preventDefault(); select(el);
      const k=mm(), sx=e.clientX, sy=e.clientY, l0=parseFloat(el.style.left), t0=parseFloat(el.style.top);
      const im=el.classList.contains('lab')&&e.shiftKey?el.querySelector('img'):null; const ih0=im?im.getBoundingClientRect().height/k:0;
      const mv=ev=>{ if(im){ im.style.height=Math.max(8,ih0+(ev.clientY-sy)/k)+'mm'; } else { el.style.left=(l0+(ev.clientX-sx)/k)+'mm'; el.style.top=(t0+(ev.clientY-sy)/k)+'mm'; } show(el); };
      const up=()=>{ window.removeEventListener('mousemove',mv); window.removeEventListener('mouseup',up); rec(el); };
      window.addEventListener('mousemove',mv); window.addEventListener('mouseup',up);
    });
    rz.addEventListener('mousedown',e=>{
      e.preventDefault(); e.stopPropagation(); select(el);
      const k=mm(), sx=e.clientX, sy=e.clientY, w0=parseFloat(el.style.width), h0=el.getBoundingClientRect().height/k;
      const fixH=el.classList.contains('showroom')||el.classList.contains('logo')||el.classList.contains('sig');
      const circ=el.parentElement&&el.querySelector('img')&&!el.classList.contains('lab')&&!el.classList.contains('lift');
      const img=el.querySelector('img'); const iw0=img?img.getBoundingClientRect().width/k:0;
      const mv=ev=>{ const nw=Math.max(10,w0+(ev.clientX-sx)/k); el.style.width=nw+'mm';
        if(fixH) el.style.height=Math.max(5,h0+(ev.clientY-sy)/k)+'mm';
        if(circ&&img){ const s=nw/w0; img.style.width=(iw0*s)+'mm'; img.style.height=(iw0*s)+'mm'; }
        show(el); };
      const up=()=>{ window.removeEventListener('mousemove',mv); window.removeEventListener('mouseup',up); rec(el); if(circ&&img){ layout[el.dataset.k].iw=+(img.getBoundingClientRect().width/mm()).toFixed(2); save(); } };
      window.addEventListener('mousemove',mv); window.addEventListener('mouseup',up);
    });
    // apply saved circle image size
    const o=layout[el.dataset.k]; if(o&&o.iw){ const img=el.querySelector('img'); if(img){img.style.width=o.iw+'mm';img.style.height=o.iw+'mm';} }
  });
  function select(el){ if(sel.el) sel.el.classList.remove('sel'); sel.el=el; el.classList.add('sel'); show(el); }
  window.addEventListener('keydown',e=>{
    if(!sel.el||!/^Arrow/.test(e.key)) return; e.preventDefault();
    const el=sel.el, d=e.shiftKey?2:0.5;
    if(e.key==='ArrowLeft') el.style.left=(parseFloat(el.style.left)-d)+'mm';
    if(e.key==='ArrowRight') el.style.left=(parseFloat(el.style.left)+d)+'mm';
    if(e.key==='ArrowUp') el.style.top=(parseFloat(el.style.top)-d)+'mm';
    if(e.key==='ArrowDown') el.style.top=(parseFloat(el.style.top)+d)+'mm';
    rec(el);
  });
  document.getElementById('copy').onclick=()=>{ const t=JSON.stringify(layout,null,1); navigator.clipboard?.writeText(t).then(()=>toast('Layout copied. Paste it to Nikki.'),()=>toast('Copy blocked, use Download instead.')); };
  document.getElementById('dl').onclick=()=>{ const b=new Blob([JSON.stringify(layout,null,1)],{type:'application/json'}); const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='commercial_layout.json'; a.click(); };
  document.getElementById('reset').onclick=()=>{ if(confirm('Put every block back where the build placed it?')){ localStorage.removeItem(KEY); location.reload(); } };
  function toast(m){ const t=document.createElement('div'); t.textContent=m; t.style.cssText='position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#1F3D28;color:#fff;padding:10px 16px;border-radius:999px;font:13px Poppins,Arial;z-index:99'; document.body.appendChild(t); setTimeout(()=>t.remove(),2200); }
})();
