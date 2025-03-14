import time
from scapy.all import sniff, IP, UDP
from collections import defaultdict
import subprocess
import sys
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

class DefenseMonitor:
    def __init__(self):
        self.interface = self._get_interface()
        self.udp_threshold = self._get_threshold()
        self.duration = self._get_duration()
        self.baseline = self._learn_baseline()
        
        self.counters = {
            'total_udp': 0,
            'unique_src_ips': defaultdict(int),
            'dst_ports': defaultdict(int),
            'start_time': time.time(),
            'blocked_ips': set()
        }

    def _get_interface(self):
        """Get network interface with validation"""
        while True:
            interface = input(Fore.BLUE + "Enter monitoring interface (e.g., eth0): " + Fore.MAGENTA)
            try:
                # Verify interface exists
                subprocess.check_output(f"ip link show {interface}", shell=True)
                return interface
            except subprocess.CalledProcessError:
                print(Fore.RED + f"Interface {interface} not found. Please try again.")

    def _get_threshold(self):
        """Validate UDP packet threshold"""
        while True:
            try:
                threshold = int(input(Fore.BLUE + "Enter UDP flood threshold (packets/sec): " + Fore.MAGENTA))
                if threshold >= 10:
                    return threshold
                print(Fore.RED + "Threshold must be ≥ 10 packets/sec")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

    def _get_duration(self):
        """Validate monitoring duration"""
        while True:
            try:
                duration = int(input(Fore.BLUE + "Enter monitoring duration (minutes, 1-60): " + Fore.MAGENTA))
                if 1 <= duration <= 60:
                    return duration * 60  # Convert to seconds
                print(Fore.RED + "Duration must be between 1-60 minutes")
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a number.")

    def _learn_baseline(self):
        """Establish normal traffic baseline"""
        print(Fore.YELLOW + "\n[!] Learning normal traffic baseline (10 seconds)...")
        baseline = {'udp_count': 0, 'unique_ips': set()}
        
        def baseline_callback(pkt):
            if pkt.haslayer(UDP):
                baseline['udp_count'] += 1
                baseline['unique_ips'].add(pkt[IP].src)
        
        sniff(iface=self.interface, prn=baseline_callback, timeout=10)
        return baseline

    def _packet_handler(self, pkt):
        """Analyze incoming packets"""
        if pkt.haslayer(UDP):
            self.counters['total_udp'] += 1
            src_ip = pkt[IP].src
            dst_port = pkt[UDP].dport
            
            self.counters['unique_src_ips'][src_ip] += 1
            self.counters['dst_ports'][dst_port] += 1

            # Auto-block suspicious IPs
            if self.counters['unique_src_ips'][src_ip] > self.udp_threshold:
                self._block_ip(src_ip)

    def _block_ip(self, ip):
        """Block IP using iptables"""
        if ip not in self.counters['blocked_ips']:
            print(Fore.RED + f"[!] Blocking suspicious IP: {ip}")
            subprocess.run(
                f"iptables -A INPUT -s {ip} -j DROP",
                shell=True,
                check=True
            )
            self.counters['blocked_ips'].add(ip)

    def _analyze_traffic(self):
        """Generate security report"""
        current_time = time.time()
        elapsed = current_time - self.counters['start_time']
        
        report = {
            'monitoring_duration': f"{elapsed:.2f} seconds",
            'total_udp_packets': self.counters['total_udp'],
            'unique_attack_ips': len(self.counters['unique_src_ips']),
            'top_source_ips': sorted(
                self.counters['unique_src_ips'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'targeted_ports': self.counters['dst_ports'],
            'blocked_ips': list(self.counters['blocked_ips']),
            'average_udp_rate': self.counters['total_udp'] / elapsed,
            'baseline_comparison': {
                'normal_udp_rate': self.baseline['udp_count'] / 10,
                'current_udp_rate': self.counters['total_udp'] / elapsed
            }
        }
        
        return report

    def _print_report(self, report):
        """Display formatted security report"""
        print(Fore.MAGENTA + "\n=== SECURITY REPORT ===")
        print(Fore.CYAN + f"Monitoring Duration: {report['monitoring_duration']}")
        print(Fore.CYAN + f"Total UDP Packets: {report['total_udp_packets']}")
        print(Fore.CYAN + f"Unique Source IPs: {report['unique_attack_ips']}")
        
        print(Fore.YELLOW + "\nTop 5 Suspicious IPs:")
        for ip, count in report['top_source_ips']:
            print(f"  {ip}: {count} packets")

        print(Fore.YELLOW + "\nTargeted Ports:")
        for port, count in report['targeted_ports'].items():
            print(f"  Port {port}: {count} packets")

        print(Fore.RED + "\nBlocked IPs:")
        print("\n".join(report['blocked_ips']) if report['blocked_ips'] else print("  None")

        print(Fore.GREEN + "\nTraffic Analysis:")
        print(f"Baseline UDP Rate: {report['baseline_comparison']['normal_udp_rate']:.2f} pps")
        print(f"Current UDP Rate: {report['baseline_comparison']['current_udp_rate']:.2f} pps")
        
        if report['baseline_comparison']['current_udp_rate'] > 3 * report['baseline_comparison']['normal_udp_rate']:
            print(Fore.RED + "ALERT: UDP flood detected!")
        else:
            print(Fore.GREEN + "Network status: Normal")

    def start_monitoring(self):
        """Main monitoring loop"""
        print(Fore.YELLOW + f"\n[!] Starting monitoring on {self.interface} for {self.duration/60} minutes")
        print(Fore.CYAN + f"UDP flood threshold: {self.udp_threshold} packets/sec")
        
        try:
            # Start packet capture in background
            sniff_thread = threading.Thread(
                target=sniff,
                kwargs={
                    'iface': self.interface,
                    'prn': self._packet_handler,
                    'timeout': self.duration
                }
            )
            sniff_thread.start()

            # Periodic reporting
            while sniff_thread.is_alive():
                time.sleep(5)
                report = self._analyze_traffic()
                self._print_report(report)
                print("\n" + "-"*50 + "\n")

        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Monitoring stopped by user")
        
        finally:
            self._cleanup()

    def _cleanup(self):
        """Remove firewall rules and final report"""
        print(Fore.YELLOW + "\n[!] Cleaning up firewall rules...")
        for ip in self.counters['blocked_ips']:
            subprocess.run(
                f"iptables -D INPUT -s {ip} -j DROP",
                shell=True,
                stderr=subprocess.DEVNULL
            )
        
        final_report = self._analyze_traffic()
        print(Fore.MAGENTA + "\n=== FINAL REPORT ===")
        self._print_report(final_report)

if __name__ == "__main__":
    print(Fore.MAGENTA + Style.BRIGHT + "\nNetwork Defense Monitor")
    print(Fore.BLUE + "UDP Flood Detection and Mitigation System\n")
    
    if not 'sudo' in sys.argv:
        print(Fore.RED + "Warning: Run with sudo for active mitigation capabilities")
    
    monitor = DefenseMonitor()
    monitor.start_monitoring()
