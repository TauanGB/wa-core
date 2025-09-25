"""
Cliente WhatsApp que utiliza o SeleniumDriver para interagir com o WhatsApp Web.
Interface de alto nível que encapsula todas as funcionalidades do SeleniumDriver,
fornecendo uma API limpa e segura para interação com o WhatsApp Web.

Funcionalidades principais:
- Envio e recebimento de mensagens
- Gerenciamento completo de dados de clientes (CRUD)
- Autenticação e gerenciamento de sessão
- Recarregamento dinâmico de seletores
- Extração automática de contatos
- Injeção de scripts JavaScript

O SeleniumDriver é completamente encapsulado e não deve ser acessado diretamente.
"""
import time as tm
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from .selenium_driver import SeleniumDriver
from .exceptions import WhatsAppConnectionError, WhatsAppMessageError


class WhatsAppClient:
    """
    Cliente para interagir com o WhatsApp Web usando Selenium.
    
    Esta classe fornece uma interface de alto nível e segura para interagir com o WhatsApp Web,
    encapsulando completamente o SeleniumDriver. O usuário nunca deve acessar diretamente
    o driver interno.
    
    Funcionalidades principais:
    - Envio e recebimento de mensagens (send_message_to_contact, check_new_messages)
    - Gerenciamento de contatos (buscar_numero_contato, buscar_cliente_por_apelido)
    - Gerenciamento de dados de clientes (adicionar_cliente, atualizar_dados_cliente, remover_cliente, obter_dados_cliente, listar_clientes)
    - Autenticação e sessão (wait_for_login, is_logged_in, save_session)
    - Recarregamento dinâmico de seletores (reload_selectors)
    - Extração automática de contatos (extract_all_contacts)
    - Injeção de scripts JavaScript (inject_javascript)
    
    Exemplo de uso:
        client = WhatsAppClient("my_session")
        client.wait_for_login()
        
        # Adicionar cliente sem incrementar mensagens
        client.adicionar_cliente("5511999999999", "João Silva", incrementar_mensagem=False)
        
        # Enviar mensagem e atualizar dados
        client.send_message_to_contact("5511999999999", "João", "Olá!")
        
        # Atualizar dados específicos
        client.atualizar_dados_cliente_especificos("5511999999999", apelido="João Atualizado")
        
        # Buscar cliente por apelido
        numero = client.buscar_cliente_por_apelido("João Atualizado")
        
        # Listar todos os clientes
        clientes = client.listar_clientes()
        
        messages = client.check_new_messages()
        client.close()
    """
    
    def __init__(self, session_path: str = "whatsapp_session"):
        """
        Inicializa o cliente WhatsApp.
        
        Args:
            session_path: Caminho para salvar a sessão do WhatsApp
        """
        print("[WhatsAppClient] Iniciando...")
        
        self.session_path = session_path
        self._driver = SeleniumDriver(session_path)
        
        # Dicionário para armazenar dados dos clientes (número -> dados do cliente)
        self.dados_clientes = {}
        
        # Carrega dados existentes dos clientes
        self.carregar_dados_clientes()


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


    def extrair_contatos_automaticamente(self) -> int:
        """
        Extrai todos os contatos automaticamente usando o SeleniumDriver.
        
        Returns:
            int: Número de contatos extraídos
        """
        try:
            print("[WhatsAppClient] Iniciando extração automática de contatos...")
            
            # Usa o método do driver para extrair contatos
            contatos = self._driver.extrair_todos_contatos()
            
            # Adiciona os contatos aos dados dos clientes
            for nome, numero in contatos.items():
                self.atualizar_dados_cliente(numero, nome, "")
            
            print(f"[WhatsAppClient] Extração automática concluída: {len(contatos)} contatos")
            return len(contatos)
            
        except Exception as e:
            print(f"[WhatsAppClient] Erro na extração automática de contatos: {e}")
            return 0

    def buscar_numero_contato(self, nome: str) -> Optional[str]:
        """
        Busca número de um contato pelo nome.
        
        Args:
            nome: Nome do contato
            
        Returns:
            Optional[str]: Número do contato ou None se não encontrado
        """
        try:
            # Primeiro verifica se já temos o contato nos dados dos clientes
            for numero, dados in self.dados_clientes.items():
                if dados.get('apelido') == nome:
                    return numero
            
            # Se não tem, usa o SeleniumDriver para buscar
            numero = self._driver.buscar_numero_contato(nome)
            if numero:
                # Adiciona aos dados dos clientes para futuras consultas
                self.atualizar_dados_cliente(numero, nome, "")
                return numero
            
            return None
            
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao buscar número do contato '{nome}': {e}")
            return None

    def adicionar_cliente(self, numero: str, apelido: str, ultima_mensagem: str = "", incrementar_mensagem: bool = True) -> bool:
        """
        Adiciona ou atualiza dados básicos de um cliente.
        
        Args:
            numero: Número do cliente
            apelido: Nome/apelido do contato
            ultima_mensagem: Última mensagem (opcional)
            incrementar_mensagem: Se deve incrementar o contador de mensagens
            
        Returns:
            True se adicionou/atualizou com sucesso, False caso contrário
        """
        try:
            # Mantém dados existentes se o cliente já existe
            dados_existentes = self.dados_clientes.get(numero, {})
            total_mensagens = dados_existentes.get('total_mensagens', 0)
            
            if incrementar_mensagem:
                total_mensagens += 1
            
            self.dados_clientes[numero] = {
                'numero': numero,
                'apelido': apelido,
                'ultima_mensagem': ultima_mensagem,
                'ultima_atividade': datetime.now().isoformat(),
                'total_mensagens': total_mensagens,
                'data_criacao': dados_existentes.get('data_criacao', datetime.now().isoformat())
            }
            
            # Salva automaticamente após cada atualização
            self.salvar_dados_clientes()
            print(f"[WhatsAppClient] Cliente adicionado/atualizado: {apelido} ({numero})")
            return True
            
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao adicionar cliente {numero}: {e}")
            return False

    def atualizar_dados_cliente(self, numero: str, nome_contato: str, ultima_mensagem: str):
        """
        Atualiza ou cria dados de um cliente (método legado - mantido para compatibilidade).
        
        Args:
            numero: Número do cliente
            nome_contato: Nome do contato
            ultima_mensagem: Última mensagem enviada pelo cliente
        """
        return self.adicionar_cliente(numero, nome_contato, ultima_mensagem, incrementar_mensagem=True)

    def atualizar_dados_cliente_especificos(self, numero: str, **kwargs) -> bool:
        """
        Atualiza campos específicos de um cliente existente.
        
        Args:
            numero: Número do cliente
            **kwargs: Campos para atualizar (apelido, ultima_mensagem, etc.)
            
        Returns:
            True se atualizou com sucesso, False caso contrário
        """
        try:
            if numero not in self.dados_clientes:
                print(f"[WhatsAppClient] Cliente {numero} não encontrado")
                return False
            
            # Atualiza apenas os campos fornecidos
            for campo, valor in kwargs.items():
                if campo in ['apelido', 'ultima_mensagem']:
                    self.dados_clientes[numero][campo] = valor
            
            # Atualiza sempre a última atividade
            self.dados_clientes[numero]['ultima_atividade'] = datetime.now().isoformat()
            
            # Salva automaticamente após cada atualização
            self.salvar_dados_clientes()
            print(f"[WhatsAppClient] Dados do cliente {numero} atualizados")
            return True
            
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao atualizar dados específicos do cliente {numero}: {e}")
            return False

    def remover_cliente(self, numero: str) -> bool:
        """
        Remove um cliente dos dados salvos.
        
        Args:
            numero: Número do cliente a ser removido
            
        Returns:
            True se removeu com sucesso, False caso contrário
        """
        try:
            if numero in self.dados_clientes:
                apelido = self.dados_clientes[numero].get('apelido', numero)
                del self.dados_clientes[numero]
                self.salvar_dados_clientes()
                print(f"[WhatsAppClient] Cliente removido: {apelido} ({numero})")
                return True
            else:
                print(f"[WhatsAppClient] Cliente {numero} não encontrado")
                return False
                
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao remover cliente {numero}: {e}")
            return False

    def obter_dados_cliente(self, numero: str) -> Optional[Dict[str, Any]]:
        """
        Obtém dados completos de um cliente específico.
        
        Args:
            numero: Número do cliente
            
        Returns:
            Dicionário com dados do cliente ou None se não encontrado
        """
        return self.dados_clientes.get(numero)

    def listar_clientes(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna todos os clientes cadastrados.
        
        Returns:
            Dicionário com todos os clientes
        """
        return self.dados_clientes.copy()

    def buscar_cliente_por_apelido(self, apelido: str) -> Optional[str]:
        """
        Busca o número de um cliente pelo apelido.
        
        Args:
            apelido: Apelido/nome do cliente
            
        Returns:
            Número do cliente se encontrado, None caso contrário
        """
        for numero, dados in self.dados_clientes.items():
            if dados.get('apelido') == apelido:
                return numero
        return None

    def close(self):
        """Fecha o cliente e salva os dados"""
        try:
            # Salva dados dos clientes antes de fechar
            self.salvar_dados_clientes()
            
            # Fecha o driver
            self._driver.close()
            print("[WhatsAppClient] Cliente fechado, dados dos clientes salvos")
        except:
            pass

    # =============================================================================
    # MÉTODOS PÚBLICOS - INTERFACE PARA MENSAGENS E CONTATOS
    # =============================================================================
    
    def check_new_messages(self) -> List[Dict[str, Any]]:
        """
        Verifica se há novas mensagens não lidas.
        
        Returns:
            Lista de dicionários com informações das mensagens não lidas
        """
        try:
            return self._driver.check_for_new_messages()
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao verificar novas mensagens: {e}")
            return []

    def send_message_to_contact(self, phone_number: str, phone_name: str, message: str) -> bool:
        """
        Envia uma mensagem para um contato específico.
        
        Args:
            phone_number: Número do telefone do contato
            phone_name: Nome do contato
            message: Texto da mensagem a ser enviada
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            # Atualiza dados do cliente antes de enviar
            self.atualizar_dados_cliente(phone_number, phone_name, message)
            
            # Envia a mensagem usando o driver
            success = self._driver.send_message(phone_number, phone_name, message)
            
            if success:
                print(f"[WhatsAppClient] Mensagem enviada com sucesso para {phone_name}")
            
            return success
            
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao enviar mensagem para {phone_name}: {e}")
            return False

    def get_contact_messages(self, phone_number: str, phone_name: str, messages_quantity: int = 1) -> Dict[str, Any]:
        """
        Obtém mensagens de um contato específico.
        
        Args:
            phone_number: Número do telefone do contato
            phone_name: Nome do contato
            messages_quantity: Quantidade de mensagens a obter
            
        Returns:
            Dicionário com as mensagens do contato
        """
        try:
            return self._driver.get_messages_by_contact(phone_number, phone_name, messages_quantity)
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao obter mensagens de {phone_name}: {e}")
            return {'messages': {}, 'phone_number': phone_number, 'phone_name': phone_name}

    def get_contact_info(self, phone_number: str, phone_name: str) -> Dict[str, str]:
        """
        Obtém informações completas de um contato.
        
        Args:
            phone_number: Número do telefone do contato
            phone_name: Nome do contato
            
        Returns:
            Dicionário com informações do contato (nome e número)
        """
        try:
            return self._driver.get_contact_info(phone_number, phone_name)
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao obter informações do contato {phone_name}: {e}")
            return {'nome': phone_name, 'numero': phone_number}

    # =============================================================================
    # MÉTODOS PÚBLICOS - INTERFACE PARA UTILITÁRIOS E CONFIGURAÇÃO
    # =============================================================================
    
    def reload_selectors(self) -> bool:
        """
        Recarrega os seletores do arquivo JSON.
        
        Returns:
            True se recarregou com sucesso, False caso contrário
        """
        try:
            return self._driver.reload_selectors()
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao recarregar seletores: {e}")
            return False

    def inject_javascript(self) -> bool:
        """
        Injeta script JavaScript no WhatsApp Web para funcionalidades avançadas.
        
        Returns:
            True se injetou com sucesso, False caso contrário
        """
        try:
            return self._driver.inject_js_script()
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao injetar JavaScript: {e}")
            return False

    def extract_all_contacts(self) -> int:
        """
        Extrai todos os contatos automaticamente do WhatsApp Web.
        
        Returns:
            Número de contatos extraídos
        """
        try:
            return self.extrair_contatos_automaticamente()
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao extrair contatos: {e}")
            return 0

    # =============================================================================
    # MÉTODOS PÚBLICOS - INTERFACE PARA AUTENTICAÇÃO E SESSÃO
    # =============================================================================
    
    def wait_for_login(self) -> None:
        """
        Aguarda o login no WhatsApp Web.
        """
        try:
            self._driver.wait_for_login()
            print("[WhatsAppClient] Login realizado com sucesso!")
        except Exception as e:
            print(f"[WhatsAppClient] Erro durante login: {e}")

    def is_logged_in(self) -> bool:
        """
        Verifica se está logado no WhatsApp Web.
        
        Returns:
            True se está logado, False caso contrário
        """
        try:
            return self._driver.load_session()
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao verificar status de login: {e}")
            return False

    def save_session(self) -> bool:
        """
        Salva a sessão atual do WhatsApp.
        
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            return self._driver.save_session()
        except Exception as e:
            print(f"[WhatsAppClient] Erro ao salvar sessão: {e}")
            return False


