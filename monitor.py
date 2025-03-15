import time
import json
from scapy.all import sniff, IP, UDP, TCP
import psutil
from collections import defaultdict
from colorama import Fore, Style, init
import threading

# Initialize Colorama
init(autoreset=True)

# Traffic thresholds
PACKET_THRESHOLD = 100  # Max packets per second from a single IP
DATA_THRESHOLD_MB = 10  # Max data received from an IP (in MB)
MONITOR_DURATION = 10    # Check every 10 seconds

# Global variables for tracking traffic
traffic_data = defaultdict(lambda: {"packets": 0, "bytes": 0, "flagged": False})

# Monitor system performance
def monitor_system():
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        net_io = psutil.net_io_counters()
        
        print(Fore.CYAN + f"[SYSTEM] CPU: {cpu_usage}%, RAM: {ram_usage}%, Net I/O: {net_io.bytes_recv / 1e6:.2f} MB")
        time.sleep(5)

# Packet processing function
def process_packet(packet):
    if IP in packet:
        src_ip = packet[IP].src
        packet_size = len(packet)

        traffic_data[src_ip]["packets"] += 1
        traffic_data[src_ip]["bytes"] += packet_size

# Traffic monitoring function
def monitor_traffic():
    while True:
        print(Fore.YELLOW + "\n[MONITOR] Checking traffic for anomalies...\n")
        for ip, data in traffic_data.items():
            if data["packets"] > PACKET_THRESHOLD or (data["bytes"] / 1e6) > DATA_THRESHOLD_MB:
                if not data["flagged"]:
                    print(Fore.RED + f"[ALERT] Suspicious traffic detected from {ip}")
                    print(Fore.RED + f"        Packets: {data['packets']}, Data: {data['bytes'] / 1e6:.2f} MB\n")
                    data["flagged"] = True  # Mark as flagged
                    log_suspicious_activity(ip, data)

        # Reset traffic stats every MONITOR_DURATION seconds
        traffic_data.clear()
        time.sleep(MONITOR_DURATION)

# Log suspicious activity to a file
def log_suspicious_activity(ip, data):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ip": ip,
        "packets": data["packets"],
        "data_mb": round(data["bytes"] / 1e6, 2)
    }
    
    with open("suspicious_traffic_log.json", "a") as log_file:
        json.dump(log_entry, log_file, indent=2)
        log_file.write(",\n")

    print(Fore.GREEN + f"[LOGGED] Suspicious traffic from {ip} has been recorded.")

# Sniff network traffic
def start_sniffing():
    print(Fore.MAGENTA + Style.BRIGHT + "\n[DEFENDER] Monitoring network traffic...")
    sniff(filter="ip", prn=process_packet, store=False)

# Run monitoring functions in separate threads
if __name__ == "__main__":
    system_thread = threading.Thread(target=monitor_system, daemon=True)
    traffic_thread = threading.Thread(target=monitor_traffic, daemon=True)
    
    system_thread.start()
    traffic_thread.start()
    
    start_sniffing()
