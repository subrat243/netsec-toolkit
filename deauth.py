import time
import random
import socket
import sys
import json
import threading
import ipaddress
from multiprocessing import Pool, cpu_count
from scapy.all import *
from scapy.error import Scapy_Exception
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
            "errors": 0,
            "spoofed_ips_used": 0,
            "start_time": None,
            "end_time": None,
            "public_ip_warning": False
        }

        try:
            self._validate_environment()
            self._get_user_input()
            self._verify_network_scope()
        except KeyboardInterrupt:
            self._safe_exit("Operation cancelled by user")
        except Exception as e:
            self._handle_error(f"Initialization failed: {str(e)}", exit=True)

    def _validate_environment(self):
        """Check system prerequisites"""
        if os.geteuid() != 0:
            raise PermissionError("Root privileges required. Run with sudo.")
            
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8 or higher required")

    def _verify_network_scope(self):
        """Verify network scope and get confirmation"""
        self.target_is_public = False
        try:
            target_ip = ipaddress.IPv4Address(self.target_ip)
            if target_ip.is_global:
                self.metrics["public_ip_warning"] = True
                print(Fore.RED + "\n[!] WARNING: Public IP Address Detected!")
                print(Fore.YELLOW + "Legal requirements for public network testing:")
                print("1. Written authorization from network owner")
                print("2. ISP coordination for bandwidth testing")
                print("3. Compliance with local regulations")
                
                confirm = input(Fore.RED + "Type 'CONFIRM PUBLIC' to proceed: ")
                if confirm != "CONFIRM PUBLIC":
                    raise RuntimeError("Public IP test cancelled")
                
                self.target_is_public = True
                print(Fore.YELLOW + "[!] Starting public network test in 5 seconds...")
                time.sleep(5)

        except ipaddress.AddressValueError:
            raise ValueError("Invalid IP address format")

    def _get_user_input(self):
        """Gather and validate all user inputs"""
        try:
            self.target_ip = self._get_valid_ip()
            self.target_port = self._get_valid_port()
            self.test_duration = self._get_valid_duration()
            self.spoof_interval = self._get_valid_spoof_interval()
            self.min_packet_size, self.max_packet_size = self._get_valid_packet_sizes()
        except ValueError as ve:
            raise ValueError(f"Invalid input: {str(ve)}")
        except socket.error as se:
            raise RuntimeError(f"Network error: {str(se)}")

    def _get_valid_ip(self):
        """Validate IP address format"""
        while True:
            ip = input(Fore.BLUE + "Enter target IP address: " + Fore.MAGENTA)
            try:
                socket.inet_aton(ip)
                return ip
            except socket.error:
                print(Fore.RED + "Invalid IP address format. Please try again.")

    # [Keep other input validation methods unchanged]

    def _verify_permissions(self):
        """Enhanced authorization check"""
        print(Fore.RED + "\nETHICAL REQUIREMENTS:")
        print("1. Written authorization from network owner")
        print("2. Isolated testing environment" + 
              (" (NOT APPLICABLE - PUBLIC IP)" if self.target_is_public else ""))
        print("3. No production services impacted")
        print("4. Proper network containment measures")
        
        if self.target_is_public:
            print(Fore.RED + "5. ISP coordination for bandwidth testing")
            print(Fore.RED + "6. Compliance with CFAA and local laws")
        
        consent = input(Fore.WHITE + "[?] Confirm all requirements are met (yes/no): ").lower()
        if consent != "yes":
            print(Fore.RED + "[!] Test aborted - ethical requirements not met")
            return False
            
        if self.target_is_public:
            token = input("Enter legal authorization code: ")
            if len(token) < 10:
                print(Fore.RED + "[!] Invalid authorization code")
                return False
                
        return True

    def _send_packets(self, count=100):
        """Modified send method with public IP precautions"""
        try:
            if self.target_is_public:
                # Rate limit for public networks
                time.sleep(0.01 * random.random())
                
            packets = [p for p in (self._generate_packet() for _ in range(count)) if p]
            
            # Additional validation for public targets
            if self.target_is_public:
                for p in packets:
                    if p[IP].src == self.target_ip:
                        self.metrics["errors"] += 1
                        raise ValueError("Self-spoofing protection triggered")
            
            send_result = send(packets, verbose=0)
            actual_sent = len(send_result)
            
            self.metrics["total_packets"] += actual_sent
            self.metrics["total_bytes"] += sum(len(p) for p in packets[:actual_sent])

        except PermissionError:
            self._handle_error("Permission denied - check raw socket access", exit=True)
        except Exception as e:
            self.metrics["errors"] += 1
            print(Fore.RED + f"[!] Send error: {str(e)}")
            if "No route to host" in str(e):
                self._safe_exit("Network unreachable - check connectivity")

    # [Keep other methods with added public IP awareness]

if __name__ == "__main__":
    try:
        print(Fore.MAGENTA + Style.BRIGHT + "\nNetwork Traffic Generator - Educational Tool")
        print(Fore.RED + "PUBLIC NETWORK TESTING REQUIRES EXPLICIT LEGAL AUTHORIZATION")
        generator = TrafficGenerator()
        generator.start_test()
    except Exception as e:
        print(Fore.RED + f"[!] Unhandled fatal error: {str(e)}")
        sys.exit(1)
