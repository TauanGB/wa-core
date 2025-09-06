"""
Exceções customizadas para wa-core
"""


class WACoreError(Exception):
    """Exceção base para wa-core"""
    pass


class WhatsAppConnectionError(WACoreError):
    """Erro de conexão com o WhatsApp"""
    pass


class WhatsAppLoginError(WACoreError):
    """Erro de login no WhatsApp"""
    pass


class WhatsAppSessionError(WACoreError):
    """Erro de sessão do WhatsApp"""
    pass


class WhatsAppMessageError(WACoreError):
    """Erro ao enviar/receber mensagens"""
    pass


class WhatsAppContactError(WACoreError):
    """Erro relacionado a contatos"""
    pass


class SeleniumDriverError(WACoreError):
    """Erro do driver Selenium"""
    pass
