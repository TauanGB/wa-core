"""
Constantes de seletores para automação do WhatsApp Web.
Carrega seletores de um arquivo JSON e permite recarregamento dinâmico.
"""
import json
import os


class WhatsAppSelectors:
    """Constantes de seletores para elementos do WhatsApp Web"""
    
    # Inicializa as variáveis com valores padrão
    CSS_SELECTOR_LOCK_OUTLINE = 'span[data-icon="lock-outline"]'
    CSS_SELECTOR_CONVERSATIONS_LIST = 'div[aria-label="Lista de conversas"]'
    CSS_SELECTOR_QR_CODE = 'canvas[aria-label="Código QR"]'
    CSS_SELECTOR_UNREAD_MESSAGES = 'span[aria-label*="mensagens não lidas"]'
    XPATH_UNREAD_MESSAGES_ANCESTOR = '//span[contains(@aria-label,"mensagens não lidas")]/ancestor::div[@role="none"]'
    XPATH_UNREAD_MESSAGES_CONTACT_NAME = '//span[contains(@aria-label,"mensagens não lidas")]/ancestor::div[@role="none"]//div[@role="gridcell"]//span'
    CSS_SELECTOR_UNREAD_INSIDE_CONTACT_NAME = 'span[title][dir]'
    XPATH_UNREAD_MESSAGES_COUNT = '//span[contains(@aria-label,"mensagens não lidas")]'
    CSS_SELECTOR_INSIDE_MESSAGES_COUNT = 'div[role] span[aria-label*="mensa"]'
    CSS_SELECTOR_MESSAGE_OUT = 'div[data-id] div[class*="message-out"]'
    XPATH_MESSAGE_IN = '//div[@data-id]/descendant::div[contains(@class,"message-in")]'
    XPATH_MESSAGE_TEXT = '//div[@data-pre-plain-text]'
    XPATH_MESSAGE_DATE = '//div[@data-pre-plain-text]'
    XPATH_MESSAGE_INPUT = '//div[@aria-placeholder and @spellcheck and @aria-activedescendant]'
    XPATH_SEARCH_INPUT = '//div[@id="side"]//div[contains(@class,"lexical-rich-text-input")]'
    CSS_SELECTOR_MESSAGE_COMPOSER = 'footer div[contenteditable="true"]'
    XPATH_SEND_BUTTON = '//span[@data-icon="wds-ic-send-filled"]'
    CSS_SELECTOR_MORE_BUTTON = 'div#main span[data-icon="more-refreshed"]'
    XPATH_INFO_BUTTON = '//span[@data-icon="info-refreshed"]/ancestor::li'
    CSS_SELECTOR_CLOSE_BUTTON = 'span[data-icon="close-refreshed"]'
    CSS_SELECTOR_CLOSE_CIRCLE_BUTTON = 'span[data-icon="close-circle-refreshed"]'
    XPATH_CLOSE_INFO_BUTTON = '(//header)[5]//span[contains(@data-icon,"close-refreshed")]'
    CSS_SELECTOR_CONTACTS_LIST = 'div[id="pane-side"] div[aria-label*="pesquisa"] > div'
    CSS_SELECTOR_CONTACT_SPAN = 'span'
    CSS_SELECTOR_MAIN_HEADER = 'div#main header'
    XPATH_CONTACT_NAME_IN_HEADER = '//div[@id="main"]//header//span[@dir]'
    XPATH_CONTACT_NUMBER = '//div/ancestor::section//div[contains(text(),"+55")]'
    XPATH_NEW_MESSAGES_CHECK = '//span[contains(@aria-label,"mensagens não lidas")]/ancestor::div[@role="none"]'
    CSS_SELECTOR_MESSAGE_OUT_ICON = 'span[data-icon][aria-label]'
    
    @classmethod
    def reload_selectors(cls):
        """
        Recarrega os seletores do arquivo JSON e atualiza as variáveis.
        
        Returns:
            True se recarregou com sucesso, False caso contrário
        """
        try:
            # Caminho para o arquivo JSON
            json_path = os.path.join(os.path.dirname(__file__), 'selectors.json')
            
            if not os.path.exists(json_path):
                print(f"[WhatsAppSelectors] Arquivo JSON não encontrado: {json_path}")
                return False
            
            # Carrega o JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                selectors_data = json.load(f)
            
            # Atualiza as variáveis da classe
            for key, value in selectors_data.items():
                if hasattr(cls, key):
                    setattr(cls, key, value)
                    print(f"[WhatsAppSelectors] Atualizado {key}: {value}")
                else:
                    print(f"[WhatsAppSelectors] Aviso: {key} não encontrado na classe")
            
            print("[WhatsAppSelectors] Seletores recarregados do JSON com sucesso!")
            return True
            
        except Exception as e:
            print(f"[WhatsAppSelectors] Erro ao recarregar seletores: {e}")
            return False


# Carrega os seletores do JSON na inicialização
WhatsAppSelectors.reload_selectors()
