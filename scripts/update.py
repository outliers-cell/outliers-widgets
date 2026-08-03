#!/usr/bin/env python3
"""
Fayetteville Outliers — Daily Widget Generator
Writes all widget HTML files directly to the repo root folder.
Run by GitHub Actions every morning at 7 AM ET.
"""

import json, os, re, sys
from datetime import date, datetime

# ── Key paths ──────────────────────────────────────────────────────────────
# scripts/ is next to the repo root, so parent of scripts/ IS the root
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR    = os.path.dirname(SCRIPTS_DIR)   # ← widget HTML files go here
CACHE_FILE  = os.path.join(ROOT_DIR, "last_data.json")

BASE = "https://www.maxpreps.com/nc/fayetteville/fayetteville-outliers-outliers"

# ── Team data ──────────────────────────────────────────────────────────────
TEAMS = [
    # Girls Volleyball
    {"id":"volleyball-girls-varsity","sport":"Girls Volleyball","level":"Varsity Girls","icon":"volleyball",
     "url":BASE+"/volleyball/schedule/","mp_url":BASE+"/volleyball/",
     "year":"2026","season_start":"2026-08-01","season_end":"2026-11-15","history":[]},
    {"id":"volleyball-girls-jv","sport":"Girls Volleyball","level":"JV Girls","icon":"volleyball",
     "url":BASE+"/volleyball/jv/schedule/","mp_url":BASE+"/volleyball/jv/",
     "year":"2026","season_start":"2026-08-01","season_end":"2026-11-15","history":[]},
    {"id":"volleyball-girls-ms","sport":"Girls Volleyball","level":"Middle School Girls","icon":"volleyball",
     "url":BASE+"/volleyball/freshman/schedule/","mp_url":BASE+"/volleyball/freshman/",
     "year":"2026","season_start":"2026-08-01","season_end":"2026-11-15",
     "ms_note":"Results on MaxPreps under the \u201cFreshman\u201d tab.","history":[]},
    # Basketball
    {"id":"basketball-varsity-boys","sport":"Basketball","level":"Varsity Boys","icon":"basketball",
     "url":BASE+"/basketball/schedule/","mp_url":BASE+"/basketball/",
     "year":"2026-27","season_start":"2026-07-11","season_end":"2027-03-15",
     # fallback_games: used if MaxPreps scraping fails on any given day
     "fallback_games":[
         {"date":"2026-11-07","opp":"Tournament TBA (Preseason)","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2026-11-07","opp":"Tournament TBA (Preseason)","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2026-11-13","opp":"Tournament TBA (Preseason)","ha":"away","time":"TBA","res":None,"score":None},
         {"date":"2026-11-14","opp":"Tournament TBA (Preseason)","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2026-11-16","opp":"Freedom Christian Academy","ha":"away","time":"7:00PM","res":None,"score":None},
         {"date":"2026-11-17","opp":"Father Capodanno","ha":"home","time":"6:00PM","res":None,"score":None},
         {"date":"2026-11-19","opp":"Riverside Christian Academy","ha":"away","time":"7:00PM","res":None,"score":None},
         {"date":"2026-12-04","opp":"Father Capodanno","ha":"away","time":"5:30PM","res":None,"score":None},
         {"date":"2026-12-08","opp":"Alpha Academy","ha":"home","time":"7:00PM","res":None,"score":None},
         {"date":"2026-12-10","opp":"Freedom Christian Academy","ha":"away","time":"7:00PM","res":None,"score":None},
         {"date":"2026-12-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"7:00PM","res":None,"score":None},
         {"date":"2026-12-15","opp":"Cornerstone Christian Academy","ha":"home","time":"6:30PM","res":None,"score":None},
         {"date":"2026-12-21","opp":"Tournament TBA (Christmas)","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2026-12-22","opp":"Tournament TBA (Christmas)","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2026-12-23","opp":"Tournament TBA (Christmas)","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2027-01-11","opp":"Christ the Cornerstone Academy","ha":"away","time":"7:00PM","res":None,"score":None},
         {"date":"2027-01-15","opp":"Grovemont","ha":"home","time":"7:15PM","res":None,"score":None},
         {"date":"2027-01-22","opp":"Riverside Christian Academy","ha":"home","time":"6:00PM","res":None,"score":None},
         {"date":"2027-01-26","opp":"Alpha Academy","ha":"away","time":"7:00PM","res":None,"score":None},
         {"date":"2027-01-29","opp":"Cornerstone Christian Academy","ha":"away","time":"6:30PM","res":None,"score":None},
         {"date":"2027-02-18","opp":"Grovemont","ha":"away","time":"7:15PM","res":None,"score":None},
         {"date":"2027-03-08","opp":"Gatlinburg National Championship","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2027-03-09","opp":"Gatlinburg National Championship","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2027-03-10","opp":"Gatlinburg National Championship","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2027-03-11","opp":"Gatlinburg National Championship","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2027-03-12","opp":"Gatlinburg National Championship","ha":"home","time":"TBA","res":None,"score":None},
     ],
     "history":[{"year":"2025-26","startDate":"2025-11-01","endDate":"2026-02-28",
                 "mpUrl":BASE+"/basketball/25-26/schedule/","record":{"w":10,"l":8},
                 "note":"2025\u201326 season complete.","games":[
                     {"date":"2026-01-23","opp":"Cornerstone Christian Academy","ha":"away","time":None,"res":"W","score":"70-63"},
                     {"date":"2026-01-30","opp":"The Capitol Encore Academy","ha":"away","time":None,"res":"W","score":"58-49"},
                     {"date":"2026-02-10","opp":"The Capitol Encore Academy","ha":"home","time":None,"res":"W","score":"69-44"}]}]},
    {"id":"basketball-jv-boys","sport":"Basketball","level":"JV Boys","icon":"basketball",
     "url":BASE+"/basketball/jv/schedule/","mp_url":BASE+"/basketball/jv/",
     "year":"2026-27","season_start":"2026-07-07","season_end":"2027-02-28",
     "fallback_games":[
         {"date":"2026-11-16","opp":"Freedom Christian Academy","ha":"away","time":"5:00PM","res":None,"score":None},
         {"date":"2026-12-08","opp":"Alpha Academy","ha":"home","time":"5:30PM","res":None,"score":None},
         {"date":"2026-12-10","opp":"Freedom Christian Academy","ha":"away","time":"5:30PM","res":None,"score":None},
         {"date":"2026-12-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"5:00PM","res":None,"score":None},
         {"date":"2026-12-15","opp":"Cornerstone Christian Academy","ha":"home","time":"5:00PM","res":None,"score":None},
         {"date":"2027-01-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"5:30PM","res":None,"score":None},
         {"date":"2027-01-15","opp":"Grovemont","ha":"home","time":"6:00PM","res":None,"score":None},
         {"date":"2027-01-26","opp":"Alpha Academy","ha":"away","time":"7:00PM","res":None,"score":None},
         {"date":"2027-01-29","opp":"Cornerstone Christian Academy","ha":"away","time":"5:00PM","res":None,"score":None},
         {"date":"2027-02-18","opp":"Grovemont","ha":"away","time":"5:30PM","res":None,"score":None},
     ],
     "history":[{"year":"2025-26","startDate":"2025-11-01","endDate":"2026-02-28",
                 "mpUrl":BASE+"/basketball/jv/25-26/schedule/","record":{"w":8,"l":17},
                 "note":"2025\u201326 season complete.","games":[
                     {"date":"2026-02-12","opp":"Father Capodanno","ha":"home","time":None,"res":"W","score":"52-46"},
                     {"date":"2026-02-13","opp":"End of Season Tournament","ha":"home","time":None,"res":"W","score":"77-52"},
                     {"date":"2026-02-14","opp":"End of Season Tournament","ha":"home","time":None,"res":"W","score":"56-44"}]}]},
    {"id":"basketball-ms-boys","sport":"Basketball","level":"Middle School Boys","icon":"basketball",
     "url":BASE+"/basketball/freshman/schedule/","mp_url":BASE+"/basketball/freshman/",
     "year":"2026-27","season_start":"2026-07-07","season_end":"2027-02-28",
     "ms_note":"Results on MaxPreps under the \u201cFreshman\u201d tab.",
     "fallback_games":[
         {"date":"2026-11-14","opp":"Tournament TBA","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2026-11-14","opp":"Tournament TBA","ha":"home","time":"TBA","res":None,"score":None},
         {"date":"2026-11-16","opp":"Freedom Christian Academy","ha":"away","time":"4:00PM","res":None,"score":None},
         {"date":"2026-11-19","opp":"Riverside Christian Academy","ha":"away","time":"6:00PM","res":None,"score":None},
         {"date":"2026-11-20","opp":"Opponent TBA","ha":"home","time":"4:30PM","res":None,"score":None},
         {"date":"2026-12-07","opp":"Opponent TBA","ha":"home","time":"4:00PM","res":None,"score":None},
         {"date":"2026-12-08","opp":"Alpha Academy","ha":"home","time":"4:30PM","res":None,"score":None},
         {"date":"2026-12-11","opp":"Christ the Cornerstone Academy","ha":"home","time":"4:30PM","res":None,"score":None},
         {"date":"2026-12-15","opp":"Cornerstone Christian Academy","ha":"home","time":"4:00PM","res":None,"score":None},
         {"date":"2026-12-17","opp":"Opponent TBA","ha":"home","time":"4:30PM","res":None,"score":None},
         {"date":"2027-01-08","opp":"Opponent TBA","ha":"home","time":"4:00PM","res":None,"score":None},
         {"date":"2027-01-11","opp":"Christ the Cornerstone Academy","ha":"away","time":"4:30PM","res":None,"score":None},
         {"date":"2027-01-15","opp":"Grovemont","ha":"home","time":"5:00PM","res":None,"score":None},
         {"date":"2027-01-22","opp":"Riverside Christian Academy","ha":"home","time":"5:00PM","res":None,"score":None},
         {"date":"2027-01-28","opp":"Alpha Academy","ha":"away","time":"4:30PM","res":None,"score":None},
         {"date":"2027-01-29","opp":"Cornerstone Christian Academy","ha":"home","time":"4:00PM","res":None,"score":None},
         {"date":"2027-02-18","opp":"Grovemont","ha":"away","time":"4:30PM","res":None,"score":None},
     ],
     "history":[{"year":"2025-26","startDate":"2025-11-01","endDate":"2026-02-28",
                 "mpUrl":BASE+"/basketball/freshman/25-26/schedule/","record":{"w":7,"l":17},
                 "note":"2025\u201326 season complete. Results on MaxPreps under the \u201cFreshman\u201d tab.","games":[
                     {"date":"2026-01-30","opp":"Capitol Encore Academy","ha":"away","time":None,"res":"L","score":"20-47"},
                     {"date":"2026-02-05","opp":"South Wake","ha":"away","time":None,"res":"W","score":"43-25"},
                     {"date":"2026-02-10","opp":"Capitol Encore Academy","ha":"home","time":None,"res":"L","score":"15-54"}]}]},
    # Baseball
    {"id":"baseball-ms","sport":"Baseball","level":"Middle School Boys","icon":"baseball",
     "live_gc":True,"gc_url":"https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb",
     "gc_widget_id":"9b48626c-98b5-400b-9f19-467268938605",
     "note":"Inaugural 2026 season \u2014 NCHEAC league, reached state tournament in Pittsboro.","seasons":[]},
    {"id":"baseball-hs","sport":"Baseball","level":"High School Boys","icon":"baseball",
     "url":BASE+"/baseball/schedule/","mp_url":BASE+"/baseball/",
     "year":"2026-27","season_start":"2027-03-01","season_end":"2027-05-31","history":[]},
    # Boys Volleyball
    {"id":"volleyball-boys-varsity","sport":"Boys Volleyball","level":"Varsity Boys","icon":"volleyball",
     "url":BASE+"/volleyball/boys/schedule/","mp_url":BASE+"/volleyball/boys/",
     "year":"2026-27","season_start":"2027-03-01","season_end":"2027-05-31",
     "history":[{"year":"2025-26","startDate":"2026-03-01","endDate":"2026-05-15",
                 "mpUrl":BASE+"/volleyball/boys/","record":{"w":11,"l":2},
                 "note":"2025\u201326 season complete \u2014 finished #35 in NC.","games":[
                     {"date":"2026-04-24","opp":"Village Christian Academy","ha":"away","time":None,"res":"W","score":"3-0"},
                     {"date":"2026-04-28","opp":"Purnell Swett","ha":"away","time":None,"res":"W","score":"3-0"},
                     {"date":"2026-04-30","opp":"Freedom Christian Academy","ha":"away","time":None,"res":"W","score":"3-2"}]}]},
]

WIDGET_SPECS = [
    {"filename":"widget-basketball.html","widget_id":"fhs-basketball",
     "tagline":"Basketball \u2014 Schedules &amp; Records",
     "team_ids":["basketball-varsity-boys","basketball-jv-boys","basketball-ms-boys"],
     "footer":'From <a href="'+BASE+'/basketball/" target="_blank" rel="noopener">MaxPreps</a> (MS under Freshman tab). Auto-updated daily.',
     "has_gc":False,"multi":True},
    {"filename":"widget-girls-volleyball.html","widget_id":"fhs-volleyball-girls",
     "tagline":"Girls Volleyball \u2014 Schedules &amp; Records",
     "team_ids":["volleyball-girls-varsity","volleyball-girls-jv","volleyball-girls-ms"],
     "footer":'From <a href="'+BASE+'/volleyball/" target="_blank" rel="noopener">MaxPreps</a> (MS under Freshman tab). Auto-updated daily.',
     "has_gc":False,"multi":True},
    {"filename":"widget-boys-volleyball.html","widget_id":"fhs-volleyball-boys",
     "tagline":"Boys Volleyball \u2014 Schedules &amp; Records",
     "team_ids":["volleyball-boys-varsity"],
     "footer":'From <a href="'+BASE+'/volleyball/boys/" target="_blank" rel="noopener">MaxPreps</a>. Auto-updated daily.',
     "has_gc":False,"multi":False},
    {"filename":"widget-baseball.html","widget_id":"fhs-baseball",
     "tagline":"Baseball \u2014 Schedules &amp; Records",
     "team_ids":["baseball-ms","baseball-hs"],
     "footer":'MS Baseball live from <a href="https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb" target="_blank" rel="noopener">GameChanger</a>. HS begins Spring 2027. Auto-updated daily.',
     "has_gc":True,"multi":False},
    {"filename":"widget-all-sports.html","widget_id":"fhs-all",
     "tagline":"All Sports \u2014 Schedules &amp; Records",
     "team_ids":["volleyball-girls-varsity","volleyball-girls-jv","volleyball-girls-ms",
                 "basketball-varsity-boys","basketball-jv-boys","basketball-ms-boys",
                 "baseball-ms","baseball-hs","volleyball-boys-varsity"],
     "footer":'Basketball &amp; Volleyball from <a href="'+BASE+'/" target="_blank" rel="noopener">MaxPreps</a> &mdash; MS Baseball from <a href="https://web.gc.com/teams/kGxt3T18uW0u/2026-spring-fayetteville-outliers-msb" target="_blank" rel="noopener">GameChanger</a>. Auto-updated daily.',
     "has_gc":True,"multi":True},
]

# ── Scraper ────────────────────────────────────────────────────────────────
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
        print(f"    fetch error: {e}")
        return None

def clean_opp(raw):
    raw = raw.strip()
    for ph in ("Non Freshman Opponent","Non Varsity Opponent","TBA Opponent","Non JV Opponent"):
        if ph.lower() in raw.lower(): return "Opponent TBA"
    return re.sub(r"\s*\*+$","",raw).strip() or "Opponent TBA"

def parse_date(text, yr_label):
    m = re.search(r"(\d{1,2})/(\d{1,2})", text)
    if not m: return None
    mo,dy = int(m.group(1)),int(m.group(2))
    if "-" in yr_label:
        sy = int(yr_label.split("-")[0]); yr = sy if mo>=7 else sy+1
    else:
        yr = int(yr_label)
    return f"{yr:04d}-{mo:02d}-{dy:02d}"

def parse_time(t):
    m = re.search(r"(\d+:\d+\s*[aApP][mM])", t)
    return m.group(1).upper().replace(" ","") if m else None

def parse_result(t):
    t = t.strip().upper()
    for ch in ("W","L","T"):
        m = re.search(rf"\b{ch}\s*(\d+[-\u2013]\d+)", t)
        if m: return ch, m.group(1).replace("\u2013","-")
    return None, None

def scrape(team):
    yr = team.get("year","")
    html = fetch_page(team["url"])
    if not html: return None
    # Try __NEXT_DATA__
    nd = re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', html, re.S)
    if nd:
        try:
            data = json.loads(nd.group(1))
            def walk(o, *keys):
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
            sched = walk(data,"contestSchedule","schedule","teamSchedule","games","contests")
            if isinstance(sched,list) and sched:
                games=[]
                for item in sched:
                    if not isinstance(item,dict): continue
                    rd=str(item.get("contestDate") or item.get("date") or "")
                    iso=re.search(r"(\d{4}-\d{2}-\d{2})",rd)
                    gd=iso.group(1) if iso else parse_date(rd,yr)
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
    # HTML fallback
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
                dtxt=cells[0].get_text(" ",strip=True); otxt=cells[1].get_text(" ",strip=True)
                itxt=cells[2].get_text(" ",strip=True) if len(cells)>2 else ""
                gd=parse_date(dtxt,yr)
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

# ── JS / HTML builders ─────────────────────────────────────────────────────
def j(v):
    if v is None: return "null"
    if isinstance(v,bool): return "true" if v else "false"
    if isinstance(v,(int,float)): return str(v)
    return '"'+str(v).replace("\\","\\\\").replace('"','\\"')+'"'

def game_js(g):
    return f'{{date:{j(g["date"])},opp:{j(g["opp"])},ha:{j(g["ha"])},time:{j(g.get("time"))},res:{j(g.get("res"))},score:{j(g.get("score"))}}}'

def build_team_js(team, scraped):
    i4,i6,i8="    ","      ","        "
    lines=[f"{i4}{{"]
    lines.append(f"{i6}id:{j(team['id'])},sport:{j(team['sport'])},level:{j(team['level'])},icon:{j(team['icon'])},")
    if team.get("live_gc"):
        lines+=[f"{i6}liveEmbed:{{cid:{j('gc-'+team['id'])}}},",
                f"{i6}gcUrl:{j(team['gc_url'])},",
                f"{i6}note:{j(team.get('note',''))},",
                f"{i6}seasons:[]"]
        lines.append(f"{i4}}}"); return "\n".join(lines)
    seasons=list(team.get("history",[]))
    cur={"year":team["year"],"startDate":team["season_start"],"endDate":team["season_end"],
         "mpUrl":team["mp_url"],"record":None,"note":team.get("ms_note",""),"games":[]}
    if scraped:
        cur["record"]=scraped.get("record"); cur["games"]=scraped.get("games",[])
        if cur["record"] is None:
            played=[g for g in cur["games"] if g.get("res") in ("W","L","T")]
            if played:
                w=sum(1 for g in played if g["res"]=="W"); l=sum(1 for g in played if g["res"]=="L"); t=sum(1 for g in played if g["res"]=="T")
                cur["record"]={"w":w,"l":l} if not t else {"w":w,"l":l,"t":t}
    else:
        # Scraping failed — use fallback_games so the schedule still shows
        if team.get("fallback_games"):
            cur["games"] = team["fallback_games"]
    seasons.append(cur)
    parts=[]
    for s in seasons:
        rec=s.get("record")
        rj="null" if rec is None else f'{{w:{rec.get("w",0)},l:{rec.get("l",0)}'+(',t:'+str(rec["t"]) if rec.get("t") else "")+"}}"
        gl=s.get("games",[])
        gj=("[\n"+",\n".join(f"{i8}{game_js(g)}" for g in gl)+f"\n{i6}]") if gl else "[]"
        parts.append(f"{i6}{{\n{i8}year:{j(s['year'])},startDate:{j(s['startDate'])},endDate:{j(s['endDate'])},\n{i8}mpUrl:{j(s['mpUrl'])},record:{rj},note:{j(s.get('note',''))},games:{gj}\n{i6}}}")
    lines.append(f"{i6}seasons:[\n"+",\n".join(parts)+f"\n{i4}  ]")
    lines.append(f"{i4}}}"); return "\n".join(lines)

CSS_TEMPLATE = """
  #%%ID%% {
    --ink:#1a0a0d;--maroon:#7c021e;--maroon-deep:#4a0112;
    --blue:#0bc8ee;--blue-soft:#bdf1fb;--chalk:#F4F6F9;
    --line:#DDE2E8;--muted:#93909a;
    --font-body:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    --font-mono:'Inter','SFMono-Regular',Consolas,Menlo,monospace;
    --font-brand:'Forte','Comic Sans MS',cursive;
    box-sizing:border-box;background:var(--chalk);color:var(--ink);
    font-family:var(--font-body);border-radius:14px;overflow:hidden;border:1px solid var(--line);
  }
  #%%ID%% *,#%%ID%% *::before,#%%ID%% *::after{box-sizing:border-box;}
  #%%ID%% .fhs-header{background:#000;color:#fff;padding:18px 24px 16px;position:relative;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 18px;}
  #%%ID%% .fhs-header::after{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,var(--blue) 0%,var(--blue-soft) 60%,transparent 100%);}
  #%%ID%% .fhs-logo{height:46px;width:auto;display:block;}
  #%%ID%% .fhs-tagline{font-family:var(--font-brand);font-size:17px;letter-spacing:.02em;color:var(--blue);margin:0;}
  #%%ID%% .fhs-updated{font-size:11.5px;opacity:.7;font-family:var(--font-mono);white-space:nowrap;width:100%;text-align:right;}
  #%%ID%% .fhs-header-left{display:flex;align-items:center;gap:12px;}
  #%%ID%% .fhs-filters{display:flex;flex-wrap:wrap;gap:8px;padding:16px 20px 4px;}
  #%%ID%% .fhs-pill{font-family:var(--font-body);font-size:13px;font-weight:600;padding:7px 14px;border-radius:999px;border:1.5px solid var(--maroon);background:transparent;color:var(--maroon);cursor:pointer;transition:background .15s,color .15s;}
  #%%ID%% .fhs-pill:hover{background:rgba(124,2,30,.08);}
  #%%ID%% .fhs-pill[aria-pressed="true"]{background:var(--maroon);color:#fff;}
  #%%ID%% .fhs-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px;padding:16px 20px 22px;}
  #%%ID%% .fhs-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 16px 14px;display:flex;flex-direction:column;gap:10px;}
  #%%ID%% .fhs-card.fhs-hidden{display:none;}
  #%%ID%% .fhs-card-head{display:flex;align-items:flex-start;gap:10px;}
  #%%ID%% .fhs-badge-plate{width:52px;height:52px;flex:none;background:#000;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden;}
  #%%ID%% .fhs-badge-plate img{width:90%;height:90%;object-fit:contain;}
  #%%ID%% .fhs-card-titles{flex:1;min-width:0;}
  #%%ID%% .fhs-sport{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--maroon);font-weight:700;margin:0 0 1px;}
  #%%ID%% .fhs-level{font-size:15px;font-weight:700;margin:0;color:var(--ink);}
  #%%ID%% .fhs-season-yr{font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:2px 0 0;font-family:var(--font-mono);}
  #%%ID%% .fhs-status{font-size:10.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:3px 8px;border-radius:999px;white-space:nowrap;flex:none;background:var(--chalk);color:var(--muted);border:1px solid var(--line);}
  #%%ID%% .fhs-status.is-final{background:#FDEDEF;color:var(--maroon);border-color:#F5C9D1;}
  #%%ID%% .fhs-status.is-pre{background:#E6F9FD;color:#047a93;border-color:#BDEEF8;}
  #%%ID%% .fhs-status.is-live{background:#E8F8EE;color:#1a7a40;border-color:#B8EAC9;}
  #%%ID%% .fhs-record-row{display:flex;align-items:baseline;gap:10px;}
  #%%ID%% .fhs-record{font-family:var(--font-mono);font-size:28px;font-weight:800;color:var(--maroon-deep);line-height:1;}
  #%%ID%% .fhs-pct{font-family:var(--font-mono);font-size:12px;color:var(--muted);}
  #%%ID%% .fhs-strip-label{font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:0;}
  #%%ID%% .fhs-strip{display:flex;gap:4px;flex-wrap:wrap;margin-top:2px;}
  #%%ID%% .fhs-pip{width:13px;height:13px;border-radius:3px;border:1.5px solid var(--maroon);flex:none;}
  #%%ID%% .fhs-pip.is-win{background:var(--blue);border-color:var(--blue);}
  #%%ID%% .fhs-pip.is-loss{background:transparent;}
  #%%ID%% .fhs-pip.is-tie{background:var(--muted);border-color:var(--muted);}
  #%%ID%% .fhs-next{font-size:13px;background:var(--chalk);border-radius:8px;padding:8px 10px;line-height:1.4;margin:0;}
  #%%ID%% .fhs-next strong{color:var(--maroon-deep);}
  #%%ID%% .fhs-note{font-size:13px;color:var(--muted);font-style:italic;line-height:1.4;margin:0;}
  #%%ID%% details.fhs-sched{border-top:1px solid var(--line);padding-top:8px;margin-top:2px;}
  #%%ID%% details.fhs-sched summary{font-size:13px;font-weight:600;color:var(--maroon);cursor:pointer;list-style:none;}
  #%%ID%% details.fhs-sched summary::-webkit-details-marker{display:none;}
  #%%ID%% details.fhs-sched summary::before{content:"\\25B8 ";display:inline-block;transition:transform .15s;}
  #%%ID%% details.fhs-sched[open] summary::before{transform:rotate(90deg);}
  #%%ID%% .fhs-game-list{margin:8px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px;max-height:240px;overflow-y:auto;}
  #%%ID%% .fhs-game-list li{display:flex;justify-content:space-between;gap:8px;font-size:12.5px;padding:4px 2px;border-bottom:1px dashed var(--line);}
  #%%ID%% .fhs-game-date{font-family:var(--font-mono);color:var(--muted);flex:none;width:64px;}
  #%%ID%% .fhs-game-opp{flex:1;}
  #%%ID%% .fhs-game-res{font-family:var(--font-mono);font-weight:700;flex:none;}
  #%%ID%% .fhs-game-res.w{color:#1f8a4c;}
  #%%ID%% .fhs-game-res.l{color:#b3273e;}
  #%%ID%% .fhs-live-embed{min-height:180px;}
  #%%ID%% .fhs-live-cap{font-size:11px;color:var(--muted);text-align:center;margin:0;}
  #%%ID%% .fhs-link{margin-top:auto;font-size:12.5px;font-weight:600;color:var(--maroon);text-decoration:none;border-top:1px solid var(--line);padding-top:8px;}
  #%%ID%% .fhs-link:hover{color:var(--blue);text-decoration:underline;}
  #%%ID%% .fhs-footer{font-size:11.5px;color:var(--muted);text-align:center;padding:4px 20px 18px;line-height:1.6;}
  #%%ID%% .fhs-footer a{color:var(--maroon);text-decoration:none;font-weight:600;}
  #%%ID%% .fhs-footer a:hover{text-decoration:underline;}
"""

JS_ENGINE = r"""
  function localToday(){var d=new Date(),mm=d.getMonth()+1,dd=d.getDate();return d.getFullYear()+'-'+(mm<10?'0':'')+mm+'-'+(dd<10?'0':'')+dd;}
  function daysFromNow(n){var d=new Date();d.setDate(d.getDate()+n);var mm=d.getMonth()+1,dd=d.getDate();return d.getFullYear()+'-'+(mm<10?'0':'')+mm+'-'+(dd<10?'0':'')+dd;}
  function pickSeason(seasons){
    if(!seasons||!seasons.length)return null;
    var today=localToday(),preview=daysFromNow(60),i,s;
    for(i=0;i<seasons.length;i++){s=seasons[i];if(today>=s.startDate&&today<=s.endDate)return s;}
    var soon=seasons.filter(function(s){return s.startDate>today&&s.startDate<=preview;}).sort(function(a,b){return a.startDate<b.startDate?-1:1;});
    if(soon.length)return soon[0];
    var past=seasons.filter(function(s){return s.endDate<today;}).sort(function(a,b){return a.endDate>b.endDate?-1:1;});
    if(past.length)return past[0];
    var future=seasons.filter(function(s){return s.startDate>today;}).sort(function(a,b){return a.startDate<b.startDate?-1:1;});
    return future.length?future[0]:seasons[seasons.length-1];
  }
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
  function fmtDate(iso){var d=new Date(iso+'T12:00:00');return isNaN(d)?iso:d.toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'});}
  function cardHead(team,yr,stTxt,stCls){
    return '<div class="fhs-card-head"><span class="fhs-badge-plate"><img src="'+BADGES[team.icon]+'" alt="'+esc(team.sport)+'"></span>'+
      '<div class="fhs-card-titles"><p class="fhs-sport">'+esc(team.sport)+'</p><h3 class="fhs-level">'+esc(team.level)+'</h3>'+(yr?'<p class="fhs-season-yr">'+esc(yr)+'</p>':'')+
      '</div><span class="fhs-status '+stCls+'">'+stTxt+'</span></div>';
  }
  function buildCard(team){
    var el=document.createElement('article');el.className='fhs-card';el.dataset.sport=team.sport;el.dataset.group=team.level;
    if(team.liveEmbed){
      el.innerHTML=cardHead(team,null,'Live','is-live')+(team.note?'<p class="fhs-note">'+esc(team.note)+'</p>':'')+
        '<div class="fhs-live-embed" id="'+team.liveEmbed.cid+'"></div>'+
        '<p class="fhs-live-cap">Live schedule &amp; scores via GameChanger</p>'+
        '<a class="fhs-link" href="'+esc(team.gcUrl)+'" target="_blank" rel="noopener">View on GameChanger &#x2192;</a>';
      return el;
    }
    var sn=pickSeason(team.seasons);if(!sn)return el;
    var today=localToday();
    var played=sn.games.filter(function(g){return g.res==='W'||g.res==='L'||g.res==='T';});
    var upcoming=sn.games.filter(function(g){return g.res!=='W'&&g.res!=='L'&&g.res!=='T';});
    var next=upcoming.length?upcoming.slice().sort(function(a,b){return a.date<b.date?-1:1;})[0]:null;
    var last=played.length?played.slice().sort(function(a,b){return a.date<b.date?-1:1;})[played.length-1]:null;
    var hasRec=sn.record!=null,w=hasRec?sn.record.w:0,l=hasRec?sn.record.l:0,t=hasRec&&sn.record.t?sn.record.t:0;
    var tot=w+l+t,pct=hasRec&&tot>0?Math.round(((w+0.5*t)/tot)*100):null;
    var stCls,stTxt;
    if(!hasRec){stCls='is-pre';stTxt=sn.startDate>today?'Upcoming':'Pre-Season';}
    else if(next){stCls='is-pre';stTxt='In Season';}else{stCls='is-final';stTxt='Final';}
    var strip='';
    if(played.length){
      var shown=played.slice().sort(function(a,b){return a.date<b.date?-1:1;}).slice(-10);
      strip='<p class="fhs-strip-label">Recent form</p><div class="fhs-strip">'+shown.map(function(g){return'<span class="fhs-pip '+(g.res==='W'?'is-win':g.res==='T'?'is-tie':'is-loss')+'" title="'+(g.res==='W'?'Win':g.res==='T'?'Tie':'Loss')+' vs '+esc(g.opp)+'"></span>';}).join('')+'</div>';
    }
    var mid='';
    if(next){mid='<p class="fhs-next">Next: <strong>'+fmtDate(next.date)+'</strong> '+(next.ha==='home'?'vs ':'@ ')+esc(next.opp)+(next.time&&next.time!=='TBA'?' \u00b7 '+esc(next.time):'')+' </p>';}
    else if(last){mid='<p class="fhs-next">Last: <strong>'+last.res+' '+esc(last.score||'')+'</strong> '+(last.ha==='home'?'vs ':'@ ')+esc(last.opp)+' ('+fmtDate(last.date)+')</p>';}
    else if(sn.note){mid='<p class="fhs-note">'+esc(sn.note)+'</p>';}
    var list='';
    if(sn.games.length){
      var sorted=sn.games.slice().sort(function(a,b){return a.date<b.date?-1:1;});
      list='<details class="fhs-sched"><summary>Schedule &amp; results ('+sorted.length+')</summary><ul class="fhs-game-list">'+
        sorted.map(function(g){var done=g.res==='W'||g.res==='L'||g.res==='T';
          return'<li><span class="fhs-game-date">'+fmtDate(g.date)+'</span><span class="fhs-game-opp">'+(g.ha==='home'?'vs ':'@ ')+esc(g.opp)+'</span><span class="fhs-game-res '+(done?g.res.toLowerCase():'')+'">'+(done?g.res+' '+esc(g.score||''):g.time&&g.time!=='TBA'?esc(g.time):'TBD')+'</span></li>';
        }).join('')+'</ul></details>';
    }
    el.innerHTML=cardHead(team,sn.year,stTxt,stCls)+'<div class="fhs-record-row">'+(hasRec?'<span class="fhs-record">'+w+'\u2013'+l+(t?'\u2013'+t:'')+'</span>'+(pct!=null?'<span class="fhs-pct">'+pct+'% win rate</span>':''):'<span class="fhs-record" style="color:var(--muted)">\u2014</span>')+'</div>'+strip+mid+list+'<a class="fhs-link" href="'+esc(sn.mpUrl)+'" target="_blank" rel="noopener">View on MaxPreps &#x2192;</a>';
    return el;
  }
  function addPill(parent,label,active){var b=document.createElement('button');b.className='fhs-pill';b.type='button';b.textContent=label;b.dataset.sport=label;b.setAttribute('aria-pressed',active?'true':'false');parent.appendChild(b);}
"""

def make_widget(spec, team_js_map, LOGO, BB, BVB, BBSB):
    teams_js="[\n"+",\n".join(team_js_map[tid] for tid in spec["team_ids"] if tid in team_js_map)+"\n  ]"
    badge_map={"basketball":BB,"volleyball":BVB,"baseball":BBSB}
    icons=set(t["icon"] for t in TEAMS if t["id"] in spec["team_ids"])
    b_lines=[f'    {ic}:"data:image/png;base64,{badge_map[ic]}"' for ic in sorted(icons)]
    badges_js="{\n"+",\n".join(b_lines)+"\n  }"
    nav='<nav class="fhs-filters" id="fhs-filters" aria-label="Filter"></nav>\n' if spec["multi"] else ""
    if spec["multi"]:
        render="""  function render(){
    // Show today's date — generated live so caching never makes it stale
    document.getElementById('fhs-stamp').textContent=
      'Updated: '+new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
    var grid=document.getElementById('fhs-grid'),filters=document.getElementById('fhs-filters'),groups=[];
    TEAMS.forEach(function(t){if(groups.indexOf(t.level)===-1)groups.push(t.level);});
    addPill(filters,'All',true);groups.forEach(function(g){addPill(filters,g,false);});
    TEAMS.forEach(function(t){grid.appendChild(buildCard(t));});
    filters.addEventListener('click',function(e){
      var btn=e.target.closest('.fhs-pill');if(!btn)return;
      [].forEach.call(filters.querySelectorAll('.fhs-pill'),function(p){p.setAttribute('aria-pressed','false');});
      btn.setAttribute('aria-pressed','true');var sp=btn.dataset.sport;
      [].forEach.call(grid.querySelectorAll('.fhs-card'),function(c){c.classList.toggle('fhs-hidden',sp!=='All'&&c.dataset.sport!==sp);});
    });
  }"""
    else:
        render="""  function render(){
    document.getElementById('fhs-stamp').textContent=
      'Updated: '+new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
    TEAMS.forEach(function(t){document.getElementById('fhs-grid').appendChild(buildCard(t));});
  }"""
    gc_block=""
    if spec["has_gc"]:
        gc_t=next((t for t in TEAMS if t.get("live_gc")),None)
        if gc_t:
            gc_block=f"""
<script src="https://widgets.gc.com/static/js/sdk.v1.js"></script>
<script>
(function(){{var GC_ID="{gc_t['gc_widget_id']}";if(window.GC&&window.GC.team&&window.GC.team.schedule){{window.GC.team.schedule.init({{target:"#gc-{gc_t['id']}",widgetId:GC_ID,maxVerticalGamesVisible:4}});}}
}})();
</script>"""
    wid=spec["widget_id"]
    css=CSS_TEMPLATE.replace("%%ID%%",wid)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Outliers Athletics</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>body{{margin:0;padding:0;background:transparent;}}\n{css}\n</style>
</head>
<body>
<div id="{wid}" class="fhs-widget">
<header class="fhs-header">
  <div class="fhs-header-left">
    <img class="fhs-logo" alt="Outliers Athletics" src="data:image/png;base64,{LOGO}">
    <p class="fhs-tagline">{spec['tagline']}</p>
  </div>
  <span class="fhs-updated" id="fhs-stamp"></span>
</header>
{nav}<div class="fhs-grid" id="fhs-grid"></div>
<p class="fhs-footer">{spec['footer']}</p>
</div>
<script>
(function(){{
  var TEAMS={teams_js};
  var BADGES={badges_js};
{JS_ENGINE}
{render}
  render();
}})();
</script>{gc_block}
</body>
</html>"""

def main():
    now = datetime.utcnow()
    print(f"Outliers widget update — {date.today()} {now.strftime('%H:%M')} UTC")
    print("="*60)

    LOGO=open(os.path.join(SCRIPTS_DIR,"LOGO.b64")).read().strip()
    BB  =open(os.path.join(SCRIPTS_DIR,"BB.b64")).read().strip()
    BVB =open(os.path.join(SCRIPTS_DIR,"BVB.b64")).read().strip()
    BBSB=open(os.path.join(SCRIPTS_DIR,"BBSB.b64")).read().strip()

    cache={}
    if os.path.exists(CACHE_FILE):
        try: cache=json.load(open(CACHE_FILE))
        except: pass

    team_js_map={}
    new_cache={}

    for team in TEAMS:
        print(f"\n{team['sport']} — {team['level']}")
        if team.get("live_gc"):
            print("  → GameChanger live embed"); scraped=None
        elif not team.get("url"):
            scraped=None
        else:
            print(f"  → fetching ...",end="",flush=True)
            scraped=scrape(team)
            if scraped is None:
                cached=cache.get(team["id"])
                if cached:
                    print(f"  ⚠ using cache from {cached.get('date','?')}")
                    scraped=cached.get("scraped")
                else:
                    print("  ⚠ no cache, using hardcoded history only")
            else:
                new_cache[team["id"]]={"date":str(date.today()),"scraped":scraped}
        team_js_map[team["id"]]=build_team_js(team,scraped)

    merged={**cache,**new_cache}
    with open(CACHE_FILE,"w") as f: json.dump(merged,f,indent=2)

    print("\n"+"="*60+"\nGenerating widget files...")
    for spec in WIDGET_SPECS:
        html=make_widget(spec,team_js_map,LOGO,BB,BVB,BBSB)
        # Write to ROOT_DIR (repo root), not a subfolder
        path=os.path.join(ROOT_DIR,spec["filename"])
        with open(path,"w",encoding="utf-8") as f: f.write(html)
        print(f"  ✓  {spec['filename']}  ({len(html)//1024} KB)")

    # Heartbeat file — always changes, guarantees git has something to commit
    hb=os.path.join(ROOT_DIR,"last_run.txt")
    with open(hb,"w") as f:
        f.write(f"Last run: {date.today()} at {now.strftime('%H:%M')} UTC\n")
    print(f"  ✓  last_run.txt")

    # Index page
    rows="".join(f"<li><a href='{s['filename']}'>{s['tagline'].replace('&amp;','&').replace('\\u2014',chr(8212))}</a></li>" for s in WIDGET_SPECS)
    idx=os.path.join(ROOT_DIR,"index.html")
    with open(idx,"w") as f:
        f.write(f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Outliers Widgets</title>"
                f"<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}}"
                f"a{{color:#7c021e;font-weight:bold}}li{{margin:12px 0}}</style></head>"
                f"<body><h1>Outliers Athletics Widget Directory</h1>"
                f"<p>Embed these URLs in Google Sites via <strong>Insert \u2192 Embed \u2192 By URL</strong></p>"
                f"<ul>{rows}</ul>"
                f"<p style='color:#999;font-size:13px'>Script last ran: {date.today()} {now.strftime('%H:%M')} UTC</p>"
                f"</body></html>")
    print(f"  ✓  index.html\n\nDone ✓")

if __name__=="__main__":
    main()
