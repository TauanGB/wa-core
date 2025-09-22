"""
Cliente WhatsApp que utiliza o SeleniumDriver para interagir com o WhatsApp Web.
"""
import time as tm
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from .selenium_driver import SeleniumDriver
from .exceptions import WhatsAppConnectionError, WhatsAppMessageError
from .contact_extractor import ContactExtractor


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
        
        # Inicializa o extrator de contatos
        self.contact_extractor = ContactExtractor(self.driver.driver)
        
        # Dicionário para armazenar dados dos clientes (número -> dados do cliente)
        self.dados_clientes = {}
        
        # Dicionário temporário com contatos atuais do WhatsApp Web (nome -> número)
        self.contatos_whatsapp = {}
        
        # Carrega dados existentes dos clientes
        self.carregar_dados_clientes()
        
        # Carrega contatos do WhatsApp
        self.carregar_contatos_whatsapp()

    def check_for_new_messages(self) -> bool:
        """
        Verifica se há novas mensagens não lidas.
        
        Returns:
            True se há mensagens não lidas, False caso contrário
        """
        return self.driver.check_for_new_messages()

    def send_message(self, phone_number: str, phone_name: str, text: str) -> bool:
        """
        Envia uma mensagem no WhatsApp.
        
        Args:
            phone_number: Número do telefone para envio
            phone_name: Nome do telefone para envio
            text: Texto da mensagem a ser enviada
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        return self.driver.send_message(phone_number, phone_name, text)

    def get_current_contact_info(self, phone_number: str, phone_name: str) -> dict:
        """
        Obtém informações completas do contato atual (nome e número).
        
        Args:
            phone_number: Número do telefone
            phone_name: Nome do contato
            
        Returns:
            Dict com 'nome' e 'numero' do contato atual
        """
        return self.driver.get_contact_info(phone_number, phone_name)

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

    def carregar_contatos_whatsapp(self):
        """Carrega contatos do WhatsApp de um arquivo JSON"""
        try:
            contatos_file = f"{self.session_path}/contatos_whatsapp.json"
            if os.path.exists(contatos_file):
                with open(contatos_file, 'r', encoding='utf-8') as f:
                    self.contatos_whatsapp = json.load(f)
                print(f"[WhatsAppClient] {len(self.contatos_whatsapp)} contatos do WhatsApp carregados")
            else:
                print("[WhatsAppClient] Nenhum arquivo de contatos do WhatsApp encontrado")
                self.contatos_whatsapp = {}
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao carregar contatos do WhatsApp: {e}")
            self.contatos_whatsapp = {}

    def salvar_contatos_whatsapp(self) -> bool:
        """
        Salva contatos do WhatsApp em um arquivo JSON.
        
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            contatos_file = f"{self.session_path}/contatos_whatsapp.json"
            with open(contatos_file, 'w', encoding='utf-8') as f:
                json.dump(self.contatos_whatsapp, f, indent=2, ensure_ascii=False)
            print(f"[WhatsAppClient] {len(self.contatos_whatsapp)} contatos do WhatsApp salvos")
            return True
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao salvar contatos do WhatsApp: {e}")
            return False

    def adicionar_contato_whatsapp(self, nome: str, numero: str):
        """
        Adiciona ou atualiza um contato no dicionário do WhatsApp.
        
        Args:
            nome: Nome do contato
            numero: Número do contato
        """
        self.contatos_whatsapp[nome] = {
            'nome': nome,
            'numero': numero,
            'ultima_atualizacao': datetime.now().isoformat()
        }
        
        # Salva automaticamente após cada atualização
        self.salvar_contatos_whatsapp()
        print(f"[WhatsAppClient] Contato adicionado: {nome} -> {numero}")

    def remover_contato_whatsapp(self, nome: str):
        """
        Remove um contato do dicionário do WhatsApp.
        
        Args:
            nome: Nome do contato a ser removido
        """
        if nome in self.contatos_whatsapp:
            numero = self.contatos_whatsapp[nome]['numero']
            del self.contatos_whatsapp[nome]
            self.salvar_contatos_whatsapp()
            print(f"[WhatsAppClient] Contato removido: {nome} ({numero})")
            return True
        return False

    def buscar_contato_por_nome(self, nome: str) -> Optional[str]:
        """
        Busca o número de um contato pelo nome.
        
        Args:
            nome: Nome do contato
            
        Returns:
            Número do contato se encontrado, None caso contrário
        """
        return self.contatos_whatsapp.get(nome, {}).get('numero')

    def buscar_contato_por_numero(self, numero: str) -> Optional[str]:
        """
        Busca o nome de um contato pelo número.
        
        Args:
            numero: Número do contato
            
        Returns:
            Nome do contato se encontrado, None caso contrário
        """
        for nome, dados in self.contatos_whatsapp.items():
            if dados.get('numero') == numero:
                return nome
        return None

    def listar_contatos_whatsapp(self) -> Dict[str, Dict[str, str]]:
        """
        Retorna todos os contatos do WhatsApp.
        
        Returns:
            Dicionário com todos os contatos
        """
        return self.contatos_whatsapp.copy()

    def extrair_contatos_automaticamente(self) -> int:
        """
        Extrai todos os contatos automaticamente usando o ContactExtractor.
        
        Returns:
            int: Número de contatos extraídos
        """
        try:
            print("[WhatsAppClient] Iniciando extração automática de contatos...")
            contatos = self.contact_extractor.get_all_contacts()
            
            for nome, numero in contatos.items():
                self.adicionar_contato_whatsapp(nome, numero)
            
            print(f"[WhatsAppClient] Extração automática concluída: {len(contatos)} contatos")
            return len(contatos)
            
        except Exception as e:
            print(f"[WhatsAppClient] Erro na extração automática de contatos: {e}")
            return 0

    def buscar_numero_contato(self, nome: str) -> Optional[str]:
        """
        Busca número de um contato pelo nome usando o ContactExtractor.
        
        Args:
            nome: Nome do contato
            
        Returns:
            Optional[str]: Número do contato ou None se não encontrado
        """
        try:
            # Primeiro verifica se já temos o contato no dicionário
            numero_existente = self.buscar_contato_por_nome(nome)
            if numero_existente:
                return numero_existente
            
            # Se não tem, usa o ContactExtractor para buscar
            numero = self.contact_extractor.get_contact_number(nome)
            if numero:
                # Adiciona ao dicionário para futuras consultas
                self.adicionar_contato_whatsapp(nome, numero)
                return numero
            
            return None
            
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao buscar número do contato '{nome}': {e}")
            return None

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
        
        # Atualiza também o dicionário de contatos do WhatsApp
        self.adicionar_contato_whatsapp(nome_contato, numero)
        
        # Salva automaticamente após cada atualização
        self.salvar_dados_clientes()

    def close(self):
        """Fecha o cliente e salva os dados"""
        try:
            # Salva dados dos clientes antes de fechar
            self.salvar_dados_clientes()
            
            # Salva contatos do WhatsApp antes de fechar
            self.salvar_contatos_whatsapp()
            
            # Fecha o driver
            self.driver.close()
            print("[WhatsAppClient] Cliente fechado, dados dos clientes e contatos salvos")
        except:
            pass

    def force_send_message(self, phone_number: str, message: str, method: str = "url") -> bool:
        """
        Força envio de mensagem quando contato não é encontrado
        
        Args:
            phone_number: Número do telefone
            message: Mensagem a ser enviada
            method: Método a ser usado ("url" ou "search")
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            print(f"[WhatsAppClient] Tentando envio forçado para {phone_number}")
            return self.driver.force_send_message(phone_number, message, method)
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao forçar envio de mensagem: {e}")
            return False
