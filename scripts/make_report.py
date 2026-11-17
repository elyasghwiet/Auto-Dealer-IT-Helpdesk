import json, csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

S = json.load(open("data/ticket_stats.json"))
rows = list(csv.DictReader(open("data/tickets.csv", encoding="utf-8-sig")))
os.makedirs("docs/img", exist_ok=True)
NAVY, BLUE, RED, GREY = "#1F3A5F", "#3B7DD8", "#C0392B", "#8A96A3"

# charts
cats = S["by_category"][::-1]
fig, ax = plt.subplots(figsize=(7, 3.8))
ax.barh([c[0] for c in cats], [c[1] for c in cats], color=BLUE)
for i, c in enumerate(cats): ax.text(c[1] + .08, i, str(c[1]), va="center", fontsize=9)
ax.set_title("Tickets by category - October 2026 (40 simulated)", fontsize=11, loc="left"); ax.set_xlabel("Tickets")
for s in ("top", "right"): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("docs/img/by_category.png", dpi=200); plt.close()

pr = ["Urgent", "High", "Medium", "Low"]
tot = {p: sum(1 for r in rows if r["priority"] == p) for p in pr}
met = {p: sum(1 for r in rows if r["priority"] == p and r["sla_met"] == "Yes") for p in pr}
fig, ax = plt.subplots(figsize=(7, 3.4))
pct = [100 * met[p] / tot[p] for p in pr]
ax.bar(pr, pct, color=[RED if v < 90 else BLUE for v in pct])
ax.axhline(90, color=GREY, ls="--", lw=1); ax.text(3.45, 91, "target 90%", ha="right", fontsize=8, color=GREY)
for i, p in enumerate(pr): ax.text(i, pct[i] + 1.5, "%d/%d" % (met[p], tot[p]), ha="center", fontsize=9)
ax.set_ylim(0, 112); ax.set_ylabel("SLA met (%)"); ax.set_title("SLA compliance by priority", fontsize=11, loc="left")
for s in ("top", "right"): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("docs/img/sla_priority.png", dpi=200); plt.close()

days = {}
for r in rows: days[int(r["opened"][8:10])] = days.get(int(r["opened"][8:10]), 0) + 1
fig, ax = plt.subplots(figsize=(7, 3))
xs = list(range(1, 32)); ax.bar(xs, [days.get(d, 0) for d in xs], color=NAVY)
ax.set_title("Tickets opened per day", fontsize=11, loc="left"); ax.set_xlabel("Day of October"); ax.set_ylabel("Tickets")
for s in ("top", "right"): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("docs/img/per_day.png", dpi=200); plt.close()

# document
d = Document()
for s in d.sections: s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2)
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
def shade(cell, hexcol):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcol); tcPr.append(sh)
def table(header, data, widths):
    t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "1F3A5F")
    for row in data:
        cells = t.add_row().cells
        for i, v in enumerate(row): cells[i].text = str(v)
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    for i, w in enumerate(widths): t.columns[i].width = Cm(w)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs: r.font.size = Pt(9.5)
    d.add_paragraph()
def H(t, l=1): d.add_heading(t, level=l)
def P(t): return d.add_paragraph(t)

d.add_heading("Monthly Helpdesk Report - October 2026", 0)
P("Organisation: EV fleet operator, Ahmedabad (fictional, 80 employees)\nPrepared by: Elyas Ghwiet, IT Helpdesk (training project)\nTool: GLPI service desk")
p = P("Important: this is a training project. The 40 tickets are simulated. Times were modelled to follow the rules a real helpdesk would use, not measured on real users. Figures below are computed from the ticket log (Ticket_Log.xlsx).")
p.runs[0].italic = True

H("1. Summary")
P("In October the helpdesk handled %d tickets. %d of %d met their full SLA (first response and resolution), which is %.1f%% and above the 90%% target. First-response compliance was %.1f%% and resolution compliance %.1f%%. The average first response was %.0f minutes and the average resolution time was %.1f hours."
  % (S["tickets"], S["sla_met"], S["tickets"], S["sla_pct"], S["tto_met_pct"], S["ttr_met_pct"], S["avg_first_response_min"], S["avg_resolution_h"]))
P("Three tickets breached the SLA (T-007, T-021, T-037). One of them is the phishing incident, an Urgent ticket, so Urgent compliance is 2 of 3. With only three Urgent tickets, one miss moves that number a lot, so read it as a pointer to look at the case, not as a trend.")
table(["Measure", "Result", "Target"], [
    ["Tickets handled", S["tickets"], "-"],
    ["SLA met (both parts)", "%.1f%% (%d/%d)" % (S["sla_pct"], S["sla_met"], S["tickets"]), "90% or more"],
    ["First response SLA", "%.1f%%" % S["tto_met_pct"], "90% or more"],
    ["Resolution SLA", "%.1f%%" % S["ttr_met_pct"], "90% or more"],
    ["Average first response", "%.0f min" % S["avg_first_response_min"], "-"],
    ["Average resolution", "%.1f h" % S["avg_resolution_h"], "-"]], [7, 5, 4])

H("2. Ticket volume")
d.add_picture("docs/img/per_day.png", width=Cm(14))
P("Tickets are spread evenly across the week (6 per day on most days, 4 on Wednesday), so the simulation shows no weekday peak. In a real month, check this chart for peaks before changing the shift plan.")

H("3. Top categories")
d.add_picture("docs/img/by_category.png", width=Cm(14))
P("Accounts and Access, Network and VPN, and Hardware are tied at 6 tickets each (15% each), together 45% of the month. Accounts and Access is the easiest to reduce, because most of those tickets are forgotten passwords and locked accounts that the knowledge-base articles KB-01 and KB-02 already explain.")
tot_c = S["tickets"]
table(["Category", "Tickets", "Share"], [[c, n, "%.1f%%" % (100 * n / tot_c)] for c, n in S["by_category"]], [8, 3, 3])

H("4. SLA compliance")
d.add_picture("docs/img/sla_priority.png", width=Cm(13))
table(["Priority", "Tickets", "SLA met", "First response target", "Resolution target"], [
    ["Urgent", tot["Urgent"], "%d (%.0f%%)" % (met["Urgent"], 100 * met["Urgent"] / tot["Urgent"]), "15 min", "4 h"],
    ["High", tot["High"], "%d (%.0f%%)" % (met["High"], 100 * met["High"] / tot["High"]), "30 min", "8 h"],
    ["Medium", tot["Medium"], "%d (%.0f%%)" % (met["Medium"], 100 * met["Medium"] / tot["Medium"]), "2 h", "24 h"],
    ["Low", tot["Low"], "%d (%.0f%%)" % (met["Low"], 100 * met["Low"] / tot["Low"]), "4 h", "72 h"]], [2.5, 2.2, 3, 4.3, 4])
P("Clock rule used: the SLA clock runs 24/7 in this simulation (calendar 24/7), so nights and weekends count. A real operator with a night shift would likely use a business-hours calendar for Low and Medium tickets.")

H("5. Breached tickets and what we learned")
table(["Ticket", "Priority", "Target", "Actual", "Why it was missed", "Action"], [
    ["T-007", "Urgent", "4 h", "4.6 h", "Phishing click: account was secured within the hour, but the full investigation (mail trace, other recipients) took longer.", "Split into two steps: containment (target 1 h) and investigation. Report the clock on containment."],
    ["T-021", "High", "8 h", "9.2 h", "A faulty switch port had to be found; the user was away from the desk for part of the time.", "Keep a spare, tested patch cable and port map in the asset sheet."],
    ["T-037", "Medium", "TTO 2 h / TTR 24 h", "150 min / 27 h", "Ticket sat in the Service Desk queue behind urgent work, then needed a profile rebuild.", "Review the queue at midday; add a KB article for calendar sync."]], [1.5, 1.7, 2.2, 2, 5, 4.4])

H("6. How competing urgent tickets are prioritised")
P("When two tickets need attention at the same time, the helpdesk decides in this order:")
for t in ["1. Safety and security first. A security incident (for example a clicked phishing link) is handled before anything else, because the damage grows with time.",
          "2. Number of people affected. A whole-office outage comes before a problem for one user.",
          "3. Business impact. A broken charging dashboard (vehicles cannot be dispatched) comes before a printer problem.",
          "4. Priority level and SLA clock. If everything above is equal, the ticket closest to missing its SLA goes first.",
          "5. Quick wins. A 10-minute fix (for example a locked account before a shift) is done in between, so it does not wait hours."]:
    P(t)
P("Priority is set as Impact x Urgency (the GLPI priority matrix). The automatic rules in GLPI set the category, the group, and the priority, so a technician does not have to decide this under pressure.")
P("Examples from the October log (the tickets were handled by different groups, so these show the order of attention, not a shortage of staff):")
table(["Day", "Ticket A", "Ticket B", "Decision"], [
    ["4 Oct", "T-007 Urgent, phishing click, 08:15", "T-008 Medium, locked account, 10:50", "A first (security). B is a 10-minute fix, done by the Service Desk in parallel."],
    ["5 Oct", "T-009 Medium, onboarding 2 dispatchers, 09:00", "T-010 Urgent, charging dashboard down, 14:25", "B immediately. Onboarding resumes afterwards; its 24 h target leaves room."],
    ["9 Oct", "T-017 Urgent, office internet down, 08:30", "T-018 Medium, scanner blank pages, 10:40", "A first (whole office affected). B waits and is solved in 1.4 h."]], [1.6, 5, 5, 5.2])

H("7. Deflection estimate (stretch goal)")
P("Ticket categories that have a knowledge-base article can be reduced if people find the answer before opening a ticket. The estimate below is an assumption, not a measurement: it counts tickets in the log whose topic is covered by a KB article and assumes that a share of those users would solve it alone from the self-service portal.")
kb_cats = {"Accounts and Access", "Printers and Scanners", "Email"}
cov = sum(1 for r in rows if r["category"] in kb_cats)
P("Tickets in categories with KB coverage (Accounts and Access, Printers and Scanners, Email): %d of %d (%.0f%%). If 30%% of these were solved through the portal, about %d tickets per month would be avoided. How to measure it in practice: count KB article views that are not followed by a ticket from the same user within 24 hours."
  % (cov, S["tickets"], 100 * cov / S["tickets"], round(0.3 * cov)))

H("8. Time saved by automation")
P("The onboarding script (New-EmployeeOnboarding.ps1) uses an assumption of 12 minutes of manual work per new account; the script reports the time saved after each run. For the 5 sample hires this is 60 minutes manually against a few seconds of script time. The disk-cleanup script (disk_cleanup.sh) reports disk space before and after each run. These measurements come from the screenshots captured when running the scripts; the 12-minute figure is an assumption and should be replaced by a measured value.")

H("9. Recommendations")
for t in ["Publish the 18 KB articles in the GLPI self-service portal, starting with KB-01, KB-02 and KB-03.",
          "Split security incidents into containment and investigation so the SLA measures what the user feels.",
          "Review the Service Desk queue at midday to prevent Medium tickets from ageing.",
          "Keep the asset sheet current: it flags laptops whose warranty ends within 180 days, so renewals can be planned (see Asset_Inventory.xlsx)."]:
    d.add_paragraph(t, style="List Bullet")
d.save("docs/Monthly_Helpdesk_Report_October_2026.docx")
print("ok")
