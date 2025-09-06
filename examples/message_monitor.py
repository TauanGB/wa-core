#!/usr/bin/env python3
"""
Monitor de Mensagens
Sistema de monitoramento e logging de mensagens do WhatsApp
"""

import time
import json
import logging
from datetime import datetime
from wa_core import WhatsAppClient


class MessageMonitor:
    """Monitor de mensagens com logging e análise"""
    
    def __init__(self, session_path="monitor_sessao"):
        self.client = WhatsAppClient(session_path)
        self.setup_logging()
        
        # Estatísticas
        self.stats = {
            "total_messages": 0,
            "unique_contacts": set(),
            "messages_by_hour": {},
            "messages_by_contact": {},
            "start_time": datetime.now()
        }
        
        # Filtros
        self.keywords = ["urgente", "emergência", "emergencia", "urgent", "help", "ajuda"]
        self.blocked_contacts = set()
    
    def setup_logging(self):
        """Configura sistema de logging"""
        # Configuração do logger principal
        self.logger = logging.getLogger('WhatsAppMonitor')
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(
            f'whatsapp_monitor_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato das mensagens
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_message(self, contact: str, message: str):
        """Registra mensagem no log"""
        timestamp = datetime.now()
        
        # Log principal
        self.logger.info(f"[{contact}] {message}")
        
        # Atualiza estatísticas
        self.stats["total_messages"] += 1
        self.stats["unique_contacts"].add(contact)
        
        # Conta mensagens por hora
        hour = timestamp.hour
        self.stats["messages_by_hour"][hour] = self.stats["messages_by_hour"].get(hour, 0) + 1
        
        # Conta mensagens por contato
        self.stats["messages_by_contact"][contact] = self.stats["messages_by_contact"].get(contact, 0) + 1
        
        # Verifica palavras-chave importantes
        if any(keyword in message.lower() for keyword in self.keywords):
            self.logger.warning(f"🚨 MENSAGEM URGENTE de {contact}: {message}")
    
    def save_stats(self):
        """Salva estatísticas em arquivo JSON"""
        try:
            # Converte set para list para serialização JSON
            stats_copy = self.stats.copy()
            stats_copy["unique_contacts"] = list(stats_copy["unique_contacts"])
            stats_copy["last_updated"] = datetime.now().isoformat()
            
            with open("monitor_stats.json", "w", encoding="utf-8") as f:
                json.dump(stats_copy, f, indent=2, ensure_ascii=False)
            
            print("📊 Estatísticas salvas")
        except Exception as e:
            print(f"❌ Erro ao salvar estatísticas: {e}")
    
    def print_stats(self):
        """Imprime estatísticas atuais"""
        runtime = datetime.now() - self.stats["start_time"]
        
        print("\n" + "="*50)
        print("📊 ESTATÍSTICAS DO MONITOR")
        print("="*50)
        print(f"⏱️  Tempo de execução: {runtime}")
        print(f"📨 Total de mensagens: {self.stats['total_messages']}")
        print(f"👥 Contatos únicos: {len(self.stats['unique_contacts'])}")
        
        if self.stats["messages_by_contact"]:
            print("\n📈 Top 5 contatos mais ativos:")
            sorted_contacts = sorted(
                self.stats["messages_by_contact"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            for contact, count in sorted_contacts:
                print(f"   • {contact}: {count} mensagens")
        
        if self.stats["messages_by_hour"]:
            print("\n🕒 Mensagens por hora:")
            for hour in sorted(self.stats["messages_by_hour"].keys()):
                count = self.stats["messages_by_hour"][hour]
                print(f"   • {hour:02d}h: {count} mensagens")
        
        print("="*50)
    
    def monitor(self):
        """Monitora mensagens continuamente"""
        self.logger.info("🔍 Monitor de mensagens iniciado")
        print("🔍 Monitor de mensagens iniciado!")
        print("📝 Logs salvos em: whatsapp_monitor_YYYYMMDD.log")
        print("📊 Estatísticas salvas em: monitor_stats.json")
        print("⏹️  Pressione Ctrl+C para parar")
        print("-" * 50)
        
        last_stats_print = time.time()
        
        try:
            while True:
                if self.client.check_for_new_messages():
                    if self.client.click_unread_message():
                        contact = self.client.get_current_contact()
                        message = self.client.get_last_message()
                        
                        # Verifica se o contato não está bloqueado
                        if contact not in self.blocked_contacts:
                            self.log_message(contact, message)
                            
                            # Atualiza dados do cliente
                            self.client.atualizar_dados_cliente(contact, contact, message)
                        else:
                            self.logger.info(f"🚫 Mensagem de contato bloqueado ignorada: {contact}")
                        
                        self.client.close_current_chat()
                
                # Imprime estatísticas a cada 5 minutos
                if time.time() - last_stats_print > 300:  # 5 minutos
                    self.print_stats()
                    self.save_stats()
                    last_stats_print = time.time()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitor interrompido pelo usuário")
            print("\n🛑 Monitor interrompido pelo usuário")
            self.print_stats()
        except Exception as e:
            self.logger.error(f"❌ Erro no monitor: {e}")
            print(f"❌ Erro no monitor: {e}")
        finally:
            self.save_stats()
            self.client.close()
            self.logger.info("🔚 Monitor finalizado")
            print("🔚 Monitor finalizado")


def main():
    """Função principal"""
    monitor = MessageMonitor()
    monitor.monitor()


if __name__ == "__main__":
    main()
