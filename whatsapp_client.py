"""
Cliente WhatsApp que utiliza o SeleniumDriver para interagir com o WhatsApp Web.
"""
import time as tm
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from selenium_driver import SeleniumDriver


class WhatsAppClient:
    """Cliente para interagir com o WhatsApp Web usando Selenium"""
    
    def __init__(self, session_path: str = "whatsapp_session"):
        """
        Inicializa o cliente WhatsApp.
        
        Args:
            session_path: Caminho para salvar a sessão do WhatsApp
        """
        print("[WhatsAppClient] Iniciando...")
        
        self.session_path = session_path
        self.driver = SeleniumDriver(session_path)
        
        # Dicionário para armazenar dados dos clientes (número -> dados do cliente)
        self.dados_clientes = {}
        
        # Carrega dados existentes dos clientes
        self.carregar_dados_clientes()

    def check_for_new_messages(self) -> bool:
        """
        Verifica se há novas mensagens não lidas.
        
        Returns:
            True se há mensagens não lidas, False caso contrário
        """
        return self.driver.check_for_new_messages()

    def send_message(self, text: str) -> bool:
        """
        Envia uma mensagem no WhatsApp.
        
        Args:
            text: Texto da mensagem a ser enviada
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        return self.driver.send_message(text)

    def get_current_contact(self) -> str:
        """
        Obtém o nome do contato atual.
        
        Returns:
            Nome do contato atual
        """
        return self.driver.get_current_contact()

    def click_unread_message(self) -> bool:
        """
        Clica na primeira mensagem não lida.
        
        Returns:
            True se clicou com sucesso, False caso contrário
        """
        return self.driver.click_unread_message()

    def get_last_message(self) -> str:
        """
        Obtém a última mensagem recebida.
        
        Returns:
            Texto da última mensagem
        """
        return self.driver.get_last_message()

    def close_current_chat(self):
        """Fecha a conversa atual"""
        self.driver.close_current_chat()

    def carregar_dados_clientes(self):
        """Carrega dados dos clientes de um arquivo JSON"""
        try:
            clientes_file = f"{self.session_path}/dados_clientes.json"
            if os.path.exists(clientes_file):
                with open(clientes_file, 'r', encoding='utf-8') as f:
                    self.dados_clientes = json.load(f)
                print(f"[WhatsAppClient] Dados de {len(self.dados_clientes)} clientes carregados")
            else:
                print("[WhatsAppClient] Nenhum arquivo de dados de clientes encontrado")
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao carregar dados dos clientes: {e}")
            self.dados_clientes = {}

    def salvar_dados_clientes(self) -> bool:
        """
        Salva dados dos clientes em um arquivo JSON.
        
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            clientes_file = f"{self.session_path}/dados_clientes.json"
            with open(clientes_file, 'w', encoding='utf-8') as f:
                json.dump(self.dados_clientes, f, indent=2, ensure_ascii=False)
            print(f"[WhatsAppClient] Dados de {len(self.dados_clientes)} clientes salvos")
            return True
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao salvar dados dos clientes: {e}")
            return False

    def atualizar_dados_cliente(self, numero: str, nome_contato: str, ultima_mensagem: str):
        """
        Atualiza ou cria dados de um cliente.
        
        Args:
            numero: Número do cliente
            nome_contato: Nome do contato
            ultima_mensagem: Última mensagem enviada pelo cliente
        """
        self.dados_clientes[numero] = {
            'numero': numero,
            'apelido': nome_contato,
            'ultima_mensagem': ultima_mensagem,
            'ultima_atividade': datetime.now().isoformat(),
            'total_mensagens': self.dados_clientes.get(numero, {}).get('total_mensagens', 0) + 1
        }
        
        # Salva automaticamente após cada atualização
        self.salvar_dados_clientes()

    def close(self):
        """Fecha o cliente e salva os dados"""
        try:
            # Salva dados dos clientes antes de fechar
            self.salvar_dados_clientes()
            
            # Fecha o driver
            self.driver.close()
            print("[WhatsAppClient] Cliente fechado, dados dos clientes salvos")
        except:
            pass
