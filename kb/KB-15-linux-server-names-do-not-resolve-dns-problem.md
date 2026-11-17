# KB-15: Linux server: names do not resolve (DNS problem)

**Category:** Network and VPN  |  **Applies to:** Ubuntu 24.04/26.04 servers

## The problem
'ping 8.8.8.8' works but 'ping google.com' says 'Temporary failure in name resolution'.

## Fix it yourself
1. Check the connection: 'ip a' and 'ip route'.
2. Check DNS: 'resolvectl status'. If no DNS server is listed, DNS is the problem.
3. Edit the netplan file in '/etc/netplan/' and add the nameservers under the interface.
4. Apply: 'sudo netplan apply'. Test again with 'ping google.com'.
5. Document the change in the ticket.

**[SCREENSHOT]** The output of 'resolvectl status'.

## Still not working?
If DNS servers are listed but the lookup fails, test another server: 'resolvectl query google.com'.

## How to avoid it
Keep a copy of the working netplan file before editing.

## Open a ticket
Category and priority: Network and VPN (Infrastructure and Network L2)
