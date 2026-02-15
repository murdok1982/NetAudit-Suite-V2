import nmap
import socket
from loguru import logger

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def discover_hosts(self, target_network):
        logger.info(f"Discovering hosts in {target_network}")
        try:
            self.nm.scan(hosts=target_network, arguments='-sn -PR')
            return self.nm.all_hosts()
        except Exception as e:
            logger.error(f"Host discovery failed: {e}")
            return []

    def audit_host(self, ip):
        logger.info(f"Auditing host: {ip}")
        try:
            # -sS (TCP SYN scan), -sV (Version detection), --script=vulners (CVE detection)
            # Using -p- (all ports) can be slow, might want to make it configurable
            results = self.nm.scan(ip, arguments='-sS -sV --script=vulners -Pn --open --min-rate 5000')
            host_data = results['scan'].get(ip, {})
            
            return {
                "ip": ip,
                "hostname": host_data.get('hostname', 'N/A'),
                "status": host_data.get('status', {}).get('state', 'unknown'),
                "vendor": host_data.get('vendor', {}),
                "osmatch": host_data.get('osmatch', []),
                "ports": host_data.get('tcp', {}),
                "raw": host_data
            }
        except Exception as e:
            logger.error(f"Audit of {ip} failed: {e}")
            return None

    @staticmethod
    def get_local_network():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            network = f"{ip.rsplit('.', 1)[0]}.0/24"
            return ip, network
        except Exception as e:
            logger.error(f"Could not detect local network: {e}")
            return None, None
