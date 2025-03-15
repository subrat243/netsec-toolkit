# **NetSec ToolKit - Network Traffic Generator & Defensive Monitor**  

🚀 **DeAuth** is a **network traffic generator** for educational and authorized testing, alongside a **defensive monitoring script** to detect and prevent abnormal network activity. These scripts are built using Python and Scapy to help cybersecurity professionals, researchers, and network administrators analyze network traffic effectively.  

---

## **⚠️ Disclaimer**  
> **This tool is for educational and authorized testing purposes only.**  
> Unauthorized usage against networks or individuals is illegal and unethical.  
> The developer is not responsible for any misuse of this software.  

---

## **🛠 Features**
### **1️⃣ Network Traffic Generator (`deauth.py`)**
✅ **Generates Realistic UDP Traffic** – Creates packets with customizable size and rate.  
✅ **Multi-Core Processing (Limited to 6 cores)** – Ensures efficient load testing.  
✅ **RAM Usage Control** – Prevents excessive resource consumption.  
✅ **Live Process Updates** – Displays real-time progress on the terminal.  
✅ **Generates JSON Test Reports** – Saves network test results automatically.  
✅ **Supports Custom Payloads** – Users can provide custom packet payloads for simulation.  
✅ **Adjustable Packet Rate** – Control how fast packets are sent.  
✅ **Targeted Port Flooding** – Simulates high-traffic conditions on specific ports.  
✅ **Auto-Termination on Network Saturation** – Prevents excessive congestion.  

---

### **2️⃣ Defensive Monitor (`monitor.py`)**
🛡 **Monitors Real-Time Network Traffic** – Captures incoming packets and tracks suspicious activity.  
🔍 **Detects High Traffic Volume** – Flags potential DoS or network anomalies.  
📊 **Tracks System Resource Usage** – Monitors CPU, RAM, and Network I/O.  
⚠️ **Alerts on Unusual Activity** – Warns when a single IP sends excessive traffic.  
📁 **Logs Suspicious Activity** – Saves flagged events to a JSON report.  
🛑 **Auto-Blocking Feature** – Can blacklist and drop packets from malicious IPs.  
📌 **Whitelist & Blacklist Support** – Allows users to specify trusted and blocked IPs.  
📊 **Graphical Report Generation** – Creates network activity reports using Matplotlib.  
🔄 **Real-Time Logging Dashboard** – View network threats as they occur.  

---

## **📦 Installation & Requirements**
**Prerequisites**:  
- **Python 3.x**  
- **pip (Python package manager)**  

**Required Python Libraries**:
```bash
pip install scapy psutil colorama matplotlib
```

---

## **🚀 How to Use**
### **1️⃣ Network Traffic Generator**
⚠️ **Ensure you have permission before running network tests.**  

🔹 **Run the script**:  
```bash
python3 deauth.py
```
🔹 **Provide required inputs** (Target IP, Port, Packet Size, Duration, etc.).  
🔹 **Live updates will be displayed on the terminal.**  
🔹 **A JSON report will be saved after the test.**  

---

### **2️⃣ Defensive Network Monitor**
🔹 **Run the script**:  
```bash
python3 monitor.py
```
🔹 **The script will start monitoring network traffic in real-time.**  
🔹 **Any suspicious activity will be flagged and logged in `suspicious_traffic_log.json`.**  
🔹 **CPU, RAM, and Network I/O stats will be displayed.**  
🔹 **Optional Auto-Blocking will prevent attacks.**  

---

## **📜 Example Usage**
### **1️⃣ Traffic Generator Output**
```
▓█████▄ ▓█████ ▄▄▄       █    ██ ▄▄▄█████▓ ██░ ██ 
▒██▀ ██▌▓█   ▀▒████▄     ██  ▓██▒▓  ██▒ ▓▒▓██░ ██▒
░██   █▌▒███  ▒██  ▀█▄  ▓██  ▒██░▒ ▓██░ ▒░▒██▀▀██░
░▓█▄   ▌▒▓█  ▄░██▄▄▄▄██ ▓▓█  ░██░░ ▓██▓ ░ ░▓█ ░██ 
░▒████▓ ░▒████▒▓█   ▓██▒▒▒█████▓   ▒██▒ ░ ░▓█▒░██▓
 ▒▒▓  ▒ ░░ ▒░ ░▒▒   ▓▒█░░▒▓▒ ▒ ▒   ▒ ░░    ▒ ░░▒░▒
 ░ ▒  ▒  ░ ░  ░ ▒   ▒▒ ░░░▒░ ░ ░     ░     ▒ ░▒░ ░
 ░ ░  ░    ░    ░   ▒    ░░░ ░ ░   ░       ░  ░░ ░
   ░       ░  ░     ░  ░   ░               ░  ░  ░
 ░                                DeAuth.v1   

[!] Starting authorized educational test
• Target: 192.168.1.10:80
• Duration: 60s
• Packet Size: 64-1024 bytes
• Spoofing: Disabled
• Cores used: 6
```

### **2️⃣ Defensive Monitor Output**
```
[DEFENDER] Monitoring network traffic...

[SYSTEM] CPU: 12.5%, RAM: 43.2%, Net I/O: 1.23 MB

[MONITOR] Checking traffic for anomalies...

[ALERT] Suspicious traffic detected from 192.168.1.50
        Packets: 250, Data: 15.6 MB

[LOGGED] Suspicious traffic from 192.168.1.50 has been recorded.

[ACTION] IP 192.168.1.50 added to blacklist.
```

---

## **🤝 Contributing**
Want to improve this project? Follow these steps:  
1. **Fork** the repository.  
2. **Create** a new branch (`feature-newfeature`).  
3. **Commit** your changes.  
4. **Push** to your branch.  
5. **Submit** a Pull Request.  

---

**⚡ Stay Ethical. Stay Secure. Happy Hacking!** 🚀
