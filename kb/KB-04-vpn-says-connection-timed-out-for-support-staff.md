# KB-04: VPN says 'connection timed out' (for support staff)

**Category:** Network and VPN  |  **Applies to:** Windows 11; VPN service desk staff

## The problem
The user has internet but the VPN client cannot connect.

## Fix it yourself
1. Test the internet: 'ping 8.8.8.8' in a terminal.
2. Test DNS: 'ping google.com'. If only this fails, see KB-15.
3. Ask the user to connect through a mobile hotspot. If the VPN connects, the user's network blocks the VPN port.
4. Change the user's profile to use TCP 443, which is rarely blocked.
5. Check the VPN gateway log for the user's name and confirm the session appears.

**[SCREENSHOT]** The VPN profile setting that selects TCP 443.

## Still not working?
If the hotspot also fails, check the gateway status and the user's account (locked or MFA problem).

## How to avoid it
Document the port and protocol in the VPN profile template.

## Open a ticket
Category and priority: Network and VPN (assigned to Infrastructure and Network L2)
