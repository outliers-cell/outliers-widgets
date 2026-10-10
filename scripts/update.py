# test
#!/usr/bin/env python3
"""
Fayetteville Outliers - Daily Widget Generator (v3)
Reads each team's MaxPreps /schedule/ page (a clean server-rendered table,
one team per page - no mixed feed), then writes STATIC HTML widgets.
* Season is chosen automatically from today's date (MaxPreps school-year
  naming: fall 2026, winter 2026-27 and spring 2027 are all "26-27"; the
  school year rolls over July 1). No yearly editing needed.
* The page title must contain the expected season token or it is ignored.
* Scores are shown Outliers-first. MaxPreps lists the winner's score first.
* If a scrape fails: last good copy (schedule_cache_v2.json), then the
  built-in seed schedule. One bad team never breaks the others.
"""
import json, os, re, sys, traceback
from datetime import date, datetime
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.dirname(SCRIPTS_DIR)
CACHE_FILE  = os.path.join(ROOT_DIR, "schedule_cache_v2.json")
BASE        = "https://www.maxpreps.com/nc/fayetteville/fayetteville-outliers-outliers"
def _load_assets():
    """Logo + badge images live in scripts/assets_src.py (the previous update.py)."""
    src = open(os.path.join(SCRIPTS_DIR, "assets_src.py"), encoding="utf-8").read()
    return [re.search(r"^" + n + r"\s*=\s*[\"']([^\"']+)[\"']", src, re.M).group(1)
            for n in ("_LOGO", "_BB", "_VB", "_BSB")]
VB_ABBR = {"BCA":"Brookside Christian Academy","CCA":"Christ the Cornerstone Academy",
           "RCA":"Riverside Christian Academy","ECA":"ECA","SW":"South Wake"}
BK_ABBR = {"CCA":"Cornerstone Christian Academy","RCA":"Riverside Christian Academy",
           "TCEA":"The Capitol Encore Academy","BCA":"Brookside Christian Academy"}
# Seed rows ("m/d|time|@or vs|opponent|result as MaxPreps lists it") are the
# last-resort fallback only (scrape failed AND no cache). Verified 2026-10-10.
SEED_JV_VB = """8/18|5:30pm|@|Northwood Temple Academy|L 2-0
8/27|4:30pm|@|BCA|W 3-1
8/28|5:30pm|@|JV Opponent|W 2-0
8/31|5:30pm|@|Liberty Christian Academy|L 2-0
9/1|6:00pm|@|Non JV Opponent|L 3-0
9/3|4:00pm|@|CCA|L 2-0
9/8|7:00pm|@|RCA|L 3-0
9/11|5:00pm|@|JV Opponent|L 2-0
9/14|5:30pm|vs|Alpha Academy|L 3-0
9/15|4:00pm|vs|Father Capodanno|L 3-1
9/17|5:00pm|vs|BCA|W 3-0
9/22|5:00pm|vs|RCA|L 2-0
9/29|5:30pm|vs|Non JV Opponent|W 3-1
10/1|4:30pm|vs|Non JV Opponent|L 3-1
10/6|4:00pm|vs|CCA|L 2-0
10/8|6:00pm|vs|Non JV Opponent|L 3-0
10/13|4:00pm|@|CCA|"""
SEED_MS_VB = """8/18|4:00pm|@|Northwood Temple Academy|L 2-0
8/25|4:00pm|@|Non Freshman Opponent|L 2-0
8/28|4:30pm|@|Non Freshman Opponent|W 2-1
8/31|4:00pm|@|Liberty Christian Academy|L 2-0
9/1|5:00pm|@|Non Freshman Opponent|L 2-0
9/8|6:30pm|@|RCA|L 2-0
9/9|4:00pm|@|Non Freshman Opponent|L 2-0
9/10|4:00pm|@|Non Freshman Opponent|L 2-0
9/11|4:00pm|@|Non Freshman Opponent|L 2-0
9/14|4:30pm|vs|Alpha Academy|L 2-0
9/21|4:00pm|vs|Non Freshman Opponent|L 2-0
9/22|4:00pm|vs|RCA|L 2-0
9/24|4:00pm|vs|Non Freshman Opponent|L 2-1
9/28|4:00pm|vs|Non Freshman Opponent|L 2-0
9/29|4:30pm|vs|Non Freshman Opponent|L 2-0
10/8|5:00pm|vs|Non Freshman Opponent|L 2-0
10/16|4:00pm|vs|Northwood Temple Academy|"""
SEED_V_VB = """9/14|5:30pm|vs|Alpha Academy|L 3-0
9/22|5:00pm|vs|RCA|W 3-2"""
SEED_V_BK = """11/7|1:15pm|vs|Durham Flight HomeSchool***|
11/13|7:45pm|vs|Lee Christian***|
11/14|7:45pm|vs|Father Capodanno***|
12/1|7:15pm|@|Covenant Crusaders*|
12/4|5:30pm|@|Father Capodanno*|
12/21|TBA|vs|TBA*** (Christmas tournament )|
12/22|TBA|vs|TBA*** (Christmas Tournament )|
12/23|TBA|vs|TBA*** (Christmas tournament )|
1/4|6:45pm|vs|Covenant Crusaders*|
3/1|TBA|vs|TBA*** (2027 Gatlinburg Homeschool Classic National Champi)|
3/2|TBA|vs|TBA*** (2027 Gatlinburg Homeschool Classic National Champi)|
3/3|TBA|vs|TBA*** (2027 Gatlinburg Homeschool Classic National Champi)|
3/4|TBA|vs|TBA*** (2027 Gatlinburg Homeschool Classic National Champi)|
3/5|TBA|vs|TBA*** (2027 Gatlinburg Homeschool Classic National Champi)|"""
def _t(id_, sport, level, icon, kind, path, abbr, seed="", note="", **kw):
    d = {"id":id_, "sport":sport, "level":level, "icon":icon, "kind":kind,
         "path":path, "abbr":abbr, "seed":seed, "note":note}
    d.update(kw); return d
TEAMS = [
    _t("volleyball-girls-varsity","Girls Volleyball","Varsity Girls","volleyball","fall","/volleyball/",VB_ABBR,SEED_V_VB),
    _t("volleyball-girls-jv","Girls Volleyball","JV Girls","volleyball","fall","/volleyball/jv/",VB_ABBR,SEED_JV_VB),
    _t("volleyball-girls-ms","Girls Volleyball","Middle School Girls","volleyball","fall","/volleyball/freshman/",VB_ABBR,SEED_MS_VB,
       note="Results are on MaxPreps under the Freshman tab."),
    _t("basketball-varsity-boys","Basketball","Varsity Boys","basketball","winter","/basketball/",BK_ABBR,SEED_V_BK),
    _t("basketball-jv-boys","Basketball","JV Boys","basketball","winter","/basketball/jv/",BK_ABBR),
    _t("basketball-ms-boys","Basketball","Middle School Boys","basketball","winter","/basketball/freshman/",BK_ABBR,
       note="Results are on MaxPreps under the Freshman tab."),
    {"id":"baseball-ms","sport":"Baseball","level":"Middle School Boys","icon":"baseball","live_gc":True,
     "gc_url":"https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb",
     "gc_widget_id":"9b48626c-98b5-400b-9f19-467268938605",
     "note":"Inaugural 2026 season - NCHEAC league, reached the state tournament in Pittsboro."},
    _t("baseball-hs","Baseball","High School Boys","baseball","spring","/baseball/",{},
       note="First HS season planned for Spring 2027."),
    _t("volleyball-boys-varsity","Boys Volleyball","Varsity Boys","volleyball","spring","/volleyball/boys/",VB_ABBR,
       note="Season begins March 2027. Last season: 11-2, finished #35 in NC."),
]
for _t_ in TEAMS:
    if "path" in _t_:
        _t_["mp_url"]    = BASE + _t_["path"]
        _t_["sched_url"] = BASE + _t_["path"] + "schedule/"
WIDGET_SPECS = [
    {"file":"widget-basketball.html","title":"Basketball &mdash; Schedules &amp; Records",
     "ids":["basketball-varsity-boys","basketball-jv-boys","basketball-ms-boys"],
     "footer":'Schedules from <a href="' + BASE + '/basketball/">MaxPreps</a> (MS under Freshman tab). Auto-updated daily.'},
    {"file":"widget-girls-volleyball.html","title":"Girls Volleyball &mdash; Schedules &amp; Records",
     "ids":["volleyball-girls-varsity","volleyball-girls-jv","volleyball-girls-ms"],
     "footer":'Schedules from <a href="' + BASE + '/volleyball/">MaxPreps</a> (MS under Freshman tab). Auto-updated daily.'},
    {"file":"widget-boys-volleyball.html","title":"Boys Volleyball &mdash; Schedules &amp; Records",
     "ids":["volleyball-boys-varsity"],
     "footer":'Schedule from <a href="' + BASE + '/volleyball/boys/">MaxPreps</a>. Auto-updated daily.'},
    {"file":"widget-baseball.html","title":"Baseball &mdash; Schedules &amp; Records",
     "ids":["baseball-ms","baseball-hs"],
     "footer":'MS Baseball live from <a href="https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb">GameChanger</a>. HS begins Spring 2027.'},
    {"file":"widget-all-sports.html","title":"All Sports &mdash; Schedules &amp; Records",
     "ids":["volleyball-girls-varsity","volleyball-girls-jv","volleyball-girls-ms",
            "basketball-varsity-boys","basketball-jv-boys","basketball-ms-boys",
            "baseball-ms","baseball-hs","volleyball-boys-varsity"],
     "footer":'Basketball &amp; Volleyball: <a href="' + BASE + '/">MaxPreps</a> &mdash; MS Baseball: <a href="https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb">GameChanger</a>. Auto-updated daily.'},
]
_ids = {t["id"] for t in TEAMS}
for _s in WIDGET_SPECS:
    for _i in _s["ids"]:
        if _i not in _ids: raise SystemExit("CONFIG ERROR: unknown team id " + _i)
def season_for(kind, today=None):
    """MaxPreps school-year season. Rolls over July 1."""
    today = today or date.today()
    Y = today.year if today.month >= 7 else today.year - 1
    token = "%02d-%02d" % (Y % 100, (Y + 1) % 100)
    if kind == "fall":
        return {"label":str(Y), "token":token, "start":"%d-08-01"%Y, "end":"%d-11-30"%Y, "year0":Y, "wrap":False}
    if kind == "winter":
        return {"label":"%d-%02d"%(Y,(Y+1)%100), "token":token, "start":"%d-11-01"%Y, "end":"%d-03-31"%(Y+1), "year0":Y, "wrap":True}
    return {"label":str(Y+1), "token":token, "start":"%d-03-01"%(Y+1), "end":"%d-06-15"%(Y+1), "year0":Y+1, "wrap":False}
def row_date(mo, dy, season):
    if season["wrap"]:
        yr = season["year0"] if mo >= 7 else season["year0"] + 1
    else:
        yr = season["year0"]
    return "%04d-%02d-%02d" % (yr, mo, dy)
def clean_opp(raw, abbr):
    s = re.sub(r"\s+", " ", raw).strip()
    # tournament / TBA placeholders:  "TBA*** (Christmas tournament )"
    if re.match(r"^TBA\b", s, re.I):
        m = re.search(r"\(([^)]*)\)", s)
        name = m.group(1).strip().title() if m else ""
        return name if name else "Tournament TBA"
    s = re.sub(r"\s*\*+\s*$", "", s).strip()
    if re.match(r"^(non\s+)?(jv|freshman|varsity|jv/varsity)?\s*opponent\b", s, re.I):
        return "Opponent TBA"
    return abbr.get(s, s) or "Opponent TBA"
def norm_time(t):
    m = re.search(r"(\d{1,2}:\d{2})\s*([ap])m", t or "", re.I)
    return (m.group(1) + m.group(2).upper() + "M") if m else None
def norm_result(res, score):
    """MaxPreps lists the winner's score first; return (res, own-first score)."""
    a, b = [int(x) for x in score.split("-")]
    hi, lo = max(a, b), min(a, b)
    if res == "W": return "W", "%d-%d" % (hi, lo)
    if res == "L": return "L", "%d-%d" % (lo, hi)
    return "T", "%d-%d" % (a, b)
def make_game(md, time_txt, ha_tok, opp_raw, res_txt, season, abbr):
    m = re.match(r"(\d{1,2})/(\d{1,2})", md.strip())
    if not m: return None
    mo, dy = int(m.group(1)), int(m.group(2))
    g = {"date":row_date(mo, dy, season),
         "time":norm_time(time_txt),
         "ha":"away" if ha_tok.strip() == "@" else "home",
         "opp":clean_opp(opp_raw, abbr), "res":None, "score":None}
    r = re.match(r"^([WLT])\s*(\d+)\s*[-–]\s*(\d+)", (res_txt or "").strip())
    if r:
        g["res"], g["score"] = norm_result(r.group(1), r.group(2) + "-" + r.group(3))
    return g
def parse_seed(text, season, abbr):
    out = []
    for line in text.strip().splitlines():
        p = line.split("|")
        if len(p) < 5: continue
        g = make_game(p[0], p[1], p[2], p[3], p[4], season, abbr)
        if g: out.append(g)
    return sorted(out, key=lambda g: g["date"])
def parse_schedule_html(html, season, abbr):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    games = []
    for tr in soup.select("table tr"):
        tds = tr.find_all("td")
        if len(tds) < 2: continue
        sp0 = [s.get_text(" ", strip=True) for s in tds[0].find_all("span")]
        if not sp0: sp0 = tds[0].get_text("|", strip=True).split("|")
        md = sp0[0]
        tm = sp0[1] if len(sp0) > 1 else ""
        pieces = [s.get_text(" ", strip=True) for s in tds[1].find_all("span")]
        if not pieces:
            pieces = tds[1].get_text("|", strip=True).split("|")
        pieces = [x for x in pieces if x]
        if not pieces: continue
        ha_tok = pieces[0] if pieces[0] in ("@", "vs", "N") else "vs"
        rest = pieces[1:] if pieces[0] in ("@", "vs", "N") else pieces
        # drop the one-letter badge that repeats the opponent's first letter
        if len(rest) > 1 and len(rest[0]) == 1 and rest[1][:1].upper() == rest[0].upper():
            rest = rest[1:]
        opp = " ".join(rest)
        # MaxPreps glues badge letter into text in some layouts ("N Non JV Opponent")
        opp = re.sub(r"^([A-Za-z]) (?=\1)", "", opp, flags=re.I)
        res_txt = tds[2].get_text(" ", strip=True) if len(tds) > 2 else ""
        g = make_game(md, tm, ha_tok, opp, res_txt, season, abbr)
        if g: games.append(g)
    games.sort(key=lambda g: g["date"])
    return games
def fetch_page(url):
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            br = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            ctx = br.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800})
            pg = ctx.new_page()
            pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            try: pg.wait_for_selector("table", timeout=15000)
            except Exception: pass
            pg.wait_for_timeout(1500)
            html = pg.content()
            br.close()
            return html
    except Exception as e:
        print(" fetch error: " + str(e)[:120])
        return None
def looks_blocked(html):
    low = html[:3000].lower()
    return any(m in low for m in ("just a moment", "attention required", "captcha", "access denied"))
def scrape(team, season):
    print("  fetching " + team["sched_url"] + " ...", end="", flush=True)
    html = fetch_page(team["sched_url"])
    if not html: print(" FAILED"); return None
    if looks_blocked(html): print(" BLOCKED"); return None
    m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
    title = m.group(1) if m else ""
    if season["token"] not in title:
        print(" season mismatch (title '" + title[-30:].strip() + "', want " + season["token"] + ") - ignoring")
        return None
    games = parse_schedule_html(html, season, team["abbr"])
    print(" parsed " + str(len(games)) + " games")
    return games or None
CSS = """<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#F4F6F9;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1a0a0d;}
.widget{border:1px solid #DDE2E8;border-radius:14px;overflow:hidden;background:#F4F6F9;}
.hdr{background:#000;color:#fff;padding:16px 20px;position:relative;display:flex;align-items:center;gap:14px;flex-wrap:wrap;}
.hdr::after{content:'';position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,#0bc8ee,#bdf1fb 60%,transparent);}
.hdr img{height:42px;width:auto;}
.hdr-title{flex:1;}
.hdr h1{font-family:'Forte','Comic Sans MS',cursive;font-size:16px;color:#0bc8ee;font-weight:normal;letter-spacing:.02em;}
.hdr .upd{font-size:11px;opacity:.6;margin-top:2px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;padding:14px 18px 18px;}
.card{background:#fff;border:1px solid #DDE2E8;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:9px;}
.card.err{border-color:#F5C9D1;background:#FDEDEF;}
.card-head{display:flex;align-items:flex-start;gap:10px;}
.badge{width:48px;height:48px;flex:none;background:#000;border-radius:9px;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.badge img{width:88%;height:88%;object-fit:contain;}
.card-titles{flex:1;}
.sport{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:#7c021e;font-weight:700;margin-bottom:1px;}
.level{font-size:14px;font-weight:700;color:#1a0a0d;}
.yr{font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;color:#93909a;font-family:monospace;margin-top:2px;}
.status{font-size:10px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap;flex:none;background:#F4F6F9;color:#93909a;border:1px solid #DDE2E8;}
.status.final{background:#FDEDEF;color:#7c021e;border-color:#F5C9D1;}
.status.pre{background:#E6F9FD;color:#047a93;border-color:#BDEEF8;}
.status.live{background:#E8F8EE;color:#1a7a40;border-color:#B8EAC9;}
.rec{font-size:26px;font-weight:800;color:#4a0112;font-family:monospace;line-height:1;}
.pct{font-size:11px;color:#93909a;font-family:monospace;margin-top:1px;}
.note{font-size:12.5px;color:#93909a;font-style:italic;line-height:1.4;background:#F4F6F9;border-radius:8px;padding:7px 9px;}
.nxt{font-size:12.5px;background:#F4F6F9;border-radius:8px;padding:7px 9px;line-height:1.4;}
.nxt strong{color:#4a0112;}
details{border-top:1px solid #DDE2E8;padding-top:8px;margin-top:2px;}
summary{font-size:12.5px;font-weight:600;color:#7c021e;cursor:pointer;list-style:none;padding:2px 0;}
summary::-webkit-details-marker{display:none;}
summary::before{content:'\\25B8 ';}
details[open] summary::before{content:'\\25BE ';}
.glist{margin-top:8px;display:flex;flex-direction:column;gap:5px;max-height:220px;overflow-y:auto;}
.grow{display:flex;justify-content:space-between;gap:6px;font-size:12px;padding:3px 2px;border-bottom:1px dashed #DDE2E8;}
.gdate{color:#93909a;flex:none;width:62px;font-family:monospace;}
.gopp{flex:1;}
.gres{font-family:monospace;font-weight:700;flex:none;}
.gres.w{color:#1f8a4c;}.gres.l{color:#b3273e;}
.mplink{margin-top:auto;font-size:12px;font-weight:600;color:#7c021e;text-decoration:none;border-top:1px solid #DDE2E8;padding-top:8px;display:block;}
.mplink:hover{color:#0bc8ee;}
.footer{font-size:11px;color:#93909a;text-align:center;padding:4px 18px 16px;line-height:1.6;}
.footer a{color:#7c021e;text-decoration:none;font-weight:600;}
.live-box{background:#E8F8EE;border:1px solid #B8EAC9;border-radius:8px;padding:10px;font-size:12.5px;color:#1a7a40;text-align:center;}
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">"""
def fmt(iso):
    try:
        return date.fromisoformat(iso).strftime('%a %b %-d')
    except Exception:
        return iso
def make_card_inner(team, games, season, LOGO, BB, VB, BSB):
    badge_b64 = {'basketball': BB, 'volleyball': VB, 'baseball': BSB}[team['icon']]
    if team.get('live_gc'):
        h = '<div class="card"><div class="card-head">'
        h += '<div class="badge"><img src="data:image/png;base64,' + badge_b64 + '" alt="' + team['sport'] + '"></div>'
        h += '<div class="card-titles"><div class="sport">' + team['sport'] + '</div>'
        h += '<div class="level">' + team['level'] + '</div><div class="yr">2026</div></div>'
        h += '<span class="status live">Live</span></div>'
        h += '<div class="note">' + team.get('note', '') + '</div>'
        h += '<div class="live-box" id="gc-' + team['id'] + '">&#9654; Live schedule &amp; scores loading from GameChanger...</div>'
        h += '<a class="mplink" href="' + team['gc_url'] + '" target="_blank" rel="noopener">View on GameChanger &rarr;</a></div>'
        return h
    today = date.today().isoformat()
    played = sorted([g for g in games if g.get('res') in ('W', 'L', 'T')], key=lambda g: g['date'])
    upcoming = sorted([g for g in games if g.get('res') not in ('W', 'L', 'T')], key=lambda g: g['date'])
    if played:
        w = sum(1 for g in played if g['res'] == 'W')
        l = sum(1 for g in played if g['res'] == 'L')
        t = sum(1 for g in played if g['res'] == 'T')
        tot = w + l + t
        pct = round(((w + 0.5 * t) / tot) * 100)
        rec_html = ('<div class="rec">' + str(w) + '&ndash;' + str(l) + (('&ndash;' + str(t)) if t else '')
                    + '</div><div class="pct">' + str(pct) + '% win rate</div>')
        status_cls, status_txt = ('pre', 'In Season') if (upcoming or today <= season['end']) else ('final', 'Final')
    else:
        rec_html = '<div class="rec" style="color:#93909a">&mdash;</div>'
        status_cls = 'pre'
        status_txt = 'Upcoming' if (upcoming or today < season['start']) else 'Pre-Season'
    mid = ''
    if upcoming:
        n = upcoming[0]
        ha = 'vs' if n['ha'] == 'home' else '@'
        tm = (' &middot; ' + n['time']) if n.get('time') else ''
        mid = '<div class="nxt">Next: <strong>' + fmt(n['date']) + '</strong> ' + ha + ' ' + n['opp'] + tm + '</div>'
    elif played:
        last = played[-1]
        ha = 'vs' if last['ha'] == 'home' else '@'
        mid = ('<div class="nxt">Last: <strong>' + last['res'] + ' ' + (last.get('score') or '') + '</strong> '
               + ha + ' ' + last['opp'] + ' (' + fmt(last['date']) + ')</div>')
    elif team.get('note'):
        mid = '<div class="note">' + team['note'] + '</div>'
    else:
        mid = '<div class="note">Schedule will appear here once it is posted on MaxPreps.</div>'
    list_html = ''
    if games:
        rows = ''
        for g in sorted(games, key=lambda g: g['date']):
            ha = 'vs' if g['ha'] == 'home' else '@'
            if g.get('res'):
                rh = '<span class="gres ' + g['res'].lower() + '">' + g['res'] + ' ' + (g.get('score') or '') + '</span>'
            else:
                rh = '<span class="gres">' + (g.get('time') or 'TBA') + '</span>'
            rows += ('<div class="grow"><span class="gdate">' + fmt(g['date']) + '</span><span class="gopp">'
                     + ha + ' ' + g['opp'] + '</span>' + rh + '</div>')
        list_html = ('<details><summary>Schedule &amp; results (' + str(len(games))
                     + ')</summary><div class="glist">' + rows + '</div></details>')
    out = '<div class="card"><div class="card-head">'
    out += '<div class="badge"><img src="data:image/png;base64,' + badge_b64 + '" alt="' + team['sport'] + '"></div>'
    out += '<div class="card-titles"><div class="sport">' + team['sport'] + '</div>'
    out += '<div class="level">' + team['level'] + '</div><div class="yr">' + season['label'] + '</div></div>'
    out += '<span class="status ' + status_cls + '">' + status_txt + '</span></div>'
    out += rec_html + mid + list_html
    out += '<a class="mplink" href="' + team['mp_url'] + '" target="_blank" rel="noopener">View on MaxPreps &rarr;</a></div>'
    return out
def make_card(team, games, season, LOGO, BB, VB, BSB):
    try:
        return make_card_inner(team, games, season, LOGO, BB, VB, BSB)
    except Exception as e:
        tb = traceback.format_exc(limit=3)
        print("  CARD ERROR for " + str(team.get('id', '?')) + ": " + str(e))
        print(tb)
        safe_name = team.get('level', team.get('id', 'Unknown team'))
        out = '<div class="card err"><div class="card-titles">'
        out += '<div class="sport">Error</div><div class="level">' + str(safe_name) + '</div></div>'
        out += '<div class="note">This card could not be built (' + str(e)[:100] + '). Other teams are unaffected.</div></div>'
        return out
def make_page(spec, cards, team_map, run_time, LOGO):
    has_gc = any(team_map[tid].get('live_gc') for tid in spec['ids'] if tid in team_map)
    gc_block = ''
    if has_gc:
        gc_t = next((team_map[tid] for tid in spec['ids'] if team_map.get(tid, {}).get('live_gc')), None)
        if gc_t:
            gc_block = "\n<script src=\"https://widgets.gc.com/static/js/sdk.v1.js\"></script>\n<script>\n"
            gc_block += "(function(){\n  var GC_ID=\"" + gc_t["gc_widget_id"] + "\";\n"
            gc_block += "  if(window.GC&&window.GC.team&&window.GC.team.schedule){\n"
            gc_block += "    window.GC.team.schedule.init({target:\"#gc-" + gc_t["id"] + "\",widgetId:GC_ID,maxVerticalGamesVisible:4});\n"
            gc_block += "  }\n})();\n</script>"
    html = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
    html += '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    html += '<title>Outliers Athletics</title>\n' + CSS + '\n</head>\n<body>\n'
    html += '<div class="widget">\n<div class="hdr">\n  <img src="data:image/png;base64,' + LOGO + '" alt="Outliers Athletics">\n'
    html += '  <div class="hdr-title">\n    <h1>' + spec["title"] + '</h1>\n'
    html += '    <div class="upd">fayhomeschoolsports.org &mdash; Updated ' + run_time + '</div>\n  </div>\n</div>\n'
    html += '<div class="grid">' + cards + '</div>\n<div class="footer">' + spec["footer"] + '</div>\n</div>\n'
    html += gc_block + '\n</body>\n</html>'
    return html
def resolve(team, season, cache):
    """scrape -> cache (same season) -> seed. Returns (games, source)."""
    games = None
    try:
        games = scrape(team, season)
    except Exception as e:
        print("  SCRAPE EXCEPTION: " + str(e)[:150]); traceback.print_exc(limit=2)
    if games:
        return games, "live"
    c = cache.get(team["id"])
    if c and c.get("label") == season["label"] and c.get("games"):
        print("  using cache from " + str(c.get("date")))
        return c["games"], "cache"
    if team.get("seed"):
        print("  using built-in seed schedule")
        return parse_seed(team["seed"], season, team["abbr"]), "seed"
    print("  nothing available - card shows upcoming/no-schedule state")
    return [], "none"
def main():
    now = datetime.utcnow()
    run_time = now.strftime('%b %-d, %Y')
    print("Outliers widget build - " + str(date.today()) + " " + now.strftime('%H:%M') + " UTC")
    LOGO, BB, VB, BSB = _load_assets()
    cache = {}
    if os.path.exists(CACHE_FILE):
        try: cache = json.load(open(CACHE_FILE))
        except Exception: cache = {}
    team_map = {t['id']: t for t in TEAMS}
    data = {}
    new_cache = dict(cache)
    for team in TEAMS:
        print("\n" + team['sport'] + " - " + team['level'])
        if team.get('live_gc'):
            data[team['id']] = ([], season_for('spring')); continue
        season = season_for(team['kind'])
        games, src = resolve(team, season, cache)
        data[team['id']] = (games, season)
        if src == "live":
            new_cache[team['id']] = {"label": season["label"], "date": str(date.today()), "games": games}
    with open(CACHE_FILE, 'w') as f:
        json.dump(new_cache, f, indent=1)
    print("\nWriting widgets...")
    for spec in WIDGET_SPECS:
        cards = ''
        for tid in spec['ids']:
            games, season = data[tid]
            cards += make_card(team_map[tid], games, season, LOGO, BB, VB, BSB)
        html = make_page(spec, cards, team_map, run_time, LOGO)
        with open(os.path.join(ROOT_DIR, spec['file']), 'w', encoding='utf-8') as f:
            f.write(html)
        print("  wrote " + spec['file'] + " (" + str(html.count('<div class="card')) + " cards)")
    with open(os.path.join(ROOT_DIR, 'last_run.txt'), 'w') as f:
        f.write("Last run: " + str(date.today()) + " at " + now.strftime('%H:%M') + " UTC\n")
    rows = ''.join('<li><a href="' + s['file'] + '">' + s['title'].replace('&mdash;', '-').replace('&amp;', '&') + '</a></li>' for s in WIDGET_SPECS)
    with open(os.path.join(ROOT_DIR, 'index.html'), 'w') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Outliers Widgets</title>"
                "<style>body{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}"
                "a{color:#7c021e;font-weight:bold}li{margin:12px 0}</style></head>"
                "<body><h1>Outliers Athletics Widget Directory</h1>"
                "<p>Embed these URLs in Google Sites via <strong>Insert &rarr; Embed &rarr; By URL</strong></p>"
                "<ul>" + rows + "</ul><p style='color:#999;font-size:13px'>Script last ran: "
                + str(date.today()) + " " + now.strftime('%H:%M') + " UTC</p></body></html>")
    print("Done.")
if __name__ == '__main__':
    main()
