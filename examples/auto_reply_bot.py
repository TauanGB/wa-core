#!/usr/bin/env python3
"""
Bot de Resposta Automática
Exemplo de como criar um bot que responde automaticamente às mensagens
"""

import time
import re
from wa_core import WhatsAppClient


class AutoReplyBot:
    """Bot de resposta automática com múltiplas funcionalidades"""
    
    def __init__(self, session_path="bot_sessao"):
        self.client = WhatsAppClient(session_path)
        self.responses = {
            "oi": "Olá! Como posso ajudar? 😊",
            "olá": "Olá! Como posso ajudar? 😊",
            "hello": "Hello! How can I help you? 😊",
            "ajuda": self.get_help_message(),
            "help": self.get_help_message(),
            "horario": "🕒 Nosso horário de funcionamento é de segunda a sexta, das 9h às 18h.",
            "contato": "📞 Entre em contato conosco pelo email: contato@empresa.com",
            "preço": "💰 Para informações sobre preços, envie 'preços' ou entre em contato conosco.",
            "preços": "💰 Nossos preços variam conforme o serviço. Entre em contato para um orçamento personalizado!",
            "obrigado": "De nada! Foi um prazer ajudar! 😊",
            "thanks": "You're welcome! It was a pleasure to help! 😊",
        }
        
        # Contadores de uso
        self.message_count = 0
        self.contacts_helped = set()
    
    def get_help_message(self):
        """Retorna mensagem de ajuda"""
        return """
🤖 *Bot de Atendimento Automático*

Comandos disponíveis:
• *oi/olá* - Saudação
• *ajuda* - Esta mensagem de ajuda
• *horario* - Horário de funcionamento
• *contato* - Informações de contato
• *preços* - Informações sobre preços
• *obrigado* - Agradecimento

Digite qualquer comando para obter informações! 😊
        """
    
    def process_message(self, message: str) -> str:
        """Processa a mensagem e retorna resposta apropriada"""
        message_lower = message.lower().strip()
        
        # Remove caracteres especiais para melhor matching
        clean_message = re.sub(r'[^\w\s]', '', message_lower)
        
        # Procura por palavras-chave
        for keyword, response in self.responses.items():
            if keyword in clean_message:
                return response
        
        # Resposta padrão para mensagens não reconhecidas
        return """
🤔 Não entendi sua mensagem. 

Digite *ajuda* para ver os comandos disponíveis ou entre em contato conosco para atendimento personalizado.

Obrigado! 😊
        """
    
    def log_interaction(self, contact: str, message: str, response: str):
        """Registra a interação para análise"""
        self.message_count += 1
        self.contacts_helped.add(contact)
        
        print(f"📊 Estatísticas:")
        print(f"   • Total de mensagens processadas: {self.message_count}")
        print(f"   • Contatos únicos atendidos: {len(self.contacts_helped)}")
        print(f"   • Última interação: {contact}")
    
    def run(self):
        """Executa o bot em loop contínuo"""
        print("🤖 Bot de Resposta Automática iniciado!")
        print("📋 Comandos disponíveis: oi, ajuda, horario, contato, preços")
        print("⏹️  Pressione Ctrl+C para parar")
        print("-" * 50)
        
        try:
            while True:
                if self.client.check_for_new_messages():
                    if self.client.click_unread_message():
                        contact = self.client.get_current_contact()
                        message = self.client.get_last_message()
                        
                        print(f"📨 Nova mensagem de {contact}: {message}")
                        
                        # Processa e envia resposta
                        response = self.process_message(message)
                        
                        if self.client.send_message(contact, response):
                            print(f"✅ Resposta enviada para {contact}")
                            
                            # Registra a interação
                            self.log_interaction(contact, message, response)
                            
                            # Atualiza dados do cliente
                            self.client.atualizar_dados_cliente(
                                contact, contact, message
                            )
                        else:
                            print(f"❌ Erro ao enviar resposta para {contact}")
                        
                        self.client.close_current_chat()
                        print("-" * 30)
                
                time.sleep(2)  # Verifica a cada 2 segundos
                
        except KeyboardInterrupt:
            print("\n🛑 Bot interrompido pelo usuário")
            print(f"📊 Resumo final:")
            print(f"   • Total de mensagens: {self.message_count}")
            print(f"   • Contatos únicos: {len(self.contacts_helped)}")
        except Exception as e:
            print(f"❌ Erro no bot: {e}")
        finally:
            self.client.close()
            print("🔚 Bot finalizado")


def main():
    """Função principal"""
    bot = AutoReplyBot()
    bot.run()


if __name__ == "__main__":
    main()
