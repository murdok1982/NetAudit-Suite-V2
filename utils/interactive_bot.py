from utils.telegram_bot import TelegramBot
from lib.scanner import NetworkScanner
from loguru import logger

class InteractiveBot(TelegramBot):
    def handle_command(self, command, chat_id):
        """
        Skeleton for interactive commands.
        In a real scenario, this would poll or use webhooks.
        """
        if command == "/start":
            self.send_message("🛡️ *NetAudit-Suite Bot*\nComandos:\n/scan - Iniciar escaneo\n/status - Estado actual\n/report - Último reporte")
        elif command == "/scan":
            self.send_message("🚀 Iniciando escaneo de red...")
            # Trigger scan logic here
        else:
            self.send_message("❌ Comando no reconocido.")

    def format_scan_report(self, session_name, results):
        vulns = sum(1 for r in results if r.get('vulnerable'))
        msg = f"🚀 *Auditoría Finalizada: {session_name}*\n"
        msg += f"🖥️ Dispositivos: {len(results)}\n"
        msg += f"⚠️ Vulnerables: {vulns}\n\n"
        
        for r in results[:10]: # Limit to top 10 for Telegram readability
            status = "🔴" if r.get('vulnerable') else "🟢"
            msg += f"{status} `{r['ip']}` - {r['category']}\n"
            
        return msg
