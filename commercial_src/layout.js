// Shared layout engine for the BSUK trifold.
// Every movable block gets a stable key from its position in the page. A LAYOUT object
// (key -> {l,t,w,h} in mm, relative to its panel) pins blocks to absolute positions.
// Both the editor and the print file run this, so what you drag is what prints.
(function(){
  const SEL = '.pad > *:not(.tiles):not(.circ), .tiles > .lab, .circ > div, .lifts > .lift, .showroom, .logo, .txt, .sig';
  function blocks(){
    const out=[];
    document.querySelectorAll('.panel').forEach((panel,pi)=>{
      const seen=new Map();
      panel.querySelectorAll(SEL).forEach(el=>{
        const cls=(el.className||'').toString().split(/\s+/).filter(c=>c&&!/^p\d|bleed|dark|flap|back|cover|g1|g2$/.test(c))[0]||el.tagName.toLowerCase();
        const n=(seen.get(cls)||0)+1; seen.set(cls,n);
        const key=`p${pi}_${cls}${n>1?n:''}`;
        el.dataset.k=key; out.push({el,panel,key});
      });
    });
    return out;
  }
  function pxPerMm(){ return document.querySelector('.sheet').getBoundingClientRect().width/303; }
  function measure(b){
    const k=pxPerMm(), r=b.el.getBoundingClientRect(), p=b.panel.getBoundingClientRect();
    return {l:(r.left-p.left)/k, t:(r.top-p.top)/k, w:r.width/k, h:r.height/k};
  }
  // Freeze: measure everything in flow, then pin each block absolutely inside its panel.
  function freeze(layout){
    const bs=blocks(); const nat={};
    bs.forEach(b=>{ nat[b.key]=measure(b); });
    bs.forEach(b=>{
      const pos=(layout&&layout[b.key])||nat[b.key];
      const el=b.el;
      el.dataset.natW=nat[b.key].w; el.dataset.natH=nat[b.key].h;
      b.panel.appendChild(el);
      el.style.position='absolute'; el.style.left=pos.l+'mm'; el.style.top=pos.t+'mm';
      el.style.width=pos.w+'mm'; el.style.margin='0'; el.style.boxSizing='border-box'; el.style.zIndex=2;
      if(el.classList.contains('showroom')||el.classList.contains('logo')||el.classList.contains('sig')) el.style.height=pos.h+'mm';
      if(el.classList.contains('lab')){ const im=el.querySelector('img'); if(im&&pos.ih) im.style.height=pos.ih+'mm'; }
      if(el.parentElement.classList.contains('panel')){ /* ok */ }
    });
    // empty pads and grids no longer needed
    document.querySelectorAll('.pad,.tiles,.circ,.lifts').forEach(x=>{ if(!x.children.length) x.remove(); else x.style.position='static'; });
    document.querySelectorAll('.pad').forEach(x=>{x.style.inset='0';x.style.padding='0';x.style.height='216mm';x.style.position='absolute';});
    return {blocks:bs, nat};
  }
  window.BSUKLayout={blocks,measure,freeze,pxPerMm,SEL};
})();
