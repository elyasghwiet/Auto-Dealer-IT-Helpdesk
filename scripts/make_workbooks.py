"""Builds the asset inventory workbook and the ticket log workbook (formulas, not pasted numbers)."""
import csv, sys, os
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs"
os.makedirs(OUT, exist_ok=True)
HEAD = PatternFill("solid", fgColor="1F3A5F"); HF = Font(bold=True, color="FFFFFF")
thin = Side(style="thin", color="C5CDD6"); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c); cell.fill = HEAD; cell.font = HF
        cell.alignment = Alignment(wrap_text=True, vertical="center"); cell.border = BORDER
def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1): ws.column_dimensions[get_column_letter(i)].width = w

# ========================================================= ASSET INVENTORY
wb = Workbook()
ws = wb.active; ws.title = "Laptops"
cols = ["Asset tag", "Make / model", "Serial number (simulated)", "CPU / RAM / disk", "OS", "Purchase date", "Warranty end",
        "Assigned to", "Department", "Location", "Status", "Last audit", "Warranty days left", "Warranty flag"]
ws.append(cols); style_header(ws, 1, len(cols))
people = [("Aarav Desai","Operations"),("Meera Joshi","Finance"),("Vikram Patel","Sales"),("Ananya Bhatt","HR"),("Ishaan Parmar","IT"),
 ("Neha Trivedi","HR"),("Rohan Shah","Sales"),("Karan Mehta","IT"),("Priya Patel","IT"),("Rahul Shah","IT"),
 ("Sneha Pandya","Finance"),("Hiren Modi","Operations"),("Pooja Solanki","Operations"),("Jay Thakkar","Sales"),("Dhruv Vyas","Operations"),
 ("Kinjal Rana","Finance"),("Mehul Chauhan","Operations"),("Bhavna Dave","HR"),("Nirav Kothari","Sales"),("Riya Amin","Finance"),
 ("Tejas Gohil","Operations"),("Foram Brahmbhatt","Sales"),("Yash Raval","IT"),("Disha Kapadia","Operations"),("Chirag Barot","Finance"),
 ("Hetal Panchal","Sales"),("Parth Jani","Operations"),("Shreya Nair","HR"),("Smit Dalal","Operations"),("(spare)","IT")]
models = [("Lenovo ThinkPad L14 Gen 4","Ryzen 5 / 16 GB / 512 GB SSD"),("Dell Latitude 5440","Core i5 / 16 GB / 512 GB SSD"),
          ("HP ProBook 450 G10","Core i5 / 8 GB / 256 GB SSD")]
locs = ["Head office - 2nd floor", "Head office - 1st floor", "Charging depot", "Remote (home)"]
for i, (name, dept) in enumerate(people, 1):
    m, spec = models[i % 3]
    purchase = date(2024 + (i % 3 == 0), 1 + (i * 3) % 12, 5 + i % 20)
    warranty = date(purchase.year + 3, purchase.month, purchase.day)
    status = "In stock" if name == "(spare)" else ("In repair" if i == 14 else "In use")
    ws.append(["EVF-LT-%03d" % i, m, "SIM-%s-%05d" % ("LN" if "Lenovo" in m else "DL" if "Dell" in m else "HP", 10000 + i * 37),
               spec, "Windows 11 Pro", purchase, warranty, name, dept, locs[i % 4], status, date(2026, 10, 15), None, None])
    r = ws.max_row
    ws.cell(r, 13).value = '=G%d-TODAY()' % r
    ws.cell(r, 14).value = '=IF(M%d<0,"Expired",IF(M%d<=180,"Expires soon","OK"))' % (r, r)
    for c in (6, 7, 12): ws.cell(r, c).number_format = "yyyy-mm-dd"
last = ws.max_row
widths(ws, [13, 26, 22, 28, 15, 13, 13, 20, 13, 24, 11, 12, 11, 14])
ws.freeze_panes = "A2"; ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(cols)), last)
dv = DataValidation(type="list", formula1='"In use,In stock,In repair,Retired"', allow_blank=False); ws.add_data_validation(dv); dv.add("K2:K%d" % (last + 50))
ws.conditional_formatting.add("N2:N%d" % last, CellIsRule(operator="equal", formula=['"Expired"'], fill=PatternFill("solid", bgColor="F4C7C3")))
ws.conditional_formatting.add("N2:N%d" % last, CellIsRule(operator="equal", formula=['"Expires soon"'], fill=PatternFill("solid", bgColor="FCE8B2")))

wl = wb.create_sheet("Licences")
lcols = ["Software", "Licence type", "Vendor", "Seats owned", "Seats in use", "Seats free", "Utilisation %", "Renewal date", "Cost per seat / year (INR)", "Annual cost (INR)", "Owner", "Note"]
wl.append(lcols); style_header(wl, 1, len(lcols))
lic = [("Microsoft 365 Business Standard","Subscription","Microsoft",80,76,date(2027,3,31),14400,"IT","1 licence per employee; 4 free for new hires"),
       ("Adobe Acrobat Pro","Subscription","Adobe",10,6,date(2027,1,15),15600,"Finance","4 free seats; PDF editor requests"),
       ("Endpoint antivirus","Subscription","Vendor A (simulated)",90,82,date(2027,6,30),1800,"IT","Includes servers"),
       ("VPN client","Subscription","Vendor B (simulated)",60,47,date(2027,2,28),2400,"IT","Remote staff"),
       ("Charging dashboard","Perpetual + support","Fleet vendor (simulated)",25,22,date(2027,4,30),30000,"Operations","Dispatchers"),
       ("Zoom / Teams Rooms","Subscription","Microsoft",3,3,date(2027,3,31),20400,"IT","Meeting rooms"),
       ("GLPI","Open source (GPL)","GLPI Project",1,1,None,0,"IT","Service desk, no licence fee")]
for i, (n, t, v, own, used, ren, cost, owner, note) in enumerate(lic, 2):
    wl.append([n, t, v, own, used, None, None, ren, cost, None, owner, note])
    wl.cell(i, 6).value = "=D%d-E%d" % (i, i); wl.cell(i, 7).value = "=IF(D%d=0,0,E%d/D%d)" % (i, i, i)
    wl.cell(i, 10).value = "=D%d*I%d" % (i, i)
    wl.cell(i, 7).number_format = "0%"; wl.cell(i, 8).number_format = "yyyy-mm-dd"
    wl.cell(i, 9).number_format = "#,##0"; wl.cell(i, 10).number_format = "#,##0"
lr = wl.max_row
wl.append(["TOTAL", None, None, "=SUM(D2:D%d)" % lr, "=SUM(E2:E%d)" % lr, "=SUM(F2:F%d)" % lr, "=E%d/D%d" % (lr + 1, lr + 1), None, None, "=SUM(J2:J%d)" % lr])
for c in range(1, 11): wl.cell(lr + 1, c).font = Font(bold=True)
wl.cell(lr + 1, 7).number_format = "0%"; wl.cell(lr + 1, 10).number_format = "#,##0"
widths(wl, [32, 20, 22, 11, 11, 10, 12, 13, 16, 16, 12, 38]); wl.freeze_panes = "A2"
wl.conditional_formatting.add("G2:G%d" % lr, CellIsRule(operator="greaterThanOrEqual", formula=["0.95"], fill=PatternFill("solid", bgColor="FCE8B2")))

wsu = wb.create_sheet("Summary", 0)
wsu["A1"] = "Asset inventory summary - EV fleet operator (SIMULATED data)"; wsu["A1"].font = Font(bold=True, size=14, color="1F3A5F")
rows = [("Laptops registered", "=COUNTA(Laptops!A2:A%d)" % last), ("In use", '=COUNTIF(Laptops!K2:K%d,"In use")' % last),
        ("In stock (spares)", '=COUNTIF(Laptops!K2:K%d,"In stock")' % last), ("In repair", '=COUNTIF(Laptops!K2:K%d,"In repair")' % last),
        ("Warranty expires within 180 days", '=COUNTIF(Laptops!N2:N%d,"Expires soon")' % last), ("Warranty expired", '=COUNTIF(Laptops!N2:N%d,"Expired")' % last),
        ("Licence seats owned", "=Licences!D%d" % (lr + 1)), ("Licence seats in use", "=Licences!E%d" % (lr + 1)),
        ("Overall licence utilisation", "=Licences!G%d" % (lr + 1)), ("Annual licence cost (INR)", "=Licences!J%d" % (lr + 1))]
for i, (k, f) in enumerate(rows, 3):
    wsu.cell(i, 1, k); wsu.cell(i, 2, f); wsu.cell(i, 1).border = BORDER; wsu.cell(i, 2).border = BORDER
wsu["B11"].number_format = "0%"; wsu["B12"].number_format = "#,##0"
wsu["A14"] = "Note: serial numbers, names and prices are fictional. The 30 laptops shown are the first batch of an 80-employee fleet; the rest follow the same format."
wsu["A14"].alignment = Alignment(wrap_text=True); wsu.merge_cells("A14:B16")
widths(wsu, [44, 18])
wb.save(os.path.join(OUT, "Asset_Inventory.xlsx"))

# ========================================================= TICKET LOG
rows = list(csv.DictReader(open("data/tickets.csv", encoding="utf-8-sig")))
wb = Workbook(); ws = wb.active; ws.title = "Ticket log"
tcols = ["Ticket", "Opened", "Category", "Priority", "Platform", "Department", "Assigned group", "Title", "Symptom", "Troubleshooting steps",
         "Resolution", "First response (min)", "TTO target (min)", "TTO met", "Resolution (hours)", "TTR target (h)", "TTR met", "SLA met"]
ws.append(tcols); style_header(ws, 1, len(tcols))
for i, r in enumerate(rows, 2):
    ws.append([r["ticket"], r["opened"], r["category"], r["priority"], r["platform"], r["department"], r["assigned_group"], r["title"], r["symptom"],
               r["troubleshooting_steps"], r["resolution"], float(r["first_response_min"]), None, None, float(r["resolution_hours"]), None, None, None])
    ws.cell(i, 13).value = '=IF(D%d="Urgent",15,IF(D%d="High",30,IF(D%d="Medium",120,240)))' % (i, i, i)
    ws.cell(i, 14).value = '=IF(L%d<=M%d,"Yes","No")' % (i, i)
    ws.cell(i, 16).value = '=IF(D%d="Urgent",4,IF(D%d="High",8,IF(D%d="Medium",24,72)))' % (i, i, i)
    ws.cell(i, 17).value = '=IF(O%d<=P%d,"Yes","No")' % (i, i)
    ws.cell(i, 18).value = '=IF(AND(N%d="Yes",Q%d="Yes"),"Yes","No")' % (i, i)
    for c in (8, 9, 10, 11): ws.cell(i, c).alignment = Alignment(wrap_text=True, vertical="top")
n = ws.max_row
widths(ws, [8, 16, 24, 9, 9, 12, 28, 34, 36, 60, 36, 10, 9, 8, 10, 9, 8, 8]); ws.freeze_panes = "B2"; ws.auto_filter.ref = "A1:R%d" % n
for col in ("N", "Q", "R"):
    ws.conditional_formatting.add("%s2:%s%d" % (col, col, n), CellIsRule(operator="equal", formula=['"No"'], fill=PatternFill("solid", bgColor="F4C7C3")))
st = wb.create_sheet("SLA statistics", 0)
st["A1"] = "Helpdesk statistics - simulated month (October 2026)"; st["A1"].font = Font(bold=True, size=14, color="1F3A5F")
L = "'Ticket log'!"
kp = [("Tickets", "=COUNTA(%sA2:A%d)" % (L, n)), ("SLA met (first response AND resolution)", '=COUNTIF(%sR2:R%d,"Yes")' % (L, n)),
      ("SLA compliance %", "=B4/B3"), ("First response SLA %", '=COUNTIF(%sN2:N%d,"Yes")/B3' % (L, n)),
      ("Resolution SLA %", '=COUNTIF(%sQ2:Q%d,"Yes")/B3' % (L, n)), ("Average resolution (hours)", "=AVERAGE(%sO2:O%d)" % (L, n)),
      ("Average first response (minutes)", "=AVERAGE(%sL2:L%d)" % (L, n))]
for i, (k, f) in enumerate(kp, 3): st.cell(i, 1, k); st.cell(i, 2, f)
for c in ("B5", "B6", "B7"): st[c].number_format = "0.0%"
st["B8"].number_format = "0.0"; st["B9"].number_format = "0.0"
st["A11"] = "By category"; st["A11"].font = Font(bold=True)
cats = ["Accounts and Access","Network and VPN","Hardware (Laptops and Desktops)","Software and Licences","Email","Printers and Scanners",
        "Fleet and Charging Software","Security Incident","New Joiner / Leaver","Other"]
# category names in the log use the short name 'Hardware'
real = ["Accounts and Access","Network and VPN","Hardware","Software and Licences","Email","Printers and Scanners","Fleet and Charging Software","Security Incident","New Joiner / Leaver","Other"]
st.append([]); 
for i, c in enumerate(real, 12):
    st.cell(i, 1, c); st.cell(i, 2, '=COUNTIF(%sC2:C%d,A%d)' % (L, n, i)); st.cell(i, 3, "=B%d/$B$3" % i); st.cell(i, 3).number_format = "0%"
st["A23"] = "By priority"; st["A23"].font = Font(bold=True)
for i, p in enumerate(["Urgent", "High", "Medium", "Low"], 24):
    st.cell(i, 1, p); st.cell(i, 2, '=COUNTIF(%sD2:D%d,A%d)' % (L, n, i))
    st.cell(i, 3, '=COUNTIFS(%sD2:D%d,A%d,%sR2:R%d,"Yes")/B%d' % (L, n, i, L, n, i)); st.cell(i, 3).number_format = "0%"
st["C23"] = "SLA met %"; st["C23"].font = Font(bold=True)
st["A29"] = "By platform"; st["A29"].font = Font(bold=True)
for i, p in enumerate(["Windows", "Linux", "Network"], 30):
    st.cell(i, 1, p); st.cell(i, 2, '=COUNTIF(%sE2:E%d,A%d)' % (L, n, i))
st["A34"] = "Data is SIMULATED for training; times were modelled, not measured on live users."
widths(st, [42, 12, 12])
wb.save(os.path.join(OUT, "Ticket_Log.xlsx"))
print("saved", os.listdir(OUT))
