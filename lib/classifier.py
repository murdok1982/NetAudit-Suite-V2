import re
from loguru import logger

class DeviceClassifier:
    CRITERIOS = [
        ("Teles", ["samsung", "lg-tv", "webos", "bravia", "sony interactive", "allshare", "dlna", "airtunes"]),
        ("Windows", ["microsoft-ds", "msrpc", "netbios-ssn", "3389/tcp", "windows", "tpv"]),
        ("Routers", ["gateway", "router", "tp-link", "ubiquiti", "mikrotik", "asus", "technicolor", "livebox", "arcadyan"]),
        ("Camaras", ["rtsp", "554/tcp", "37777/tcp", "8000/tcp", "dahua", "hikvision", "lorex", "zenointel", "webcam"]),
        ("Moviles", ["android", "iphone", "apple-mobile", "ipad", "phone", "xiaomi"]),
    ]

    @classmethod
    def classify(cls, ip, scan_data):
        """
        Classifies a device based on nmap scan data and IP.
        scan_data: dict from NetworkScanner.audit_host
        """
        # Convert scan data to a single searchable string
        str_data = str(scan_data).lower()
        
        # Check for gateway
        if ip.endswith(".1") or "gateway" in str_data:
            return "Routers"

        # Check against criteria
        for category, keywords in cls.CRITERIOS:
            if any(key in str_data for key in keywords):
                return category

        return "Otros"
