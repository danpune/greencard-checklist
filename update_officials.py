#!/usr/bin/env python3
"""Build officials.json: the civics answers that depend on who holds office and where you live.

Sources, all read fresh on every run (stdlib only; run daily by .github/workflows/news.yml):
  senators         senate.gov member list (official)
  representatives  clerk.house.gov member list (official)
  governors        nga.org, National Governors Association
  federal names    uscis.gov/citizenship/testupdates (the answers USCIS itself accepts)
A source that fails, or returns an implausible count, keeps its previous data and fails the run.
"""
import html, json, re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
STATES = {  # postal code: (name, capital)
 "AL": ("Alabama", "Montgomery"), "AK": ("Alaska", "Juneau"), "AZ": ("Arizona", "Phoenix"), "AR": ("Arkansas", "Little Rock"),
 "CA": ("California", "Sacramento"), "CO": ("Colorado", "Denver"), "CT": ("Connecticut", "Hartford"), "DE": ("Delaware", "Dover"),
 "FL": ("Florida", "Tallahassee"), "GA": ("Georgia", "Atlanta"), "HI": ("Hawaii", "Honolulu"), "ID": ("Idaho", "Boise"),
 "IL": ("Illinois", "Springfield"), "IN": ("Indiana", "Indianapolis"), "IA": ("Iowa", "Des Moines"), "KS": ("Kansas", "Topeka"),
 "KY": ("Kentucky", "Frankfort"), "LA": ("Louisiana", "Baton Rouge"), "ME": ("Maine", "Augusta"), "MD": ("Maryland", "Annapolis"),
 "MA": ("Massachusetts", "Boston"), "MI": ("Michigan", "Lansing"), "MN": ("Minnesota", "Saint Paul"), "MS": ("Mississippi", "Jackson"),
 "MO": ("Missouri", "Jefferson City"), "MT": ("Montana", "Helena"), "NE": ("Nebraska", "Lincoln"), "NV": ("Nevada", "Carson City"),
 "NH": ("New Hampshire", "Concord"), "NJ": ("New Jersey", "Trenton"), "NM": ("New Mexico", "Santa Fe"), "NY": ("New York", "Albany"),
 "NC": ("North Carolina", "Raleigh"), "ND": ("North Dakota", "Bismarck"), "OH": ("Ohio", "Columbus"), "OK": ("Oklahoma", "Oklahoma City"),
 "OR": ("Oregon", "Salem"), "PA": ("Pennsylvania", "Harrisburg"), "RI": ("Rhode Island", "Providence"), "SC": ("South Carolina", "Columbia"),
 "SD": ("South Dakota", "Pierre"), "TN": ("Tennessee", "Nashville"), "TX": ("Texas", "Austin"), "UT": ("Utah", "Salt Lake City"),
 "VT": ("Vermont", "Montpelier"), "VA": ("Virginia", "Richmond"), "WA": ("Washington", "Olympia"), "WV": ("West Virginia", "Charleston"),
 "WI": ("Wisconsin", "Madison"), "WY": ("Wyoming", "Cheyenne"),
 "DC": ("District of Columbia", None), "PR": ("Puerto Rico", "San Juan"), "GU": ("Guam", "Hagåtña"),
 "VI": ("U.S. Virgin Islands", "Charlotte Amalie"), "AS": ("American Samoa", "Pago Pago"), "MP": ("Northern Mariana Islands", "Saipan"),
}
BY_NAME = {name.lower(): code for code, (name, _) in STATES.items()}
BY_NAME.update({"virgin islands": "VI", "commonwealth of the northern mariana islands": "MP"})

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
        return r.read()

def clean(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s or "")).split())

def senators():
    out = {}
    for m in ET.fromstring(get("https://www.senate.gov/general/contact_information/senators_cfm.xml")).iter("member"):
        first, _, suffix = clean(m.findtext("first_name")).partition(", ")   # "Angus S., Jr." + "King" -> "Angus S. King, Jr."
        last = clean(m.findtext("last_name"))
        assert first and last, "a senator without a name"
        out.setdefault(m.findtext("state").strip(), []).append(first + " " + last + (", " + suffix if suffix else ""))
    # a seat can be empty for a while, so a state may have one senator; never none, never three
    assert len(out) == 50 and all(1 <= len(v) <= 2 for v in out.values()) and sum(map(len, out.values())) >= 95, "expected 50 states with 1 or 2 senators each, 95 or more in all"
    return {k: sorted(v) for k, v in out.items()}

CONGRESS = []  # the number of the Congress the House list is for; the page compares it with the one in zipcd.json

def representatives():
    out, named = {}, 0
    root = ET.fromstring(get("https://clerk.house.gov/xml/lists/MemberData.xml"))
    for m in root.iter("member"):
        # the statedistrict prefix is not always the postal code (American Samoa is "AQ"), so read the postal code itself
        state = m.find("member-info/state")
        code = state.get("postal-code") if state is not None and state.get("postal-code") else m.findtext("statedistrict").strip()[:2]
        name = clean(m.findtext("member-info/official-name"))
        named += bool(name)
        out.setdefault(code, []).append([clean(m.findtext("member-info/district")) or "At Large", name or "Vacant"])
    assert named >= 425 and sum(map(len, out.values())) == 441 and sorted(out) == sorted(STATES), "expected 441 House seats for exactly the 56 states and territories"
    CONGRESS.append(int(root.findtext("title-info/congress-num")))
    key = lambda d: (0, int(re.sub(r"\D", "", d[0]))) if re.search(r"\d", d[0]) else (1, 0)
    return {k: sorted(v, key=key) for k, v in out.items()}

def governors():
    page = get("https://www.nga.org/governors/").decode("utf-8", "replace")
    out = {}
    for state, name in re.findall(r'<small class="state">([^<]+)</small>\s*Gov\.\s*([^<]+?)\s*</div>', page):
        code = BY_NAME.get(clean(state).lower())
        if code:
            out[code] = clean(name)
    assert sorted(out) == sorted(c for c in STATES if c != "DC"), "expected 50 state and 5 territory governors"
    return out

def federal():
    page = get("https://www.uscis.gov/citizenship/testupdates").decode("utf-8", "replace")
    page = page[page.index("Civics Test (2025 Naturalization Civics Test) Updates"):]
    out = {}
    for num, answers in re.findall(r"<p>(?:\s|<[^>]+>)*(\d+)\..*?</p>\s*<ul>(.*?)</ul>", page, re.S):
        names = [clean(a) for a in re.findall(r"<li>(.*?)</li>", answers, re.S)]
        if names and not names[0].lower().startswith("answers will vary"):
            out[num] = names
    assert set(out) == {"30", "38", "39", "57"}, "expected the four named-official questions, got %s" % sorted(out)
    return out

try:
    old = json.load(open("officials.json", encoding="utf-8"))
except (OSError, ValueError):
    old = {}
parts, failed = {}, []
for name, fn in (("senators", senators), ("reps", representatives), ("governors", governors), ("federal", federal)):
    try:
        parts[name] = fn()
    except Exception as e:  # one source down must not wipe the others
        failed.append("%s: %s" % (name, e))
        if name not in old.get("parts", {}):
            sys.exit("no previous data to fall back on. " + "; ".join(failed))
        parts[name] = old["parts"][name]
print("failed:", failed or "none")

new = {"changed": datetime.now(timezone(timedelta(hours=-11))).strftime("%Y-%m-%d"),   # UTC-11: never a future date for any U.S. visitor
       "congress": CONGRESS[0] if CONGRESS else old.get("congress"),
       "sources": ["senate.gov", "clerk.house.gov", "nga.org", "uscis.gov/citizenship/testupdates"],
       "states": {c: {"name": n, "capital": cap} for c, (n, cap) in STATES.items()},
       "parts": parts}
if old.get("parts") == parts and old.get("states") == new["states"] and old.get("congress") == new["congress"]:
    new["changed"] = old["changed"]  # no churn commits when nothing changed
json.dump(new, open("officials.json", "w", encoding="utf-8"), indent=0, ensure_ascii=False, sort_keys=True)
print("officials.json: %d senators, %d House seats, %d governors, federal %s, changed %s" % (
    sum(len(v) for v in parts["senators"].values()), sum(len(v) for v in parts["reps"].values()),
    len(parts["governors"]), sorted(parts["federal"]), new["changed"]))
if failed:
    sys.exit("kept the previous data for: " + "; ".join(failed))   # turns the run red, so GitHub emails the owner
