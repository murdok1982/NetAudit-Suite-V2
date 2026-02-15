import os
import sys
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich import box

# Add current dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, SHODAN_API_KEY
except ImportError:
    TELEGRAM_TOKEN = TELEGRAM_CHAT_ID = SHODAN_API_KEY = None

from lib.scanner import NetworkScanner
from lib.classifier import DeviceClassifier
from lib.osint import OSINTLookup
from utils.interactive_bot import InteractiveBot
from db.models import get_session, AuditSession, HostResult

console = Console()

def main():
    console.clear()
    console.print(Panel.fit("[bold white on blue] NET-AUDIT PRO v2.0 [/bold white on blue]", box=box.SQUARE))

    bot = InteractiveBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    scanner = NetworkScanner()
    classifier = DeviceClassifier()
    osint = OSINTLookup(SHODAN_API_KEY)
    db = get_session()

    mi_ip, red = scanner.get_local_network()
    if not red:
        return logger.error("No network detected")

    console.print(f"[blue]📡 Red:[/blue] {red} | [blue]💻 IP:[/blue] {mi_ip}\n")
    nombre = console.input("[bold yellow]Nombre de la auditoría: [/bold yellow]").strip() or "Auditoria_v2"

    # Create session in DB
    session = AuditSession(name=nombre, network=red)
    db.add(session)
    db.commit()

    with console.status("[green]Escaneando red...[/green]"):
        hosts = scanner.discover_hosts(red)
        hosts = [ip for ip in hosts if ip != mi_ip]

    if not hosts:
        return console.print("[red]❌ No hosts found[/red]")

    results_data = []
    for ip in hosts:
        audit_data = scanner.audit_host(ip)
        if audit_data:
            category = classifier.classify(ip, audit_data)
            vuln = "cvss" in str(audit_data).lower()
            
            # Save to DB
            host_res = HostResult(
                session_id=session.id,
                ip=ip,
                hostname=audit_data['hostname'],
                category=category,
                vendor=str(audit_data['vendor']),
                vulnerable=vuln,
                scan_data=audit_data
            )
            db.add(host_res)
            
            results_data.append({
                "ip": ip,
                "category": category,
                "vulnerable": vuln
            })

    db.commit()
    
    # Send Report
    report_msg = bot.format_scan_report(nombre, results_data)
    bot.send_message(report_msg)
    
    console.print("[bold green]✅ Auditoría completada y guardada en base de datos.[/bold green]")

if __name__ == "__main__":
    main()
