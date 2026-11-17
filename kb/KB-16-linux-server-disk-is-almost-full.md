# KB-16: Linux server: disk is almost full

**Category:** Other  |  **Applies to:** Ubuntu servers

## The problem
A server says 'No space left on device' or df -h shows over 90%.

## Fix it yourself
1. Check usage: 'df -h'.
2. Find the big folders: 'sudo du -sh /var/* | sort -h'.
3. Look for old logs ('/var/log') and the package cache ('/var/cache/apt').
4. Run the disk cleanup script in dry-run mode first, then for real.
5. Verify with 'df -h' and note the freed space in the ticket.

**[SCREENSHOT]** The 'df -h' output before and after cleanup.

## Still not working?
If the space is used by an application's data, do not delete it; tell the owner.

## How to avoid it
Set up log rotation and monitor disk usage weekly.

## Open a ticket
Category and priority: Other, Medium
