#!/usr/bin/env python3
"""Rebuild the helpdesk configuration in a fresh GLPI through its REST API.

Creates: ITIL categories, support groups, technician users (linked to groups, Technician profile),
service levels (TTO/TTR), and the ticket business rules (default rule first, specific rules after).

STATUS: written against the GLPI 10 REST API documentation; it has NOT been run against a live
GLPI by the author. Run with --dry-run first, then without. Safe to re-run: existing names are skipped.

Before running, in GLPI: Setup > General > API > enable REST API and "login with credentials",
then Setup > General > API > add an API client (allow your IP) and copy its App-Token.

Usage:
  python3 rebuild_glpi.py --url http://localhost:8080 --app-token TOKEN --user glpi --password '...' [--dry-run]
"""
import argparse, json, sys, urllib.request, urllib.error, urllib.parse, base64, secrets, string

CATEGORIES = ["Accounts and Access", "Network and VPN", "Hardware", "Software and Licences", "Email",
              "Printers and Scanners", "Fleet and Charging Software", "Security Incident", "New Joiner / Leaver", "Other"]
GROUPS = ["Service Desk L1", "Infrastructure and Network L2", "Fleet Applications Support"]
TECHS = [("priya.patel", "Priya", "Patel", "Service Desk L1"), ("rahul.shah", "Rahul", "Shah", "Infrastructure and Network L2"),
         ("karan.mehta", "Karan", "Mehta", "Fleet Applications Support")]
# category -> group (default rule sends everything to L1, specific rules override)
ROUTING = {"Network and VPN": "Infrastructure and Network L2", "Security Incident": "Infrastructure and Network L2",
           "Fleet and Charging Software": "Fleet Applications Support"}
# name, type (1 = time to own, 0 = time to resolve), minutes
SLAS = [("TTO Urgent 15 min", 1, 15), ("TTO High 30 min", 1, 30), ("TTO Medium 2 h", 1, 120), ("TTO Low 4 h", 1, 240),
        ("TTR Urgent 4 h", 0, 240), ("TTR High 8 h", 0, 480), ("TTR Medium 24 h", 0, 1440), ("TTR Low 72 h", 0, 4320)]
PRIORITY = {"Urgent": 5, "High": 4, "Medium": 3, "Low": 2}  # GLPI: 1 very low, 2 low, 3 medium, 4 high, 5 very high

class Glpi:
    def __init__(self, url, app, dry):
        self.base = url.rstrip("/") + "/apirest.php"; self.app = app; self.dry = dry; self.token = None
    def call(self, method, path, body=None, headers=None, write=False):
        h = {"App-Token": self.app, "Content-Type": "application/json"}
        if self.token: h["Session-Token"] = self.token
        h.update(headers or {})
        if self.dry and write:
            print("  [dry-run]", method, path, json.dumps(body)[:150]); return {"id": -1}
        req = urllib.request.Request(self.base + path, method=method, headers=h, data=json.dumps(body).encode() if body is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = r.read().decode(); return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            sys.exit("HTTP %s on %s %s: %s" % (e.code, method, path, e.read().decode()[:300]))
    def login(self, user, pw):
        cred = base64.b64encode(("%s:%s" % (user, pw)).encode()).decode()
        self.token = self.call("GET", "/initSession", headers={"Authorization": "Basic " + cred})["session_token"]
    def find(self, itemtype, name, field=1):
        q = "/search/%s?criteria[0][field]=%d&criteria[0][searchtype]=equals&criteria[0][value]=%s&forcedisplay[0]=2" % (itemtype, field, urllib.parse.quote(name))
        r = self.call("GET", q)
        return int(r["data"][0]["2"]) if r.get("totalcount", 0) else None
    def ensure(self, itemtype, name, fields, label=None):
        found = self.find(itemtype, name) if not self.dry else None
        if found: print("  exists :", label or name); return found
        r = self.call("POST", "/" + itemtype, {"input": dict(fields, name=name)}, write=True)
        print("  created:", label or name); return r.get("id")

def main():
    a = argparse.ArgumentParser(); a.add_argument("--url", required=True); a.add_argument("--app-token", required=True)
    a.add_argument("--user", required=True); a.add_argument("--password", required=True); a.add_argument("--dry-run", action="store_true")
    o = a.parse_args(); g = Glpi(o.url, o.app_token, o.dry_run); g.login(o.user, o.password)

    print("Categories"); cat = {c: g.ensure("ITILCategory", c, {"is_incident": 1, "is_request": 1}) for c in CATEGORIES}
    print("Groups"); grp = {n: g.ensure("Group", n, {"is_assign": 1, "is_requester": 0}) for n in GROUPS}

    print("Technician users (temporary passwords are printed once; change them at first login)")
    profs = g.call("GET", "/Profile") if not o.dry_run else []
    tech_profile = next((p["id"] for p in profs if p["name"].lower() == "technician"), None)
    alphabet = string.ascii_letters + string.digits
    for login, first, last, group in TECHS:
        pw = "".join(secrets.choice(alphabet) for _ in range(16)) + "!1"
        uid = g.ensure("User", login, {"realname": last, "firstname": first, "password": pw, "password2": pw,
                                       "_profiles_id": tech_profile or 6, "is_active": 1}, label=login + "  password: " + pw)
        g.call("POST", "/Group_User", {"input": {"users_id": uid, "groups_id": grp[group]}}, write=True)
        if tech_profile: g.call("POST", "/Profile_User", {"input": {"users_id": uid, "profiles_id": tech_profile, "entities_id": 0, "is_recursive": 1}}, write=True)

    print("Service levels (calendar: none = 24/7)")
    sla_ids = {}
    for name, typ, minutes in SLAS:
        sla_ids[name] = g.ensure("SLA", name, {"type": typ, "number_time": minutes, "definition_time": "minute", "calendars_id": 0})

    print("Ticket rules (rank: default first, then specific rules so they override)")
    def rule(name, criteria, actions):
        rid = g.ensure("RuleTicket", name, {"sub_type": "RuleTicket", "match": "AND", "is_active": 1, "entities_id": 0})
        for crit, cond, pattern in criteria:
            g.call("POST", "/RuleCriteria", {"input": {"rules_id": rid, "criteria": crit, "condition": cond, "pattern": pattern}}, write=True)
        for field, value in actions:
            g.call("POST", "/RuleAction", {"input": {"rules_id": rid, "action_type": "assign", "field": field, "value": value}}, write=True)
    # condition 6 = regular expression matches, 0 = is
    rule("Default - Service Desk L1", [("itilcategories_id", 6, "/.*/")], [("_groups_id_assign", grp["Service Desk L1"])])
    for category, group in ROUTING.items():
        rule("Route %s" % category, [("itilcategories_id", 0, cat[category])], [("_groups_id_assign", grp[group])])
    # priority -> SLA (the ticket priority field is 'priority')
    for label, value in PRIORITY.items():
        rule("SLA %s" % label, [("priority", 0, value)], [("slas_id_tto", sla_ids["TTO %s %s" % (label, {'Urgent':'15 min','High':'30 min','Medium':'2 h','Low':'4 h'}[label])]),
                                                           ("slas_id_ttr", sla_ids["TTR %s %s" % (label, {'Urgent':'4 h','High':'8 h','Medium':'24 h','Low':'72 h'}[label])])])
    print("\nDone. Next, check in GLPI: Administration > Rules > Business rules for tickets.")
    print("The ranking of rules must be: Default first, specific rules after it. Use 'Test rules engine' to confirm.")
    print("Note: rules created through the API are appended in creation order, which matches this requirement.")
    g.call("GET", "/killSession")

if __name__ == "__main__": main()
