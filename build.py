#!/usr/bin/env python3
"""Static site builder for Signature Africa.
Reads content.json (the single source of truth, also editable via /admin)
and renders the HTML shell around it, tagging every text/image element with
data-key / data-img-key so assets/js/content.js can hot-swap content after a
CMS edit without needing a rebuild.
"""
import json
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://signatureafrica.co.zw"
WA_LINK = "https://wa.me/263784564644"

with open(os.path.join(OUT_DIR, "content.json"), encoding="utf-8") as f:
    C = json.load(f)

G = C["global"]

NAV = [
    {"label": "Home", "href": "index.html"},
    {"label": "Tours &amp; Transfers", "href": "victoria-falls.html", "children": [
        ("victoria-falls.html", "Victoria Falls, Zimbabwe"),
        ("livingstone.html", "Livingstone, Zambia"),
        ("kasane.html", "Kasane, Botswana"),
    ]},
    {"label": "Fleet", "href": "fleet.html"},
    {"label": "Aviation", "href": "aviation.html", "children": [
        ("aviation.html#vip", "VIP Airport Services"),
        ("aviation.html#charters", "Private Charter Flights"),
        ("aviation.html#destinations", "Destinations"),
    ]},
    {"label": "Contact", "href": "contact.html"},
]


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(page, key, tag="span", cls="", extra=""):
    """Render a text node bound to content.json[page][key]."""
    value = C[page].get(key, "")
    paras = str(value).split("\n\n")
    inner = "</p><p>".join(p.replace("\n", "<br>") for p in paras)
    if len(paras) > 1 and tag not in ("span", "div", "h1", "h2", "h3", "h4"):
        pass
    class_attr = f' class="{cls}"' if cls else ""
    return f'<{tag}{class_attr} data-key="{page}.{key}"{extra}>{inner}</{tag}>'


def img_attr(page, key):
    return f'data-img-key="{page}.{key}"'


def img_src(page, key):
    return C[page].get(key, "")


def head(title, desc, slug):
    canonical = SITE_URL + "/" + (slug if slug != "index.html" else "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE_URL}/assets/img/hero-falls-rainbow.jpg">
<meta name="theme-color" content="#14192A">
<link rel="icon" href="assets/img/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sacramento&family=Jost:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
"""


def header(active_slug):
    links = ""
    for item in NAV:
        children = item.get("children")
        own_slug = item["href"].split("#")[0]
        child_slugs = [c[0].split("#")[0] for c in children] if children else []
        is_active = active_slug == own_slug or active_slug in child_slugs
        active = " active" if is_active else ""
        if children:
            sub = "".join(
                f'<a href="{href}">{label}</a>' for href, label in children
            )
            links += f"""<div class="nav-drop">
        <a href="{item['href']}" class="{active.strip()}">{item['label']}<span class="nav-caret">&#9662;</span></a>
        <div class="nav-drop-menu">{sub}</div>
      </div>\n"""
        else:
            links += f'<a href="{item["href"]}" class="{active.strip()}">{item["label"]}</a>\n'
    return f"""<header class="site-header">
  <div class="container">
    <a href="index.html" class="logo">
      <img src="assets/img/logo-white.png" alt="Signature Africa">
    </a>
    <nav class="nav-links">
      {links}
    </nav>
    <div class="nav-cta">
      <a href="#" class="btn btn-gold js-book-btn">Book Now</a>
    </div>
    <button class="nav-toggle" aria-label="Toggle menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</header>
"""


def footer():
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-col">
        <img src="assets/img/logo-white.png" alt="Signature Africa">
        <p data-key="global.footer_blurb">{esc(G['footer_blurb'])}</p>
      </div>
      <div class="footer-col">
        <h4>Explore</h4>
        <ul>
          <li><a href="victoria-falls.html">Victoria Falls, Zimbabwe</a></li>
          <li><a href="livingstone.html">Livingstone, Zambia</a></li>
          <li><a href="kasane.html">Kasane, Botswana</a></li>
          <li><a href="fleet.html">Our Fleet</a></li>
          <li><a href="aviation.html">Frontier Aviation</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Get In Touch</h4>
        <ul>
          <li><a href="tel:{G['phone_office_tel']}" data-key="global.phone_office">{esc(G['phone_office'])}</a></li>
          <li><a href="tel:{G['phone_cell_tel']}" data-key="global.phone_cell">{esc(G['phone_cell'])}</a></li>
          <li><a href="mailto:{G['email']}" data-key="global.email">{esc(G['email'])}</a></li>
          <li><a href="contact.html" data-key="global.address">{esc(G['address'])}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span id="year"></span> Signature Africa. All rights reserved.</span>
      <span>Crafted for unforgettable African journeys.</span>
    </div>
  </div>
</footer>
<a href="{WA_LINK}" class="wa-float" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">&#9742;</a>
<script src="assets/js/content.js"></script>
<script src="assets/js/main.js"></script>
<script src="https://identity.netlify.com/v1/netlify-identity-widget.js"></script>
<script>
  // Invite/reset-password emails link to the homepage with a token in the
  // URL hash. Bounce straight to the editor so the widget can pick it up
  // and show the "set your password" form.
  if (window.netlifyIdentity && /invite_token=|recovery_token=|confirmation_token=/.test(window.location.hash)) {{
    window.location.replace("/admin/" + window.location.hash);
  }}
</script>
</body>
</html>
"""


def page(title, desc, slug, content):
    return head(title, desc, slug) + header(slug) + content + footer()


def write(slug, html):
    path = os.path.join(OUT_DIR, slug)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", path)


# ---------------------------------------------------------------- INDEX ----
def page_index():
    p = "home"
    return f"""
<section class="hero" style="background-image:url('{img_src(p,'hero_image')}');">
  <div class="container">
    <span class="script" data-key="{p}.hero_script">{esc(C[p]['hero_script'])}</span>
    {txt(p,'hero_heading','h1')}
    {txt(p,'hero_text','p','lead')}
    <a href="#" class="btn btn-gold js-book-btn">Book Now</a>
  </div>
</section>

<section class="section" data-reveal>
  <div class="container">
    <div class="intro-split">
      <div>
        <span class="script" data-key="{p}.intro_script">{esc(C[p]['intro_script'])}</span>
        {txt(p,'intro_heading','h2')}
      </div>
      <div>
        {txt(p,'intro_text','p')}
        <a href="contact.html" class="btn btn-outline">Plan Your Journey</a>
      </div>
    </div>
  </div>
</section>

<section class="section--tight section--cream" data-reveal>
  <div class="container">
    <div class="offer-list offer-list--plain">
      <a href="victoria-falls.html" class="offer-row">
        <div class="offer-text"><h3>Victoria Falls, Zimbabwe</h3><p>Transfers, helicopter flights, adventure activities, Falls tours and Zambezi cruises.</p></div>
        <span class="offer-arrow">&rarr;</span>
      </a>
      <a href="livingstone.html" class="offer-row">
        <div class="offer-text"><h3>Livingstone, Zambia</h3><p>Devil's Pool, the Elephant Cafe, helicopter flights and cultural tours.</p></div>
        <span class="offer-arrow">&rarr;</span>
      </a>
      <a href="kasane.html" class="offer-row">
        <div class="offer-text"><h3>Kasane, Botswana</h3><p>Chobe National Park game drives and river safaris.</p></div>
        <span class="offer-arrow">&rarr;</span>
      </a>
      <a href="fleet.html" class="offer-row">
        <div class="offer-text"><h3>Our Fleet</h3><p>From a 4-seater Ineos Grenadier to a 28-seater coach.</p></div>
        <span class="offer-arrow">&rarr;</span>
      </a>
      <a href="aviation.html" class="offer-row">
        <div class="offer-text"><h3>Frontier Aviation</h3><p>Private Pilatus PC-12 charter flights across Southern Africa.</p></div>
        <span class="offer-arrow">&rarr;</span>
      </a>
    </div>
  </div>
</section>

<section class="split" data-reveal>
  <div class="split-media">
    <img src="{img_src(p,'feature1_image')}" {img_attr(p,'feature1_image')} alt="{esc(C[p]['feature1_heading'])}">
  </div>
  <div class="split-copy">
    <span class="script" data-key="{p}.feature1_script">{esc(C[p]['feature1_script'])}</span>
    {txt(p,'feature1_heading','h2')}
    {txt(p,'feature1_text','p')}
    <a href="{C[p]['feature1_link']}" class="btn btn-outline-light" data-key="{p}.feature1_link_label">{esc(C[p]['feature1_link_label'])}</a>
  </div>
</section>

<section class="split reverse light" data-reveal>
  <div class="split-media">
    <img src="{img_src(p,'feature2_image')}" {img_attr(p,'feature2_image')} alt="{esc(C[p]['feature2_heading'])}">
  </div>
  <div class="split-copy">
    <span class="script" data-key="{p}.feature2_script">{esc(C[p]['feature2_script'])}</span>
    {txt(p,'feature2_heading','h2')}
    {txt(p,'feature2_text','p')}
    <a href="{C[p]['feature2_link']}" class="btn btn-outline" data-key="{p}.feature2_link_label">{esc(C[p]['feature2_link_label'])}</a>
  </div>
</section>

<section class="cta-band" data-reveal>
  <div class="container">
    <span class="script" data-key="{p}.cta_script">{esc(C[p]['cta_script'])}</span>
    {txt(p,'cta_heading','h2')}
    {txt(p,'cta_text','p')}
    <a href="#" class="btn btn-gold js-book-btn">Book Now</a>
  </div>
</section>
"""


# ------------------------------------------------------- REGION HELPERS ----
def region_group(p, gkey, n_items, reverse=False):
    """Renders a split (image+intro) followed by a plain text offer-list for
    one sitemap group (e.g. 'g1' = Transfers & Airport Handling)."""
    light = " light" if reverse else ""
    rev = " reverse" if reverse else ""
    items_html = ""
    for n in range(1, n_items + 1):
        ik = f"{gkey}_i{n}"
        items_html += f"""
      <div class="offer-row">
        <div class="offer-text">
          <h3 data-key="{p}.{ik}_name">{esc(C[p][f'{ik}_name'])}</h3>
          <p data-key="{p}.{ik}_text">{esc(C[p][f'{ik}_text'])}</p>
        </div>
      </div>"""
    return f"""
<section class="split{rev}{light}" data-reveal>
  <div class="split-media">
    <img src="{img_src(p, f'{gkey}_image')}" {img_attr(p, f'{gkey}_image')} alt="{esc(C[p][f'{gkey}_heading'])}">
  </div>
  <div class="split-copy">
    <span class="script" data-key="{p}.{gkey}_script">{esc(C[p][f'{gkey}_script'])}</span>
    {txt(p, f'{gkey}_heading', 'h2')}
    {txt(p, f'{gkey}_text', 'p')}
  </div>
</section>
<section class="section--tight{' section--cream' if reverse else ''}" data-reveal>
  <div class="container">
    <div class="offer-list offer-list--plain offer-list--text">{items_html}
    </div>
  </div>
</section>"""


def region_hero_intro(p, breadcrumb):
    return f"""
<section class="hero hero--page" style="background-image:url('{img_src(p,'hero_image')}');">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / {breadcrumb}</div>
    {txt(p,'hero_heading','h1')}
    {txt(p,'hero_text','p','lead')}
  </div>
</section>

<section class="section" data-reveal>
  <div class="container">
    <div class="intro-split">
      <div>
        <span class="script" data-key="{p}.intro_script">{esc(C[p]['intro_script'])}</span>
        {txt(p,'intro_heading','h2')}
      </div>
      <div>
        {txt(p,'intro_text','p')}
      </div>
    </div>
  </div>
</section>"""


def region_cta(script, heading, text):
    return f"""
<section class="cta-band" data-reveal>
  <div class="container">
    <span class="script">{script}</span>
    <h2>{heading}</h2>
    <p>{text}</p>
    <a href="#" class="btn btn-gold js-book-btn">Book Now</a>
  </div>
</section>
"""


# --------------------------------------------------------- VICTORIA FALLS ----
def page_victoria_falls():
    p = "victoria_falls"
    blocks = (
        region_group(p, "g1", 5, reverse=False)
        + region_group(p, "g2", 3, reverse=True)
        + region_group(p, "g3", 4, reverse=False)
        + region_group(p, "g4", 2, reverse=True)
        + region_group(p, "g5", 3, reverse=False)
    )

    experiences = ""
    for idx, key in enumerate(["e1", "e2", "e3"]):
        light = " light" if idx % 2 == 1 else ""
        rev = " reverse" if idx % 2 == 1 else ""
        experiences += f"""
<section class="split{rev}{light}" data-reveal>
  <div class="split-media">
    <img src="{img_src(p, f'{key}_image')}" {img_attr(p, f'{key}_image')} alt="{esc(C[p][f'{key}_name'])}">
  </div>
  <div class="split-copy">
    {txt(p, f'{key}_name', 'h2')}
    {txt(p, f'{key}_text', 'p')}
    <a href="#" class="btn {"btn-outline" if idx % 2 == 1 else "btn-outline-light"} js-book-btn">Enquire</a>
  </div>
</section>"""

    return f"""{region_hero_intro(p, "Victoria Falls")}
{blocks}
<section class="section section--navy center" data-reveal>
  <div class="container">
    <span class="eyebrow">More To Explore</span>
    {txt(p,'g6_heading','h2')}
    {txt(p,'g6_text','p')}
  </div>
</section>
{experiences}
{region_cta("Plan Your Victoria Falls Itinerary", "Combine Transfers, Tours &amp; Adventure", "Tell us what you'd like to experience and we'll design the day around it.")}"""


# ----------------------------------------------------------- LIVINGSTONE ----
def page_livingstone():
    p = "livingstone"
    blocks = (
        region_group(p, "g1", 4, reverse=False)
        + region_group(p, "g2", 3, reverse=True)
        + region_group(p, "g3", 2, reverse=False)
        + region_group(p, "g4", 2, reverse=True)
        + region_group(p, "g5", 3, reverse=False)
    )
    return f"""{region_hero_intro(p, "Livingstone")}
{blocks}
{region_cta("Plan Your Livingstone Itinerary", "Cross The Border In Comfort", "Tell us your dates and we'll build your Zambia side itinerary.")}"""


# ---------------------------------------------------------------- KASANE ----
def page_kasane():
    p = "kasane"
    blocks = (
        region_group(p, "g1", 4, reverse=False)
        + region_group(p, "g2", 2, reverse=True)
        + region_group(p, "g3", 2, reverse=False)
    )
    return f"""{region_hero_intro(p, "Kasane")}
{blocks}
{region_cta("Plan Your Chobe Safari", "See Botswana's Elephant Capital", "Tell us your dates and we'll build your Kasane itinerary.")}"""


# ----------------------------------------------------------------FLEET ----
def page_fleet():
    p = "fleet"
    blocks = ""
    for i in range(1, 7):
        light = " light" if i % 2 == 0 else ""
        rev = " reverse" if i % 2 == 0 else ""
        blocks += f"""
<section class="split{rev}{light}" data-reveal>
  <div class="split-media">
    <img src="{img_src(p, f'v{i}_image')}" {img_attr(p, f'v{i}_image')} alt="{esc(C[p][f'v{i}_name'])}">
  </div>
  <div class="split-copy">
    <span class="script" data-key="{p}.v{i}_script">{esc(C[p][f'v{i}_script'])}</span>
    {txt(p, f'v{i}_name', 'h2')}
    <div class="meta-row"><span data-key="{p}.v{i}_tag">{esc(C[p][f'v{i}_tag'])}</span></div>
    {txt(p, f'v{i}_text', 'p')}
    <a href="#" class="btn {"btn-outline" if light else "btn-outline-light"} js-book-btn">Enquire About This Vehicle</a>
  </div>
</section>"""
    return f"""
<section class="hero hero--page" style="background-image:url('{img_src(p,'hero_image')}');">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Our Fleet</div>
    {txt(p,'hero_heading','h1')}
    {txt(p,'hero_text','p','lead')}
  </div>
</section>
{blocks}
<section class="cta-band" data-reveal>
  <div class="container">
    <span class="script">Not Sure Which Vehicle You Need?</span>
    <h2>Tell Us Your Group Size</h2>
    <p>We'll match you with the right vehicle, and driver-guide, for the journey ahead.</p>
    <a href="#" class="btn btn-gold js-book-btn">Book Now</a>
  </div>
</section>
"""


# ------------------------------------------------------------- AVIATION ----
def page_aviation():
    p = "aviation"
    specs = ""
    for label, key in [
        ("Base", "spec_base"), ("Year Of Manufacture", "spec_year"),
        ("Passengers", "spec_pax"), ("Crew", "spec_crew"),
        ("Typical Cruise Altitude", "spec_alt"), ("Typical Cruise Speed", "spec_speed"),
        ("Maximum Range", "spec_range"),
    ]:
        specs += f'<tr><td>{label}</td><td data-key="{p}.{key}">{esc(C[p][key])}</td></tr>\n'

    trips = ""
    for idx, i in enumerate((1, 2, 3)):
        light = " light" if idx % 2 == 1 else ""
        rev = " reverse" if idx % 2 == 1 else ""
        trips += f"""
<section class="split{rev}{light}" data-reveal>
  <div class="split-media">
    <img src="{img_src(p, f'd{i}_image')}" {img_attr(p, f'd{i}_image')} alt="{esc(C[p][f'd{i}_name'])}">
  </div>
  <div class="split-copy">
    {txt(p, f'd{i}_name', 'h2')}
    {txt(p, f'd{i}_text', 'p')}
    <a href="#" class="btn {"btn-outline" if idx % 2 == 1 else "btn-outline-light"} js-book-btn">Enquire About This Trip</a>
  </div>
</section>"""

    def simple_group(gkey, n_items, heading_tag="h2"):
        items_html = ""
        for n in range(1, n_items + 1):
            ik = f"{gkey}_i{n}"
            items_html += f"""
      <li><strong data-key="{p}.{ik}_name">{esc(C[p][f'{ik}_name'])}</strong><span data-key="{p}.{ik}_text">{esc(C[p][f'{ik}_text'])}</span></li>"""
        return f"""
    <span class="script" data-key="{p}.{gkey}_script">{esc(C[p][f'{gkey}_script'])}</span>
    {txt(p, f'{gkey}_heading', heading_tag)}
    <ul class="plain-list">{items_html}
    </ul>"""

    dest_rows = ""
    for key in ["dest_zw", "dest_bw", "dest_za", "dest_na", "dest_ke", "dest_zm", "dest_mw", "dest_mz"]:
        dest_rows += f'\n      <li data-key="{p}.{key}">{esc(C[p][key])}</li>'

    return f"""
<section class="hero hero--page" style="background-image:url('{img_src(p,'hero_image')}');">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Frontier Aviation</div>
    {txt(p,'hero_heading','h1')}
    {txt(p,'hero_text','p','lead')}
  </div>
</section>

<section class="split" data-reveal>
  <div class="split-media">
    <img src="{img_src(p,'intro_image')}" {img_attr(p,'intro_image')} alt="Pilatus PC-12 interior">
  </div>
  <div class="split-copy">
    <span class="script" data-key="{p}.intro_script">{esc(C[p]['intro_script'])}</span>
    {txt(p,'intro_heading','h2')}
    {txt(p,'intro_text','p')}
    <table class="specs">{specs}</table>
  </div>
</section>

<section class="split light" id="vip" data-reveal>
  <div class="split-media">
    <img src="{img_src(p,'hero_image')}" {img_attr(p,'hero_image')} alt="VIP airport services">
  </div>
  <div class="split-copy">{simple_group("vip", 3)}
  </div>
</section>

<section class="split reverse" id="charters" data-reveal>
  <div class="split-media">
    <img src="{img_src(p,'intro_image')}" {img_attr(p,'intro_image')} alt="Private charter flights">
  </div>
  <div class="split-copy">{simple_group("charter", 2)}
  </div>
</section>

<section class="section section--navy" id="destinations" data-reveal>
  <div class="container center">
    <span class="eyebrow" data-key="{p}.dest_script">{esc(C[p]['dest_script'])}</span>
    {txt(p,'dest_heading','h2')}
    {txt(p,'dest_text','p')}
    <ul class="plain-list" style="max-width:640px;margin:30px auto 0;text-align:left;">{dest_rows}
    </ul>
  </div>
</section>

<section class="section" data-reveal>
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Curated Day Trips</span>
      <h2>PC-12 Private Charter Day Trips</h2>
    </div>
  </div>
</section>
{trips}
<section class="cta-band" data-reveal>
  <div class="container">
    <span class="script">Charter A Flight</span>
    <h2>Take To The Sky With Frontier Aviation</h2>
    <p>Share your dates and destination and we'll put together your private charter.</p>
    <a href="#" class="btn btn-gold js-book-btn">Book Now</a>
  </div>
</section>
"""


# --------------------------------------------------------------- CONTACT ----
def page_contact():
    p = "contact"
    return f"""
<section class="hero hero--page" style="background-image:url('{img_src(p,'hero_image')}');min-height:46vh;">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Contact</div>
    {txt(p,'hero_heading','h1')}
    {txt(p,'hero_text','p','lead')}
  </div>
</section>

<section class="contact-grid" data-reveal>
  <div class="contact-info">
    <h2>Contact Details</h2>
    <div class="contact-row">
      <span class="label">Office</span>
      <a href="tel:{G['phone_office_tel']}" data-key="global.phone_office">{esc(G['phone_office'])}</a>
    </div>
    <div class="contact-row">
      <span class="label">Cell / WhatsApp</span>
      <a href="tel:{G['phone_cell_tel']}" data-key="global.phone_cell">{esc(G['phone_cell'])}</a>
    </div>
    <div class="contact-row">
      <span class="label">Email</span>
      <a href="mailto:{G['email']}" data-key="global.email">{esc(G['email'])}</a>
    </div>
    <div class="contact-row">
      <span class="label">Location</span>
      <div class="value" data-key="global.address">{esc(G['address'])}</div>
    </div>
    <div class="contact-row" style="border-top:none;padding-top:34px;">
      <a href="#" class="btn btn-gold js-book-btn">Book Now</a>
      &nbsp; &nbsp;
      <a href="{WA_LINK}" target="_blank" rel="noopener" class="btn btn-whatsapp">WhatsApp Us</a>
    </div>
  </div>
  <iframe class="map-frame" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
    src="https://maps.google.com/maps?q=Victoria%20Falls%2C%20Zimbabwe&t=&z=12&ie=UTF8&iwloc=&output=embed"
    title="Signature Africa location map">
  </iframe>
</section>

<section class="section section--cream center" data-reveal>
  <div class="container">
    <span class="eyebrow">Prefer To Browse First?</span>
    <h2 style="margin-bottom:34px;">Explore What Signature Africa Offers</h2>
    <a href="victoria-falls.html" class="btn btn-outline" style="margin:6px;">Victoria Falls</a>
    <a href="livingstone.html" class="btn btn-outline" style="margin:6px;">Livingstone</a>
    <a href="kasane.html" class="btn btn-outline" style="margin:6px;">Kasane</a>
    <a href="fleet.html" class="btn btn-outline" style="margin:6px;">Our Fleet</a>
    <a href="aviation.html" class="btn btn-outline" style="margin:6px;">Frontier Aviation</a>
  </div>
</section>
"""


write("index.html", page(
    "Signature Africa | Luxury Transfers & Tailored Tours in Victoria Falls",
    "Premium ground handling, luxury transfers, tailored tours and private air charters across Victoria Falls, Hwange, Kasane and Livingstone.",
    "index.html", page_index()))

write("victoria-falls.html", page(
    "Victoria Falls, Zimbabwe | Signature Africa",
    "VIP transfers, helicopter flights, adrenaline activities, guided Falls tours and Zambezi cruises in Victoria Falls, Zimbabwe.",
    "victoria-falls.html", page_victoria_falls()))

write("livingstone.html", page(
    "Livingstone, Zambia | Signature Africa",
    "VIP transfers, Devil's Pool, the Elephant Cafe, helicopter flights and cultural tours in Livingstone, Zambia.",
    "livingstone.html", page_livingstone()))

write("kasane.html", page(
    "Kasane, Botswana | Signature Africa",
    "VIP transfers and Chobe National Park game drives and river safaris in Kasane, Botswana.",
    "kasane.html", page_kasane()))

write("fleet.html", page(
    "Our Fleet | Signature Africa",
    "A luxury fleet built for every party size, Ineos Grenadier, Toyota Majesty, Quantum, Hiace, Hino Coaster and our King Long coach.",
    "fleet.html", page_fleet()))

write("aviation.html", page(
    "Frontier Aviation | PC-12 Private Charters | Signature Africa",
    "Private Pilatus PC-12 charter flights and curated day trips to Hwange, Matopos and Great Zimbabwe.",
    "aviation.html", page_aviation()))

write("contact.html", page(
    "Contact Us | Signature Africa",
    "Get in touch with Signature Africa in Victoria Falls, Zimbabwe, office, WhatsApp and email details.",
    "contact.html", page_contact()))

print("Build complete.")
