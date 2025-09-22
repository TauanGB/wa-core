"""
Extrator de Contatos do WhatsApp Web
Este módulo contém funções para extrair números de contatos do WhatsApp Web usando Selenium.

INSTRUÇÕES:
1. Substitua o conteúdo deste arquivo pelo código Python com Selenium que você receberá
2. Certifique-se de que as funções retornem os dados no formato esperado
3. Integre as funções ao WhatsAppClient conforme necessário
"""

from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class ContactExtractor:
    """
    Classe para extrair contatos do WhatsApp Web.
    
    INSTRUÇÃO: Substitua o conteúdo desta classe pelo código Python com Selenium
    que você receberá do usuário.
    """
    
    def __init__(self, driver):
        """
        Inicializa o extrator de contatos.
        
        Args:
            driver: Instância do Selenium WebDriver
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def _click_more_button(self):
        """Clica no botão mais"""
        try:
            more = self.driver.find_element(By.CSS_SELECTOR, 'div#main span[data-icon="more-refreshed"]')
            more.click()
            return True
        except Exception as e:
            print(f"[ContactExtractor] Erro ao clicar no botão mais: {e}")
            return False
    
    def get_all_contacts(self) -> Dict[str, str]:
        """
        Extrai todos os contatos do WhatsApp Web.
        
        Returns:
            Dict[str, str]: Dicionário com nome -> número dos contatos
        """
        all_contacts = {}
        
        try:
            print("[ContactExtractor] Iniciando extração de todos os contatos...")
            
            # Primeiro tenta obter contatos da lista de chats
            chat_contacts = self.get_contacts_from_chat_list()
            for name, number in chat_contacts:
                all_contacts[name] = number
            
            print(f"[ContactExtractor] Contatos da lista de chats: {len(chat_contacts)}")
            
            # Depois tenta obter contatos da página de contatos
            page_contacts = self.get_contacts_from_contacts_page()
            for name, number in page_contacts:
                all_contacts[name] = number  # Sobrescreve se já existir
            
            print(f"[ContactExtractor] Contatos da página de contatos: {len(page_contacts)}")
            print(f"[ContactExtractor] Total de contatos únicos obtidos: {len(all_contacts)}")
            
            return all_contacts
            
        except Exception as e:
            print(f"[ContactExtractor] Erro ao extrair todos os contatos: {e}")
            return all_contacts
    
    def get_contact_number(self, contact_name: str) -> Optional[str]:
        """
        Obtém o número de um contato específico pelo nome.
        
        Args:
            contact_name: Nome do contato
            
        Returns:
            Optional[str]: Número do contato ou None se não encontrado
        """
        try:
            # Primeiro, busca o contato na lista de chats
            if not self._find_contact_in_chat_list(contact_name):
                print(f"[ContactExtractor] Contato '{contact_name}' não encontrado na lista de chats")
                return None
            
            # Abre as informações do contato
            if not self._open_contact_info():
                print(f"[ContactExtractor] Falha ao abrir informações do contato '{contact_name}'")
                return None
            
            # Extrai o número do contato
            number = self._extract_contact_number()
            if number:
                print(f"[ContactExtractor] Número encontrado para '{contact_name}': {number}")
                return number
            else:
                print(f"[ContactExtractor] Número não encontrado para '{contact_name}'")
                return None
                
        except Exception as e:
            print(f"[ContactExtractor] Erro ao obter número do contato '{contact_name}': {e}")
            return None
    
    def _find_contact_in_chat_list(self, contact_name: str) -> bool:
        """
        Procura um contato na lista de chats do WhatsApp.
        
        Args:
            contact_name: Nome do contato para procurar
            
        Returns:
            bool: True se encontrou o contato, False caso contrário
        """
        try:
            # Procura pelo contato na lista de chats
            contact_xpath = f"//span[@title='{contact_name}']"
            contact_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, contact_xpath))
            )
            contact_element.click()
            print(f"[ContactExtractor] Contato '{contact_name}' encontrado e clicado")
            return True
        except TimeoutException:
            print(f"[ContactExtractor] Timeout ao procurar contato '{contact_name}'")
            return False
        except Exception as e:
            print(f"[ContactExtractor] Erro ao procurar contato '{contact_name}': {e}")
            return False
    
    def _open_contact_info(self) -> bool:
        """
        Abre as informações do contato clicando no botão 'mais' e depois 'info'.
        
        Returns:
            bool: True se conseguiu abrir as informações, False caso contrário
        """
        try:
            # Verifica se há botão "mais" disponível
            if not self.driver.find_elements(By.CSS_SELECTOR, 'div#main span[data-icon="more-refreshed"]'):
                print("[ContactExtractor] Botão 'mais' não encontrado")
                return False
            
            # Clica no botão "mais"
            if not self._click_more_button():
                print("[ContactExtractor] Erro ao clicar no botão 'mais'")
                return False
            print("[ContactExtractor] Botão 'mais' clicado")
            
            # Aguarda e clica no botão "info"
            info_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[data-icon="info-refreshed"]'))
            )
            info_btn.click()
            print("[ContactExtractor] Botão 'info' clicado")
            
            return True
            
        except TimeoutException:
            print("[ContactExtractor] Timeout ao abrir informações do contato")
            return False
        except Exception as e:
            print(f"[ContactExtractor] Erro ao abrir informações do contato: {e}")
            return False
    
    def _extract_contact_number(self) -> Optional[str]:
        """
        Extrai o número do contato das informações abertas.
        
        Returns:
            Optional[str]: Número do contato ou None se não encontrado
        """
        try:
            # Aguarda o elemento com o número aparecer
            number_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div/ancestor::section//div[contains(text(), "+55")]'))
            )
            
            # Extrai o texto do número
            number_text = number_element.text.strip()
            print(f"[ContactExtractor] Número extraído: {number_text}")
            
            # Limpa e formata o número (remove caracteres especiais, espaços, etc.)
            cleaned_number = self._clean_phone_number(number_text)
            
            return cleaned_number
            
        except TimeoutException:
            print("[ContactExtractor] Timeout ao extrair número do contato")
            return None
        except Exception as e:
            print(f"[ContactExtractor] Erro ao extrair número do contato: {e}")
            return None
    
    def _clean_phone_number(self, number_text: str) -> str:
        """
        Limpa e formata o número de telefone.
        
        Args:
            number_text: Texto do número extraído
            
        Returns:
            str: Número limpo e formatado
        """
        import re
        
        # Remove todos os caracteres não numéricos exceto o +
        cleaned = re.sub(r'[^\d+]', '', number_text)
        
        # Se não tem +55, adiciona
        if not cleaned.startswith('+55'):
            if cleaned.startswith('55'):
                cleaned = '+' + cleaned
            elif cleaned.startswith('11') or cleaned.startswith('21') or cleaned.startswith('85'):
                cleaned = '+55' + cleaned
            else:
                cleaned = '+55' + cleaned
        
        # Remove o + para retornar apenas números
        final_number = cleaned.replace('+', '')
        
        return final_number
    
    def search_contact_by_name(self, name: str) -> Optional[Tuple[str, str]]:
        """
        Busca um contato pelo nome e retorna nome e número.
        
        Args:
            name: Nome do contato para buscar
            
        Returns:
            Optional[Tuple[str, str]]: Tupla (nome, número) ou None se não encontrado
        """
        try:
            number = self.get_contact_number(name)
            if number:
                return (name, number)
            return None
        except Exception as e:
            print(f"[ContactExtractor] Erro ao buscar contato '{name}': {e}")
            return None
    
    def get_contacts_from_chat_list(self) -> List[Tuple[str, str]]:
        """
        Obtém contatos da lista de chats.
        
        Returns:
            List[Tuple[str, str]]: Lista de tuplas (nome, número)
        """
        contacts = []
        try:
            # Procura por todos os elementos de contato na lista de chats
            chat_elements = self.driver.find_elements(By.XPATH, "//div[@data-testid='chat-list']//span[@title]")
            
            for element in chat_elements:
                try:
                    contact_name = element.get_attribute('title')
                    if contact_name and contact_name.strip():
                        # Obtém o número do contato
                        number = self.get_contact_number(contact_name)
                        if number:
                            contacts.append((contact_name, number))
                            print(f"[ContactExtractor] Contato adicionado: {contact_name} -> {number}")
                        else:
                            print(f"[ContactExtractor] Não foi possível obter número para: {contact_name}")
                except Exception as e:
                    print(f"[ContactExtractor] Erro ao processar elemento: {e}")
                    continue
            
            print(f"[ContactExtractor] Total de contatos obtidos da lista de chats: {len(contacts)}")
            return contacts
            
        except Exception as e:
            print(f"[ContactExtractor] Erro ao obter contatos da lista de chats: {e}")
            return []
    
    def get_contacts_from_contacts_page(self) -> List[Tuple[str, str]]:
        """
        Obtém contatos da página de contatos.
        
        Returns:
            List[Tuple[str, str]]: Lista de tuplas (nome, número)
        """
        contacts = []
        try:
            # Navega para a página de contatos (se necessário)
            # Nota: Esta implementação assume que já estamos na página correta
            # ou que a navegação será feita pelo método que chama esta função
            
            # Procura por elementos de contato na página de contatos
            contact_elements = self.driver.find_elements(By.XPATH, "//div[@data-testid='contact']//span[@title]")
            
            for element in contact_elements:
                try:
                    contact_name = element.get_attribute('title')
                    if contact_name and contact_name.strip():
                        # Obtém o número do contato
                        number = self.get_contact_number(contact_name)
                        if number:
                            contacts.append((contact_name, number))
                            print(f"[ContactExtractor] Contato adicionado: {contact_name} -> {number}")
                        else:
                            print(f"[ContactExtractor] Não foi possível obter número para: {contact_name}")
                except Exception as e:
                    print(f"[ContactExtractor] Erro ao processar elemento: {e}")
                    continue
            
            print(f"[ContactExtractor] Total de contatos obtidos da página de contatos: {len(contacts)}")
            return contacts
            
        except Exception as e:
            print(f"[ContactExtractor] Erro ao obter contatos da página de contatos: {e}")
            return []


# INSTRUÇÕES PARA INTEGRAÇÃO:
"""
1. Substitua o conteúdo da classe ContactExtractor acima pelo código Python com Selenium
   que você receberá do usuário.

2. Integre as funções ao WhatsAppClient modificando o arquivo whatsapp_client.py:

   from .contact_extractor import ContactExtractor
   
   # No método __init__ do WhatsAppClient:
   self.contact_extractor = ContactExtractor(self.driver.driver)
   
   # Adicione métodos para usar o extrator:
   def extrair_contatos_automaticamente(self):
       \"\"\"Extrai todos os contatos automaticamente\"\"\"
       contatos = self.contact_extractor.get_all_contacts()
       for nome, numero in contatos.items():
           self.adicionar_contato_whatsapp(nome, numero)
       return len(contatos)
   
   def buscar_numero_contato(self, nome: str) -> Optional[str]:
       \"\"\"Busca número de um contato pelo nome\"\"\"
       return self.contact_extractor.get_contact_number(nome)

3. O sistema já está preparado para:
   - Salvar contatos automaticamente em contatos_whatsapp.json
   - Buscar contatos por nome ou número
   - Integrar com o sistema de filas
   - Atualizar em tempo real conforme novos contatos são encontrados

4. Os contatos serão automaticamente adicionados ao dicionário quando:
   - Uma nova mensagem é recebida
   - O sistema detecta um novo contato
   - Uma busca manual é realizada

FORMATO ESPERADO DOS DADOS:
- Nome do contato: String (como aparece no WhatsApp Web)
- Número: String no formato "5511999999999" (com código do país)
- Os dados serão salvos automaticamente em JSON no diretório da sessão
"""
