import socket
import random
import time
import colorama
from colorama import Fore, Style

# Initialize Colorama
colorama.init(autoreset=True)

# Clear terminal and display header
print("\n" * 100)
print(Fore.MAGENTA + Style.BRIGHT)
print("""
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
""")
print(Fore.BLUE + "This tool is for authorized stress testing of your own systems only.")
print(Fore.RED + "Unauthorized use is illegal and unethical. Proceed only with explicit permission.")
print("")

# Logging function
def log_test(ip, port, duration, packet_size):
    with open("test_log.txt", "a") as log_file:
        log_file.write(f"Target: {ip}, Port: {port}, Duration: {duration}s, Packet Size: {packet_size} bytes, Time: {time.ctime()}\n")
    print(Fore.GREEN + "[*] Test details logged.")

# Validate target IP
def is_private_ip(ip):
    private_ranges = [
        ("10.0.0.0", "10.255.255.255"),
        ("172.16.0.0", "172.31.255.255"),
        ("192.168.0.0", "192.168.255.255")
    ]
    ip_parts = list(map(int, ip.split(".")))
    for start, end in private_ranges:
        start_parts = list(map(int, start.split(".")))
        end_parts = list(map(int, end.split(".")))
        if start_parts <= ip_parts <= end_parts:
            return True
    return False

# Get user input
ip = input(Fore.BLUE + "Enter the target IP (must be private, e.g., 192.168.x.x): " + Fore.MAGENTA)
if not is_private_ip(ip):
    print(Fore.RED + "[!] Error: Only private IP addresses are allowed for testing.")
    exit()

port = int(input(Fore.BLUE + "Enter the target port: " + Fore.MAGENTA))
packet_size = int(input(Fore.BLUE + "Enter the packet size (bytes, max 65500): " + Fore.MAGENTA))
if packet_size > 65500:
    print(Fore.RED + "[!] Error: Maximum packet size is 65500 bytes.")
    exit()

duration = int(input(Fore.BLUE + "Enter the duration for the test (seconds): " + Fore.MAGENTA))
print("")

# Display summary and get user confirmation
print(Fore.YELLOW + "Test Summary:")
print(Fore.CYAN + f"Target IP: {ip}")
print(Fore.CYAN + f"Target Port: {port}")
print(Fore.CYAN + f"Packet Size: {packet_size} bytes")
print(Fore.CYAN + f"Duration: {duration} seconds")
confirm = input(Fore.RED + "Do you confirm that you have permission to test this target? (yes/no): " + Fore.MAGENTA)
if confirm.lower() != "yes":
    print(Fore.RED + "[!] Test aborted by user.")
    exit()

# Logging the test details
log_test(ip, port, duration, packet_size)

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = random._urandom(packet_size)

# Perform the stress test
timeout = time.time() + duration
sent = 0
print(Fore.GREEN + "[*] Starting stress test...")
while time.time() < timeout:
    sock.sendto(data, (ip, port))
    sent += 1
    print(Fore.MAGENTA + f"[+] Sent {sent} packets to {ip} on port {port}", end="\r")

print(Fore.GREEN + f"\n[*] Test completed. Sent {sent} packets.")
sock.close()
