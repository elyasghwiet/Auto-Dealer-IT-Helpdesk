import json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

S = json.load(open("data/ticket_stats.json"))
d = Document()
for s in d.sections: s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2)
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
fig = [0]
def shade(cell, col):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), col); tcPr.append(sh)
def H(t, l=1): d.add_heading(t, level=l)
def P(t, bold=False, italic=False):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold; r.italic = italic; return p
def B(items):
    for t in items: d.add_paragraph(t, style="List Bullet")
def F(path, cap, w=15.5):
    fig[0] += 1
    d.add_picture("screenshots/" + path, width=Cm(w)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c = d.add_paragraph("Figure %d. %s" % (fig[0], cap)); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.runs[0].italic = True; c.runs[0].font.size = Pt(9)
def T(header, rows, widths):
    t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255); shade(c, "1F3A5F")
    for row in rows:
        cs = t.add_row().cells
        for i, v in enumerate(row): cs[i].text = str(v)
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Cm(w)
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs: r.font.size = Pt(9.5)
    for i, w in enumerate(widths): t.columns[i].width = Cm(w)
    d.add_paragraph()

d.add_heading("Auto Dealer IT Helpdesk Setup", 0)
P("Week 4 project report - GLPI service desk for a fictional EV fleet operator", bold=True)
P("Author: Elyas Ghwiet | Programme: Yuva virtual internship (IT support) | November 2026")
P("Scenario: a fictional electric-vehicle fleet operator in Ahmedabad with 80 employees. All people, devices, serial numbers and ticket data are simulated for training. Where something was measured on my own machine, the report says so; where something is an estimate or was not completed, the report says that too (section 10).", italic=True)

H("1. Summary")
P("I installed and configured the open-source GLPI service desk in a local Docker environment, built the ITIL category structure, three support groups and technician accounts, automatic ticket routing rules, eight service levels (time to own and time to resolve) with rules that apply them by priority, and a mailbox receiver for email-to-ticket. I wrote 18 knowledge-base articles, a log of 40 simulated tickets with troubleshooting steps (Windows, Linux and network), two automation scripts (Bash disk cleanup and PowerShell onboarding), an asset inventory workbook and a monthly helpdesk report.")
T(["Deliverable", "Status", "Evidence"], [
  ["GLPI installed, categories, groups, technicians", "Done", "Figures 1-3"],
  ["Auto-assignment rules", "Done and tested", "Figure 4"],
  ["SLA / TTO / TTR by priority", "Done and tested on a live ticket", "Figures 5-8"],
  ["Email-to-ticket", "Configured; live mailbox test not completed", "Figures 11-12, section 10"],
  ["Knowledge base (15+ articles)", "18 written; 5 loaded in GLPI", "Figure 13, Knowledge_Base_18_Articles.docx"],
  ["40 simulated tickets with troubleshooting", "40 in the log; 8 entered in GLPI", "Figures 9-10, Ticket_Log.xlsx"],
  ["Two scripts (PowerShell, Bash)", "Done; run in simulation / dry-run mode", "Figures 14-16"],
  ["Asset inventory sheet", "Done (30 laptops, 7 licence lines)", "Asset_Inventory.xlsx"],
  ["Monthly helpdesk report", "Done (simulated October 2026)", "Monthly_Helpdesk_Report_October_2026.docx"],
  ["Stretch: self-service portal", "Not built; deflection estimated only", "Section 8"]], [6, 5, 5.2])

H("2. Environment")
P("GLPI runs in Docker Desktop on Windows with WSL2 (Ubuntu), using two containers: the GLPI web application and MariaDB 10.11. Project files live in the Ubuntu home folder and are started with a small script that also takes a database backup. This setup is for training; a production helpdesk would run on a dedicated server with scheduled backups.")

H("3. Categories, groups and technicians")
P("Ten ITIL categories cover the problems an 80-person fleet operator sees: Accounts and Access, Email, Network and VPN, Hardware (Laptops and Desktops), Printers and Scanners, Software and Licences, Security Incident, Fleet and Charging Software, New Joiner / Leaver, and Other. The fleet-specific category exists because dispatchers depend on the charging dashboard.")
F("01_itil_categories.png", "The ten ITIL categories.")
P("Three support groups reflect a simple two-level model: Service Desk L1 handles everyday requests, Infrastructure and Network L2 handles network and security issues, and Fleet Applications Support owns the charging and fleet software. Each group has one technician account.")
F("02_groups.png", "Support groups.")
F("03_users.png", "Technician accounts (one per group) and the default GLPI accounts.")

H("4. Automatic assignment")
P("Business rules for tickets assign the group automatically from the category. The order matters: a default rule matches every category and sends the ticket to Service Desk L1; the specific rules come after it and override it for Network and VPN, Security Incident, and Fleet and Charging Software. In my first attempt a rule without criteria did not match anything, so the default rule uses the regular expression /.*/ on the category. I checked the behaviour with the GLPI rules engine test and with real tickets.")
F("04_rules_routing_and_sla.png", "Routing rules (ranks 3-6) and the first SLA rules (ranks 7-8).", 14.5)

H("5. Priorities and SLAs")
T(["Priority", "Time to own (first response)", "Time to resolve"], [
  ["Urgent (Very high)", "15 minutes", "4 hours"], ["High", "30 minutes", "8 hours"],
  ["Medium", "2 hours", "24 hours"], ["Low", "4 hours", "72 hours"]], [5, 6, 5])
P("The targets are my own choices for this scenario. They follow the usual helpdesk logic that a whole-office outage must be acknowledged within minutes while a printer fault can wait. The service-level calendar is empty, which in GLPI means 24/7; a real operator might use business hours for Low and Medium tickets. One GLPI detail cost me time: a Service level is only a container, and the actual SLA with the time and type (own or resolve) is created inside it on the SLA tab. Four empty containers from my first attempt remain in the list and are not used.")
F("06_service_levels.png", "Service levels: four unused first-attempt entries and the eight in use.")
P("Four rules apply the right SLA by priority:")
F("05_rules_sla_medium_low.png", "SLA rules for Medium and Low priority (ranks 9-10).", 13.5)
P("Live test: I opened an Urgent ticket for an office-wide internet outage at 14:43:54. GLPI set the time to own to 14:58 (15 minutes) and the time to resolve to 18:43 (4 hours) automatically.")
F("07_urgent_ticket.png", "Urgent test ticket: category Network and VPN, status Processing (assigned).", 13.5)
F("08_urgent_ticket_sla.png", "The same ticket: TTO Urgent 15 min and TTR Urgent 4 h applied by the rule.", 13.5)

H("6. Tickets")
P("The full log has 40 simulated tickets for October 2026 across Windows (32), Linux (4) and network (4) problems, each with category, priority, symptom, troubleshooting steps and resolution (Ticket_Log.xlsx). I entered eight representative ones into GLPI. All eight were categorised as intended, and the resolve-by dates match the priority.")
T(["Log ID", "Title", "Category", "Priority"], [
  ["T-003", "VPN client fails with 'connection timed out'", "Network and VPN", "High"],
  ["T-004", "Laptop very slow after startup", "Hardware", "Medium"],
  ["T-007", "Phishing e-mail clicked", "Security Incident", "Urgent"],
  ["T-008", "Account locked after wrong passwords", "Accounts and Access", "Medium"],
  ["T-010", "Charging dashboard not loading", "Fleet and Charging Software", "Urgent"],
  ["T-013", "Ubuntu server cannot resolve hostnames", "Network and VPN", "Medium"],
  ["T-017", "Internet down in the whole office", "Network and VPN", "Urgent"],
  ["T-025", "Printout has black lines", "Printers and Scanners", "Low"]], [2, 7.5, 4.5, 2.2])
F("09_ticket_list_a.png", "Tickets in GLPI (1 of 2).")
F("10_ticket_list_b.png", "Tickets in GLPI (2 of 2).")
P("Example troubleshooting (T-003, VPN): confirm the user has internet (ping 8.8.8.8); try another network - the VPN connected on a mobile hotspot, so the home router blocked the VPN port; change the VPN profile to TCP 443. Example (T-013, Linux): ping 8.8.8.8 works but ping google.com does not; resolvectl status showed no DNS server; add the DNS servers in netplan and apply them.")

H("7. How competing urgent tickets are prioritised")
B(["Safety and security first: a clicked phishing link is handled before anything else because damage grows with time.",
   "Number of people affected: a whole-office outage comes before a single-user problem.",
   "Business impact: a broken charging dashboard (vehicles cannot be dispatched) comes before a printer fault.",
   "Priority level and SLA clock: when everything else is equal, the ticket closest to breaching its SLA goes first.",
   "Quick wins: a ten-minute fix, such as a locked account before a shift, is done in between."])
P("Examples from the log: on 4 October T-007 (phishing, Urgent) was handled before T-008 (locked account, Medium); on 9 October T-017 (office internet down, Urgent) before T-018 (scanner, Medium). Priority itself is set from urgency and impact, and the GLPI rules apply the group and SLA so that nobody has to decide this under pressure.")

H("8. Knowledge base, email-to-ticket and deflection")
P("The 18 articles are written in plain language for employees and support staff, each with the problem, step-by-step fix, what to do if it still fails, prevention, and the ticket category to use. They cover password reset, locked accounts, VPN, company mail, Wi-Fi, suspicious links, software requests, large files, MFA codes, shared access, printers, Windows Update, Linux DNS and disk space, Teams devices and the charging dashboard. Five were loaded into the GLPI knowledge base for the screenshot below; the rest are in the project repository.")
F("13_knowledge_base.png", "GLPI knowledge base with the first articles loaded.", 14.5)
P("Email-to-ticket: I configured a mailbox receiver (IMAP over SSL, imap.gmail.com, port 993). The connection failed at login because Gmail requires an app password, and I decided not to spend the remaining time on that. I therefore created a ticket manually with an email-style message to show the intended result. A working live test is listed as future work.")
F("11_mail_receiver.png", "Mailbox receiver configuration.", 14.5)
F("12_email_style_ticket.png", "Ticket created manually to represent an incoming email (not received by the collector).", 14.5)
P("Deflection (stretch goal): 14 of the 40 tickets (35%) fall in categories that have knowledge-base articles (accounts, printers, email). If 30% of those were solved by the employee from the articles, about 4 tickets per month would not be opened. This is an assumption, not a measurement. A real measurement would count article views that are not followed by a ticket from the same user within 24 hours. I did not build the self-service portal.")

H("9. Automation scripts")
P("disk_cleanup.sh (Bash) removes old files from temporary and cache folders safely: dry run is the default, only regular files are touched, it never crosses filesystems, a list of forbidden directories (for example /, /etc, /home) is refused, and every run is logged with disk usage before and after. PowerShell New-EmployeeOnboarding.ps1 reads a CSV of new hires, builds usernames and temporary passwords, assigns department groups, supports -WhatIf, and prints the time saved.")
F("14_disk_cleanup_dryrun.png", "disk_cleanup.sh in dry-run mode: 3 files found, nothing deleted.", 16)
F("15_powershell_whatif.png", "Onboarding script with -WhatIf: nothing is changed; estimated time saved is shown.", 16)
F("16_powershell_simulation.png", "Onboarding script in Simulation mode: five accounts processed, none rejected.", 16)
P("Measured result: the onboarding script processed five hires in 0.3 seconds. The comparison figure of 60 minutes assumes 12 minutes of manual work per account; that assumption is mine and was not measured. The cleanup run found nothing to delete (0 MB) because no old files existed on my machine, so I report no saving for it.")

H("10. Results against the success criteria and limitations")
T(["Criterion", "Result"], [
  ["All tickets categorised correctly", "8 of 8 entered tickets, checked by rule and by hand."],
  ["SLA compliance of 90% or more", "%.1f%% (%d of %d) in the simulated log; first response %.1f%%, resolution %.1f%%. Times were modelled, not measured on live users." % (S["sla_pct"], S["sla_met"], S["tickets"], S["tto_met_pct"], S["ttr_met_pct"])],
  ["Scripts save measurable time", "Onboarding: 0.3 s run time against an assumed 60 minutes by hand. Cleanup: no measurable saving in my test."]], [5.5, 10.7])
P("Breaches in the simulated month: T-007 (phishing, 4.6 h against 4 h), T-021 (one PC without network, 9.2 h against 8 h) and T-037 (calendar sync, Medium). Details and corrective actions are in the monthly report.")
P("What I did not complete:", bold=True)
B(["Email-to-ticket was configured but not proven with a real incoming message.",
   "Only 8 of the 40 tickets and 5 of the 18 articles were entered into GLPI; all 40 and 18 exist in the log and repository.",
   "The self-service portal (stretch) was not built, and the deflection figure is an estimate.",
   "Knowledge-base articles contain screenshot placeholders; real screenshots were not added to every article.",
   "The PowerShell script was tested in WhatIf and Simulation modes only, not against real directory accounts."])

H("11. Incident review: GLPI lost its data after restarts")
P("During the project the GLPI installation repeatedly showed the setup page or an empty database after I restarted the laptop, and some configuration work disappeared. Evidence and most likely cause: the database server log showed a brand-new initialisation, while the real database files were still intact in my project folder. The containers had been set to restart automatically, so Docker most likely started them at Windows boot before the Ubuntu folder was available, created an empty folder and let MariaDB initialise a fresh database. I cannot prove this step by step, but recreating the containers from the correct folder brought all my data back, and changing the restart policy stopped the problem from returning. The GLPI database configuration file was also missing after some restarts (cause not established); the start script now recreates it. Fixes: automatic restart switched off; a start script that recreates the configuration file if missing and takes a backup; a stop script that backs up before shutdown; and a rule never to rename a database folder while containers exist. The most useful lesson: backups come before configuration work.")

H("12. Conclusion")
P("The helpdesk now classifies tickets, routes them to the right group and applies the right SLA automatically, and the supporting material (articles, ticket log, scripts, asset inventory and monthly report) is ready. The main gaps are a live email test and the self-service portal, which are the first things I would do next.")
H("Deliverables in the repository", 2)
B(["kb/ - 18 knowledge-base articles", "data/ - ticket log, statistics, sample new hires", "scripts/ - disk_cleanup.sh, New-EmployeeOnboarding.ps1",
   "glpi_setup/rebuild_glpi.py - optional API script to rebuild the configuration (not run against a live system)",
   "docs/ - Asset_Inventory.xlsx, Ticket_Log.xlsx, Monthly_Helpdesk_Report_October_2026.docx, Knowledge_Base_18_Articles.docx", "screenshots/ - the figures in this report"])
d.save("docs/Elyas_Week4_Helpdesk_Report.docx")
print("saved")
