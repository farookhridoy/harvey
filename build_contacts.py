import csv, re, sqlite3, urllib.request, ssl
ctx = ssl.create_default_context()
SKIP = ("whatclinic","findoutdoctor","sasthyaseba","practo","doctorbangladesh")
BAD = re.compile(r"sentry|example|wixpress|yourname|\.(png|jpe?g|webp|gif)$", re.I)
db = sqlite3.connect("data/harvey.db")
rows = db.execute("select name,phone,website,location from companies where website like 'http%' or phone!=''").fetchall()
out = []
for name, phone, site, loc in rows:
    emails = set()
    if site and not any(s in site for s in SKIP):
        try:
            html = urllib.request.urlopen(urllib.request.Request(site, headers={"User-Agent": "Mozilla/5.0"}), timeout=8, context=ctx).read().decode("utf-8", "ignore")
            emails = {e.lower() for e in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}", html) if not BAD.search(e)}
        except Exception:
            pass
    if site and any(s in site for s in SKIP): continue
    name = re.split(r"\s[:|\-–]\s|: ", name)[0].replace("Home","").strip(" |-") or name
    out.append([name, phone, site, loc, "; ".join(sorted(emails)), "new"])
out.sort(key=lambda r: (not r[4], not r[1]))
with open("dhaka_dentist_contacts.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["clinic","phone","website","location","public_email","status"]); w.writerows(out)
print(len(out), "rows;", sum(1 for r in out if r[4]), "with email;", sum(1 for r in out if r[1]), "with phone")
