"""
wa-core - Gerenciador funcional do WhatsApp

Um pacote Python para automação e gerenciamento do WhatsApp Web,
perfeito para criar assistentes, bots e aplicações de automação.

Exemplo de uso:
    from wa_core import WhatsAppClient
    
    client = WhatsAppClient()
    if client.check_for_new_messages():
        client.click_unread_message()
        contact_info = client.get_current_contact_info("", "")
        message = client.get_last_message()
        client.send_message(contact_info['numero'], contact_info['nome'], "Olá! Como posso ajudar?")
    client.close()
"""

__version__ = "1.0.0"
__author__ = "WhatsApp Assistant Team"
__email__ = "contact@whatsapp-assistant.com"

from .whatsapp_client import WhatsAppClient
from .selenium_driver import SeleniumDriver

__all__ = [
    "WhatsAppClient",
    "SeleniumDriver",
    "__version__",
    "__author__",
    "__email__",
]
