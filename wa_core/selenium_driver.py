"""
Driver Selenium para automação do WhatsApp Web.
"""
import time as tm
import json
import os
import signal
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from typing import Optional, List, Dict, Any

from .exceptions import SeleniumDriverError, WhatsAppConnectionError


class SeleniumDriver:
    """Driver Selenium para automação do WhatsApp Web"""
    
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

    def wait_for_login(self):
        """Aguarda login no WhatsApp Web"""
        print("[SeleniumDriver] Aguardando login...")
        print("TODO: Faça o scan do QR Code no seu celular")
        
        while True:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Lista de conversas"]'))
                )
                print("[SeleniumDriver] Conectado ao WhatsApp!")
                
                # Salva a sessão após login bem-sucedido
                self.save_session()
                break
            except:
                print("[SeleniumDriver] Aguardando...")
                tm.sleep(1)

    def check_for_new_messages(self) -> bool:
        """
        Verifica se há novas mensagens não lidas.
        
        Returns:
            True se há mensagens não lidas, False caso contrário
        """
        try:
            # Verifica se há mensagens não lidas
            unread = self.driver.find_elements(By.CSS_SELECTOR, 'span[aria-label*="não lida"]')
            return len(unread) > 0
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao verificar mensagens: {e}")
            return False

    def send_message(self, text: str) -> bool:
        """
        Envia mensagem usando JavaScript para inserir texto e Selenium para enviar.
        
        Args:
            text: Texto da mensagem a ser enviada
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            # Primeiro injeta o script se ainda não estiver disponível
            if not self.driver.execute_script('return typeof window.whatsType === "function"'):
                self.inject_js_script()
                tm.sleep(1)
            
            # Usa JavaScript para inserir o texto no campo
            result = self.driver.execute_script(
                f'return window.whatsType(arguments[0]);', text
            )
            
            if result:
                print(f"[SeleniumDriver] Texto inserido via JavaScript: {text}")
                # Aguarda um momento para o texto ser processado
                tm.sleep(0.5)
                
                # Agora usa Selenium para enviar a mensagem (sem reinserir o texto)
                return self.send_message_selenium(text, skip_input=True)
            else:
                print(f"[SeleniumDriver] Falha ao inserir texto via JavaScript: {text}")
                # Fallback: usa apenas Selenium (inserindo o texto)
                return self.send_message_selenium(text, skip_input=False)
                
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao inserir texto via JavaScript: {e}")
            # Fallback para o método Selenium se o JavaScript falhar
            try:
                print("[SeleniumDriver] Tentando método Selenium completo...")
                return self.send_message_selenium(text)
            except Exception as e2:
                print(f"[SeleniumDriver] Erro no método Selenium: {e2}")
                return False

    def send_message_selenium(self, text: str, skip_input: bool = False) -> bool:
        """
        Envia mensagem usando Selenium (método alternativo).
        
        Args:
            text: Texto da mensagem
            skip_input: Se True, não insere o texto (apenas envia)
            
        Returns:
            True se enviou com sucesso, False caso contrário
        """
        try:
            # Aguarda o campo de mensagem aparecer
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]'))
            )
            
            # Envia a mensagem
            message_input = self.driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            
            if not skip_input:
                message_input.send_keys(text)
            
            # Tenta clicar no botão de enviar
            try:
                send_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-hidden="true"][data-icon="wds-ic-send-filled"]'))
                )
                send_button.click()
                print(f"[SeleniumDriver] Mensagem enviada via Selenium (clique): {text}")
                return True
            except:
                # Se não encontrar o botão, tenta Enter como último recurso
                message_input.send_keys(Keys.ENTER)
                print(f"[SeleniumDriver] Mensagem enviada via Selenium (Enter): {text}")
                return True
                
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao enviar via Selenium: {e}")
            return False

    def get_current_contact(self) -> str:
        """
        Obtém o nome do contato atual.
        
        Returns:
            Nome do contato atual ou "Desconhecido" se não conseguir obter
        """
        try:
            header = self.driver.find_element(By.CSS_SELECTOR, 'div#main header')
            return header.text.split('\n')[0].strip()
        except:
            return "Desconhecido"

    def click_unread_message(self) -> bool:
        """
        Clica na primeira mensagem não lida.
        
        Returns:
            True se clicou com sucesso, False caso contrário
        """
        try:
            unread = self.driver.find_elements(By.CSS_SELECTOR, 'span[aria-label*="não lida"]')
            if unread:
                while True:
                    try:
                        unread[1].click()
                        WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#main header'))
                        )
                        return True
                    except:
                        tm.sleep(1)
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao clicar: {e}")
        return False

    def get_last_message(self) -> str:
        """
        Obtém a última mensagem recebida.
        
        Returns:
            Texto da última mensagem ou string vazia se não conseguir obter
        """
        try:
            messages = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="message-in"] [class*="selectable-text copyable-text"]')
            if messages:
                return messages[-1].text.strip()
            return ""
        except:
            return ""

    def close_current_chat(self):
        """Fecha a conversa atual"""
        try:
            if self.driver.find_elements(By.CSS_SELECTOR, 'div#main button[aria-label="Mais opções"]'):
                more = self.driver.find_element(By.CSS_SELECTOR, 'div#main button[aria-label="Mais opções"]')
                more.click()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-icon="close-circle-refreshed"]'))
                )
                close_btn = self.driver.find_element(By.CSS_SELECTOR, 'span[data-icon="close-circle-refreshed"]')
                close_btn.click()
                tm.sleep(1)
                print("[SeleniumDriver] Conversa fechada")
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao fechar: {e}")

    def inject_js_script(self) -> bool:
        """
        Injeta o script JavaScript na página para permitir uso manual da função whatsType.
        
        Returns:
            True se injetou com sucesso, False caso contrário
        """
        try:
            js_script = """
            (() => {
              // Tenta localizar o compositor da mensagem de forma robusta (PT/EN/ES e variações do WhatsApp)
              function getComposer() {
                const all = [...document.querySelectorAll('[contenteditable="true"]')];
                const candidates = all.filter(el => {
                  const ph = (el.getAttribute('aria-placeholder') || el.getAttribute('placeholder') || '').toLowerCase();
                  const role = el.getAttribute('role');
                  const dataTab = el.getAttribute('data-tab');
                  // Heurísticas comuns no WhatsApp Web
                  const looksLikeComposer =
                    ph.includes('mensagem') || ph.includes('message') || ph.includes('mensaje') ||
                    role === 'textbox' || dataTab === '10' || dataTab === '6';
                  // Mantém apenas os visíveis
                  const rect = el.getBoundingClientRect();
                  const visible = rect.width > 0 && rect.height > 0;
                  return looksLikeComposer && visible;
                });
                // Normalmente o compositor fica mais para baixo na tela
                return candidates.sort((a, b) => b.getBoundingClientRect().top - a.getBoundingClientRect().top)[0] || null;
              }

              function setText(el, text, { append = false } = {}) {
                el.focus();

                // Limpa o campo (se não for append)
                if (!append) {
                  const sel = window.getSelection();
                  sel.removeAllRanges();
                  const range = document.createRange();
                  range.selectNodeContents(el);
                  sel.addRange(range);
                  document.execCommand('delete');
                  el.dispatchEvent(new InputEvent('input', { bubbles: true }));
                }

                // Insere texto de forma compatível com apps baseados em React
                const parts = String(text).split(/\\n/);
                parts.forEach((p, i) => {
                    if (p) document.execCommand('insertText', false, p);
                    if (i < parts.length - 1) {
                        el.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter',code: 'Enter',keyCode: 13,which: 13,shiftKey: true,bubbles: true,cancelable: true,composed: true}));
                        el.dispatchEvent(new KeyboardEvent('keypress', {key: 'Enter',code: 'Enter',keyCode: 13,which: 13,shiftKey: true,bubbles: true,cancelable: true,composed: true}));
                        el.dispatchEvent(new KeyboardEvent('keyup', {key: 'Enter',code: 'Enter',keyCode: 13,which: 13,shiftKey: true,bubbles: true,cancelable: true,composed: true}));
                    }
                });
                console.log('Texto inserido:', text);
                el.dispatchEvent(new InputEvent('input', { bubbles: true }));
              }

              // Exponha uma função global para usar facilmente:
              window.whatsType = function (text, { append = false } = {}) {
                const composer = getComposer();
                if (!composer) {
                  console.warn('Não encontrei o campo de mensagem. Abra uma conversa e tente novamente.');
                  return false;
                }
                setText(composer, text, { append });
                // Retorna true se conseguiu inserir o texto, mas não tenta enviar
                return true;
              };

              console.log('Pronto! Use: whatsType("Sua mensagem aqui") - O envio será feito via Selenium');
            })();
            """
            
            # Injeta o script JavaScript na página
            self.driver.execute_script(js_script)
            print("[SeleniumDriver] Script JavaScript injetado com sucesso!")
            print("[SeleniumDriver] Agora você pode usar 'whatsType(\"mensagem\")' no console do navegador")
            return True
            
        except Exception as e:
            print(f"[SeleniumDriver] Erro ao injetar script JavaScript: {e}")
            return False

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
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Lista de conversas"]'))
                )
                print("[SeleniumDriver] Sessão ativa detectada - já logado!")
                self.save_session()  # Salva a sessão ativa
                return True
            except:
                # Se não encontrar, verifica se há QR code (indica não logado)
                try:
                    qr_code = self.driver.find_element(By.CSS_SELECTOR, 'canvas[aria-label="Código QR"]')
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
