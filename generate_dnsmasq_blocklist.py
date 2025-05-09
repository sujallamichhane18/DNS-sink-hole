import json

with open('blacklist.json', 'r') as f:
    domains = json.load(f)

with open('/etc/dnsmasq.blocklist', 'w') as f:
    for domain in domains:
        f.write(f"0.0.0.0 {domain}\n")
