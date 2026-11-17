# Auto Dealer IT Helpdesk Setup (GLPI) - Week 4 project

Fictional EV fleet operator in Ahmedabad, 80 employees. All people, serial numbers and ticket data are simulated.

| Folder | Content |
|---|---|
| `kb/` | 18 knowledge-base articles (Markdown) + INDEX |
| `data/` | `tickets.csv` (40 simulated tickets), `ticket_stats.json`, `new_hires.csv` |
| `scripts/` | `disk_cleanup.sh` (Bash), `New-EmployeeOnboarding.ps1` (PowerShell), generators |
| `glpi_setup/` | `rebuild_glpi.py` - recreates categories, groups, technicians, SLAs and rules via the GLPI REST API |
| `docs/` | Asset inventory, ticket log, monthly report, KB (Word/Excel) |
| `screenshots/` | GLPI configuration screenshots (added by the author) |

## Scripts
```
./scripts/disk_cleanup.sh                 # dry run (default), nothing is deleted
./scripts/disk_cleanup.sh --apply --days 7
.\scripts\New-EmployeeOnboarding.ps1 -CsvPath .\data\new_hires.csv -WhatIf
.\scripts\New-EmployeeOnboarding.ps1 -CsvPath .\data\new_hires.csv -Mode Simulation
```
Testing status: `disk_cleanup.sh` was tested in a sandbox. `New-EmployeeOnboarding.ps1` and `rebuild_glpi.py` have not been run by the author's tooling against a live system.
