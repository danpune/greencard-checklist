#!/usr/bin/env python3
"""Weekly link check. Exits 1 (GitHub emails the repo owner) when a link in index.html is dead."""
import re, sys, urllib.request, urllib.error

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
links = sorted(set(re.findall(r'href="(https://[^"]+)"', open("index.html", encoding="utf-8").read())))
dead = []
for u in links:
    try:
        urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30)
    except urllib.error.HTTPError as e:
        # ponytail: only 404/410 count as dead. uscis.gov, ssa.gov and others answer 403/5xx to bots.
        if e.code in (404, 410):
            dead.append(f"{e.code} {u}")
    except Exception as e:
        print("skipped (network):", u, e)
print(f"checked {len(links)} links, {len(dead)} dead")
print("\n".join(dead))
sys.exit(1 if dead else 0)
