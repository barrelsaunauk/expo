#!/usr/bin/env python3
# BSUK expo booklet, A4 portrait, saddle stitched, 16 pages.
# Run: python3 -I build_booklet.py v1   (from anywhere)
# Photos: drop files into photos/ named by slot id (S01.jpg, S02.png ...). Empty slots print as labelled placeholders.
import os, sys, base64, io, glob
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
VER = sys.argv[1] if len(sys.argv) > 1 else 'v1'

def b64(path):
    ext = path.rsplit('.', 1)[1].lower(); mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'woff2': 'font/woff2'}[ext]
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def font(fam, file, w, style='normal'):
    return f"@font-face{{font-family:'{fam}';font-weight:{w};font-style:{style};src:url({b64(f'{HERE}/fonts/{file}')}) format('woff2')}}"

FONTS = '\n'.join([
    font('Fraunces', 'fraunces-latin-600-normal.woff2', 600), font('Fraunces', 'fraunces-latin-600-italic.woff2', 600, 'italic'),
    font('Lora', 'lora-latin-400-normal.woff2', 400), font('Lora', 'lora-latin-400-italic.woff2', 400, 'italic'),
    font('Lora', 'lora-latin-600-normal.woff2', 600),
    open(f'{HERE}/fonts/raleway700.css').read()])

LOGO, QR, SIG, BADGE, BAND = (b64(f'{HERE}/{f}') for f in ('logo.png', 'img03.png', 'img05.jpeg', 'badge.png', 'bg_band.jpeg'))
DRAW = [b64(f'{HERE}/img0{i}.png') for i in range(3)]

CSS = '''
:root{--ground:#16261C;--deep:#1F3D28;--forest:#2B5336;--mid:#417C51;--sage:#50795F;--sagep:#8fae86;--honey:#C08B41;--honeyl:#D6A868;--tint:#dbe7dd;--tint2:#eef4ef}
*{box-sizing:border-box;margin:0;padding:0}
@page{size:216mm 303mm;margin:0}
html{background:#e9ece9}
body{font-family:'Lora',Georgia,serif;color:#2c3a31;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:216mm;height:303mm;position:relative;overflow:hidden;margin:8mm auto;background:#fff;page-break-after:always;break-after:page}
@media print{html{background:#fff}.page{margin:0}.noprint{display:none}}
.page.dark{background:var(--ground);color:rgba(255,255,255,.88)}
.pad{position:absolute;inset:0;padding:20mm 19mm 18mm}
.pad>*{zoom:1.2}
.kicker{font-family:'Raleway',sans-serif;font-weight:700;font-size:7.5pt;letter-spacing:.3em;text-transform:uppercase;color:var(--honey);margin-bottom:4mm}
.dark .kicker{color:var(--honeyl)}
h1,h2,h3{font-family:'Fraunces',Georgia,serif;font-weight:600;line-height:1.08;letter-spacing:-.01em}
h1 em,h2 em,h3 em{font-style:italic;color:var(--honey)}
.dark h1 em,.dark h2 em,.dark h3 em{color:var(--honeyl)}
h2{font-size:27pt;color:var(--deep);margin-bottom:5mm;max-width:165mm}
.dark h2,.dark h3{color:#fff}
h3{font-size:14pt;color:var(--deep);margin:7mm 0 3.5mm}
p{font-size:10pt;line-height:1.6}
.lede{font-size:11.5pt;line-height:1.6;margin-bottom:7mm;max-width:160mm}
.ph{background:center/cover no-repeat var(--tint);border-radius:3.5mm;width:100%;display:block}
.ph.empty{display:flex;align-items:center;justify-content:center;text-align:center;background:repeating-linear-gradient(135deg,#dbe7dd 0 6mm,#d2e0d5 6mm 12mm);border:.4mm dashed var(--sage)}
.dark .ph.empty{background:repeating-linear-gradient(135deg,#25392c 0 6mm,#21342a 6mm 12mm);border-color:var(--sagep)}
.ph.empty span{font-family:'Raleway',sans-serif;font-weight:700;font-size:7pt;letter-spacing:.06em;color:var(--sage);padding:3mm;line-height:1.5}
.dark .ph.empty span{color:var(--sagep)}
.ph.empty b{display:block;font-size:13pt;color:var(--honey);letter-spacing:.04em}
.ph.empty i{font-family:'Lora',serif;font-weight:400;font-size:7.5pt;letter-spacing:0}
.ph.native{height:auto;border-radius:3mm}
.ph.bleed{position:absolute;inset:0;border-radius:0;height:auto}
.ph.band{position:absolute;left:0;right:0;top:0;border-radius:0}
.ph.round{width:30mm;height:30mm;border-radius:50%;margin:0 auto 3mm;border:.8mm solid #fff;box-shadow:0 0 0 .3mm var(--tint)}
.ph.round.empty span{font-size:5.5pt;padding:2mm}.ph.round.empty b{font-size:10pt}.ph.round.empty i{font-size:5.5pt}
/* cover */
.cover .veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(22,38,28,.88) 0%,rgba(22,38,28,.55) 38%,rgba(22,38,28,0) 62%,rgba(22,38,28,.75) 100%)}
.cover .logo{position:absolute;left:19mm;top:20mm;width:78mm}
.covertxt{position:absolute;left:19mm;right:19mm;top:62mm}
.cover h1{font-size:40pt;color:#fff;margin-bottom:6mm}
.cover p{font-size:11.5pt;max-width:140mm;color:rgba(255,255,255,.9)}
.coverfoot{position:absolute;left:19mm;right:19mm;bottom:16mm;font-family:'Raleway',sans-serif;font-weight:700;font-size:7.5pt;letter-spacing:.32em;color:var(--honeyl)}
/* lift cards */
.lift{display:flex;align-items:center;gap:5mm;background:#fff;border:.25mm solid #e3e8e4;border-radius:3.5mm;padding:5mm;box-shadow:0 1.2mm 3.5mm rgba(22,38,28,.08)}
.lift img{width:20mm;flex:none}
.lift b{display:block;font-family:'Raleway',sans-serif;font-weight:700;font-size:7.5pt;letter-spacing:.2em;text-transform:uppercase;color:var(--deep);margin-bottom:1.5mm}
.lift span{font-size:9pt;line-height:1.45;color:#4a554f}
.split{display:grid;grid-template-columns:1fr 1fr;gap:7mm;align-items:start}
.stack{display:flex;flex-direction:column;gap:5mm}
.pills{display:flex;gap:3mm;margin-top:10mm;flex-wrap:wrap}
.pills span{font-family:'Raleway',sans-serif;font-weight:700;font-size:7pt;letter-spacing:.18em;text-transform:uppercase;color:var(--deep);background:var(--tint2);border-radius:20mm;padding:2.5mm 5mm}
/* contents */
.contents{display:grid;grid-template-columns:1fr 1fr;gap:3.5mm 10mm;margin-top:4mm}
.contents div{display:flex;gap:4mm;align-items:baseline;border-bottom:.2mm solid rgba(255,255,255,.14);padding-bottom:2.5mm}
.contents b{font-family:'Fraunces',serif;font-size:15pt;color:var(--honeyl);width:10mm}
.contents span{font-size:10pt;color:#fff}
/* grids and captions */
.two{display:grid;grid-template-columns:1fr 1fr;gap:7mm}
.two.tight{gap:5mm;align-items:center}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:7mm 7mm;margin-top:3mm}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:5mm;margin-top:5mm}
.cap{font-size:9pt;line-height:1.5;margin-top:3mm;color:#4a554f}
.cap b{display:block;font-family:'Fraunces',serif;font-weight:600;font-size:11.5pt;color:var(--deep);margin-bottom:1mm}
.cap.d,.dark .cap{color:rgba(255,255,255,.8)}.cap.d b,.dark .cap b{color:#fff}
.lengths{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm}
.lengths div{background:#fff;border:.25mm solid #e3e8e4;border-radius:3mm;padding:3.5mm;box-shadow:0 1mm 3mm rgba(22,38,28,.07)}
.lengths b{display:block;font-family:'Fraunces',serif;font-size:16pt;color:var(--forest)}
.lengths span{font-size:8pt;line-height:1.4;color:#4a554f}
.circs{display:grid;grid-template-columns:repeat(3,1fr);gap:6mm;text-align:center}
.circs.four{grid-template-columns:repeat(4,1fr);gap:4mm}
.circs.four .ph.round{width:26mm;height:26mm}
.circ b{display:block;font-family:'Raleway',sans-serif;font-weight:700;font-size:7.5pt;letter-spacing:.16em;text-transform:uppercase;color:var(--deep);margin-bottom:1mm}
.circ span{display:block;font-size:8.5pt;line-height:1.4;color:#4a554f}
.circ.side{display:flex;align-items:center;gap:4mm;text-align:left}.circ.side .ph.round{margin:0;flex:none}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin-top:5mm}
.card{background:rgba(255,255,255,.06);border:.25mm solid rgba(255,255,255,.12);border-radius:3.5mm;padding:4.5mm}
.card b{display:block;font-family:'Fraunces',serif;font-weight:600;font-size:11.5pt;color:#fff;margin-bottom:1.5mm}
.card span{font-size:8.8pt;line-height:1.5}
.bandtxt{position:absolute;left:0;right:0;top:0;height:96mm;display:flex;align-items:flex-end;padding:0 19mm 8mm;background:linear-gradient(180deg,rgba(22,38,28,0) 40%,rgba(22,38,28,.85))}
.bandtxt h2{margin:0}
.ticks{display:flex;flex-wrap:wrap;gap:3mm;margin-top:7mm}
.ticks span{font-family:'Raleway',sans-serif;font-weight:700;font-size:7pt;letter-spacing:.14em;text-transform:uppercase;color:var(--honeyl);border:.3mm solid rgba(214,168,104,.5);border-radius:20mm;padding:2.3mm 4.5mm}
.quote{font-family:'Fraunces',serif;font-style:italic;font-size:20pt;color:var(--honeyl);text-align:center;margin-top:16mm}
/* journey */
.journey{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin:4mm 0 8mm}
.journey div{background:#fff;border:.25mm solid #e3e8e4;border-radius:3.5mm;padding:5mm;box-shadow:0 1.2mm 3.5mm rgba(22,38,28,.08)}
.journey i{font-style:normal;display:flex;width:12mm;height:12mm;border-radius:50%;background:var(--tint2);align-items:center;justify-content:center;font-size:15pt;margin-bottom:3mm;font-family:'Noto Color Emoji','Apple Color Emoji',sans-serif}
.journey b{display:block;font-family:'Fraunces',serif;font-size:12pt;color:var(--deep);margin-bottom:1mm}
.journey span{font-size:8.6pt;line-height:1.45;color:#4a554f}
.gs{display:flex;align-items:center;gap:6mm;background:var(--deep);border-radius:4mm;padding:6mm 7mm;color:#fff}
.gs .bd{width:24mm;height:24mm;border-radius:50%;background:#fff;overflow:hidden;display:flex;align-items:center;justify-content:center;flex:none}
.gs .bd img{width:82%}
.gs b{display:block;font-family:'Fraunces',serif;font-size:17pt;color:var(--honeyl);margin-bottom:1.5mm}
.gs span{font-size:10pt;line-height:1.5}
/* installs */
.masonry{columns:3;column-gap:4mm}
.masonry>*{break-inside:avoid;margin-bottom:5mm}
.masonry .ph.empty{height:44mm}
.detband{position:absolute;left:0;right:0;bottom:0;height:46mm;background:center/cover;display:flex;align-items:flex-end;padding:0 19mm 12mm}
.detband::before{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(22,38,28,.35),rgba(22,38,28,.85))}
.detband div{position:relative}.detband h3{color:#fff;margin:0 0 1.5mm;font-size:17pt}
/* back */
.qr{display:flex;align-items:center;gap:6mm;background:#fff;border-top:1.2mm solid var(--honey);border-radius:4mm;padding:6mm;margin:4mm 0 9mm;color:var(--deep)}
.qr img{width:36mm}
.qr b{display:block;font-family:'Fraunces',serif;font-size:15pt;margin-bottom:2mm}
.qr span{font-size:10pt;color:#4a554f}
.contacts{display:grid;grid-template-columns:1fr 1fr;gap:5mm 8mm;font-family:'Raleway',sans-serif;font-weight:700;font-size:12pt;color:#fff}
.contacts small{display:block;font-size:7pt;letter-spacing:.26em;text-transform:uppercase;color:var(--sagep);margin-bottom:1mm}
.sign{font-family:'Fraunces',serif;font-size:15pt;color:#fff;margin-top:12mm}
.back .sig{position:absolute;left:19mm;right:19mm;bottom:16mm;background:#fff;border-radius:4mm;overflow:hidden}
.back .sig img{width:100%;display:block}
.folio{position:absolute;left:19mm;bottom:9mm;font-family:'Raleway',sans-serif;font-weight:700;font-size:6.5pt;letter-spacing:.24em;text-transform:uppercase;color:var(--sage)}
.folio.d{color:var(--sagep)}
/* shot list (screen only) */
.shotlist{width:216mm;margin:8mm auto 20mm;background:#fff;padding:14mm 16mm;font-family:'Raleway',sans-serif}
.shotlist h2{font-size:20pt}
.shotlist table{width:100%;border-collapse:collapse;font-size:9pt}
.shotlist td{border-bottom:.2mm solid #e3e8e4;padding:2mm 2mm;vertical-align:top}
.shotlist td:first-child{font-weight:700;color:var(--honey);width:12mm}
.shotlist td:nth-child(2){color:var(--sage);width:42mm}
.shotlist .got{color:var(--mid);font-weight:700}
'''

# ---- v4 pages: 20 page A4 booklet, photos at their own ratio, no captions ----
PH = f'{HERE}/photos'
_cache = {}
def src(rel, maxpx=1800):
    if rel in _cache: return _cache[rel]
    im = ImageOps.exif_transpose(Image.open(f'{PH}/{rel}').convert('RGB'))
    if max(im.size) > maxpx:
        r = maxpx / max(im.size); im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=84, optimize=True)
    _cache[rel] = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    return _cache[rel]
def img(rel, style=''):  # whole photo, own ratio
    return f'<img class="pic" style="{style}" src="{src(rel)}">'
def fill(rel, cls='', style='', pos='50% 50%'):  # full bleed backgrounds only
    return f'<div class="fill {cls}" style="{style};background-image:url({src(rel)});background-position:{pos}"></div>'
def sq(rel, pos='50% 50%'):  # square insert (windows page, as asked)
    return f'<div class="sq" style="background-image:url({src(rel)});background-position:{pos}"></div>'
def lab(t): return f'<div class="lab">{t}</div>'
def kicker(t): return f'<div class="kicker">{t}</div>'
def lift(i, t, x): return f'<div class="lift"><img src="{i}"><div><b>{t}</b><span>{x}</span></div></div>'
def card(t, x): return f'<div class="card"><b>{t}</b><span>{x}</span></div>'
def folio(n, dark=False): return f'<div class="folio{" d" if dark else ""}">{n:02d} · Barrel Sauna UK</div>'

P = []
# 1 cover
P.append(f'''<section class="page dark cover">{fill("S01.png", "bleed")}<div class="veil"></div>
<img class="logo" src="{LOGO}">
<div class="covertxt">{kicker("The Barrel Sauna UK Collection")}
<h1>Handbuilt in Wales.<br><em>Made to order.</em><br>Built to last.</h1>
<p>Barrel saunas, hot tubs, cold plunges, mobile saunas and garden buildings, made by one Welsh family workshop.</p></div>
<div class="coverfoot">BARRELSAUNAUK.COM &nbsp;·&nbsp; 2026 EDITION</div></section>''')
# 2 who we are
P.append(f'''<section class="page light"><div class="pad">{kicker("Who we are")}
<h2>A Welsh family business with <em>woodworking in our blood</em></h2>
<p class="lede">We have been building bespoke outdoor saunas since day one. Every sauna is made to order in our Caerphilly workshop, then delivered and installed by our own team across the UK and Ireland.</p>
<div class="split" style="grid-template-columns:62mm 1fr">{img("S02.png")}
<div class="stack">{lift(DRAW[0],"Made to order","Choose your length, diameter, windows, heater and layout. Nothing comes off a shelf.")}
{lift(DRAW[1],"Built to last","Thermowood is heat treated timber that resists moisture, warping and decay.")}
{lift(DRAW[2],"Based in Wales","Every build comes out of the same workshop, with the same joinery and the same care.")}
<div class="pills"><span>Family business</span><span>Commercial grade</span><span>UK and Ireland installs</span></div></div></div>
</div>{folio(2)}</section>''')
# 3 contents
toc = [(4,'The gallery'),(6,'Sizing'),(7,'Step inside'),(8,'Bench layouts'),(9,'Windows'),(10,'The view from the bench'),(11,'Heaters'),(12,'Porch and changing room'),(13,'Mobile saunas'),(14,'Hot tubs'),(15,'Ice baths and the Double Dipper'),(16,'Pods, huts, cabins and showers'),(17,'Delivery and installation'),(18,'Your build, start to finish'),(19,'Owned and loved')]
P.append(f'''<section class="page dark"><div class="pad">{kicker("Inside")}
<h2>Everything we <em>build for you</em></h2>
<div class="contents">{''.join(f'<div><b>{n:02d}</b><span>{t}</span></div>' for n,t in toc)}</div>
{fill("S03.png","",'height:88mm;margin-top:8mm;border-radius:4mm',"50% 30%")}
</div>{folio(3, True)}</section>''')
# 4-5 gallery spread
P.append(f'''<section class="page dark gal"><div class="gp">
<div class="gcol">{img("gallery/G01.png")}{img("gallery/G08.png")}</div>
<div class="gcol">{img("gallery/G05.png")}{img("gallery/G03.png")}{img("gallery/G02.png")}</div>
</div>{folio(4, True)}</section>''')
P.append(f'''<section class="page dark gal"><div class="gp">
<div class="gcol">{img("gallery/G10.png")}{img("gallery/G06.png")}{img("gallery/G09.png")}</div>
<div class="gcol">{img("gallery/G04.png")}{img("gallery/G07.png")}</div>
</div><div class="galfoot">Every one of these was built in our Caerphilly workshop.</div>{folio(5, True)}</section>''')
# 6 sizing
P.append(f'''<section class="page light"><div class="pad">{kicker("Sizing")}
<h2>Choose the size that <em>fits your space</em></h2>
<div class="two" style="align-items:end"><div>{img("S04.png")}{lab("Compact")}</div><div>{img("S05.jpg")}{lab("Grand")}</div></div>
<p class="lede" style="margin-top:6mm">2m or 2.3m diameter. Go wider for 30cm more bench width and headroom, the pick for taller users.</p>
<div class="lengths">
<div><b>1.8m</b><span>Compact. Two to four people.</span></div><div><b>2.4m</b><span>Standard, with porch.</span></div>
<div><b>3.2m</b><span>Spacious. Porch or changing room.</span></div><div><b>3.7m</b><span>Popular. Porch and changing room.</span></div>
<div><b>4.2m</b><span>Extra spacious.</span></div><div><b>4.7m</b><span>XL. Side entrance option.</span></div>
<div><b>6m</b><span>Grand. Full changing room and porch.</span></div></div>
</div>{folio(6)}</section>''')
# 7 step inside
P.append(f'''<section class="page light"><div class="pad">{kicker("Step inside")}
<h2>Porch, changing room, <em>sauna</em></h2>
<p class="lede">Three spaces in one barrel. Step in off the porch, change in the warm, then take the heat.</p>
{img("renders/R1_full3d.png")}
{img("renders/R4_topdown_long.png", "width:62%;margin:4mm auto 0")}
</div>{folio(7)}</section>''')
# 8 benches
P.append(f'''<section class="page dark"><div class="pad">{kicker("Bench layouts")}
<h2>How you sit, stretch <em>and share the heat</em></h2>
<div class="b3">
<div>{lab("U-shape")}{img("renders/R3_U_trailer.png")}{img("S06.jpg","margin-top:3mm")}</div>
<div>{lab("Straight")}{img("renders/R5_straight_topdown.png")}{img("S07.jpg","margin-top:3mm")}</div>
<div>{lab("L-shape")}{img("renders/R2_L_compact.jpg")}{lab("Globe seating")}{img("S09.png")}</div>
</div></div>{folio(8, True)}</section>''')
# 9 windows
P.append(f'''<section class="page light"><div class="pad">{kicker("Windows")}
<h2>Frame the view <em>you want</em></h2>
<p class="lede">Double glazed and heat resistant as standard. Choose the back wall and the front wall separately.</p>
<h3>Back wall</h3><div class="sq3"><div>{sq("S10.png")}{lab("Half moon")}</div><div>{sq("S11.jpg")}{lab("Full flat glass")}</div><div>{sq("S12.png","50% 40%")}{lab("Panoramic dome")}</div></div>
<h3>Front wall</h3><div class="sq3"><div>{sq("S13.png")}{lab("Rectangular")}</div><div>{sq("S14.jpg")}{lab("Glass door")}</div><div>{sq("S15.png")}{lab("Glass facade")}</div></div>
</div>{folio(9)}</section>''')
# 10 view from the bench
P.append(f'''<section class="page dark"><div class="pad">{kicker("The view from the bench")}
<h2>This is what you <em>come back for</em></h2>
<div class="gp2"><div class="gcol">{img("views/V4_mountain_lake.png")}{img("views/V3_sails_halfmoon.png")}</div>
<div class="gcol">{img("views/V1_man_lake_dusk.png")}{img("views/V2_group_globe_night.png")}</div></div>
</div>{folio(10, True)}</section>''')
# 11 heaters
P.append(f'''<section class="page dark">{fill("S16.jpg","band","height:84mm","50% 72%")}
<div class="bandtxt" style="height:84mm"><h2>The heat is <em>yours to choose</em></h2></div>
<div class="pad" style="padding-top:90mm">{kicker("Heaters")}
<div class="h3row"><div>{img("H1.jpg")}{lab("Hybrid")}</div><div>{img("H2.png")}{lab("Electric switch")}</div><div>{img("H3.png")}{lab("Electric WiFi")}</div></div>
<div class="cards">
{card("Wood burning", "Loaded from inside the traditional way, or from outside the back wall so no smoke or ash comes in.")}
{card("Electric WiFi", "Our top pick. Preheat from your phone with the Harvia app.")}
{card("Electric switch", "Simple and reliable. Switch on, set the dial, no app needed.")}
{card("Hybrid", "Electric for a quick weeknight session, wood for the ritual at the weekend.")}
</div></div>{folio(11, True)}</section>''')
# 12 porch and changing room
P.append(f'''<section class="page light"><div class="pad">{kicker("Porch and changing room")}
<h2>Step out, cool down, <em>take in the view</em></h2>
<p class="lede">Add a 0.6m porch to step out and cool down, with backrests, armrests and drinks holders, or keep it clean and open. A changing room is a heat trap, a rest zone and a second room, 1m as standard and longer on request.</p>
<div class="gp2 light" style="width:72%;margin:0 auto"><div class="gcol">{img("S17.jpg")}{img("S20.jpg")}</div><div class="gcol">{img("S18.jpg")}{img("S22.jpg")}</div></div>
</div>{folio(12)}</section>''')
# 13 mobile
P.append(f'''<section class="page dark"><div class="pad">{kicker("Mobile saunas")}
<h2>Welsh built trailers. <em>Built to move.</em></h2>
{img("S23.png","width:86%;margin:0 auto")}
<p style="margin:5mm 0">Our trailers are made entirely in house, from frame and welding to galvanising and finish, and each one goes through DVSA IVA testing for UK roads. Every unit is designed around the sauna that sits on it.</p>
{img("M1.jpg","width:72%;margin:0 auto")}
<div class="ticks"><span>Galvanised frame</span><span>UK IVA tested</span><span>Braked</span><span>Steel stabilisers</span><span>Timber decking</span><span>Built-in storage</span><span>Lighting system</span><span>Clip-on timber steps</span></div>
</div>{folio(13, True)}</section>''')
# 14 hot tubs
P.append(f'''<section class="page light"><div class="pad">{kicker("Hot tubs")}
<h2>Classic look. <em>Modern performance.</em></h2>
<p class="lede">Built from the same Thermowood as our saunas. Wood fired or electric, with air jets, jacuzzi jets, LED lighting and an insulated thermo lid.</p>
{img("S24.jpg")}
<div class="h3row" style="margin-top:5mm"><div>{img("T1_lid.png")}{lab("Insulated lid")}</div><div>{img("T2_woodfired.png")}{lab("Wood fired")}</div><div>{img("T3_square.png")}{lab("Square tub")}</div></div>
</div>{folio(14)}</section>''')
# 15 ice baths
P.append(f'''<section class="page dark"><div class="pad">{kicker("Ice baths and cold plunges")}
<h2>Cold to go <em>with the hot</em></h2>
<p class="lede">Timber built cold plunge tubs made to match your sauna, for the full contrast of hot and cold.</p>
<div class="two"><div>{img("S26.png")}{lab("Single dipper")}</div><div>{img("S27.jpg")}{lab("The Double Dipper")}</div></div>
<div class="quote" style="margin:6mm 0">Sauna, then the plunge, then breathe. Repeat.</div>
<div class="two" style="align-items:end;width:78%;margin:0 auto">{img("I1.png")}{img("I2.png")}</div>
</div>{folio(15, True)}</section>''')
# 16 pods
P.append(f'''<section class="page light"><div class="pad">{kicker("More than saunas")}
<h2>Pods, huts, cabins <em>and showers</em></h2>
<p class="lede">Built in the same workshop with the same joinery. Glamping pods are made to any size and insulated for year round use, and in many cases need no planning permission, which we will check with you.</p>
<div class="two"><div>{img("S28.png")}{lab("Glamping pods")}</div><div>{img("S29.png")}{lab("Shepherd's huts")}</div>
<div>{img("S30.png")}{lab("Grill cabins")}</div><div>{img("S31.png")}{lab("Barrel showers")}</div></div>
</div>{folio(16)}</section>''')
# 17 delivery
P.append(f'''<section class="page dark"><div class="pad">{kicker("Delivery and installation")}
<h2>Difficult access <em>is not an issue</em></h2>
<div class="two" style="grid-template-columns:1.34fr 1fr;align-items:end">{img("S32.png")}{img("S33.png")}</div>
<div class="cards">
{card("Full on-site build", "Our team carries everything in and builds in place, in one day for most saunas.")}
{card("Crane or trailer", "A hiab lifts over drives and walls locally. Further afield we bring it on our own trailer.")}
{card("UK, Ireland and beyond", "Completed jobs across England, Wales, Scotland, Ireland and the Isle of Man.")}
{card("The right base", "A raised timber base, or a full deck that brings sauna, hot tub and plunge together.")}
</div></div>{folio(17, True)}</section>''')
# 18 journey
P.append(f'''<section class="page light"><div class="pad">{kicker("Your build, start to finish")}
<h2>Simple from <em>first call to first session</em></h2>
<div class="journey">
<div><i>📞</i><b>Design call</b><span>Tell us about your space and how you will use it.</span></div>
<div><i>📄</i><b>Estimate</b><span>A clear estimate for your exact build.</span></div>
<div><i>💳</i><b>Deposit</b><span>Your deposit puts you next in line in our build queue.</span></div>
<div><i>🔨</i><b>Built in Wales</b><span>Your sauna is made to order in our workshop.</span></div>
<div><i>🚚</i><b>Delivered and built</b><span>Our team installs it on site.</span></div>
<div><i>🔥</i><b>First session</b><span>Owner's manual, aftercare guide and warranty included.</span></div>
</div>
<div class="gs"><div class="bd"><img src="{BADGE}"></div><div><b>50 trees with every order</b><span>In partnership with Green Spark, every sauna, tub and hut we build plants fifty trees.</span></div></div>
<div class="two tight" style="margin-top:6mm">{lift(DRAW[0],"Showspace in Caerphilly","Come and sit in one before you decide.")}{lift(DRAW[2],"Finance available","Ask us about it on your design call.")}</div>
</div>{folio(18)}</section>''')
# 19 owned and loved
P.append(f'''<section class="page dark"><div class="pad">{kicker("Owned and loved")}
<h2>Real owners, <em>real sessions</em></h2>
<div class="gp2" style="width:92%;margin:0 auto"><div class="gcol">{img("customers/C1_globe_sunset.png")}{img("customers/C3_hot2cold.png")}</div>
<div class="gcol">{img("customers/C2_harbour_night.png")}{img("customers/C6_pod_stars.png")}</div></div>
<p class="galnote">All over the UK and Ireland.</p>
</div>{folio(19, True)}</section>''')
# 20 back
P.append(f'''<section class="page dark back"><div class="pad">
<img src="{LOGO}" style="width:70mm;margin-bottom:10mm">
{kicker("Ready when you are")}<h2>Book your <em>design call</em></h2>
<div class="qr"><img src="{QR}"><div><b>Scan to book a call back</b><span>barrelsaunauk.com/book-a-call-back</span></div></div>
<div class="contacts"><div><small>WhatsApp</small>+44 7360 274142</div><div><small>Office</small>+44 2920 676731</div>
<div><small>Email</small>info@barrelsaunauk.com</div><div><small>Web</small>barrelsaunauk.com</div></div>
<p class="sign">The Barrel Sauna UK Team</p></div>
<div class="sig"><img src="{SIG}"></div></section>''')

CSS += '''
.pic{display:block;width:100%;height:auto;border-radius:3mm}
.fill{background:center/cover no-repeat;display:block}
.fill.bleed{position:absolute;inset:0}
.fill.band{position:absolute;left:0;right:0;top:0}
.sq{width:100%;aspect-ratio:1;background:center/cover no-repeat;border-radius:3mm}
.lab{font-family:'Raleway',sans-serif;font-weight:700;font-size:6.5pt;letter-spacing:.24em;text-transform:uppercase;color:var(--honey);margin:2.2mm 0 0}
.dark .lab{color:var(--honeyl)}
.b3 .lab{margin:0 0 2mm}.b3 .lab+.pic,.b3 .pic+.lab{margin-top:3mm}
.b3{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;align-items:start}
.sq3{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.h3row{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;align-items:end}
.gal .gp{position:absolute;inset:9mm 9mm 16mm;display:grid;grid-template-columns:1fr 1fr;gap:3mm;align-items:start}
.gcol{display:flex;flex-direction:column;gap:3mm}
.gal .pic{border-radius:1.5mm}
.gp2{display:grid;grid-template-columns:1fr 1fr;gap:3mm;align-items:start}
.galfoot,.galnote{font-family:'Fraunces',serif;font-style:italic;color:var(--honeyl);font-size:11pt}
.galfoot{position:absolute;right:9mm;bottom:8mm}
.galnote{margin-top:4mm}
.split .pic{height:auto}
/* phone and tablet: scale whole pages to fit the screen */
@media screen and (max-width:860px){html{background:#16261C}}
@media print{body{zoom:1!important}}
'''
FIT = '''<script>(function(){function f(){var w=document.documentElement.clientWidth,p=816+12;var z=Math.min(1,(w-16)/p);document.body.style.zoom=z;}f();addEventListener('resize',f);})();</script>'''
html = f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>BSUK expo booklet A4 {VER}</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>{FONTS}{CSS}</style></head><body>
<!-- Barrel Sauna UK expo booklet {VER} · A4 portrait 210 x 297 mm trim, 3 mm bleed (page 216 x 303 mm), 20 pages saddle stitched -->
{''.join(P)}{FIT}</body></html>'''
out = f'{HERE}/../bsuk_expo_booklet_a4_{VER}.html'
open(out, 'w', encoding='utf-8').write(html)
print(os.path.abspath(out), round(len(html)/1e6,1), 'MB', 'pages', len(P))
