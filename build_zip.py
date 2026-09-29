#!/usr/bin/env python3
"""Build zip.json (ZIP code -> state) and zipcd.json (ZIP code -> congressional districts) from U.S. Census files.

Run by hand after each redistricting, next in January 2027 for the 120th Congress: change CD below, then
  python3 build_zip.py
Stdlib only. Downloads two Census files (about 13 MB) into the system temp folder. Needs officials.json.

zip.json    p3: first 3 digits -> state, the state most ZIP codes with that prefix lie in.
            z5: the few ZIP codes that lie wholly outside their prefix's state.
            x:  the ZIP codes that cross a state line, as one string. They keep their postal (prefix) state,
                and the page tells people to choose the other state if they live there.
zipcd.json  p[first 3 digits] = [default, {last 2 digits: districts}, "last 2 digits of every ZIP code on the default"]
            Districts are those of the ZIP code's own state, largest land share first. Every district that holds
            some of the ZIP code's land is kept, however small: house.gov also counts those as shared ZIP codes.
            A ZIP code in neither list is not in the Census table (a PO box, for example): the page then lists every district.
"""
import collections, json, os, tempfile, urllib.request

CD = "119"
CENSUS = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/"
FILES = {"county": CENSUS + "zcta520/tab20_zcta520_county20_natl.txt",
         "cd": CENSUS + "cd-sld/tab20_cd%s20_zcta520_natl.txt" % CD}
FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC", "12": "FL",
        "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
        "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
        "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
        "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
        "56": "WY", "60": "AS", "66": "GU", "69": "MP", "72": "PR", "78": "VI"}

def rows(key):
    path = os.path.join(tempfile.gettempdir(), FILES[key].rsplit("/", 1)[1])
    if not os.path.exists(path):
        urllib.request.urlretrieve(FILES[key], path)
    lines = open(path, encoding="utf-8-sig").read().splitlines()
    head = [h.replace("CD%s" % CD, "CD") for h in lines[0].split("|")]
    return [dict(zip(head, l.split("|"))) for l in lines[1:]]

# ---- zip.json ----
land = collections.defaultdict(collections.Counter)   # ZIP code -> land by state
for r in rows("county"):
    if r["GEOID_ZCTA5_20"]:
        land[r["GEOID_ZCTA5_20"]][FIPS[r["GEOID_COUNTY_20"][:2]]] += int(r["AREALAND_PART"])
by = collections.defaultdict(collections.Counter)
for z, c in land.items():
    by[z[:3]][c.most_common(1)[0][0]] += 1
p3 = {k: c.most_common(1)[0][0] for k, c in by.items()}
z5 = {z: c.most_common(1)[0][0] for z, c in sorted(land.items()) if p3[z[:3]] not in c}
def state(z):
    return z5.get(z) or p3.get(z[:3])
cross = ",".join(z for z, c in sorted(land.items()) if sum(1 for v in c.values() if v > 0) > 1)

# ---- zipcd.json ----
reps = json.load(open("officials.json", encoding="utf-8"))["parts"]["reps"]
single = {s for s, v in reps.items() if len(v) == 1}   # one seat: nothing to look up
cd = collections.defaultdict(collections.Counter)      # ZIP code -> land by district, own state only
for r in rows("cd"):
    z, g = r["GEOID_ZCTA5_20"], r["GEOID_CD_20"]
    if z and g[2:] != "ZZ" and FIPS[g[:2]] == state(z) and FIPS[g[:2]] not in single:
        cd[z][int(g[2:])] += int(r["AREALAND_PART"] or 0)
val = {z: ",".join(str(d) for d, v in c.most_common() if v > 0 or len(c) == 1) for z, c in cd.items()}
assert all(val.values())
by = collections.defaultdict(dict)
for z, v in val.items():
    by[z[:3]][z[3:]] = v
p = {}
for k, d in by.items():
    default = collections.Counter(d.values()).most_common(1)[0][0]
    p[k] = [default, {s: v for s, v in d.items() if v != default}, "".join(sorted(s for s, v in d.items() if v == default))]

# ---- self-check: the lookup the page does must give back the Census answer ----
def districts(z):
    e = p.get(z[:3])
    return e and (e[1].get(z[3:]) or (e[0] if z[3:] in [e[2][i:i + 2] for i in range(0, len(e[2]), 2)] else None))
assert all(districts(z) == v for z, v in val.items())
assert all(set(map(int, v.split(","))) <= {int(g) for g in c} for z, v in val.items() for c in [cd[z]])
if CD == "119":
    assert (state("10001"), districts("10001")) == ("NY", "12")
    assert (state("82930"), state("42223"), state("06390")) == ("WY", "KY", "NY")   # border ZIP codes
    assert districts("99362") == "5" and districts("86515") == "2"                  # no neighbouring state's district
    assert districts("77001") is None and districts("82001") is None               # PO box; one-seat state
    assert districts("77038") == "29,18" and "82930" in cross and "10001" not in cross
# written only now, after the checks above have passed
json.dump({"source": "U.S. Census Bureau, 2020 ZCTA to county relationship file", "p3": p3, "z5": z5, "x": cross},
          open("zip.json", "w"), separators=(",", ":"), sort_keys=True)
json.dump({"source": "U.S. Census Bureau, %sth Congressional District to 2020 ZCTA relationship file" % CD, "congress": int(CD), "p": p},
          open("zipcd.json", "w"), separators=(",", ":"), sort_keys=True)
print("zip.json: %d prefixes, %d exceptions, %d cross a state line. zipcd.json: %d ZIP codes in %d prefixes, %d in one district" % (
    len(p3), len(z5), cross.count(",") + 1, len(val), len(p), sum("," not in v for v in val.values())))
