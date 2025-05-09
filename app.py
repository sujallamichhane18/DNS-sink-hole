import socketserver
import json
import os
import datetime
import sqlite3
import dns.message
import dns.query
import dns.resolver

DB_FILE = 'sinkhole.db'
BLACKLIST_FILE = 'blocklist.json'
UPSTREAM_DNS = '8.8.8.8'

# ------------------ DB Setup ------------------ #
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS dns_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT,
        timestamp TEXT,
        client_ip TEXT,
        action TEXT
    )''')
    conn.commit()
    conn.close()

# ------------------ Blacklist ------------------ #
def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return []
    with open(BLACKLIST_FILE, 'r') as f:
        return json.load(f)

blacklist = set(load_blacklist())
init_db()

# ------------------ DNS Handler ------------------ #
class DNSHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        query = dns.message.from_wire(data)
        domain = str(query.question[0].name).rstrip('.')
        client_ip = self.client_address[0]

        if domain in blacklist:
            response = dns.message.make_response(query)
            response.set_rcode(3)  # NXDOMAIN
            action = 'BLOCKED'
        else:
            try:
                response = dns.query.udp(query, UPSTREAM_DNS, timeout=2)
                action = 'FORWARDED'
            except Exception:
                response = dns.message.make_response(query)
                response.set_rcode(2)  # SERVFAIL
                action = 'ERROR'

        log_query(domain, client_ip, action)
        socket.sendto(response.to_wire(), self.client_address)

def log_query(domain, client_ip, action):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO dns_logs (domain, timestamp, client_ip, action) VALUES (?, ?, ?, ?)",
              (domain, datetime.datetime.now().isoformat(), client_ip, action))
    conn.commit()
    conn.close()

# ------------------ Server Start ------------------ #
if __name__ == '__main__':
    print("[*] DNS Sinkhole running on port 53 (UDP)...")
    with socketserver.UDPServer(('', 53), DNSHandler) as server:
        server.serve_forever()
