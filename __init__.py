"""
wa-core - Interfaces e implementações para cliente WhatsApp.
"""

from .whatsapp_client import WhatsAppClient
from .selenium_driver import SeleniumDriver

__all__ = ['WhatsAppClient', 'SeleniumDriver']
