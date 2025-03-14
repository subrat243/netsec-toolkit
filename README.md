# NetSec Toolkit: Offensive-Defensive Network Testing Suite

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-GPL--3.0-red)
![Status](https://img.shields.io/badge/Status-Educational%20Use%20Only-lightgrey)

A dual-tool suite for **authorized network testing** and **defensive monitoring**, designed for cybersecurity education and professional training.

## 📦 Contents
- `deauth.py` - Realistic UDP stress tester with IP spoofing
- `monitor.py` - AIO defensive monitoring & mitigation system
- Sample reports and firewall rule templates

## ⚠️ Critical Warning
**This toolkit must ONLY be used:**
- On networks you own/administrate
- With written authorization
- In isolated lab environments
- For educational/research purposes

Unauthorized use violates laws and ethical standards.

## ✨ Features

### Offensive Tool (Stress Tester)
- 🎭 Realistic UDP traffic patterns
- 🌐 IP spoofing with customizable intervals
- 📊 Multi-core packet generation
- 📝 Automatic JSON reporting
- 🛡️ Ethical permission verification

### Defensive Tool (Monitor)
- 🚨 Real-time UDP flood detection
- 🔥 Active IP blocking (iptables integration)
- 📈 Baseline traffic learning
- 🕵️ Forensic reporting
- 🧹 Automatic rule cleanup

## 🛠️ Installation

**Requirements:**
- Python 3.8+
- Root privileges (for raw socket operations)
- Test network environment

```bash
# Clone repository
git clone https://github.com/yourusername/netsec-toolkit.git
cd netsec-toolkit

# Install dependencies
pip install scapy colorama

# Set executable permissions
chmod +x traffic_generator.py defense_monitor.py
```

🚀 Usage
Stress Tester (Offensive)
```bash
sudo ./deauth.py
```

**Interactive Setup:**

1. Enter target IP and port

2. Set test duration (1-3600s)

3. Configure packet sizes (64-65500 bytes)

4. Set IP spoof interval (1-60s)

5. Confirm ethical requirements

**Example Report:**

```json
{
  "test_id": 1678901234,
  "target": "192.168.1.100:80",
  "duration_sec": 300,
  "metrics": {
    "total_packets": 124500,
    "total_bytes": 156MB,
    "spoofed_ips_used": 42
  }
}
```

**Defense Monitor (Defensive)**
```bash
sudo ./monitor.py
```

**Workflow:**

1. Select monitoring interface (e.g., eth0)

2. Set UDP flood threshold (packets/sec)

3. Set monitoring duration (1-60 mins)

4. System learns normal traffic baseline

5. Automatic detection/mitigation engages

**Sample Output:**

```
=== SECURITY REPORT ===
Monitoring Duration: 157.32 seconds
Total UDP Packets: 24,850
Unique Source IPs: 38

Top 5 Suspicious IPs:
  192.168.5.21: 4200 packets
  10.0.0.153: 3800 packets

Blocked IPs:
  192.168.5.21
  10.0.0.153

Traffic Analysis:
Baseline UDP Rate: 12.4 pps
Current UDP Rate: 158.2 pps
ALERT: UDP flood detected!
```

⚖️ Legal & Ethical Requirements
1. **Written Authorization** - Signed document from network owner

2. **Network Isolation** - Use VLANs/air-gapped networks

3. **Time Restrictions** - Pre-approved testing windows

4. **Data Handling** - Delete logs after 24 hours

5. **Non-Disclosure** - Protect identified vulnerabilities

📚 Educational Value
Understand UDP flood attack vectors

- Analyze spoofed traffic patterns

- Practice defensive configuration:

```bash
# Example iptables rate limiting
iptables -A INPUT -p udp -m state --state NEW -m limit --limit 100/second -j ACCEPT
iptables -A INPUT -p udp -j DROP
```
- Develop incident response skills

📋 Technical Specs
- **Python**: 3.8+ (async I/O, multiprocessing)

- **Dependencies**: Scapy 2.4.5+, Colorama 0.4.4+

- **OS**: Linux (Kernel 4.15+ recommended)

- **License**: GPL-3.0

**Disclaimer**: This project is for educational purposes only. The developers assume no liability for unauthorized use. Always obtain proper authorization before testing any network system. This README provides comprehensive documentation while emphasizing ethical requirements. It includes:
- Clear warnings about legal responsibilities
- Technical setup instructions
- Usage examples for both tools
- Defensive configuration guidance
- Compliance documentation structure
- Educational context for proper use

