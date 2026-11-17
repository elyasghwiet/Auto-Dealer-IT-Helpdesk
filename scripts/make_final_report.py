import json, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

A = "/mnt/user-data/attachments/31bca1d6-4f9f-5d25-b9cd-73736375c23d/"
X = "/home/claude/helpdesk/screens_extra/"
S = json.load(open("/home/claude/helpdesk/data/ticket_stats.json"))
IMG = {
 "tickets_a": A+"17525753-image.png", "tickets_b": A+"986fab46-image.png",
 "ticket11_top": A+"a572517e-image.png", "ticket11_sla": A+"36437551-image.png",
 "kb": A+"5451bcbd-image.png", "bash": A+"8e08696b-image.png", "ps_whatif": A+"0a484df2-image.png", "ps_sim": A+"6bff5692-image.png",
 "receiver": A+"14853337-image.png", "email_ticket": A+"9d31f803-image.png",
 "tickets_c": A+"60202efb-image.png", "tickets_d": A+"23814e7e-image.png",
 "categories": A+"942897ef-image.png", "groups": A+"63a23096-image.png", "users": A+"13e484fa-image.png",
 "rules_a": A+"ea01cc1a-image.png", "rules_b": A+"982a6bcf-image.png", "slm": A+"eec3b66b-image.png"}
fig = [0]
d = Document()
for s in d.sections:
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2)
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
for name, size in (("Heading 1", 16), ("Heading 2", 13)):
    h = d.styles[name]; h.font.name = "Calibri"; h.font.size = Pt(size); h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F); h.font.bold = True

def shade(cell, col):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), col); tcPr.append(sh)
def P(t, bold=False, italic=False):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold; r.italic = italic; p.paragraph_format.space_after = Pt(6); return p
def B(t):
    p = d.add_paragraph(style="List Bullet"); p.add_run(t); p.paragraph_format.space_after = Pt(2)
def H1(t): d.add_heading(t, 1)
def H2(t): d.add_heading(t, 2)
def table(header, rows, widths):
    t = d.add_table(rows=1, cols=len(header)); t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(h); r.bold = True; r.font.color.rgb = RGBColor(255, 255, 255); r.font.size = Pt(10); shade(c, "1F3A5F")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(10)
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    for i, w in enumerate(widths): t.columns[i].width = Cm(w)
    d.add_paragraph()
def figure(key, caption, width=16):
    path = IMG.get(key) if key in IMG else X + key
    if not path or not os.path.exists(path): return False
    fig[0] += 1
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(path, width=Cm(width))
    c = d.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run("Figure %d. %s" % (fig[0], caption)); r.italic = True; r.font.size = Pt(9.5)
    return True
def extra(name): return os.path.exists(X + name)

# ---------------- title
t = d.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("\n\nAuto Dealer IT Helpdesk Setup"); r.bold = True; r.font.size = Pt(26); r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
t = d.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Week 4 Project Report - GLPI service desk for a fictional EV fleet operator"); r.font.size = Pt(14)
for line in ("Author: Elyas Ghwiet", "Programme: Yuva virtual internship - IT Support", "Date: 16 November 2026"):
    p = d.add_paragraph(line); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("\nThe company, employees, tickets, serial numbers and prices in this project are fictional. Ticket times were modelled, not measured on real users."); r.italic = True; r.font.size = Pt(10)
d.add_page_break()

# ---------------- 1
H1("1. Summary")
P("I set up an IT helpdesk for a fictional electric-vehicle fleet operator in Ahmedabad with 80 employees. The tool is GLPI, an open-source service desk, running in Docker on my laptop. I configured ten ticket categories, three support groups, three technician accounts, automatic routing rules, eight service-level targets (SLA), and four rules that attach the right SLA to every ticket by priority.")
P("Around the tool I produced 18 knowledge-base articles in simple language, a log of 40 simulated tickets for Windows, Linux and network problems with troubleshooting steps, two automation scripts (Bash and PowerShell), an asset inventory workbook, and a monthly helpdesk report. Twelve tickets were entered into GLPI and the routing and SLA rules were checked on them.")
table(["Success criterion", "Result", "Evidence"], [
    ["All tickets categorised correctly", "All 40 simulated tickets and the 12 tickets in GLPI carry one of the 10 categories", "Ticket_Log.xlsx, Figures 15-18"],
    ["SLA compliance at or above 90%", "%.1f%% (%d of %d) on the simulated month; first response %.1f%%, resolution %.1f%%" % (S["sla_pct"], S["sla_met"], S["tickets"], S["tto_met_pct"], S["ttr_met_pct"]), "Section 8, monthly report"],
    ["Scripts save measurable time", "Onboarding of 5 users: about 60 minutes by hand (assumption of 12 min each) against 0.3 s by script", "Figures 20-21"],
    ["Be able to explain prioritisation", "Written rule order with examples from the ticket log", "Section 8.2"]], [4.6, 7.4, 4.2])
P("What is not finished: email-to-ticket was configured but could not be tested with a live mailbox (Section 3.5), only 5 of the 18 articles were imported into GLPI as a sample, and the stretch goal (self-service portal and measured deflection) was not built; deflection is only estimated.", italic=True)

# ---------------- 2
H1("2. Scenario and design choices")
P("The operator runs about 80 staff across a head office, a charging depot and remote workers (dispatchers, finance, HR, sales, operations and IT). The helpdesk had to be cheap, easy to explain and realistic for a small company.")
B("Tool: GLPI. It is free, has ITIL-style categories, groups, business rules and SLA built in, and is commonly used by small IT teams.")
B("Deployment: Docker Compose with two containers, MariaDB 10.11 and the GLPI web application, on Ubuntu under WSL2 on Windows. This made the setup repeatable and easy to back up.")
B("Support structure: three groups. Service Desk L1 takes everyday requests; Infrastructure and Network L2 takes network, VPN and security incidents; Fleet Applications Support takes the charging software.")
B("Priorities: Urgent, High, Medium and Low, matching the GLPI priority levels Very high, High, Medium and Low.")

# ---------------- 3
H1("3. GLPI configuration")
H2("3.1 Categories")
P("Ten categories cover the problems seen in a fleet operator: Accounts and Access, Email, Network and VPN, Hardware (Laptops and Desktops), Printers and Scanners, Software and Licences, Security Incident, Fleet and Charging Software, New Joiner / Leaver, and Other.")
figure("categories", "ITIL categories configured in GLPI.", 15)
H2("3.2 Groups and technicians")
figure("groups", "The three support groups.", 15)
figure("users", "Technician accounts (priya.patel, rahul.shah, karan.mehta) next to the default accounts.", 15)
H2("3.3 Automatic assignment rules")
P("GLPI evaluates ticket business rules in order. The first rule is a default that matches every category with the regular expression /.*/ and sends the ticket to Service Desk L1. Rules 4 to 6 come after it and override the group for Network and VPN and Security Incident (L2) and for Fleet and Charging Software (Fleet Applications Support). A rule with no criteria did not match everything in my first test, which is why the default uses the regular expression. I checked the rules with the GLPI rules-engine test before using them.")
table(["Rank", "Rule", "Condition", "Action"], [
    ["3", "Default -> Service Desk L1", "Category matches /.*/", "Group: Service Desk L1"],
    ["4", "Network and VPN -> L2", "Category is Network and VPN", "Group: Infrastructure and Network L2"],
    ["5", "Security Incident -> L2", "Category is Security Incident", "Group: Infrastructure and Network L2"],
    ["6", "Fleet and Charging Software", "Category is Fleet and Charging Software", "Group: Fleet Applications Support"]], [1.5, 5, 5, 5])
figure("rules_a", "Routing rules 3-6 and the SLA rules for Urgent and High.", 15)
H2("3.4 Service levels (SLA)")
P("Each priority has a time to own (first response) and a time to resolve. The clock runs 24/7 in this simulation. A real operator with a night shift would likely use business hours for Medium and Low tickets.")
table(["Priority", "GLPI level", "Time to own", "Time to resolve"], [
    ["Urgent", "Very high", "15 min", "4 h"], ["High", "High", "30 min", "8 h"],
    ["Medium", "Medium", "2 h", "24 h"], ["Low", "Low", "4 h", "72 h"]], [3.5, 3.5, 4, 4])
P("In GLPI a service level is a container that holds one SLA. I created one container and one SLA for each of the eight targets (the list also shows four older containers from my first attempt, which are not used). Four rules (SLA Urgent, SLA High, SLA Medium, SLA Low) assign the matching pair of SLAs when a ticket has that priority.")
figure("slm", "Service levels in GLPI.", 15)
figure("rules_b", "SLA rules for Medium and Low priority.", 15)
H2("3.5 Email-to-ticket")
P("I configured a receiver (mail collector) for a dedicated test mailbox over IMAP with SSL on imap.gmail.com, port 993.")
figure("receiver", "Receiver settings (password not shown).", 15)
P("The connection test failed with a login error because Gmail requires an app password for external programs, and I did not complete that step. So the live collection from a mailbox was not tested. To show what the result would look like, I created one ticket by hand, titled VPN not working, with the text of a typical e-mailed request. It was categorised as Network and VPN and received the status Processing (assigned) through the rules. This is a simulation of the result, not proof that the mail collector works.")
figure("email_ticket", "Ticket created by hand to represent an e-mailed request.", 15)
H2("3.6 Test evidence")
P("Twelve tickets exist in GLPI: three early tests, one simulated e-mail request, and eight tickets taken from the ticket log (T-003, T-004, T-007, T-008, T-010, T-013, T-017, T-025). Priorities and due dates follow the SLA table: for example, Urgent tickets resolve 4 hours after opening and the Low ticket 72 hours after opening.")
figure("tickets_c", "Tickets 5-8 with priority, category and time to resolve.", 16)
figure("tickets_d", "Tickets 9-12 with priority, category and time to resolve.", 16)
figure("ticket11_top", "Ticket 11, Internet down in the whole office (Urgent).", 15)
figure("ticket11_sla", "The same ticket: time to own 14:58 (TTO Urgent 15 min) and time to resolve 18:43 (TTR Urgent 4 h).", 15)
ok1 = figure("group_l2.png", "Ticket 11 actors: assigned group Infrastructure and Network L2 (set by the routing rule).", 13)
ok2 = figure("group_l1.png", "Ticket 12 actors: assigned group Service Desk L1.", 13)

# ---------------- 4
H1("4. Knowledge base")
P("I wrote 18 articles for employees and support staff in simple language. Each has the problem, steps to fix it yourself, what to do if it still fails, prevention, and the ticket category and priority to use. Topics: forgotten Windows password, locked account, VPN connection and VPN timeout, company mail, slow laptop, Wi-Fi, suspicious link, software requests, large files, multi-factor codes, shared folders, printers, Windows Update, Linux DNS, Linux disk space, Teams camera and microphone, and the charging dashboard.")
P("The full set is in the repository (kb folder and Knowledge_Base_18_Articles.docx). Five of them were imported into GLPI as a sample.")
figure("kb", "Knowledge base in GLPI, article KB-01 open.", 15)

# ---------------- 5
H1("5. Simulated tickets")
P("The ticket log (Ticket_Log.xlsx and data/tickets.csv) holds 40 tickets for October 2026: 32 on Windows, 4 on Linux and 4 on the network. Each has a category, priority, department, assigned group, symptom, troubleshooting steps, resolution, first-response time and resolution time. SLA columns are formulas in the workbook, so they recalculate if a time is edited.")
table(["Category", "Tickets"], [[c, n] for c, n in S["by_category"]], [9, 3])
P("The times are modelled, not measured on real users.", italic=True)

# ---------------- 6
H1("6. Automation scripts")
H2("6.1 disk_cleanup.sh (Bash, Linux)")
P("The script removes old temporary files and rotated logs. It is safe by default: it runs as a dry run and deletes nothing unless --apply is given; it stays on one file system (-xdev); it deletes regular files only; it refuses to operate on system directories such as /, /etc, /usr and /home; and it writes a log with disk usage before and after. My first run on a clean laptop found nothing older than 7 days.")
figure("bash", "Dry run of disk_cleanup.sh in Ubuntu (WSL).", 16)
if extra("cleanup_apply.png"):
    P("To show a measurable result I created three 100 MB test files dated 20 days ago in /tmp, previewed the cleanup, and then applied it.")
    figure("cleanup_dry.png", "Preview: the three old files would be deleted.", 16)
    figure("cleanup_apply.png", "Applied cleanup: space freed (disk used before and after).", 16)
H2("6.2 New-EmployeeOnboarding.ps1 (PowerShell, Windows)")
P("The script reads new hires from a CSV file, builds a username, creates the account with a random temporary password and adds it to groups by department. It supports -WhatIf, validates each row, writes a report and a separate file of temporary passwords, and prints the estimated time saved. In Simulation mode no real accounts are created. The 12 minutes of manual work per user is my assumption, not a measurement.")
figure("ps_whatif", "-WhatIf run: shows what would happen for each of five hires.", 16)
figure("ps_sim", "Simulation run: 5 accounts processed, 60 minutes estimated by hand against under one second.", 16)

# ---------------- 7
H1("7. Asset inventory")
P("Asset_Inventory.xlsx has a Laptops sheet (30 laptops of the 80-person fleet: model, serial number, specification, assigned user, warranty end and a warranty flag calculated from today's date) and a Licences sheet (seven software items with seats owned, seats in use, utilisation, renewal date and annual cost). In total there are 269 licence seats with 237 in use (88%). All names, serial numbers and prices are fictional.")

# ---------------- 8
H1("8. Monthly helpdesk report (October 2026, simulated)")
H2("8.1 Results")
table(["Measure", "Result"], [
    ["Tickets handled", S["tickets"]], ["SLA met (both parts)", "%.1f%% (%d/%d)" % (S["sla_pct"], S["sla_met"], S["tickets"])],
    ["First-response SLA", "%.1f%%" % S["tto_met_pct"]], ["Resolution SLA", "%.1f%%" % S["ttr_met_pct"]],
    ["Average first response", "%.0f min" % S["avg_first_response_min"]], ["Average resolution", "%.1f h" % S["avg_resolution_h"]]], [8, 6])
P("Three tickets missed their SLA: T-007 (phishing click, 4.6 h against 4 h, because the investigation took longer than the containment), T-021 (a faulty switch port, 9.2 h against 8 h) and T-037 (calendar sync, which waited behind urgent work). Because only three tickets were Urgent, one miss gives 66.7% for that priority, so it should be read as a case to review, not as a trend. The full monthly report is a separate document.")
H2("8.2 How competing urgent tickets are prioritised")
P("When two tickets need attention at the same time I decide in this order:")
for t in ("Security first: an incident such as a clicked phishing link is handled before anything else, because damage grows with time.",
          "Number of people affected: a whole-office outage comes before a problem for one user.",
          "Business impact: a broken charging dashboard (vehicles cannot be dispatched) comes before a printer fault.",
          "SLA clock: if everything else is equal, the ticket closest to its deadline goes first.",
          "Quick wins: a 10-minute fix, such as a locked account before a shift, is done in between so it does not wait for hours."):
    B(t)
P("Examples from the log: on 9 October T-017 (office internet down, Urgent) was handled before T-018 (scanner saving blank pages, Medium), which waited and was solved in 1.4 hours. On 4 October the phishing incident T-007 came before the locked account T-008. In GLPI, priority is calculated from urgency and impact, and the rules assign the group and the SLA, so the technician does not have to decide under pressure.")

# ---------------- 9
H1("9. Problems and lessons")
P("The GLPI database appeared to disappear several times, and the site showed the installation page again. The data was not lost; it was stored in a folder on disk, but the database container sometimes started on an empty folder. The most likely cause is that the containers were set to restart automatically (restart: always) when Windows started, before the Ubuntu environment was ready, so Docker created an empty folder and started from scratch. The evidence was a fresh database log and a data folder on disk that still held the old data. Renaming the data folder while the containers existed made it worse, because a running container follows the folder rather than its name.")
P("Fixes: automatic restart was turned off; a start script (start.sh) recreates the database connection file if it is missing and takes a backup every time; a stop script takes a backup before shutdown; and data folders are never renamed while containers exist. Lessons: back up after every stage, keep copies outside the working folder, and test that data survives a restart before relying on a system.")

# ---------------- 10
H1("10. Limitations and next steps")
B("Email-to-ticket: finish the app-password step and test with a real message.")
B("Import all 18 knowledge-base articles and publish them in the GLPI self-service portal; measure deflection by counting article views that are not followed by a ticket from the same user within 24 hours.")
B("Use a business-hours calendar for Medium and Low tickets and split security incidents into containment and investigation so the SLA measures what the user feels.")
B("Replace the assumed 12 minutes per manual account with a measured value, and run the onboarding script against a real directory service in a test environment.")
B("The REST-API script that rebuilds the GLPI configuration (glpi_setup/rebuild_glpi.py) is written but was not run against a live system.")

# ---------------- 11
H1("11. Repository contents")
table(["Folder", "Content"], [
    ["kb/", "18 knowledge-base articles and an index"], ["data/", "tickets.csv (40 simulated tickets), ticket_stats.json, new_hires.csv"],
    ["scripts/", "disk_cleanup.sh, New-EmployeeOnboarding.ps1 and generator scripts"], ["glpi_setup/", "rebuild_glpi.py (untested)"],
    ["docs/", "Asset_Inventory.xlsx, Ticket_Log.xlsx, monthly report, knowledge base in Word"], ["screenshots/", "GLPI and script screenshots"]], [4, 12])
d.save("/home/claude/helpdesk/final/Elyas_Week4_IT_Helpdesk_Report.docx")
print("saved; figures:", fig[0], "group shots:", ok1, ok2)
