# Network Testing and Monitoring Toolkit

## Overview

This toolkit provides two powerful Python scripts for network assessment:
1. **Network Stress Tester**: A tool to evaluate your network's resilience under various load conditions
2. **Network Monitor**: A comprehensive monitoring solution to track network performance over time

## Features

### Network Stress Tester
- TCP flood attack simulation
- UDP flood attack simulation
- HTTP flood attack simulation
- Internet speed testing (download/upload)
- Ping latency testing

### Network Monitor
- Continuous network statistics collection
- Bandwidth usage monitoring
- Latency measurement
- Internet connectivity checks
- HTTP service availability testing
- Automated speed testing
- CSV data logging
- Graphical report generation

## Installation

1. Clone this repository or download the scripts
2. Ensure Python 3.6+ is installed
3. Install required dependencies:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain:
```
psutil
speedtest-cli
ping3
requests
matplotlib
pandas
```

## Usage

### Network Stress Tester

```
python stress_tester.py <command> [arguments]
```

**Commands:**
- `tcp <target_ip> <target_port>` - TCP flood attack
- `udp <target_ip> <target_port>` - UDP flood attack
- `http <target_url>` - HTTP flood attack
- `speedtest` - Run internet speed test
- `ping <target>` - Ping latency test

**Options:**
- `--duration` - Attack duration in seconds (default: 60)
- `--threads` - Number of threads to use (default: 50)
- `--count` - Number of pings to send (ping command only)

**Examples:**
```bash
# TCP flood attack
python stress_tester.py tcp 192.168.1.100 80 --duration 120 --threads 100

# Speed test
python stress_tester.py speedtest

# Ping test
python stress_tester.py ping google.com --count 10
```

### Network Monitor

```
python network_monitor.py [options]
```

**Options:**
- `--interval` - Monitoring interval in seconds (default: 5)
- `--duration` - Monitoring duration in seconds (default: 3600)
- `--output` - Output CSV file (default: "network_stats.csv")
- `--report` - Generate report from existing data

**Examples:**
```bash
# Monitor for 30 minutes
python network_monitor.py --duration 1800

# Monitor with 10-second intervals
python network_monitor.py --interval 10

# Generate report from collected data
python network_monitor.py --report
```

## Output

### Stress Tester
- Real-time attack statistics in console
- Speed test results in Mbps
- Ping test results with latency measurements

### Network Monitor
- CSV file with timestamped network metrics
- Optional PNG report with graphs of:
  - Network throughput (sent/received data)
  - Latency over time
- Console output with current statistics

## Legal and Ethical Considerations

⚠️ **Important:**  
- Only use these tools on networks you own or have explicit permission to test
- Unauthorized network testing may be illegal in your jurisdiction
- These tools are for educational and legitimate network assessment purposes only
- The authors assume no liability for misuse of these tools

## Support

For issues or feature requests, please open an issue on the GitHub repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
