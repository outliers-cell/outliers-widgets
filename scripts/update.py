#!/usr/bin/env python3
"""
Fayetteville Outliers — Daily Widget Generator
Generates STATIC HTML widget files (no JavaScript required to display cards).
Cards are hardcoded in HTML so they show immediately in any browser or iframe.
Runs automatically every morning via GitHub Actions.
"""

import json, os, re, sys
from datetime import date, datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.dirname(SCRIPTS_DIR)
CACHE_FILE  = os.path.join(ROOT_DIR, "last_data.json")
BASE        = "https://www.maxpreps.com/nc/fayetteville/fayetteville-outliers-outliers"

# ── Brand assets (base64-encoded images) ──────────────────────────────────
def load(name):
    return open(os.path.join(SCRIPTS_DIR, name)).read().strip()

# ── Team definitions ───────────────────────────────────────────────────────
TEAMS = [
    {"id":"volleyball-girls-varsity","sport":"Girls Volleyball","level":"Varsity Girls",
     "icon":"volleyball","url":BASE+"/volleyball/schedule/","mp_url":BASE+"/volleyball/",
     "year":"2026","season_start":"2026-08-01","season_end":"2026-11-15",
     "note":"2026 season underway — schedule will appear once entered on MaxPreps.",
     "history":[],"fallback_games":[]},

    {"id":"volleyball-girls-jv","sport":"Girls Volleyball","level":"JV Girls",
     "icon":"volleyball","url":BASE+"/volleyball/jv/schedule/","mp_url":BASE+"/volleyball/jv/",
     "year":"2026","season_start":"2026-08-01","season_end":"2026-11-15",
     "note":"2026 season underway — schedule will appear once entered on MaxPreps.",
     "history":[],"fallback_games":[]},

    {"id":"volleyball-girls-ms","sport":"Girls Volleyball","level":"Middle School Girls",
     "icon":"volleyball","url":BASE+"/volleyball/freshman/schedule/","mp_url":BASE+"/volleyball/freshman/",
     "year":"2026","season_start":"2026-08-01","season_end":"2026-11-15",
     "note":"2026 season underway. Results on MaxPreps under the Freshman tab.",
     "history":[],"fallback_games":[]},

    {"id":"basketball-varsity-boys","sport":"Basketball","level":"Varsity Boys",
     "icon":"basketball","url":BASE+"/basketball/schedule/","mp_url":BASE+"/basketball/",
     "year":"2026-27","season_start":"2026-07-11","season_end":"2027-03-15",
     "note":"First game November 7.",
     "history":[{"year":"2025-26","startDate":"2025-11-01","endDate":"2026-02-28",
                 "mpUrl":BASE+"/basketball/25-26/schedule/","record":{"w":10,"l":8},
                 "note":"2025-26 season complete.",
                 "games":[
                     {"date":"2026-01-23","opp":"Cornerstone Christian Academy","ha":"away","res":"W","score":"70-63"},
                     {"date":"2026-01-30","opp":"The Capitol Encore Academy","ha":"away","res":"W","score":"58-49"},
                     {"date":"2026-02-10","opp":"The Capitol Encore Academy","ha":"home","res":"W","score":"69-44"}]}],
     "fallback_games":[
         {"date":"2026-11-07","opp":"Tournament TBA (Preseason)","ha":"home","time":"TBA"},
         {"date":"2026-11-07","opp":"Tournament TBA (Preseason)","ha":"home","time":"TBA"},
         {"date":"2026-11-13","opp":"Tournament TBA (Preseason)","ha":"away","time":"TBA"},
         {"date":"2026-11-14","opp":"Tournament TBA (Preseason)","ha":"home","time":"TBA"},
         {"date":"2026-11-16","opp":"Freedom Christian Academy","ha":"away","time":"7:00PM"},
         {"date":"2026-11-17","opp":"Father Capodanno","ha":"home","time":"6:00PM"},
         {"date":"2026-11-19","opp":"Riverside Christian Academy","ha":"away","time":"7:00PM"},
         {"date":"2026-12-04","opp":"Father Capodanno","ha":"away","time":"5:30PM"},
         {"date":"2026-12-08","opp":"Alpha Academy","ha":"home","time":"7:00PM"},
         {"date":"2026-12-10","opp":"Freedom Christian Academy","ha":"away","time":"7:00PM"},
         {"date":"2026-12-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"7:00PM"},
         {"date":"2026-12-15","opp":"Cornerstone Christian Academy","ha":"home","time":"6:30PM"},
         {"date":"2026-12-21","opp":"Tournament TBA (Christmas)","ha":"home","time":"TBA"},
         {"date":"2026-12-22","opp":"Tournament TBA (Christmas)","ha":"home","time":"TBA"},
         {"date":"2026-12-23","opp":"Tournament TBA (Christmas)","ha":"home","time":"TBA"},
         {"date":"2027-01-11","opp":"Christ the Cornerstone Academy","ha":"away","time":"7:00PM"},
         {"date":"2027-01-15","opp":"Grovemont","ha":"home","time":"7:15PM"},
         {"date":"2027-01-22","opp":"Riverside Christian Academy","ha":"home","time":"6:00PM"},
         {"date":"2027-01-26","opp":"Alpha Academy","ha":"away","time":"7:00PM"},
         {"date":"2027-01-29","opp":"Cornerstone Christian Academy","ha":"away","time":"6:30PM"},
         {"date":"2027-02-18","opp":"Grovemont","ha":"away","time":"7:15PM"},
         {"date":"2027-03-08","opp":"Gatlinburg National Championship","ha":"home","time":"TBA"},
         {"date":"2027-03-09","opp":"Gatlinburg National Championship","ha":"home","time":"TBA"},
         {"date":"2027-03-10","opp":"Gatlinburg National Championship","ha":"home","time":"TBA"},
         {"date":"2027-03-11","opp":"Gatlinburg National Championship","ha":"home","time":"TBA"},
         {"date":"2027-03-12","opp":"Gatlinburg National Championship","ha":"home","time":"TBA"},
     ]},

    {"id":"basketball-jv-boys","sport":"Basketball","level":"JV Boys",
     "icon":"basketball","url":BASE+"/basketball/jv/schedule/","mp_url":BASE+"/basketball/jv/",
     "year":"2026-27","season_start":"2026-07-07","season_end":"2027-02-28",
     "note":"First game November 16.",
     "history":[{"year":"2025-26","startDate":"2025-11-01","endDate":"2026-02-28",
                 "mpUrl":BASE+"/basketball/jv/25-26/schedule/","record":{"w":8,"l":17},
                 "note":"2025-26 season complete.",
                 "games":[
                     {"date":"2026-02-12","opp":"Father Capodanno","ha":"home","res":"W","score":"52-46"},
                     {"date":"2026-02-13","opp":"End of Season Tournament","ha":"home","res":"W","score":"77-52"},
                     {"date":"2026-02-14","opp":"End of Season Tournament","ha":"home","res":"W","score":"56-44"}]}],
     "fallback_games":[
         {"date":"2026-11-16","opp":"Freedom Christian Academy","ha":"away","time":"5:00PM"},
         {"date":"2026-12-08","opp":"Alpha Academy","ha":"home","time":"5:30PM"},
         {"date":"2026-12-10","opp":"Freedom Christian Academy","ha":"away","time":"5:30PM"},
         {"date":"2026-12-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"5:00PM"},
         {"date":"2026-12-15","opp":"Cornerstone Christian Academy","ha":"home","time":"5:00PM"},
         {"date":"2027-01-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"5:30PM"},
         {"date":"2027-01-15","opp":"Grovemont","ha":"home","time":"6:00PM"},
         {"date":"2027-01-26","opp":"Alpha Academy","ha":"away","time":"7:00PM"},
         {"date":"2027-01-29","opp":"Cornerstone Christian Academy","ha":"away","time":"5:00PM"},
         {"date":"2027-02-18","opp":"Grovemont","ha":"away","time":"5:30PM"},
     ]},

    {"id":"basketball-ms-boys","sport":"Basketball","level":"Middle School Boys",
     "icon":"basketball","url":BASE+"/basketball/freshman/schedule/","mp_url":BASE+"/basketball/freshman/",
     "year":"2026-27","season_start":"2026-07-07","season_end":"2027-02-28",
     "note":"First game November 14. Results on MaxPreps under the Freshman tab.",
     "history":[{"year":"2025-26","startDate":"2025-11-01","endDate":"2026-02-28",
                 "mpUrl":BASE+"/basketball/freshman/25-26/schedule/","record":{"w":7,"l":17},
                 "note":"2025-26 season complete. Results on MaxPreps under the Freshman tab.",
                 "games":[
                     {"date":"2026-01-30","opp":"Capitol Encore Academy","ha":"away","res":"L","score":"20-47"},
                     {"date":"2026-02-05","opp":"South Wake","ha":"away","res":"W","score":"43-25"},
                     {"date":"2026-02-10","opp":"Capitol Encore Academy","ha":"home","res":"L","score":"15-54"}]}],
     "fallback_games":[
         {"date":"2026-11-14","opp":"Tournament TBA","ha":"home","time":"TBA"},
         {"date":"2026-11-14","opp":"Tournament TBA","ha":"home","time":"TBA"},
         {"date":"2026-11-16","opp":"Freedom Christian Academy","ha":"away","time":"4:00PM"},
         {"date":"2026-11-19","opp":"Riverside Christian Academy","ha":"away","time":"6:00PM"},
         {"date":"2026-11-20","opp":"Opponent TBA","ha":"home","time":"4:30PM"},
         {"date":"2026-12-07","opp":"Opponent TBA","ha":"home","time":"4:00PM"},
         {"date":"2026-12-08","opp":"Alpha Academy","ha":"home","time":"4:30PM"},
         {"date":"2026-12-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"4:30PM"},
         {"date":"2026-12-15","opp":"Cornerstone Christian Academy","ha":"home","time":"4:00PM"},
         {"date":"2026-12-17","opp":"Opponent TBA","ha":"home","time":"4:30PM"},
         {"date":"2027-01-08","opp":"Opponent TBA","ha":"home","time":"4:00PM"},
         {"date":"2027-01-11","opp":"Christ the Cornerstone Academy","ha":"away","time":"4:30PM"},
         {"date":"2027-01-15","opp":"Grovemont","ha":"home","time":"5:00PM"},
         {"date":"2027-01-22","opp":"Riverside Christian Academy","ha":"home","time":"5:00PM"},
         {"date":"2027-01-28","opp":"Alpha Academy","ha":"away","time":"4:30PM"},
         {"date":"2027-01-29","opp":"Cornerstone Christian Academy","ha":"home","time":"4:00PM"},
         {"date":"2027-02-18","opp":"Grovemont","ha":"away","time":"4:30PM"},
     ]},

    {"id":"baseball-ms","sport":"Baseball","level":"Middle School Boys",
     "icon":"baseball","live_gc":True,
     "gc_url":"https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb",
     "gc_widget_id":"9b48626c-98b5-400b-9f19-467268938605",
     "note":"Inaugural 2026 season — NCHEAC league, reached state tournament in Pittsboro."},

    {"id":"baseball-hs","sport":"Baseball","level":"High School Boys",
     "icon":"baseball","url":BASE+"/baseball/schedule/","mp_url":BASE+"/baseball/",
     "year":"2026-27","season_start":"2027-03-01","season_end":"2027-05-31",
     "note":"First HS season planned for Spring 2027.","history":[],"fallback_games":[]},

    {"id":"volleyball-boys-varsity","sport":"Boys Volleyball","level":"Varsity Boys",
     "icon":"volleyball","url":BASE+"/volleyball/boys/schedule/","mp_url":BASE+"/volleyball/boys/",
     "year":"2026-27","season_start":"2027-03-01","season_end":"2027-05-31",
     "note":"Season begins March 2027.",
     "history":[{"year":"2025-26","startDate":"2026-03-01","endDate":"2026-05-15",
                 "mpUrl":BASE+"/volleyball/boys/","record":{"w":11,"l":2},
                 "note":"2025-26 season complete — finished #35 in NC.",
                 "games":[
                     {"date":"2026-04-24","opp":"Village Christian Academy","ha":"away","res":"W","score":"3-0"},
                     {"date":"2026-04-28","opp":"Purnell Swett","ha":"away","res":"W","score":"3-0"},
                     {"date":"2026-04-30","opp":"Freedom Christian Academy","ha":"away","res":"W","score":"3-2"}]}],
     "fallback_games":[]},
]

WIDGET_SPECS = [
    {"file":"widget-basketball.html","title":"Basketball &mdash; Schedules &amp; Records",
     "ids":["basketball-varsity-boys","basketball-jv-boys","basketball-ms-boys"],
     "footer":f'Schedules from <a href="{BASE}/basketball/">MaxPreps</a> (MS under Freshman tab). Auto-updated daily.'},
    {"file":"widget-girls-volleyball.html","title":"Girls Volleyball &mdash; Schedules &amp; Records",
     "ids":["volleyball-girls-varsity","volleyball-girls-jv","volleyball-girls-ms"],
     "footer":f'Schedules from <a href="{BASE}/volleyball/">MaxPreps</a> (MS under Freshman tab). Auto-updated daily.'},
    {"file":"widget-boys-volleyball.html","title":"Boys Volleyball &mdash; Schedules &amp; Records",
     "ids":["volleyball-boys-varsity"],
     "footer":f'Schedule from <a href="{BASE}/volleyball/boys/">MaxPreps</a>. Auto-updated daily.'},
    {"file":"widget-baseball.html","title":"Baseball &mdash; Schedules &amp; Records",
     "ids":["baseball-ms","baseball-hs"],
     "footer":'MS Baseball live from <a href="https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb">GameChanger</a>. HS begins Spring 2027.'},
    {"file":"widget-all-sports.html","title":"All Sports &mdash; Schedules &amp; Records",
     "ids":["volleyball-girls-varsity","volleyball-girls-jv","volleyball-girls-ms",
            "basketball-varsity-boys","basketball-jv-boys","basketball-ms-boys",
            "baseball-ms","baseball-hs","volleyball-boys-varsity"],
     "footer":f'Basketball &amp; Volleyball: <a href="{BASE}/">MaxPreps</a> &mdash; MS Baseball: <a href="https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb">GameChanger</a>. Auto-updated daily.'},
]

# ── MaxPreps scraper ───────────────────────────────────────────────────────
def fetch_page(url):
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            br = p.chromium.launch(args=["--no-sandbox","--disable-setuid-sandbox"])
            ctx = br.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36",
                viewport={"width":1280,"height":800})
            pg = ctx.new_page()
            pg.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf}", lambda r: r.abort())
            pg.goto(url, wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(2000)
            html = pg.content()
            br.close()
            return html
    except Exception as e:
        print(f" fetch error: {e}")
        return None

def clean_opp(raw):
    for ph in ("Non Freshman Opponent","Non Varsity Opponent","TBA Opponent","Non JV Opponent"):
        if ph.lower() in raw.strip().lower(): return "Opponent TBA"
    return re.sub(r"\s*\*+$","",raw.strip()) or "Opponent TBA"

def parse_date(text, yr_label):
    m = re.search(r"(\d{1,2})/(\d{1,2})",text)
    if not m: return None
    mo,dy = int(m.group(1)),int(m.group(2))
    sy = int(yr_label.split("-")[0]) if "-" in yr_label else int(yr_label)
    yr = sy if mo>=7 else sy+1
    return f"{yr:04d}-{mo:02d}-{dy:02d}"

def parse_time(t):
    m = re.search(r"(\d+:\d+\s*[aApP][mM])",t)
    return m.group(1).upper().replace(" ","") if m else None

def parse_result(t):
    t = t.strip().upper()
    for ch in ("W","L","T"):
        m = re.search(rf"\b{ch}\s*(\d+[-\u2013]\d+)",t)
        if m: return ch, m.group(1).replace("\u2013","-")
    return None, None

def scrape(team):
    print(f"  fetching...", end="", flush=True)
    html = fetch_page(team["url"])
    if not html: return None
    nd = re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',html,re.S)
    if nd:
        try:
            data = json.loads(nd.group(1))
            def walk(o,*keys):
                if isinstance(o,dict):
                    for k in keys:
                        if k in o and o[k] is not None: return o[k]
                    for v in o.values():
                        r=walk(v,*keys)
                        if r is not None: return r
                elif isinstance(o,list):
                    for i in o:
                        r=walk(i,*keys)
                        if r is not None: return r
                return None
            sched=walk(data,"contestSchedule","schedule","teamSchedule","games","contests")
            if isinstance(sched,list) and sched:
                games=[]
                for item in sched:
                    if not isinstance(item,dict): continue
                    rd=str(item.get("contestDate") or item.get("date") or "")
                    iso=re.search(r"(\d{4}-\d{2}-\d{2})",rd)
                    gd=iso.group(1) if iso else parse_date(rd,team["year"])
                    if not gd: continue
                    opp=clean_opp(str(item.get("opponent") or item.get("opponentName") or ""))
                    loc=str(item.get("homeAway") or item.get("location") or "").upper()
                    ha="away" if loc in ("A","AWAY") else "home"
                    gt=parse_time(str(item.get("startTime") or item.get("time") or ""))
                    res,score=parse_result(str(item.get("result") or item.get("score") or ""))
                    games.append({"date":gd,"opp":opp,"ha":ha,"time":gt,"res":res,"score":score})
                games.sort(key=lambda g:g["date"])
                w=walk(data,"overallWins","wins"); l=walk(data,"overallLosses","losses")
                record=None
                if w is not None and l is not None:
                    try: record={"w":int(w),"l":int(l)}
                    except: pass
                print(f" {len(games)} games (JSON)")
                return {"games":games,"record":record}
        except: pass
    try:
        from bs4 import BeautifulSoup
        soup=BeautifulSoup(html,"html.parser"); games=[]
        for table in soup.find_all("table"):
            rows=table.find_all("tr")
            sample=" ".join(r.get_text() for r in rows[:4])
            if not re.search(r"\d+/\d+",sample): continue
            for row in rows:
                cells=row.find_all(["td","th"])
                if len(cells)<2: continue
                dtxt=cells[0].get_text(" ",strip=True)
                otxt=cells[1].get_text(" ",strip=True)
                itxt=cells[2].get_text(" ",strip=True) if len(cells)>2 else ""
                gd=parse_date(dtxt,team["year"])
                if not gd: continue
                ha="away" if otxt.lstrip().startswith("@") else "home"
                raw=re.sub(r"^[@]?\s*","",otxt); raw=re.sub(r"^vs\s*","",raw,flags=re.I)
                opp=clean_opp(raw); gt=parse_time(dtxt); res,score=parse_result(itxt)
                games.append({"date":gd,"opp":opp,"ha":ha,"time":gt,"res":res,"score":score})
        games.sort(key=lambda g:g["date"])
        rm=re.search(r"Overall\s*[:\-]?\s*(\d+)\s*[-\u2013]\s*(\d+)",html,re.I)
        record={"w":int(rm.group(1)),"l":int(rm.group(2))} if rm else None
        print(f" {len(games)} games (HTML)")
        return {"games":games,"record":record}
    except Exception as e:
        print(f" parse error: {e}"); return None

# ── Static HTML generation ─────────────────────────────────────────────────
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
summary::before{content:'&#9656; ';}
details[open] summary::before{content:'&#9662; ';}
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
        from datetime import date as dt
        d = dt.fromisoformat(iso)
        return d.strftime('%a %b %-d')
    except:
        return iso

def make_card(team, scraped, LOGO, BB, VB, BSB):
    badges = {'basketball':BB,'volleyball':VB,'baseball':BSB}
    badge_b64 = badges[team['icon']]

    if team.get('live_gc'):
        gc_cid = f"gc-{team['id']}"
        return f"""<div class="card">
  <div class="card-head">
    <div class="badge"><img src="data:image/png;base64,{badge_b64}" alt="{team['sport']}"></div>
    <div class="card-titles">
      <div class="sport">{team['sport']}</div>
      <div class="level">{team['level']}</div>
      <div class="yr">2026</div>
    </div>
    <span class="status live">Live</span>
  </div>
  <div class="note">{team.get('note','')}</div>
  <div class="live-box" id="{gc_cid}">&#9654; Live schedule &amp; scores loading from GameChanger...</div>
  <a class="mplink" href="{team['gc_url']}" target="_blank" rel="noopener">View on GameChanger &rarr;</a>
</div>"""

    today = date.today().isoformat()
    history = team.get('history', [])

    # Determine which season to show
    year_label = team['year']
    season_start = team['season_start']
    season_end   = team['season_end']
    mp_url       = team['mp_url']

    # Use scraped games/record if available, else fallback
    if scraped and scraped.get('games'):
        games  = scraped['games']
        record = scraped.get('record')
        # infer record from games if not returned directly
        if record is None:
            played = [g for g in games if g.get('res') in ('W','L','T')]
            if played:
                w=sum(1 for g in played if g['res']=='W')
                l=sum(1 for g in played if g['res']=='L')
                t=sum(1 for g in played if g['res']=='T')
                record = {'w':w,'l':l} if not t else {'w':w,'l':l,'t':t}
    else:
        games  = team.get('fallback_games', [])
        record = None

    # Check if current season or should show history
    showing_current = today >= season_start and today <= season_end
    if not showing_current and history:
        # Not in current season window — use most recently completed historical season
        past_hist = [h for h in history if h['endDate'] < today]
        if past_hist:
            hist = sorted(past_hist, key=lambda h: h['endDate'], reverse=True)[0]
        year_label   = hist['year']
        season_start = hist['startDate']
        mp_url       = hist['mpUrl']
        record       = hist.get('record')
        games        = hist.get('games', [])

    # Status
    played_games   = [g for g in games if g.get('res') in ('W','L','T')]
    upcoming_games = [g for g in games if g.get('res') not in ('W','L','T')]
    upcoming_games.sort(key=lambda g: g['date'])
    played_games.sort(key=lambda g: g['date'])

    if record:
        w = record.get('w',0); l = record.get('l',0); t = record.get('t',0)
        tot = w+l+t
        pct = round(((w+0.5*t)/tot)*100) if tot else 0
        rec_html = f'<div class="rec">{w}&ndash;{l}{"&ndash;"+str(t) if t else ""}</div><div class="pct">{pct}% win rate</div>'
        if upcoming_games:
            status_cls, status_txt = 'pre', 'In Season'
        else:
            status_cls, status_txt = 'final', 'Final'
    else:
        rec_html = '<div class="rec" style="color:#93909a">&mdash;</div>'
        status_cls = 'pre'
        status_txt = 'Upcoming' if season_start > today else 'Pre-Season'

    # Next/last/note line
    mid = ''
    if upcoming_games:
        nxt = upcoming_games[0]
        ha  = 'vs' if nxt['ha']=='home' else '@'
        t   = f" &middot; {nxt.get('time','')}" if nxt.get('time') and nxt.get('time')!='TBA' else ''
        mid = f'<div class="nxt">Next: <strong>{fmt(nxt["date"])}</strong> {ha} {nxt["opp"]}{t}</div>'
    elif played_games:
        last = played_games[-1]
        ha   = 'vs' if last['ha']=='home' else '@'
        mid  = f'<div class="nxt">Last: <strong>{last["res"]} {last.get("score","")}</strong> {ha} {last["opp"]} ({fmt(last["date"])})</div>'
    elif team.get('note'):
        mid = f'<div class="note">{team["note"]}</div>'

    # Schedule list
    list_html = ''
    if games:
        all_sorted = sorted(games, key=lambda g: g['date'])
        rows = ''
        for g in all_sorted:
            ha  = 'vs' if g['ha']=='home' else '@'
            res = g.get('res','')
            t   = g.get('time','TBD') or 'TBD'
            if res:
                rh = f'<span class="gres {res.lower()}">{res} {g.get("score","")}</span>'
            else:
                rh = f'<span class="gres">{t}</span>'
            rows += f'<div class="grow"><span class="gdate">{fmt(g["date"])}</span><span class="gopp">{ha} {g["opp"]}</span>{rh}</div>'
        list_html = f'<details><summary>Schedule &amp; results ({len(all_sorted)})</summary><div class="glist">{rows}</div></details>'

    return f"""<div class="card">
  <div class="card-head">
    <div class="badge"><img src="data:image/png;base64,{badge_b64}" alt="{team['sport']}"></div>
    <div class="card-titles">
      <div class="sport">{team['sport']}</div>
      <div class="level">{team['level']}</div>
      <div class="yr">{year_label}</div>
    </div>
    <span class="status {status_cls}">{status_txt}</span>
  </div>
  {rec_html}
  {mid}
  {list_html}
  <a class="mplink" href="{mp_url}" target="_blank" rel="noopener">View on MaxPreps &rarr;</a>
</div>"""

def make_page(spec, team_map, scraped_map, run_time, LOGO, BB, VB, BSB):
    cards = ''.join(make_card(team_map[tid], scraped_map.get(tid), LOGO, BB, VB, BSB)
                    for tid in spec['ids'] if tid in team_map)
    has_gc = any(team_map[tid].get('live_gc') for tid in spec['ids'] if tid in team_map)
    gc_block = ''
    if has_gc:
        gc_t = next((team_map[tid] for tid in spec['ids'] if team_map.get(tid,{}).get('live_gc')), None)
        if gc_t:
            gc_block = f"""
<script src="https://widgets.gc.com/static/js/sdk.v1.js"></script>
<script>
(function(){{
  var GC_ID="{gc_t['gc_widget_id']}";
  if(window.GC&&window.GC.team&&window.GC.team.schedule){{
    window.GC.team.schedule.init({{target:"#gc-{gc_t['id']}",widgetId:GC_ID,maxVerticalGamesVisible:4}});
  }}
}})();
</script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Outliers Athletics</title>
{CSS}
</head>
<body>
<div class="widget">
<div class="hdr">
  <img src="data:image/png;base64,{LOGO}" alt="Outliers Athletics">
  <div class="hdr-title">
    <h1>{spec['title']}</h1>
    <div class="upd">fayhomeschoolsports.org &mdash; Updated {run_time}</div>
  </div>
</div>
<div class="grid">{cards}</div>
<div class="footer">{spec['footer']}</div>
</div>
{gc_block}
</body>
</html>"""

def main():
    now = datetime.utcnow()
    run_time = now.strftime('%b %-d, %Y')
    print(f"Outliers static widget build — {date.today()} {now.strftime('%H:%M')} UTC")
    print("="*60)

    LOGO = load('LOGO.b64'); BB = load('BB.b64'); VB = load('VB.b64'); BSB = load('BSB.b64')

    cache = {}
    if os.path.exists(CACHE_FILE):
        try: cache = json.load(open(CACHE_FILE))
        except: pass

    team_map    = {t['id']: t for t in TEAMS}
    scraped_map = {}
    new_cache   = {}

    for team in TEAMS:
        print(f"\n{team['sport']} — {team['level']}")
        if team.get('live_gc'):
            print("  → GameChanger live embed"); continue
        if not team.get('url'):
            continue
        scraped = scrape(team)
        if scraped is None:
            cached = cache.get(team['id'])
            if cached:
                print(f"  ⚠ using cache from {cached.get('date','?')}")
                scraped = cached.get('scraped')
            else:
                print("  ⚠ no cache — using fallback schedule")
        else:
            new_cache[team['id']] = {'date': str(date.today()), 'scraped': scraped}
        scraped_map[team['id']] = scraped

    merged = {**cache, **new_cache}
    with open(CACHE_FILE, 'w') as f: json.dump(merged, f, indent=2)

    print("\n" + "="*60 + "\nGenerating static HTML widgets...")
    for spec in WIDGET_SPECS:
        html = make_page(spec, team_map, scraped_map, run_time, LOGO, BB, VB, BSB)
        path = os.path.join(ROOT_DIR, spec['file'])
        with open(path, 'w', encoding='utf-8') as f: f.write(html)
        print(f"  ✓  {spec['file']}  ({len(html)//1024} KB)")

    # Heartbeat + index
    hb = os.path.join(ROOT_DIR, 'last_run.txt')
    with open(hb, 'w') as f:
        f.write(f"Last run: {date.today()} at {now.strftime('%H:%M')} UTC\n")

    rows = ''.join(f"<li><a href='{s['file']}'>{s['title'].replace('&mdash;','-').replace('&amp;','&')}</a></li>"
                   for s in WIDGET_SPECS)
    with open(os.path.join(ROOT_DIR, 'index.html'), 'w') as f:
        f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Outliers Widgets</title>"
                f"<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}}"
                f"a{{color:#7c021e;font-weight:bold}}li{{margin:12px 0}}</style></head>"
                f"<body><h1>Outliers Athletics Widget Directory</h1>"
                f"<p>Embed these URLs in Google Sites via <strong>Insert &rarr; Embed &rarr; By URL</strong></p>"
                f"<ul>{rows}</ul>"
                f"<p style='color:#999;font-size:13px'>Script last ran: {date.today()} {now.strftime('%H:%M')} UTC</p>"
                f"</body></html>")
    print("  ✓  index.html\n  ✓  last_run.txt\nDone ✓")

if __name__ == '__main__':
    main()
