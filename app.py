from flask import Flask, render_template, request, jsonify
import os, json, datetime, sqlite3, requests, subprocess

app = Flask(__name__)
DB_FILE = 'sinkhole.db'
BLACKLIST_FILE = 'blacklist.json'
BLOCKLIST_HOSTS = '/etc/dnsmasq.d/blocklist.hosts'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS dns_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            timestamp TEXT,
            client_ip TEXT,
            action TEXT
        )''')

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE): return []
    with open(BLACKLIST_FILE, 'r') as f: return json.load(f)

def save_blacklist(blacklist):
    with open(BLACKLIST_FILE, 'w') as f:
        json.dump(blacklist, f, indent=2)
    update_dnsmasq_blocklist(blacklist)

def update_dnsmasq_blocklist(blacklist):
    with open(BLOCKLIST_HOSTS, 'w') as f:
        for domain in blacklist:
            f.write(f"address=/{domain}/127.0.0.1\n")
    subprocess.run(["sudo", "systemctl", "restart", "dnsmasq"])

def fetch_blacklist_from_abusech():
    url = "https://urlhaus.abuse.ch/downloads/text/"
    domains = set()
    try:
        response = requests.get(url, timeout=10)
        for line in response.text.splitlines():
            if not line.startswith('#') and line.strip():
                parts = line.strip().split('/')
                if len(parts) > 2:
                    domains.add(parts[2])
    except Exception as e:
        print("Error fetching from Abuse.ch:", e)
    return list(domains)

@app.route('/')
def index():
    with sqlite3.connect(DB_FILE) as conn:
        logs = conn.execute("SELECT domain, timestamp, client_ip, action FROM dns_logs ORDER BY timestamp DESC LIMIT 100").fetchall()
    return render_template('index.html', logs=logs, blacklist=load_blacklist())

@app.route('/api/add_domain', methods=['POST'])
def add_domain():
    domain = request.form['domain'].strip().lower()
    blacklist = load_blacklist()
    if domain not in blacklist:
        blacklist.append(domain)
        save_blacklist(blacklist)
    return jsonify(success=True)

@app.route('/api/remove_domain', methods=['POST'])
def remove_domain():
    domain = request.form['domain'].strip().lower()
    blacklist = load_blacklist()
    if domain in blacklist:
        blacklist.remove(domain)
        save_blacklist(blacklist)
    return jsonify(success=True)

@app.route('/api/update_blacklist', methods=['POST'])
def update_blacklist():
    fetched = fetch_blacklist_from_abusech()
    current = set(load_blacklist())
    updated = list(current.union(set(fetched)))
    save_blacklist(updated)
    return jsonify(success=True, added=len(updated) - len(current))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
