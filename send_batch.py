import asyncio, csv, os, sys, time
from harvey.config import load_config, load_env
from harvey.integrations.smtp_mail import SmtpImapProvider
FIX = {"Home - Dental Home BD":"Dental Home BD","Intruducing Our Uttara Branch":"Farazy Dental Hospital",
 "Dhanmondi Dental Center:Best dental clinic in bangladesh ...":"Dhanmondi Dental Center",
 "Gulshan Dental Care — Premium Dental Clinic in Dhaka ...":"Gulshan Dental Care"}
SKIP = {"info@ibnsinatrust.com"}
LOG = "sent_log.csv"
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
sent = {r[0] for r in csv.reader(open(LOG))} if os.path.exists(LOG) else set()
items = []
for blk in open("email_drafts.txt").read().split("\n=====\n"):
    head, body = blk.split("\n\n", 1)
    to = head.split("To: ",1)[1].split("\n")[0].strip()
    subj = head.split("Subject: ",1)[1].strip()
    for k, v in FIX.items(): subj = subj.replace(k, v); body = body.replace(k, v)
    if to not in sent and to not in SKIP: items.append((to, subj, body))
p = SmtpImapProvider(load_config(), load_env())
n = 0
for to, subj, body in items[:limit]:
    r = asyncio.run(p.send_email(to, subj, body))
    print(to, "OK" if r.ok else f"FAIL {r.error}")
    if r.ok:
        csv.writer(open(LOG, "a", newline="")).writerow([to, subj, time.strftime("%Y-%m-%d %H:%M")]); n += 1
    time.sleep(90)
print(f"sent {n}; remaining {max(len(items)-n,0)}")
