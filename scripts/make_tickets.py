"""Builds the simulated ticket log (40 tickets) and its SLA statistics.
All tickets are SIMULATED for the fictional EV fleet operator (80 employees, Ahmedabad).
Output: data/tickets.csv and data/ticket_stats.json"""
import csv, json, os, sys
from datetime import datetime, timedelta

OUT = sys.argv[1] if len(sys.argv) > 1 else "data"
TTO = {"Urgent": 15, "High": 30, "Medium": 120, "Low": 240}      # minutes
TTR = {"Urgent": 4, "High": 8, "Medium": 24, "Low": 72}          # hours
GROUP = {"Network and VPN": "Infrastructure and Network L2", "Security Incident": "Infrastructure and Network L2",
         "Fleet and Charging Software": "Fleet Applications Support"}
def group(cat): return GROUP.get(cat, "Service Desk L1")

# (day, hh:mm, category, priority, platform, dept, title, symptom, troubleshooting steps, resolution, first_response_min, resolution_hours)
T = [
 (1,"09:05","Accounts and Access","Medium","Windows","Sales","Forgotten Windows password","User cannot sign in after a long weekend.","1) Verified identity by phone and employee ID. 2) Checked account was not locked in the directory. 3) Reset password and set 'must change at next sign-in'.","Password reset; user changed it at first login.",12,0.6),
 (1,"10:20","Email","Medium","Windows","Finance","Outlook keeps asking for password","Outlook shows a password prompt every few minutes.","1) Checked mailbox works in the web client (it does). 2) Cleared saved credentials in Credential Manager. 3) Restarted Outlook and signed in again.","Old cached credential removed; prompt stopped.",20,1.1),
 (2,"08:40","Network and VPN","High","Network","Operations","VPN client fails with 'connection timed out'","Field supervisor cannot connect to VPN from home.","1) Confirmed the user has internet (ping 8.8.8.8). 2) Tried another network (mobile hotspot): VPN connected. 3) Home router blocked the VPN port; advised changing the VPN profile to TCP 443.","Profile switched to TCP 443; connected from home.",18,2.4),
 (2,"11:15","Hardware","Medium","Windows","HR","Laptop very slow after startup","Boot takes 6+ minutes, fan always loud.","1) Task Manager: disk at 100%. 2) Found 14 startup apps and a pending Windows update. 3) Disabled non-essential startup apps, finished the update, ran Disk Cleanup.","Boot time reduced to under 1 minute.",35,3.0),
 (3,"09:30","Printers and Scanners","Low","Windows","Finance","Printer shows 'Offline'","Finance printer offline on one PC only.","1) Other PCs print fine, so the printer is OK. 2) Checked the printer port: IP changed after a router restart. 3) Updated the port to the printer's new IP and set a DHCP reservation.","Printer online; static reservation added.",55,5.5),
 (3,"13:10","Software and Licences","Medium","Windows","Operations","Cannot install PDF reader","Installer is blocked by 'administrator required'.","1) Confirmed software is on the approved list. 2) Installed it remotely with admin rights. 3) Added it to the standard software image.","Installed; request closed.",40,1.8),
 (4,"08:15","Security Incident","Urgent","Windows","Finance","Phishing e-mail clicked","User entered credentials on a fake invoice page.","1) Disabled the account immediately. 2) Reset password and revoked active sessions. 3) Searched mail logs for the same sender, found 3 more recipients and removed the message. 4) Scanned the PC with Defender, clean. 5) Reminded user about reporting suspicious mail.","Account secured within the hour; no data loss found.",5,4.6),
 (4,"10:50","Accounts and Access","Medium","Windows","Sales","Account locked after wrong passwords","Account lockout after phone sync used an old password.","1) Checked lockout source: the user's phone mail app. 2) Removed and re-added the mail account on the phone. 3) Unlocked the account.","Lockout source fixed.",15,0.8),
 (5,"09:00","New Joiner / Leaver","Medium","Windows","HR","Onboard 2 new dispatchers","Two new employees start Monday.","1) Created accounts using the onboarding script. 2) Added both to the Operations group. 3) Prepared two laptops and updated the asset sheet.","Both accounts and laptops ready on Friday.",30,6.0),
 (5,"14:25","Fleet and Charging Software","Urgent","Windows","Operations","Charging dashboard not loading","Dispatchers cannot see charger status; 12 vehicles waiting.","1) Reproduced: web page returns HTTP 503. 2) Checked the application service on the server: stopped. 3) Restarted the service and checked the log: database connection timeout after a nightly backup. 4) Raised the backup job's timeout window.","Service restored in 1.5 hours; root cause documented.",8,1.5),
 (6,"09:45","Hardware","Low","Windows","Sales","Docking station not charging laptop","Laptop charges only through the wall charger.","1) Tested with another dock: works. 2) Checked dock power adapter wattage: too low. 3) Replaced with 90W adapter.","New adapter fixed charging.",90,26.0),
 (6,"15:00","Email","Low","Windows","HR","Cannot send attachments over 20 MB","Mail bounces with 'message too large'.","1) Explained the 20 MB mail limit. 2) Showed how to share via the company file share link. 3) Wrote a KB article on large files.","Workaround provided and documented.",110,2.0),
 (7,"08:50","Network and VPN","Medium","Linux","IT","Ubuntu server cannot resolve hostnames","'ping google.com' fails but 'ping 8.8.8.8' works.","1) Diagnosed DNS: 'resolvectl status' showed no DNS server. 2) Added the correct DNS servers in netplan. 3) Applied with 'sudo netplan apply'.","DNS resolution restored.",25,1.2),
 (7,"11:30","Hardware","High","Windows","Operations","Laptop battery drains in 40 minutes","Battery health bad, shuts down suddenly.","1) Ran 'powercfg /batteryreport': health 38%. 2) Confirmed it is out of warranty cycle. 3) Issued a spare laptop and ordered a battery.","Spare laptop issued same day; battery replaced later.",20,6.5),
 (8,"09:20","Software and Licences","Medium","Windows","Finance","Excel macro blocked","A macro workbook from a vendor will not run.","1) File came from e-mail, so it is marked 'blocked'. 2) Scanned it: clean. 3) Unblocked via file Properties and added the folder as a Trusted Location.","Macro runs; folder trusted.",45,2.5),
 (8,"13:45","Accounts and Access","Low","Windows","Sales","Need access to the shared Sales folder","User moved to Sales, cannot open the shared folder.","1) Checked manager approval. 2) Added the user to the sales-users group. 3) Asked the user to sign out and in.","Access granted.",150,4.0),
 (9,"08:30","Network and VPN","Urgent","Network","All staff","Internet down in the whole office","No website opens for all 80 users.","1) Checked the switch: link lights OK. 2) Router could not reach ISP gateway. 3) Power-cycled the ISP modem, then verified WAN link. 4) Contacted the ISP with the fault ticket and enabled the backup LTE link.","Backup link up in 20 min; ISP fixed fault in 2.8 hours.",4,2.8),
 (9,"10:40","Printers and Scanners","Medium","Windows","HR","Scanner saves blank pages","Scan-to-folder gives empty PDFs.","1) Cleaned the glass and tested copy: fine. 2) Scan-to-folder profile used the wrong paper size. 3) Reset the profile to A4.","Scanner works.",30,1.4),
 (10,"09:10","Accounts and Access","High","Windows","Operations","Dispatcher locked out before shift","Cannot sign in; shift starts in 30 minutes.","1) Verified identity. 2) Found the password expired. 3) Reset password and confirmed sign-in.","Resolved before shift start.",6,0.4),
 (10,"14:00","Software and Licences","Medium","Windows","Sales","Teams camera not detected","Camera works in Camera app but not in Teams.","1) Checked Teams device settings: no camera selected. 2) Updated camera driver. 3) Restarted Teams.","Camera works.",35,1.6),
 (11,"09:35","Network and VPN","High","Network","Finance","One PC has no network, others fine","Network icon shows 'unidentified network'.","1) Tested cable on another port: works, so the port is bad. 2) Checked the wall-to-switch patch cable. 3) Moved the cable to a free switch port and verified link.","Moved to a free port; faulty port labelled for replacement.",22,9.2),
 (11,"12:00","Hardware","Medium","Windows","Sales","Laptop screen flickers","Screen flickers when moving the lid.","1) Tested an external monitor: stable. 2) Updated the graphics driver. 3) Issue continued, so ordered a replacement display cable.","Cable replaced under warranty.",40,18.0),
 (12,"08:55","Security Incident","High","Linux","IT","Failed SSH login attempts","Log shows hundreds of failed SSH logins from one IP.","1) Checked '/var/log/auth.log'. 2) Blocked the IP with ufw. 3) Disabled password login and enabled key-only SSH. 4) Installed fail2ban.","Attack blocked; server hardened.",10,3.5),
 (12,"11:40","Email","Medium","Windows","Operations","New phone cannot get company mail","Mail app says 'cannot verify server identity'.","1) Confirmed the phone date/time was wrong. 2) Set automatic time. 3) Re-added the mail account.","Mail works on the phone.",28,1.0),
 (13,"09:25","Printers and Scanners","Low","Windows","Sales","Printout has black lines","Vertical lines on every page.","1) Ran the printer cleaning cycle. 2) Lines remained, so replaced the toner cartridge. 3) Printed a test page.","New toner fixed print quality.",120,20.0),
 (13,"13:50","Fleet and Charging Software","High","Windows","Operations","Wrong charging schedule in app","Vehicles charge at peak tariff hours.","1) Compared schedule settings with the tariff table. 2) Found the time zone set to UTC. 3) Changed to IST and re-saved schedules.","Schedules correct; savings restored.",25,4.5),
 (14,"09:00","New Joiner / Leaver","Medium","Windows","HR","Leaver: disable accounts of 3 employees","Three contractors finished their contracts today.","1) Ran the offboarding script in dry-run to check. 2) Disabled the accounts and removed groups. 3) Collected laptops and updated the asset sheet.","Access removed same day.",15,3.5),
 (14,"15:15","Software and Licences","Low","Windows","Finance","Request for a PDF editor licence","User needs to edit PDFs weekly.","1) Checked licence pool: 4 free seats. 2) Got manager approval. 3) Assigned a licence and updated the licence sheet.","Licence assigned.",200,22.0),
 (15,"08:45","Network and VPN","Medium","Linux","IT","Cannot reach a server from the office LAN","Ping to the file server times out from one subnet.","1) 'traceroute' stopped at the router. 2) Found a missing static route to the server subnet. 3) Added the route and saved the configuration.","Subnet reaches the server.",30,2.2),
 (15,"10:30","Accounts and Access","Medium","Windows","Finance","MFA prompt not arriving","Authenticator code never appears.","1) Checked phone notifications: disabled for the app. 2) Enabled notifications. 3) Re-registered the authenticator.","MFA works.",25,1.3),
 (16,"09:40","Hardware","Medium","Windows","Operations","USB headset not recognised","Headset not shown in sound settings.","1) Tried another USB port and PC: works. 2) Checked Device Manager: driver error. 3) Reinstalled the USB audio driver.","Headset works.",42,1.9),
 (16,"14:10","Other","Low","Windows","Sales","Question about booking a meeting room","User asked how to book rooms in the calendar.","1) Sent the room-booking KB article. 2) Offered a 5-minute demo.","Question answered.",180,3.0),
 (17,"08:35","Accounts and Access","High","Windows","Finance","Shared mailbox missing","Finance team lost access to the shared mailbox.","1) Checked mailbox permissions: group removed by an old script. 2) Re-added the group with Full Access. 3) Cleared the Outlook cache.","Shared mailbox visible again.",14,2.1),
 (17,"11:20","Software and Licences","Medium","Windows","IT","Windows Update stuck at 30%","PC stuck on 'working on updates'.","1) Waited 30 minutes. 2) Ran the Windows Update troubleshooter. 3) Cleared 'SoftwareDistribution' folder and retried.","Update completed.",38,3.2),
 (18,"09:15","Network and VPN","High","Network","Operations","Wi-Fi drops in the garage","Handheld scanners lose signal near the chargers.","1) Walked the area with a Wi-Fi analyzer. 2) Signal -78 dBm, too weak. 3) Moved the access point and set the channel to 11.","Signal stable at -62 dBm.",20,5.0),
 (18,"13:05","Printers and Scanners","Medium","Windows","Sales","New printer not found","User cannot add the printer.","1) Checked the printer IP: correct. 2) Added printer by IP using the manufacturer driver. 3) Added the same driver to the deployment image.","Printer added.",33,1.7),
 (19,"09:50","Email","Medium","Windows","HR","Calendar invites not syncing","Invites appear on the PC but not on the phone.","1) Checked sync settings. 2) Removed and re-added the account on the phone. 3) Verified a new invite synced.","Calendar syncs.",150,27.0),
 (19,"14:30","Fleet and Charging Software","Medium","Windows","Operations","Report export to Excel fails","'Export' button shows an error.","1) Reproduced the error and read the log: output path not writable. 2) Fixed folder permissions. 3) Exported again.","Export works.",50,3.8),
 (20,"10:00","Hardware","Low","Windows","Finance","Mouse pointer jumps","Pointer moves by itself.","1) Cleaned the sensor. 2) Changed batteries. 3) Replaced the mouse.","New mouse issued.",100,5.0),
 (20,"15:05","Other","Low","Linux","IT","Cleanup of full disk on test server","Disk 96% used.","1) 'df -h' and 'du -sh /var/*'. 2) Found old logs. 3) Ran the disk cleanup script.","Disk usage 61%.",95,1.5),
]
assert len(T) == 40, len(T)

rows = []
for i, (day, hhmm, cat, prio, plat, dept, title, sym, steps, res, tto, ttr) in enumerate(T, 1):
    opened = datetime(2026, 10, day, *map(int, hhmm.split(":")))
    first = opened + timedelta(minutes=tto)
    solved = opened + timedelta(hours=ttr)
    tto_ok = tto <= TTO[prio]; ttr_ok = ttr <= TTR[prio]
    rows.append({"ticket": "T-%03d" % i, "opened": opened.strftime("%Y-%m-%d %H:%M"), "category": cat, "priority": prio,
                 "platform": plat, "department": dept, "assigned_group": group(cat), "title": title, "symptom": sym,
                 "troubleshooting_steps": steps, "resolution": res,
                 "first_response_min": tto, "tto_target_min": TTO[prio], "tto_met": "Yes" if tto_ok else "No",
                 "resolution_hours": ttr, "ttr_target_h": TTR[prio], "ttr_met": "Yes" if ttr_ok else "No",
                 "sla_met": "Yes" if tto_ok and ttr_ok else "No",
                 "resolved": solved.strftime("%Y-%m-%d %H:%M")})
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "tickets.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

from collections import Counter
met = sum(r["sla_met"] == "Yes" for r in rows)
stats = {"tickets": len(rows), "sla_met": met, "sla_pct": round(100 * met / len(rows), 1),
         "tto_met_pct": round(100 * sum(r["tto_met"] == "Yes" for r in rows) / len(rows), 1),
         "ttr_met_pct": round(100 * sum(r["ttr_met"] == "Yes" for r in rows) / len(rows), 1),
         "avg_resolution_h": round(sum(r["resolution_hours"] for r in rows) / len(rows), 1),
         "avg_first_response_min": round(sum(r["first_response_min"] for r in rows) / len(rows), 1),
         "by_category": Counter(r["category"] for r in rows).most_common(),
         "by_priority": Counter(r["priority"] for r in rows),
         "by_platform": Counter(r["platform"] for r in rows),
         "by_group": Counter(r["assigned_group"] for r in rows),
         "breaches": [(r["ticket"], r["priority"], r["tto_met"], r["ttr_met"]) for r in rows if r["sla_met"] == "No"]}
json.dump(stats, open(os.path.join(OUT, "ticket_stats.json"), "w"), indent=2)
print(json.dumps(stats, indent=1))
