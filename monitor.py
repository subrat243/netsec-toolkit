#!/usr/bin/env python3
import time
import psutil
import speedtest
import requests
from ping3 import ping
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import os

class NetworkMonitor:
    def __init__(self, interval=5, output_file="network_stats.csv"):
        self.interval = interval
        self.output_file = output_file
        self.headers_written = False
        
    def get_network_stats(self):
        """Collect various network statistics"""
        stats = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv,
            'packets_sent': psutil.net_io_counters().packets_sent,
            'packets_recv': psutil.net_io_counters().packets_recv,
            'err_in': psutil.net_io_counters().errin,
            'err_out': psutil.net_io_counters().errout,
            'drop_in': psutil.net_io_counters().dropin,
            'drop_out': psutil.net_io_counters().dropout
        }
        return stats
    
    def check_connectivity(self, target="8.8.8.8"):
        """Check if we can reach a target (default: Google DNS)"""
        try:
            response = ping(target, timeout=2)
            return response is not None
        except:
            return False
    
    def measure_latency(self, target="8.8.8.8"):
        """Measure latency to a target"""
        try:
            return ping(target, unit='ms')
        except:
            return None
    
    def run_speed_test(self):
        """Run a speed test (this may take some time)"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1_000_000  # Mbps
            upload = st.upload() / 1_000_000  # Mbps
            return download, upload
        except:
            return None, None
    
    def check_http_service(self, url="https://www.google.com"):
        """Check if an HTTP service is available"""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def save_stats(self, stats):
        """Save statistics to CSV file"""
        file_exists = os.path.isfile(self.output_file)
        
        with open(self.output_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=stats.keys())
            if not file_exists or not self.headers_written:
                writer.writeheader()
                self.headers_written = True
            writer.writerow(stats)
    
    def monitor(self, duration=3600):
        """Main monitoring loop"""
        start_time = time.time()
        end_time = start_time + duration
        
        print(f"Starting network monitoring for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        
        try:
            while time.time() < end_time:
                stats = self.get_network_stats()
                
                # Add additional metrics
                stats['connected'] = self.check_connectivity()
                stats['latency'] = self.measure_latency()
                stats['http_available'] = self.check_http_service()
                
                # Run speed test every 5 minutes (optional as it's slow)
                if int(time.time() - start_time) % 300 == 0:
                    download, upload = self.run_speed_test()
                    stats['download_mbps'] = download
                    stats['upload_mbps'] = upload
                
                # Save and display stats
                self.save_stats(stats)
                self.display_stats(stats)
                
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        
        print("Monitoring completed")
    
    def display_stats(self, stats):
        """Display current statistics in a readable format"""
        print(f"\n[{stats['timestamp']}] Network Stats:")
        print(f"  Data: Sent {stats['bytes_sent']/1024:.1f} KB / Recv {stats['bytes_recv']/1024:.1f} KB")
        print(f"  Packets: Sent {stats['packets_sent']} / Recv {stats['packets_recv']}")
        print(f"  Errors: In {stats['err_in']} / Out {stats['err_out']}")
        print(f"  Drops: In {stats['drop_in']} / Out {stats['drop_out']}")
        
        if 'latency' in stats and stats['latency'] is not None:
            print(f"  Latency: {stats['latency']:.2f} ms")
        
        if 'download_mbps' in stats and stats['download_mbps'] is not None:
            print(f"  Speed: Download {stats['download_mbps']:.2f} Mbps / Upload {stats['upload_mbps']:.2f} Mbps")
        
        print(f"  Connectivity: {'Up' if stats['connected'] else 'Down'}")
        print(f"  HTTP Service: {'Available' if stats['http_available'] else 'Unavailable'}")
    
    def generate_report(self):
        """Generate a report from collected data"""
        try:
            import pandas as pd
            
            data = pd.read_csv(self.output_file)
            
            # Calculate transfer rates (KB/s)
            data['time'] = pd.to_datetime(data['timestamp'])
            data['time_diff'] = data['time'].diff().dt.total_seconds()
            data['sent_rate'] = (data['bytes_sent'].diff() / data['time_diff']) / 1024
            data['recv_rate'] = (data['bytes_recv'].diff() / data['time_diff']) / 1024
            
            # Plot network activity
            plt.figure(figsize=(12, 8))
            
            plt.subplot(2, 1, 1)
            plt.plot(data['time'], data['sent_rate'], label='Sent (KB/s)')
            plt.plot(data['time'], data['recv_rate'], label='Received (KB/s)')
            plt.title('Network Throughput')
            plt.ylabel('KB/s')
            plt.legend()
            plt.grid()
            
            plt.subplot(2, 1, 2)
            if 'latency' in data.columns:
                plt.plot(data['time'], data['latency'], 'r-', label='Latency (ms)')
                plt.title('Network Latency')
                plt.ylabel('ms')
                plt.legend()
                plt.grid()
            
            plt.tight_layout()
            plt.savefig('network_report.png')
            print("Report generated as network_report.png")
            
        except ImportError:
            print("Pandas and matplotlib are required for report generation")
        except Exception as e:
            print(f"Error generating report: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Network Monitoring Tool")
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds')
    parser.add_argument('--duration', type=int, default=3600, help='Monitoring duration in seconds')
    parser.add_argument('--output', default="network_stats.csv", help='Output CSV file')
    parser.add_argument('--report', action='store_true', help='Generate report from existing data')
    
    args = parser.parse_args()
    
    monitor = NetworkMonitor(interval=args.interval, output_file=args.output)
    
    if args.report:
        monitor.generate_report()
    else:
        monitor.monitor(duration=args.duration)

if __name__ == "__main__":
    main()
