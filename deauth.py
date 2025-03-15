import time
import random
import socket
from scapy.all import *
import json
import threading
from colorama import Fore, Style, init
import psutil

# Initialize Colorama
init(autoreset=True)

# ASCII Banner
print(Fore.RED + Style.BRIGHT + """
▓█████▄ ▓█████ ▄▄▄       █    ██ ▄▄▄█████▓ ██░ ██ 
▒██▀ ██▌▓█   ▀▒████▄     ██  ▓██▒▓  ██▒ ▓▒▓██░ ██▒
░██   █▌▒███  ▒██  ▀█▄  ▓██  ▒██░▒ ▓██░ ▒░▒██▀▀██░
░▓█▄   ▌▒▓█  ▄░██▄▄▄▄██ ▓▓█  ░██░░ ▓██▓ ░ ░▓█ ░██ 
░▒████▓ ░▒████▒▓█   ▓██▒▒▒█████▓   ▒██▒ ░ ░▓█▒░██▓
 ▒▒▓  ▒ ░░ ▒░ ░▒▒   ▓▒█░░▒▓▒ ▒ ▒   ▒ ░░    ▒ ░░▒░▒
 ░ ▒  ▒  ░ ░  ░ ▒   ▒▒ ░░░▒░ ░ ░     ░     ▒ ░▒░ ░
 ░ ░  ░    ░    ░   ▒    ░░░ ░ ░   ░       ░  ░░ ░
   ░       ░  ░     ░  ░   ░               ░  ░  ░
 ░                                DeAuth.v2                                        
""")


class TrafficGenerator:
    def __init__(self):
        self.running = False
        self.test_id = int(time.time())
        self.metrics = {
            "total_packets": 0,
            "total_bytes": 0,
            "start_time": None,
            "end_time": None,
            "ram_usage_mb": 0
        }

        # Get user input
        self.target_ip = self._get_valid_ip()
        self.target_port = self._get_valid_port()
        self.test_duration = self._get_valid_duration()
        self.min_packet_size, self.max_packet_size = self._get_valid_packet_sizes()

    def _get_valid_ip(self):
        while True:
            ip = input(Fore.BLUE + "Enter target IP address: " + Fore.MAGENTA)
            try:
                socket.inet_aton(ip)
                return ip
            except socket.error:
                print(Fore.RED + "Invalid IP address format. Please try again.")

    def _get_valid_port(self):
        while True:
            try:
                port = int(input(Fore.BLUE + "Enter target port (1-65535): " + Fore.MAGENTA))
                if 1 <= port <= 65535:
                    return port
                print(Fore.RED + "Port must be between 1 and 65535")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

    def _get_valid_duration(self):
        while True:
            try:
                duration = int(input(Fore.BLUE + "Enter test duration (1-3600 seconds): " + Fore.MAGENTA))
                if 1 <= duration <= 3600:
                    return duration
                print(Fore.RED + "Duration must be between 1 and 3600 seconds")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

    def _get_valid_packet_sizes(self):
        while True:
            try:
                min_size = int(input(Fore.BLUE + "Enter minimum packet size (64-65500 bytes): " + Fore.MAGENTA))
                max_size = int(input(Fore.BLUE + "Enter maximum packet size (64-65500 bytes): " + Fore.MAGENTA))
                if 64 <= min_size <= max_size <= 65500:
                    return min_size, max_size
                print(Fore.RED + "Invalid range. Minimum must be ≤ Maximum (64-65500)")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter numbers.")

    def _generate_packet(self):
        """Create a UDP packet with randomized payload"""
        ip_layer = IP(dst=self.target_ip)
        udp_layer = UDP(
            sport=random.randint(1024, 65535),
            dport=self.target_port
        )

        payload_size = random.randint(self.min_packet_size, self.max_packet_size)
        payload = bytes([random.randint(0, 255) for _ in range(payload_size)])

        return ip_layer / udp_layer / Raw(load=payload)

    def _send_packets(self):
        """Send packets continuously for the test duration"""
        start_time = time.time()
        while self.running and (time.time() - start_time) < self.test_duration:
            packet = self._generate_packet()
            send(packet, verbose=False)
            self.metrics["total_packets"] += 1
            self.metrics["total_bytes"] += len(packet)
            print(Fore.GREEN + f"[+] Sent packet {self.metrics['total_packets']} to {self.target_ip}:{self.target_port}")

    def _monitor_ram(self):
        """Monitor RAM usage in the background"""
        while self.running:
            self.metrics["ram_usage_mb"] = round(psutil.Process().memory_info().rss / 1024 ** 2, 2)
            time.sleep(1)

    def _save_report(self):
        """Generate JSON test report"""
        report = {
            "test_id": self.test_id,
            "target": f"{self.target_ip}:{self.target_port}",
            "duration_sec": self.test_duration,
            "packet_size_range": f"{self.min_packet_size}-{self.max_packet_size}",
            "metrics": self.metrics
        }
        with open(f"test_report_{self.test_id}.json", "w") as f:
            json.dump(report, f, indent=2)

    def start_test(self):
        """Run the network traffic test"""
        if not self._verify_permissions():
            return

        print(Fore.YELLOW + "\n[!] Starting authorized network test")
        print(Fore.CYAN + f"• Target: {self.target_ip}:{self.target_port}")
        print(Fore.CYAN + f"• Duration: {self.test_duration}s")
        print(Fore.CYAN + f"• Packet Size: {self.min_packet_size}-{self.max_packet_size} bytes\n")

        self.running = True
        self.metrics["start_time"] = time.time()

        # Start RAM monitoring thread
        ram_thread = threading.Thread(target=self._monitor_ram)
        ram_thread.start()

        # Start packet sending
        self._send_packets()

        # Stop monitoring
        self.running = False
        ram_thread.join()

        self.metrics["end_time"] = time.time()
        self._save_report()
        print(Fore.GREEN + f"\n[+] Test complete. Report saved to test_report_{self.test_id}.json")
        print(Fore.CYAN + f"[INFO] Peak RAM usage: {self.metrics['ram_usage_mb']} MB")

    def _verify_permissions(self):
        """Ethical requirement check"""
        print(Fore.RED + "\nETHICAL REQUIREMENTS:")
        print("1. Written authorization from network owner")
        print("2. Isolated testing environment")
        print("3. No production services impacted")
        print("4. Proper network containment measures\n")
        
        consent = input(Fore.WHITE + "[?] Confirm all requirements are met (yes/no): ").lower()
        if consent != "yes":
            print(Fore.RED + "[!] Test aborted - ethical requirements not met")
            return False
        return True

if __name__ == "__main__":
    print(Fore.MAGENTA + Style.BRIGHT + "\nNetwork Traffic Generator - Authorized Testing Only")
    print(Fore.BLUE + "This tool must only be used with explicit written authorization")
    print(Fore.RED + "Unauthorized use is illegal and unethical\n")
    
    generator = TrafficGenerator()
    generator.start_test()
