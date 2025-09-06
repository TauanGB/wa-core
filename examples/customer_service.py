#!/usr/bin/env python3
"""
Assistente de Atendimento ao Cliente
Sistema completo de tickets e atendimento automatizado
"""

import time
import json
import uuid
from datetime import datetime
from wa_core import WhatsAppClient


class CustomerServiceAssistant:
    """Assistente de atendimento com sistema de tickets"""
    
    def __init__(self, session_path="atendimento_sessao"):
        self.client = WhatsAppClient(session_path)
        self.tickets = {}
        self.next_ticket_id = 1
        self.load_tickets()
        
        # Templates de resposta
        self.templates = {
            "welcome": """
🎫 *Sistema de Atendimento*

Olá! Bem-vindo ao nosso atendimento automatizado.

Para criar um ticket, envie sua mensagem normalmente.
Para verificar status, envie: *status*
Para falar com atendente, envie: *atendente*

Como posso ajudar? 😊
            """,
            "ticket_created": """
🎫 *Ticket {ticket_id} criado com sucesso!*

📝 *Sua solicitação:* {message}
👤 *Cliente:* {customer}
🕒 *Criado em:* {created_at}

Nosso time de atendimento analisará sua solicitação e retornará em breve.

Obrigado pela preferência! 🙏
            """,
            "ticket_status": """
📊 *Status do Ticket {ticket_id}*

👤 *Cliente:* {customer}
📝 *Assunto:* {message}
🕒 *Criado em:* {created_at}
📈 *Status:* {status}

{additional_info}
            """,
            "human_agent": """
👨‍💼 *Transferindo para Atendente Humano*

Sua solicitação foi transferida para nosso time de atendimento especializado.

Um atendente entrará em contato em breve.

Obrigado pela paciência! 🙏
            """
        }
    
    def load_tickets(self):
        """Carrega tickets salvos do arquivo"""
        try:
            with open("tickets.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.tickets = data.get("tickets", {})
                self.next_ticket_id = data.get("next_id", 1)
            print(f"📂 {len(self.tickets)} tickets carregados")
        except FileNotFoundError:
            print("📂 Nenhum ticket encontrado, iniciando novo sistema")
        except Exception as e:
            print(f"❌ Erro ao carregar tickets: {e}")
    
    def save_tickets(self):
        """Salva tickets no arquivo"""
        try:
            data = {
                "tickets": self.tickets,
                "next_id": self.next_ticket_id,
                "last_updated": datetime.now().isoformat()
            }
            with open("tickets.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 {len(self.tickets)} tickets salvos")
        except Exception as e:
            print(f"❌ Erro ao salvar tickets: {e}")
    
    def create_ticket(self, customer: str, message: str) -> str:
        """Cria um novo ticket"""
        ticket_id = f"TICKET-{self.next_ticket_id:04d}"
        
        self.tickets[ticket_id] = {
            "id": ticket_id,
            "customer": customer,
            "message": message,
            "status": "open",
            "priority": "normal",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "responses": [],
            "assigned_to": None
        }
        
        self.next_ticket_id += 1
        self.save_tickets()
        
        return ticket_id
    
    def get_ticket_status(self, customer: str) -> str:
        """Obtém status dos tickets do cliente"""
        customer_tickets = [
            ticket for ticket in self.tickets.values()
            if ticket["customer"] == customer
        ]
        
        if not customer_tickets:
            return "❌ Nenhum ticket encontrado para este cliente."
        
        # Pega o ticket mais recente
        latest_ticket = max(customer_tickets, key=lambda t: t["created_at"])
        
        additional_info = ""
        if latest_ticket["status"] == "open":
            additional_info = "⏳ Aguardando análise da nossa equipe."
        elif latest_ticket["status"] == "in_progress":
            additional_info = "🔄 Em análise pela nossa equipe."
        elif latest_ticket["status"] == "resolved":
            additional_info = "✅ Ticket resolvido!"
        
        return self.templates["ticket_status"].format(
            ticket_id=latest_ticket["id"],
            customer=latest_ticket["customer"],
            message=latest_ticket["message"][:100] + "..." if len(latest_ticket["message"]) > 100 else latest_ticket["message"],
            created_at=latest_ticket["created_at"][:19].replace("T", " "),
            status=latest_ticket["status"].upper(),
            additional_info=additional_info
        )
    
    def process_message(self, customer: str, message: str) -> str:
        """Processa mensagem do cliente"""
        message_lower = message.lower().strip()
        
        # Comandos especiais
        if message_lower in ["status", "situação", "situacao"]:
            return self.get_ticket_status(customer)
        
        if message_lower in ["atendente", "humano", "pessoa"]:
            return self.templates["human_agent"]
        
        if message_lower in ["oi", "olá", "hello", "ajuda", "help"]:
            return self.templates["welcome"]
        
        # Cria novo ticket para mensagens normais
        ticket_id = self.create_ticket(customer, message)
        
        return self.templates["ticket_created"].format(
            ticket_id=ticket_id,
            message=message,
            customer=customer,
            created_at=datetime.now().strftime("%d/%m/%Y %H:%M")
        )
    
    def handle_customer_message(self):
        """Processa mensagens de clientes"""
        if self.client.check_for_new_messages():
            if self.client.click_unread_message():
                customer = self.client.get_current_contact()
                message = self.client.get_last_message()
                
                print(f"📨 Nova mensagem de {customer}: {message}")
                
                # Processa a mensagem
                response = self.process_message(customer, message)
                
                # Envia resposta
                if self.client.send_message(response):
                    print(f"✅ Resposta enviada para {customer}")
                    
                    # Atualiza dados do cliente
                    self.client.atualizar_dados_cliente(customer, customer, message)
                else:
                    print(f"❌ Erro ao enviar resposta para {customer}")
                
                self.client.close_current_chat()
                return True
        return False
    
    def run(self):
        """Executa o assistente"""
        print("🎫 Assistente de Atendimento iniciado!")
        print("📋 Sistema de tickets ativo")
        print("⏹️  Pressione Ctrl+C para parar")
        print("-" * 50)
        
        try:
            while True:
                if self.handle_customer_message():
                    print("-" * 30)
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n🛑 Assistente interrompido pelo usuário")
            print(f"📊 Resumo:")
            print(f"   • Total de tickets: {len(self.tickets)}")
            print(f"   • Próximo ID: {self.next_ticket_id}")
        except Exception as e:
            print(f"❌ Erro no assistente: {e}")
        finally:
            self.save_tickets()
            self.client.close()
            print("🔚 Assistente finalizado")


def main():
    """Função principal"""
    assistant = CustomerServiceAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
