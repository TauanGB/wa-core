#!/usr/bin/env python3
"""
Exemplo básico de uso do wa-core
Demonstra as funcionalidades principais da biblioteca
"""

import time
from wa_core import WhatsAppClient


def main():
    """Exemplo básico de uso"""
    print("=== Exemplo Básico do wa-core ===")
    
    # Inicializa o cliente com sessão personalizada
    client = WhatsAppClient("exemplo_sessao")
    
    try:
        print("Cliente inicializado! Aguardando mensagens...")
        print("Pressione Ctrl+C para parar")
        
        # Loop principal
        while True:
            # Verifica se há mensagens não lidas
            if client.check_for_new_messages():
                print("📨 Nova mensagem detectada!")
                
                # Clica na primeira mensagem não lida
                if client.click_unread_message():
                    # Obtém informações da conversa
                    contato = client.get_current_contact()
                    mensagem = client.get_last_message()
                    
                    print(f"👤 Contato: {contato}")
                    print(f"💬 Mensagem: {mensagem}")
                    
                    # Resposta automática simples
                    resposta = f"Olá {contato}! Recebi sua mensagem: '{mensagem}'. Como posso ajudar?"
                    
                    # Envia a resposta
                    if client.send_message(resposta):
                        print("✅ Resposta enviada com sucesso!")
                    else:
                        print("❌ Erro ao enviar resposta")
                    
                    # Atualiza dados do cliente
                    client.atualizar_dados_cliente(contato, contato, mensagem)
                    
                    # Fecha a conversa
                    client.close_current_chat()
                    print("🔒 Conversa fechada")
            
            # Aguarda antes da próxima verificação
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        # Sempre fecha o cliente
        client.close()
        print("🔚 Cliente fechado")


if __name__ == "__main__":
    main()
