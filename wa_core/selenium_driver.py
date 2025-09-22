"""
Driver Selenium para automação do WhatsApp Web.
"""
import time as tm
import json
import os
import signal
import sys
import importlib
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from typing import Optional, List, Dict, Any

from .exceptions import SeleniumDriverError, WhatsAppConnectionError
from .selectors import WhatsAppSelectors


class SeleniumDriver:
    """Driver Selenium para automação do WhatsApp Web"""
    
    # =============================================================================
    # CONSTRUTOR E INICIALIZAÇÃO
    # =============================================================================
    
    def __init__(self, session_path: str = "whatsapp_session"):
        """
        Inicializa o driver Selenium com perfil personalizado.
        
        Args:
            session_path: Caminho para salvar a sessão do Firefox
        """
        print("[SeleniumDriver] Iniciando...")
        
        self.session_path = session_path
        self.profile_path = f"{session_path}/firefox_profile"
        
        # Cria o diretório da sessão se não existir
        os.makedirs(self.session_path, exist_ok=True)
        os.makedirs(self.profile_path, exist_ok=True)
        
        try:
            # Configura o driver com perfil personalizado para salvar sessão
            options = webdriver.FirefoxOptions()
            options.add_argument(f"--profile")
            options.add_argument(self.profile_path)
            
            self.driver = webdriver.Firefox(options=options)
            print(f"[SeleniumDriver] Firefox iniciado com perfil em {self.profile_path}")
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao abrir Firefox: {e}")
            raise SeleniumDriverError(f"Erro ao inicializar Firefox: {e}")
        
        # Configura tratamento de sinais para fechar o driver automaticamente
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.driver.maximize_window()
        self.driver.get("https://web.whatsapp.com")
        
        # Tenta carregar sessão existente
        if self.load_session():
            print("[SeleniumDriver] Sessão carregada com sucesso!")
        else:
            print("[SeleniumDriver] Nenhuma sessão encontrada, aguardando login...")
            self.wait_for_login()

    # =============================================================================
    # MÉTODOS PÚBLICOS - AUTENTICAÇÃO E SESSÃO
    # =============================================================================
    
    def wait_for_login(self):
        """Aguarda login no WhatsApp Web"""
        print("[SeleniumDriver] Aguardando login...")
        print("TODO: Faça o scan do QR Code no seu celular")
        
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_LOCK_OUTLINE))
                )
                print("[SeleniumDriver] Conectado ao WhatsApp!")
                
                # Salva a sessão após login bem-sucedido
                self.save_session()
                break
            except:
                print("[SeleniumDriver] Aguardando...")
                tm.sleep(1)

    def load_session(self) -> bool:
        """
        Verifica se a sessão atual está ativa (logada no WhatsApp).
        
        Returns:
            True se a sessão está ativa, False caso contrário
        """
        try:
            # Aguarda a página carregar
            tm.sleep(3)
            
            # Verifica se está logado procurando por elementos da interface principal
            try:
                # Tenta encontrar a lista de conversas (indica que está logado)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_CONVERSATIONS_LIST))
                )
                print("[SeleniumDriver] Sessão ativa detectada - já logado!")
                self.save_session()  # Salva a sessão ativa
                return True
            except:
                # Se não encontrar, verifica se há QR code (indica não logado)
                try:
                    qr_code = self.driver.find_element(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_QR_CODE)
                    print("[SeleniumDriver] QR Code detectado - precisa fazer login")
                    return False
                except:
                    print("[SeleniumDriver] Estado da sessão não determinado")
                    return False
                    
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao verificar sessão: {e}")
            return False

    def save_session(self) -> bool:
        """
        Salva informações da sessão atual para reutilização.
        
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            session_data = {
                'profile_path': self.profile_path,
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'title': self.driver.title
            }
            
            session_file = f"{self.session_path}/session.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"[SeleniumDriver] Sessão salva em {session_file}")
            return True
            
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao salvar sessão: {e}")
            return False

    # =============================================================================
    # MÉTODOS PÚBLICOS - MENSAGENS E CONTATOS
    # =============================================================================
    
    def check_for_new_messages(self) -> list:
        """
        Verifica se há novas mensagens não lidas.
        
        Returns:
            Lista de mensagens não lidas
        """
        try:
            new_messages = self.pass_if_have_new_messages()
            
            if new_messages:
                unread = []
                #TODO Terminar de implementar
                for chat in new_messages:
                    contact_name = chat.find_element(By.XPATH, WhatsAppSelectors.XPATH_UNREAD_MESSAGES_CONTACT_NAME).text.strip()
                    messages_number = chat.find_element(By.XPATH, WhatsAppSelectors.XPATH_UNREAD_MESSAGES_COUNT).text.strip()
                    
                    unread.append({
                        'contact_name': contact_name,
                        'messages_number': messages_number
                    })

                    
                    
            unread = self.driver.find_elements(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_UNREAD_MESSAGES)
            return unread
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao verificar mensagens: {e}")
            return []

    def send_message(self, phone_number: str, phone_name: str, text: str) -> bool:
        """
        Envia uma mensagem utilizando dois métodos diferentes para abrir a conversa e para enviar o texto.
        
        Args:
            phone_number: Número do telefone para envio
            phone_name: Nome do contato para envio
            text: Texto da mensagem a ser enviada
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        # Validação de parâmetros
        if not phone_number or not phone_name or not text or not (len(phone_number) >= 12 and len(phone_number) <= 13):
            print("[SeleniumDriver] Parâmetros inválidos: phone_number, phone_name e text são obrigatórios")
            return False
        
        try:
            # Tenta abrir a conversa pelo método Selenium, se falhar tenta pelo URL
            chat_opened = self._open_chat_by_javaScript_injetado(phone_number, phone_name, text)
            if not chat_opened:
                print("[SeleniumDriver] Tentando método alternativo (URL)...")
                chat_opened = self._open_chat_by_url(phone_number, phone_name, text)
            
            if not chat_opened:
                print("[SeleniumDriver] Falha ao abrir conversa por ambos os métodos")
                return False

            # Tenta inserir o texto pelo Selenium, se falhar tenta via JavaScript
            text_inserted = self._send_input_text_by_javascript(phone_number, phone_name, text)
            if not text_inserted:
                print("[SeleniumDriver] Tentando inserção via Selenium...")
                
            if self._wait_is_message_inserted_in_input(text):
                print("[SeleniumDriver] Texto inserido com sucesso")
            else:
                print("[SeleniumDriver] Falha ao inserir texto")
                return False

            # Tenta enviar a mensagem pressionando Enter, se falhar tenta clicar no botão
            last_message = self.driver.find_elements(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MESSAGE_OUT)[-1]
            
            if not self._click_send_button_by_click():
                print("[SeleniumDriver] Tentando envio por clique no botão...")
                tm.sleep(1)
                
            # Verifica se a mensagem foi enviada
            if self._is_message_sent(last_message):
                print(f"[SeleniumDriver] Mensagem enviada com sucesso para {phone_name} ({phone_number})")
            else:
                print("[SeleniumDriver] Mensagem não enviada")
                return False

            self._close_current_chat()
            
        except Exception as e:
            print(f"[SeleniumDriver] Erro inesperado ao enviar mensagem: {e}")
            return False
        
    def get_messages_by_contact(self, phone_number: str, phone_name: str, messages_quantity: int = 1) -> dict:
        """
        Obtém as mensagens do contato.
        
        Args:
            phone_number: Número do telefone
            phone_name: Nome do contato
            messages_quantity: Quantidade de mensagens a serem obtidas
        Returns:
            Dict com as mensagens do contato
        """
        try:
            self._open_chat_by_javaScript_injetado(phone_number, phone_name, "")
        except:
            print("[SeleniumDriver] Erro ao abrir conversa pelo javaScript injetado")
            try:
                self._open_chat_by_url(phone_number, phone_name, "")
            except:
                print("[SeleniumDriver] Erro ao abrir conversa pelo URL")
                raise Exception("Erro ao abrir conversa por ambos os métodos")
            
        messages = self.driver.find_elements(By.XPATH, WhatsAppSelectors.XPATH_MESSAGE_IN)[:(messages_quantity*-1)]
        messages_list = {}

        for message in messages:
            text = message.find_element(By.XPATH, WhatsAppSelectors.XPATH_MESSAGE_TEXT).text.strip()
            date = message.find_element(By.XPATH, WhatsAppSelectors.XPATH_MESSAGE_DATE).get_attribute('data-pre-plain-text')
            messages_list[text] = date
        return {
            'messages': messages_list,
            'phone_number': phone_number,
            'phone_name': phone_name
        }

    def get_contact_info(self, phone_number: str, phone_name: str) -> dict:
        """
        Obtém informações completas do contato atual (nome e número).
        
        Args:
            phone_number: Número do telefone
            phone_name: Nome do contato
            
        Returns:
            Dict com 'nome' e 'numero' do contato atual
        """
        try:
            #entra no contato
            try:
                self._open_chat_by_javaScript_injetado(phone_number, phone_name, "")
            except:
                print("[SeleniumDriver] Erro ao abrir conversa pelo Selenium")
                try:
                    self._open_chat_by_url(phone_number, phone_name, "")
                except:
                    print("[SeleniumDriver] Erro ao abrir conversa pelo Selenium")
                raise Exception("Erro ao abrir conversa por ambos os métodos")
            
            # Obtém o nome do contato
            nome_contato = "Desconhecido"
            try:
                header = self.driver.find_element(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MAIN_HEADER)
                nome_contato = header.find_element(By.XPATH, WhatsAppSelectors.XPATH_CONTACT_NAME_IN_HEADER).text.strip()
            except:
                print("[SeleniumDriver] Erro ao obter nome do contato")
            
            # Obtém o número do contato
            numero_contato = None
            try:
                # Verifica se existe o botão "mais" (três pontos)
                if self.driver.find_elements(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MORE_BUTTON):
                    
                    if not self._click_more_button():
                        raise Exception("[SeleniumDriver] Erro ao clicar no botão mais")
                    
                    # Aguarda o botão de informações aparecer
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, WhatsAppSelectors.XPATH_INFO_BUTTON))
                    )
                    info_btn = self.driver.find_element(By.XPATH, WhatsAppSelectors.XPATH_INFO_BUTTON)
                    info_btn.click()

                    # Aguarda o número aparecer
                    WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, WhatsAppSelectors.XPATH_CONTACT_NUMBER)))
                    
                    # Tenta obter o número do contato com persistência (até 5 tentativas)
                    tentativas = 0
                    contact_number = None
                    while tentativas < 5:
                        try:
                            contact_number = self.driver.find_element(By.XPATH, WhatsAppSelectors.XPATH_CONTACT_NUMBER).text
                            if contact_number and contact_number.strip() != "":
                                break
                            else:
                                print(f"[SeleniumDriver] Tentativa {tentativas} de 5: Número do contato não encontrado")
                        except:
                            pass
                        tm.sleep(1)
                        tentativas += 1
                    
                    if not contact_number:
                        raise Exception("[SeleniumDriver] Número do contato não encontrado")
                    else:
                        numero_contato = contact_number.strip()
                    
                    # Fechando informações do contato
                    try:
                        close_btn = self.driver.find_element(By.XPATH, WhatsAppSelectors.XPATH_CLOSE_INFO_BUTTON)
                        close_btn.click()
                    except:
                        print("[SeleniumDriver] Erro ao fechar informações do contato")
                        print("[SeleniumDriver] Reiniciando pagina para fechar informações do contato")
                        if not self._reload_page():
                            raise Exception("[SeleniumDriver] Erro ao reiniciar pagina")
            except Exception as e:
                print(f"[SeleniumDriver] Erro ao obter número do contato: {e}")
                
            return {
                'nome': nome_contato,
                'numero': numero_contato
            }
                
        except Exception as e:
            print(f"[SeleniumDriver] Erro geral ao obter informações do contato: {e}")
            return {
                'nome': "Desconhecido",
                'numero': ""
            }

    # =============================================================================
    # MÉTODOS PÚBLICOS - UTILITÁRIOS E JAVASCRIPT
    # =============================================================================
    
    def reload_selectors(self) -> bool:
        """
        Recarrega os seletores do arquivo JSON e atualiza as variáveis.
        
        Returns:
            True se recarregou com sucesso, False caso contrário
        """
        try:
            # Usa o método reload_selectors da instância global
            sucesso = WhatsAppSelectors.reload_selectors()
            
            if sucesso:
                print("[SeleniumDriver] Seletores recarregados do JSON com sucesso!")
            else:
                print("[SeleniumDriver] Falha ao recarregar seletores do JSON")
            
            return sucesso
            
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao recarregar seletores: {e}")
            return False
    
    def inject_js_script(self) -> bool:
        """
        Injeta o script JavaScript na página para permitir uso manual da função whatsType.
        
        Returns:
            True se injetou com sucesso, False caso contrário
        """
        try:
            # Verificar se já foi injetado
            if self.driver.execute_script("return typeof window.whatsType === 'function'"):
                print("[SeleniumDriver] Script já foi injetado anteriormente")
            
            
            # Carregar script do arquivo externo
            script_path = os.path.join(os.path.dirname(__file__), 'whatsapp_scripts.js')
            
            if not os.path.exists(script_path):
                print(f"[SeleniumDriver] Arquivo de script não encontrado: {script_path}")
                return False
            
            with open(script_path, 'r', encoding='utf-8') as f:
                js_script = f.read()
            
            # Injeta o script JavaScript na página
            result = self.driver.execute_script(js_script)
            
            # Validação: Verificar se a injeção foi bem-sucedida
            if self.driver.execute_script("return typeof window.whatsType === 'function'"):
                print("[SeleniumDriver] Script JavaScript injetado com sucesso!")
                print("[SeleniumDriver] Agora você pode usar 'whatsType(\"mensagem\")' no console do navegador")
                return True
            else:
                print("[SeleniumDriver] Falha na validação do script injetado")
                return False
            
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao injetar script JavaScript: {e}")
            return False

    # =============================================================================
    # MÉTODOS PÚBLICOS - CONTROLE E FINALIZAÇÃO
    # =============================================================================
    
    def signal_handler(self, signum, frame):
        """
        Trata sinais de interrupção (Ctrl+C, SIGTERM) para fechar o driver automaticamente.
        """
        print(f"\n[SeleniumDriver] Recebido sinal {signum}. Encerrando o driver...")
        self.close()
        sys.exit(0)

    def close(self):
        """Fecha o driver e salva a sessão"""
        try:
            # Salva a sessão antes de fechar
            self.save_session()
            
            self.driver.quit()
            print("[SeleniumDriver] Driver fechado, sessão salva")
        except:
            pass

    # =============================================================================
    # MÉTODOS PRIVADOS - VERIFICAÇÃO DE ESTADO
    # =============================================================================
    
    def _is_message_sent(self,last_message: WebElement) -> bool:
        """
        Verifica se a mensagem foi enviada.
        
        Args:
            last_message: Última mensagem enviada
        """
        try:
            tentativas = 0
            max_tentativas = 10
            while tentativas < max_tentativas:
                #verifica se a ultima mensagem enviada é a mesma que a ultima mensagem na lista de mensagens enviadas
                if last_message != self.driver.find_elements(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MESSAGE_OUT)[-1]:
                    mensagem_enviada_icone = self.driver.find_elements(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MESSAGE_OUT)[-1].find_element(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MESSAGE_OUT_ICON)
                    if mensagem_enviada_icone.get_attribute('data-icon') in ('msg-dblcheck','msg-check'):
                        return True
                    tm.sleep(1)
                else:
                    #se a ultima mensagem enviada não é a mesma que a ultima mensagem na lista de mensagens enviadas, espera 1 segundo e tenta novamente
                    tm.sleep(1)
                    tentativas += 1
                    print(f"[SeleniumDriver] Tentativa {tentativas} de {max_tentativas}: Verificando se a mensagem foi enviada")
            else:
                return False

        except:
            return False
        
    def _wait_is_number_inserted_in_input(self, text: str) -> bool:
        """
        Verifica se o número foi inserido no campo de pesquisa.
        
        Args:
            text: Número do telefone
        """
        try:
            tentativas = 0
            while True:
                try:
                    print(f"[SeleniumDriver] Tentativa {tentativas} de 5: Verificando se o número foi inserido no campo de pesquisa: {text}")
                    return text in self.driver.find_element(By.XPATH, WhatsAppSelectors.XPATH_SEARCH_INPUT).text
                except Exception as e:
                    print(f"[SeleniumDriver] Erro ao verificar se o número foi inserido no campo de pesquisa: {e}")
                    tm.sleep(1)
                    tentativas += 1
                    if tentativas >= 5:
                        return False
        except:
            return False

    def _wait_is_message_inserted_in_input(self, text: str) -> bool:
        """
        Verifica se o texto foi inserido no campo de mensagem.
        
        Args:
            text: Texto da mensagem
        """
        try:
            tentativas = 0
            while True:
                try:
                    print(f"[SeleniumDriver] Tentativa {tentativas} de 5: Verificando se o texto foi inserido no campo de mensagem: {text}")
                    return text in self.driver.find_element(By.XPATH, WhatsAppSelectors.XPATH_MESSAGE_INPUT).text
                except Exception as e:
                    print(f"[SeleniumDriver] Erro ao verificar se o texto foi inserido no campo de mensagem: {e}")
                    tm.sleep(1)
                    tentativas += 1
                    if tentativas >= 5:
                        return False
        except:
            return False

    def pass_if_have_new_messages(self) -> list:
        """
        Passa se tiver novas mensagens.
        
        Returns:
            Lista de mensagens não lidas
        """
        try:
            messages = self.driver.find_elements(By.XPATH, WhatsAppSelectors.XPATH_NEW_MESSAGES_CHECK)
            if messages:
                return messages[1:]
            return []
        except:
            raise Exception("[SeleniumDriver] Erro ao verificar novas mensagens")

    # =============================================================================
    # MÉTODOS PRIVADOS - ABERTURA DE CONVERSAS
    # =============================================================================
    
    def _open_chat_by_javaScript_injetado(self, phone_number: str, phone_name: str, text: str) -> bool:
        """
        Abre conversa usando Selenium para buscar e selecionar contato.
        
        Args:
            phone_number: Número do telefone
            phone_name: Nome do contato
            text: Texto da mensagem (não usado nesta função)
            
        Returns:
            True se conseguiu abrir a conversa, False caso contrário
        """
        try:
            # Executa script para buscar o contato
            # Verifica se a função sendToWhatsAppSearch já foi injetada no contexto da página
            is_injetada = self.driver.execute_script("return typeof sendToWhatsAppSearch === 'function';")
            if not is_injetada:
                self.inject_js_script()
                tm.sleep(1)
                print("[SeleniumDriver] Função sendToWhatsAppSearch não encontrada. Injete o script JS antes de usar esta função.")
                return False
            self.driver.set_script_timeout(10)
            
            self.driver.execute_script(f'''return sendToWhatsAppSearch("{phone_number.replace('+', '')[2:]}");''')
            tm.sleep(1)

            self._wait_is_number_inserted_in_input(text)

            
            # Verifica se encontrou exatamente um contato
            tentativas = 0
            max_tentativas = 3
            while tentativas < max_tentativas:
                contacts = self.driver.find_elements(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_CONTACTS_LIST)
                if len(contacts) == 2:  # 1 resultado + header
                    if phone_name in contacts[1].find_element(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_CONTACT_SPAN).text:
                        contacts[1].click()
                        contacts[1].click()
                        break
                    else:
                        print(f"[SeleniumDriver] Contato {phone_name} não encontrado (tentativa {tentativas+1})")
                        tentativas += 1
                        tm.sleep(1)
                else:
                    print(f"[SeleniumDriver] Busca retornou {len(contacts)} resultados, esperado 2 (tentativa {tentativas+1})")
                    tentativas += 1
                    tm.sleep(1)
            else:
                print(f"[SeleniumDriver] Não foi possível encontrar o contato {phone_name} após {max_tentativas} tentativas")
                return False

            # Fecha a busca
            close_btn = self.driver.find_element(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_CLOSE_BUTTON)
            close_btn.click()
            
            # Aguarda o campo de mensagem aparecer
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MESSAGE_COMPOSER))
            )
            print(f"[SeleniumDriver] Conversa aberta com sucesso para {phone_name}")
            return True
                
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao abrir conversa pelo Selenium: {e}")
            return False
    
    def _open_chat_by_url(self, phone_number: str, phone_name: str, text: str) -> bool:
        """
        Abre conversa usando URL direta do WhatsApp Web.
        
        Args:
            phone_number: Número do telefone
            phone_name: Nome do contato
            text: Texto da mensagem (incluído na URL)
            
        Returns:
            True se conseguiu abrir a conversa, False caso contrário
        """
        try:
            # Constrói URL com número e texto
            clean_number = phone_number.replace('+', '').replace(' ', '')
            url = f"https://web.whatsapp.com/send?phone={clean_number}&text={text}"
            
            print(f"[SeleniumDriver] Navegando para URL: {url}")
            self.driver.get(url)
            
            # Aguarda o campo de mensagem aparecer
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MESSAGE_COMPOSER))
            )
            
            print(f"[SeleniumDriver] Conversa aberta via URL para {phone_name}")
            return True
            
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao abrir conversa pelo URL: {e}")
            return False

    # =============================================================================
    # MÉTODOS PRIVADOS - ENVIO DE MENSAGENS
    # =============================================================================
    
    def _send_input_text_by_javascript(self, phone_number: str, phone_name: str, text: str) -> bool:
        """
        Insere texto no campo de mensagem usando JavaScript.
        
        Args:
            phone_number: Número do telefone
            phone_name: Nome do contato
            text: Texto a ser inserido
            
        Returns:
            True se conseguiu inserir o texto, False caso contrário
        """
        try:
            # Primeiro injeta o script se ainda não estiver disponível
            if not self.driver.execute_script('return typeof window.whatsType === "function"'):
                if not self.inject_js_script():
                    print("[SeleniumDriver] Falha ao injetar script JavaScript")
                    return False
                tm.sleep(1)
            
            # Usa JavaScript para inserir o texto no campo
            result = self.driver.execute_script(
                f'return window.whatsType(arguments[0]);', text
            )
            
            if text in self.driver.page_source:
                print(f"[SeleniumDriver] Texto inserido via JavaScript para {phone_name} ({phone_number}): {text}")
                return True
            else:
                print("[SeleniumDriver] JavaScript retornou False ao inserir texto")
                return False
                
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao inserir texto via JavaScript: {e}")
            return False


    def _click_send_button_by_enter(self) -> bool:
        """
        Envia mensagem pressionando Enter no campo de texto.
        
        Returns:
            True se conseguiu enviar, False caso contrário
        """
        try:
            message_input = self.driver.find_element(By.XPATH, WhatsAppSelectors.XPATH_MESSAGE_INPUT)
            message_input.click()
            message_input.send_keys(Keys.ENTER)
            print("[SeleniumDriver] Mensagem enviada via Enter")
            return True
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao enviar mensagem via Enter: {e}")
            return False

    def _click_send_button_by_click(self) -> bool:
        """
        Envia mensagem clicando no botão de enviar.
        
        Returns:
            True se conseguiu enviar, False caso contrário
        """
        try:
            send_button = self.driver.find_element(By.XPATH, WhatsAppSelectors.XPATH_SEND_BUTTON)
            send_button.click()
            print("[SeleniumDriver] Mensagem enviada via clique no botão")
            return True
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao enviar mensagem via clique: {e}")
            return False

    # =============================================================================
    # MÉTODOS PRIVADOS - CONTROLE DE INTERFACE
    # =============================================================================
    
    def _reload_page(self) -> bool:
        """
        Reinicia a página.
        
        Returns:
            True se reiniciou com sucesso, False caso contrário
        """
        self.driver.execute_script("window.location.reload();")
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_LOCK_OUTLINE)))
        return True

    def _click_more_button(self):
        """Clica no botão mais"""
        try:
            more = self.driver.find_element(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_MORE_BUTTON)
            more.click()
            return True
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao clicar no botão mais: {e}")
            return False

    def _close_current_chat(self) -> bool:
        """Fecha a conversa atual"""
        try:
            if not self._click_more_button():
                raise Exception("[SeleniumDriver] Erro ao clicar no botão mais")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_CLOSE_CIRCLE_BUTTON))
            )
            close_btn = self.driver.find_element(By.CSS_SELECTOR, WhatsAppSelectors.CSS_SELECTOR_CLOSE_CIRCLE_BUTTON)
            close_btn.click()
            tm.sleep(1)
            print("[SeleniumDriver] Conversa fechada")
            return True
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao fechar: {e}")
            return False