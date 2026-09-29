#!/usr/bin/env python3
"""Weekly link check. Exits 1 (GitHub emails the repo owner) when a link in index.html or civics.html is dead."""
import re, socket, sys, urllib.request, urllib.error

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
html = "".join(open(f, encoding="utf-8").read() for f in ("index.html", "civics.html"))
links = sorted(set(re.findall(r'href="(https://[^"]+)"', html)))
dead, unsure = [], []
for u in links:
    try:
        urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).close()
    except urllib.error.HTTPError as e:
        # ponytail: only 404/410 count as dead. ssa.gov and others answer 403 to bots, even for a missing page.
        (dead if e.code in (404, 410) else unsure).append(f"{e.code} {u}")
    except Exception as e:
        # A host name that no longer exists is dead. Timeouts and other network errors are not.
        gone = isinstance(getattr(e, "reason", None), socket.gaierror) and e.reason.errno == socket.EAI_NONAME
        (dead if gone else unsure).append(f"{'no such website' if gone else e} {u}")
print(f"{len(links)} links: {len(links) - len(dead) - len(unsure)} ok, {len(dead)} dead, {len(unsure)} could not be checked")
print("\n".join(["DEAD " + d for d in dead] + ["NOT CHECKED " + u for u in unsure]))
sys.exit(1 if dead else 0)
