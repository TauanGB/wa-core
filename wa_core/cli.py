"""
Interface de linha de comando para wa-core
"""
import argparse
import sys
import time
from typing import Optional

from .whatsapp_client import WhatsAppClient


def main():
    """Função principal da CLI"""
    parser = argparse.ArgumentParser(
        description="wa-core - Gerenciador funcional do WhatsApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  wa-core --session-path ./my_session
  wa-core --monitor --interval 5
  wa-core --send-message "Olá!" --contact "João"
        """
    )
    
    parser.add_argument(
        "--session-path",
        default="whatsapp_session",
        help="Caminho para salvar a sessão do WhatsApp (padrão: whatsapp_session)"
    )
    
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Monitora mensagens continuamente"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Intervalo em segundos para verificar mensagens (padrão: 5)"
    )
    
    parser.add_argument(
        "--send-message",
        help="Envia uma mensagem específica"
    )
    
    parser.add_argument(
        "--contact",
        help="Nome do contato para enviar mensagem"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verboso"
    )
    
    args = parser.parse_args()
    
    try:
        # Inicializa o cliente
        if args.verbose:
            print(f"[CLI] Iniciando wa-core com sessão em: {args.session_path}")
        
        client = WhatsAppClient(args.session_path)
        
        if args.send_message:
            # Modo de envio de mensagem
            if args.contact:
                print(f"[CLI] Enviando mensagem para {args.contact}: {args.send_message}")
                # Aqui você implementaria a lógica para encontrar o contato
                # Por simplicidade, assumimos que o contato já está aberto
                success = client.send_message(args.contact, args.send_message)
                if success:
                    print("[CLI] Mensagem enviada com sucesso!")
                else:
                    print("[CLI] Erro ao enviar mensagem")
                    sys.exit(1)
            else:
                print("[CLI] Erro: --contact é obrigatório quando usar --send-message")
                sys.exit(1)
        
        elif args.monitor:
            # Modo de monitoramento
            print(f"[CLI] Iniciando monitoramento (intervalo: {args.interval}s)")
            print("[CLI] Pressione Ctrl+C para parar")
            
            try:
                while True:
                    if client.check_for_new_messages():
                        if args.verbose:
                            print("[CLI] Nova mensagem detectada!")
                        
                        if client.click_unread_message():
                            contact = client.get_current_contact()
                            message = client.get_last_message()
                            
                            print(f"[CLI] Mensagem de {contact}: {message}")
                            
                            # Aqui você pode adicionar lógica personalizada
                            # Por exemplo, responder automaticamente
                            # client.send_message("Mensagem automática")
                            
                            client.close_current_chat()
                    
                    time.sleep(args.interval)
                    
            except KeyboardInterrupt:
                print("\n[CLI] Monitoramento interrompido pelo usuário")
        
        else:
            # Modo interativo simples
            print("[CLI] Modo interativo - verificação única")
            if client.check_for_new_messages():
                print("[CLI] Mensagens não lidas encontradas!")
                if client.click_unread_message():
                    contact = client.get_current_contact()
                    message = client.get_last_message()
                    print(f"[CLI] Contato: {contact}")
                    print(f"[CLI] Mensagem: {message}")
            else:
                print("[CLI] Nenhuma mensagem não lida encontrada")
        
        # Fecha o cliente
        client.close()
        print("[CLI] wa-core finalizado")
        
    except Exception as e:
        print(f"[CLI] Erro: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
