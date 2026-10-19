#!/usr/bin/env python3
# BSUK commercial trifold, evening edition, v8 build from the 19 Oct change list.
import re, base64, io, sys
from PIL import Image, ImageOps
import numpy as np

TRI = '/tmp/claude-0/-home-claude/7b8b3e4b-5935-5230-9525-71c39d73d36c/scratchpad/tri'
HERE = '/tmp/claude-0/-home-claude/7b8b3e4b-5935-5230-9525-71c39d73d36c/scratchpad/commercial'
VER = sys.argv[1] if len(sys.argv) > 1 else 'v8'

src = open(f'{TRI}/trifold_source.html', encoding='utf-8').read()
fonts = '\n'.join(l for l in src[src.find('<style>')+7:src.find('</style>')].split('\n') if l.startswith('@font-face'))
base_css = open(f'{TRI}/css.txt').read()
marks = open(f'{TRI}/marks.html').read()

def b64file(path):
    b = open(path, 'rb').read(); ext = 'png' if path.endswith('.png') else 'jpeg'
    return f'data:image/{ext};base64,' + base64.b64encode(b).decode()

def photo(path, w, h, pos=(0.5, 0.5), q=86):
    im = ImageOps.exif_transpose(Image.open(path).convert('RGB')); W, H = im.size
    tw, th = int(w / 25.4 * 300), int(h / 25.4 * 300)
    r = max(tw / W, th / H); nw, nh = int(W * r + .5), int(H * r + .5)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = int((nw - tw) * pos[0]); y = int((nh - th) * pos[1]); im = im.crop((x, y, x + tw, y + th))
    out = io.BytesIO(); im.save(out, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(out.getvalue()).decode()

def png_rgba(path, maxw=None):
    im = Image.open(path).convert('RGBA')
    if maxw and im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    out = io.BytesIO(); im.save(out, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(out.getvalue()).decode()

def pines_honey(path, maxw=1000):
    # recolour the pine drawing to honey light on transparent, keeping its line weight
    im = Image.open(path).convert('RGBA')
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    a = np.array(im).astype(float)
    lum = (a[:, :, 0] * .299 + a[:, :, 1] * .587 + a[:, :, 2] * .114)
    alpha = np.clip((235 - lum) / 235, 0, 1) * (a[:, :, 3] / 255)
    out = np.zeros_like(a); out[:, :, 0] = 0xD6; out[:, :, 1] = 0xA8; out[:, :, 2] = 0x68; out[:, :, 3] = alpha * 255
    im2 = Image.fromarray(out.astype('uint8'), 'RGBA')
    buf = io.BytesIO(); im2.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

v13img = lambda i, ext: b64file(f'{TRI}/img{i:02d}.{ext}')
lift1, lift2, lift3 = v13img(0,'png'), v13img(1,'png'), v13img(2,'png')
qr, team, sig, logo = v13img(3,'png'), v13img(4,'png'), v13img(5,'jpeg'), b64file(f'{TRI}/logo.png')
band = b64file(f'{TRI}/bg_band.jpeg')
v = ImageOps.flip(Image.open(f'{TRI}/bg_veil.png')).convert('RGBA')
a = np.array(v).astype(float); a[:, :, 3] *= 0.42; v = Image.fromarray(a.astype('uint8'), 'RGBA')
buf = io.BytesIO(); v.save(buf, 'PNG', optimize=True); veil_top = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

_im = ImageOps.exif_transpose(Image.open(f'{HERE}/moon.png').convert('RGB'))
_W,_H=_im.size; _im=_im.crop((int(_W*.12), 0, int(_W*.88), int(_H*.90))); _im.save(f'{HERE}/moon_crop.jpg', quality=95)
cover = photo(f'{HERE}/moon_crop.jpg', 102, 216, pos=(0.5, 0.0), q=88)
flap = photo(f'{HERE}/flap.jpg', 102, 44, pos=(0.55, 0.55))
flynn_big = photo(f'{HERE}/flynn_summer.png', 85, 36, pos=(0.5, 0.55))
flynn_small = photo(f'{HERE}/flynn_winter.jpg', 22, 22, pos=(0.45, 0.6))
t_surf = photo(f'{HERE}/surf.png', 40, 18, pos=(0.5, 0.55))
t_h2c = photo(f'{HERE}/hot2cold_ed.png', 40, 18, pos=(0.5, 0.42))
t_esc = photo(f'{HERE}/escape_gold.png', 40, 18, pos=(0.5, 0.6))
t_sea = photo(f'{HERE}/seacoast.png', 40, 18, pos=(0.5, 0.6))
prods = [
 ('Barrel sauna', 'Fixed on a base or decking. Built on site by our team.', photo(f'{HERE}/p1_sauna.png', 24, 24, pos=(0.55, 0.5))),
 ('Mobile sauna', 'Move it, hire it out, take it to events. Our own Welsh built trailers.', photo(f'{HERE}/p2_mobile.png', 24, 24, pos=(0.5, 0.5))),
 ('Hot tubs', 'Pairs with the sauna for a hot and cold session. Wood fired or electric.', photo(f'{HERE}/p3_tub.jpg', 24, 24, pos=(0.45, 0.7))),
 ('Ice baths', 'Cold to go with the hot. A single plunge or the Double Dipper for two.', photo(f'{HERE}/p4_ice.jpg', 24, 24, pos=(0.55, 0.6))),
 ('Double Dipper', 'Sauna and plunge on one deck. Hot and cold in one bookable session.', photo(f'{HERE}/p5_dd.png', 24, 24, pos=(0.5, 0.55))),
 ('Barrel showers', 'Rinse off between hot and cold. Easy to keep clean.', photo(f'{HERE}/p6_shower.jpg', 24, 24, pos=(0.5, 0.5))),
 ("Shepherd's huts", 'Extra bookable stays, built in the same workshop.', photo(f'{HERE}/p7_hut.png', 24, 24, pos=(0.4, 0.5))),
 ('Glamping pods', 'Often need no planning permission.', photo(f'{HERE}/p8_pod.jpg', 24, 24, pos=(0.4, 0.5))),
 ('Grill cabins', 'Covered seating and a fire in the middle. Open all year.', photo(f'{HERE}/p9_grill.png', 24, 24, pos=(0.5, 0.5))),
]
night = photo(f'{HERE}/night.png', 85, 44, pos=(0.5, 0.62))
badge = png_rgba(f'{HERE}/badge.png', 300)
pines = pines_honey(f'{HERE}/pines.png')

css = base_css + '''
.cover .veiltop{position:absolute;inset:0;background:url(VEILTOP) center/100% 100% no-repeat}
.cover .logo.top{top:22mm;left:27.5mm}
.cover .txt.top{top:46mm;text-shadow:0 .5mm 2mm rgba(0,0,0,.55)}
.cover h1{font-size:24pt}
.cover .url.intext{position:static;text-align:left;margin-top:5mm}
/* evening edition, two greens */
.sheet{background:var(--ground)}
.panel{color:#fff}
.panel.g1{background:var(--ground)}
.panel.g2{background:var(--forest)}
.panel p{color:rgba(255,255,255,.86)}
.panel h1{color:#fff}.panel h1 em{color:var(--honeyl)}
.kicker{color:var(--honeyl)}
.sub{font-size:6.6pt;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--honeyl);opacity:.85;margin:0 0 2.2mm}
.flap .sub{color:var(--honeyl);opacity:.85}
.flap .showroom{top:60mm;height:44mm}
.flap .lifts{top:97mm}
/* labelled image */
.lab{background:#fff;border-radius:3.5mm;overflow:hidden;box-shadow:0 2mm 5mm rgba(0,0,0,.4)}
.lab img{width:100%;display:block}
.lab .tab{background:var(--deep);border-top:.8mm solid var(--honey);color:#fff;font-size:6.6pt;font-weight:700;letter-spacing:.16em;text-transform:uppercase;padding:2mm 3mm}
.lab .note{padding:2mm 3mm 2.6mm;font-size:7pt;line-height:1.4;color:#4a554f}
.lab .duo{display:flex;align-items:flex-start;gap:2.4mm;padding:1.8mm 2.6mm 2.2mm}
.lab .duo img{width:21mm;height:21mm;object-fit:cover;border-radius:2.5mm;flex:none}
.lab .duo .note{padding:0;font-size:6.5pt;line-height:1.35}
.tiles{display:grid;grid-template-columns:1fr 1fr;gap:2.6mm}
.tiles .lab img{height:14mm;object-fit:cover}
.tiles .lab .tab{font-size:5.6pt;letter-spacing:.1em;padding:1.4mm 2.3mm}
.tiles .lab .note{font-size:5.9pt;padding:1.2mm 2.2mm 1.6mm;line-height:1.28}
/* circles */
.circ{display:grid;grid-template-columns:1fr 1fr 1fr;gap:3.2mm 2mm;text-align:center;margin-top:1mm}
.circ img{width:23mm;height:23mm;border-radius:50%;object-fit:cover;border:.7mm solid rgba(255,255,255,.22);display:block;margin:0 auto 1.6mm}
.circ b{display:block;font-size:6.4pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#fff;line-height:1.2;margin-bottom:.8mm}
.circ span{display:block;font-size:6.1pt;line-height:1.3;color:rgba(255,255,255,.78);padding:0 .5mm}
/* numerals */
.num{display:flex;gap:3mm;align-items:flex-start;padding:1.7mm 0;border-bottom:.2mm solid rgba(255,255,255,.12)}
.num:last-of-type{border-bottom:none}
.num .n{font-size:18pt;font-weight:800;color:var(--honeyl);line-height:.9;width:11mm;flex:none;letter-spacing:-.02em}
.num p{font-size:7.2pt;line-height:1.35}
.num b{color:#fff;display:block;font-size:8.2pt;margin-bottom:.5mm}
.extras{background:rgba(255,255,255,.07);border-radius:3mm;padding:2.2mm 3.2mm;margin:2.4mm 0 2.4mm}
.extras p{font-size:7.2pt;line-height:1.45;margin:0 0 .9mm}
.extras p:last-child{margin:0}
.extras b{color:var(--honeyl)}
/* Green Spark card */
.gs{position:relative;overflow:hidden;display:flex;align-items:center;gap:3.5mm;background:rgba(255,255,255,.07);border:.3mm solid rgba(214,168,104,.45);border-radius:3.5mm;padding:3.2mm 3.6mm}
.gs .bd{width:14mm;height:14mm;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;flex:none;position:relative;z-index:1}
.gs .bd img{width:11.5mm;display:block}
.gs .tx{position:relative;z-index:1}
.gs b{display:block;font-size:10pt;font-weight:800;color:var(--honeyl);line-height:1.1;margin-bottom:1mm}
.gs span{display:block;font-size:7.2pt;line-height:1.4;color:rgba(255,255,255,.88)}
.gs span em{font-style:normal;font-weight:700;color:#fff}
.gs.pine{padding-bottom:10mm}
.gs .pines{position:absolute;left:0;right:0;bottom:-.5mm;height:10mm;background:url(PINES) center bottom/100% auto no-repeat;opacity:.9}
'''.replace('VEILTOP', veil_top).replace('PINES', pines)

circles = ''.join(f'<div><img src="{p[2]}"><b>{p[0]}</b><span>{p[1]}</span></div>' for p in prods)

html = f'''<!doctype html>
<html lang="en-GB"><head><meta charset="utf-8"><title>BSUK commercial trifold {VER}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
{fonts}
{css}
</style></head>
<body>
<!-- Barrel Sauna UK commercial trifold · evening edition · print file {VER} · 297 x 210 mm trim, 3 mm bleed, roll fold at 99 and 198 mm, flip on the long edge -->
<div class="sheet outside">{marks}
<div class="panel p0 bleed flap g1">
 <div class="pad">
  <div class="kicker">Who we are</div>
  <h1>A Welsh <em>family</em> business</h1>
  <div class="sub">Family business &nbsp;·&nbsp; Commercial grade quality &nbsp;·&nbsp; UK and Ireland installation</div>
  <p>A Welsh family business with woodworking in our blood, building bespoke outdoor saunas since day one. Every sauna is made to order, delivered and installed across the UK and Ireland.</p>
 </div>
 <div class="showroom" style="background-image:url({flap})"></div>
 <div class="lifts">
  <div class="lift"><img src="{lift1}"><div><b>Made to order</b><span>Every sauna is made to order. Choose your length, diameter and layout.</span></div></div>
  <div class="lift"><img src="{lift2}"><div><b>Built to last</b><span>Thermowood is heat treated timber that resists moisture, warping and decay.</span></div></div>
  <div class="lift"><img src="{lift3}"><div><b>Based in Wales</b><span>Built in the same workshop as our saunas, same joinery, same attention to detail.</span></div></div>
 </div>
</div>
<div class="panel p1 dark back g2">
 <div class="pad">
  <div class="kicker">What happens next</div>
  <h1>Ready <em>when you are</em></h1>
  <div class="how"><div class="k">HOW IT WORKS</div>
   <div class="steps">
    <div class="step"><div class="disc">📞</div><small>Design call</small></div>
    <div class="step"><div class="disc">📄</div><small>Estimate</small></div>
    <div class="step"><div class="disc">💳</div><small>Deposit</small></div>
    <div class="step"><div class="disc">🏠</div><small>Built at yours</small></div>
   </div></div>
  <div class="qr"><img src="{qr}"><div><b>Book your design call</b><span>barrelsaunauk.com/book-a-call-back</span><span>Scan with your phone camera.</span></div></div>
  <div class="contacts">
   <div><div class="k">WhatsApp</div><div class="v">+44 7360 274142</div></div>
   <div><div class="k">Office</div><div class="v">+44 2920 676731</div></div>
   <div style="grid-column:1/3"><div class="k">Email</div><div class="v">info@barrelsaunauk.com</div></div>
  </div>
  <div class="dep"><p>A <b>£500 deposit</b> secures your place in the build queue. All prices plus VAT.</p></div>
  <div class="gs" style="margin:0 0 4mm"><div class="bd"><img src="{badge}"></div><div class="tx"><b>50 trees with every order</b><span>In partnership with <em>Green Spark</em>.</span></div></div>
  <div class="team"><b>The Barrel Sauna UK Team</b><div class="k">BARRELSAUNAUK.COM &nbsp;·&nbsp; HANDCRAFTED IN WALES</div></div>
 </div>
 <div class="sig"><img src="{sig}"></div>
</div>
<div class="panel p2 bleed cover">
 <div class="ph" style="background-image:url({cover})"></div><div class="veiltop"></div>
 <img class="logo top" src="{logo}">
 <div class="txt top"><div class="rule"></div><div class="kicker" style="color:var(--honeyl)">For parks, venues and operators</div>
  <h1>A sauna that's<br><em>built to be booked.</em></h1>
  <p>From a single trailer sauna to a full site setup. Made to order and installed by our team, so you are open for bookings from day one.</p><div class="url intext">BARRELSAUNAUK.COM</div></div>
</div></div>
<div class="sheet inside">{marks}
<div class="panel p0 bleed g2">
 <div class="pad">
  <div class="kicker">Already running on our saunas</div>
  <h1 style="font-size:18pt;margin-bottom:3mm">Real venues, <em>real bookings</em></h1>
  <div class="lab" style="margin-bottom:3.2mm"><img src="{flynn_big}" style="height:36mm;object-fit:cover"><div class="tab">Sauna Snug at Flynn Park · Co. Dublin</div>
   <div class="duo"><img src="{flynn_small}"><div class="note">A family adventure park running since 1996 added barrel saunas with a spring fed lake dip. Public sessions for up to eight, private hire for one to eight, open seven days a week.</div></div></div>
  <div class="sub">Other real life examples</div>
  <div class="tiles">
   <div class="lab"><img src="{t_surf}"><div class="tab">Surf South West · Devon</div><div class="note">5m trailer sauna, panoramic window, solar lighting. Beaches, events and retreats.</div></div>
   <div class="lab"><img src="{t_h2c}"><div class="tab">Hot2Cold · Cardiff</div><div class="note">4m trailer sauna with globe window and changing room. Early swims and festivals.</div></div>
   <div class="lab"><img src="{t_esc}"><div class="tab">Escape to the Sauna · Cornwall</div><div class="note">3.5m trailer sauna, wood burner, half moon window, by the water.</div></div>
   <div class="lab"><img src="{t_sea}"><div class="tab">Sea Coast Saunas · Anglesey</div><div class="note">Sauna and hot tub on the shoreline, built for life by the sea.</div></div>
  </div>
 </div>
</div>
<div class="panel p1 g1">
 <div class="pad">
  <div class="kicker">What to put on your site</div>
  <h1 style="font-size:18pt;margin-bottom:4mm">Everything <em>guests book</em></h1>
  <div class="circ">{circles}</div>
 </div>
</div>
<div class="panel p2 bleed g2">
 <div class="pad">
  <div class="kicker">Why it works</div>
  <h1 style="font-size:18pt;margin-bottom:3mm">A sauna that <em>works for a site</em></h1>
  <div class="lab" style="margin-bottom:2.5mm"><img src="{night}" style="height:44mm;object-fit:cover"><div class="tab">Open late · booked out by the harbour</div></div>
  <div class="num"><div class="n">01</div><p><b>Any weather, any season</b>Guests book a sauna in the rain as readily as the sun. It fills the quiet months.</p></div>
  <div class="num"><div class="n">02</div><p><b>Wood or electric</b>Wood fired for off grid corners, electric where you have power. Your choice.</p></div>
  <div class="num"><div class="n">03</div><p><b>Start mobile, then build</b>A trailer sauna tests the spot. When it works, we build the fixed one.</p></div>
  <div class="extras">
   <p><b>Finance available.</b> Ask us on the call.</p>
   <p><b>Showspace in Caerphilly.</b> Come and sit in one first.</p>
   <p><b>Owner's manual, aftercare guide and warranty</b> with every build.</p>
  </div>
  <div class="gs pine"><div class="bd"><img src="{badge}"></div><div class="tx"><b>50 trees with every order</b><span>In partnership with <em>Green Spark</em>, every sauna, tub and hut we build plants fifty trees.</span></div><div class="pines"></div></div>
 </div>
</div><div class="band" style="background-image:url({band})"></div></div>
</body></html>'''

import json, os
layout_js = open(f'{HERE}/layout.js').read()
editor_js = open(f'{HERE}/editor.js').read()
lay_path = f'{HERE}/layout_current.json'
layout = json.load(open(lay_path)) if os.path.exists(lay_path) else None
# print file: pin blocks to the saved layout (if any), no UI
apply_js = f'<script>{layout_js}</script>' + (f'<script>BSUKLayout.freeze({json.dumps(layout)});</script>' if layout else '')
print_html = html.replace('</body></html>', apply_js + '</body></html>')
out = f'{HERE}/bsuk_commercial_trifold_{VER}.html'
open(out, 'w', encoding='utf-8').write(print_html)
# editor file: same page plus drag tools (starts from the saved layout too)
ed_html = html.replace('<title>', '<title>Layout editor · ').replace('</body></html>',
  f'<script>{layout_js}</script><script>window.BASE_LAYOUT={json.dumps(layout) if layout else "null"};</script><script>{editor_js}</script></body></html>')
ed_out = f'{HERE}/commercial_layout_editor_{VER}.html'
open(ed_out, 'w', encoding='utf-8').write(ed_html)
print(out, len(print_html)); print(ed_out, len(ed_html))
