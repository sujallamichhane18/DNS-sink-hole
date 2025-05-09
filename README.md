Here’s a `README.md` file for your **DNS Sinkhole Project**, structured for presentation, documentation, and GitHub use:

---

```markdown
# 🛡️ DNS Sinkhole with Flask & dnsmasq

A lightweight, Python-based DNS Sinkhole solution that helps block access to malicious or unwanted domains across your network. Featuring a web dashboard, blacklist control, and automatic updates from trusted threat intelligence sources.

---

## 📌 Features

- 🧠 Web dashboard (Flask) to manage and visualize DNS queries
- 🔒 Domain blacklist management (`blacklist.json`)
- 📥 Auto-updates from [Abuse.ch URLHaus](https://urlhaus.abuse.ch/)
- 🧾 SQLite logging of DNS queries (domain, time, client IP, action)
- 🚀 Works with `dnsmasq` for system-wide DNS sinkholing

---

## 📂 Project Structure

```

dns-sinkhole/
│
├── main.py                  # Main Flask server
├── blacklist.json           # Domain blocklist
├── sinkhole.db              # SQLite log DB
├── templates/
│   └── index.html           # Web dashboard
├── static/
│   └── style.css            # Dashboard styling
├── utils/
│   └── dnsmasq\_blocklist\_generator.py  # Converts JSON to dnsmasq-compatible config
├── blocklist.hosts          # Optional: /etc/hosts format blocklist
└── README.md

````

---

## ⚙️ Installation

### ✅ Prerequisites

- Python 3.7+
- `dnsmasq` (or use manually via `/etc/hosts`)
- Flask

### 🐍 Setup

```bash
# Clone repo
git clone https://github.com/sujallamichhane18/dns-sink-hole.git
cd dns-sink-hole

# Install dependencies
pip install flask requests

# Run the Flask server
python main.py
````

---

## 🌐 Access Web UI

Open in browser:

```
http://<your-linux-ip>:5000
```

---

## 🔁 DNS Configuration

### On Devices:

Manually set your phone, PC, or router to use your Linux system as its DNS server:

```
DNS: <your-linux-ip>
```

### On Sinkhole Host (optional):

Route unknown domains to 8.8.8.8:

```bash
sudo apt install dnsmasq

# In /etc/dnsmasq.conf or /etc/dnsmasq.d/sinkhole.conf
addn-hosts=/path/to/blocklist.hosts
server=8.8.8.8
log-queries
```

Then restart:

```bash
sudo systemctl restart dnsmasq
```

---

## 🔄 Auto-Update Blocklist (Optional)

Use `crontab -e` to automate updates:

```
0 * * * * python3 /path/to/main.py --update-blacklist
```

---





## 👨‍💻 Author

**Sujal Lamichhane** — [Your Portfolio](#)

---

```

---

