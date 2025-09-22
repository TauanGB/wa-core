"""
Testes para WhatsAppClient
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from wa_core import WhatsAppClient
from wa_core.exceptions import WhatsAppConnectionError, WhatsAppMessageError


class TestWhatsAppClient:
    """Testes para a classe WhatsAppClient"""
    
    def setup_method(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.client = None
    
    def teardown_method(self):
        """Limpeza após cada teste"""
        if self.client:
            self.client.close()
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_init_success(self, mock_driver):
        """Testa inicialização bem-sucedida do cliente"""
        mock_driver_instance = Mock()
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        
        assert client.session_path == self.temp_dir
        assert client.driver == mock_driver_instance
        assert client.dados_clientes == {}
        mock_driver.assert_called_once_with(self.temp_dir)
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_check_for_new_messages(self, mock_driver):
        """Testa verificação de mensagens não lidas"""
        mock_driver_instance = Mock()
        mock_driver_instance.check_for_new_messages.return_value = True
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        result = client.check_for_new_messages()
        
        assert result is True
        mock_driver_instance.check_for_new_messages.assert_called_once()
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_send_message_success(self, mock_driver):
        """Testa envio de mensagem com sucesso"""
        mock_driver_instance = Mock()
        mock_driver_instance.send_message.return_value = True
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        result = client.send_message("5511999999999", "Teste")
        
        assert result is True
        mock_driver_instance.send_message.assert_called_once_with("5511999999999", "Teste")
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_send_message_failure(self, mock_driver):
        """Testa falha no envio de mensagem"""
        mock_driver_instance = Mock()
        mock_driver_instance.send_message.return_value = False
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        result = client.send_message("5511999999999", "Teste")
        
        assert result is False
        mock_driver_instance.send_message.assert_called_once_with("5511999999999", "Teste")
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_get_current_contact(self, mock_driver):
        """Testa obtenção do contato atual"""
        mock_driver_instance = Mock()
        mock_driver_instance.get_current_contact.return_value = "João"
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        result = client.get_current_contact()
        
        assert result == "João"
        mock_driver_instance.get_current_contact.assert_called_once()
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_click_unread_message(self, mock_driver):
        """Testa clique em mensagem não lida"""
        mock_driver_instance = Mock()
        mock_driver_instance.click_unread_message.return_value = True
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        result = client.click_unread_message()
        
        assert result is True
        mock_driver_instance.click_unread_message.assert_called_once()
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_get_last_message(self, mock_driver):
        """Testa obtenção da última mensagem"""
        mock_driver_instance = Mock()
        mock_driver_instance.get_last_message.return_value = "Olá!"
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        result = client.get_last_message()
        
        assert result == "Olá!"
        mock_driver_instance.get_last_message.assert_called_once()
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_close_current_chat(self, mock_driver):
        """Testa fechamento da conversa atual"""
        mock_driver_instance = Mock()
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        client.close_current_chat()
        
        mock_driver_instance.close_current_chat.assert_called_once()
    
    def test_carregar_dados_clientes_file_not_exists(self):
        """Testa carregamento quando arquivo não existe"""
        with patch('wa_core.whatsapp_client.SeleniumDriver'):
            client = WhatsAppClient(self.temp_dir)
            assert client.dados_clientes == {}
    
    def test_carregar_dados_clientes_file_exists(self):
        """Testa carregamento quando arquivo existe"""
        # Cria arquivo de dados
        dados = {"5511999999999": {"numero": "5511999999999", "apelido": "João"}}
        dados_file = os.path.join(self.temp_dir, "dados_clientes.json")
        
        with open(dados_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(dados, f)
        
        with patch('wa_core.whatsapp_client.SeleniumDriver'):
            client = WhatsAppClient(self.temp_dir)
            assert client.dados_clientes == dados
    
    def test_salvar_dados_clientes_success(self):
        """Testa salvamento bem-sucedido de dados"""
        with patch('wa_core.whatsapp_client.SeleniumDriver'):
            client = WhatsAppClient(self.temp_dir)
            client.dados_clientes = {"test": "data"}
            
            result = client.salvar_dados_clientes()
            
            assert result is True
            dados_file = os.path.join(self.temp_dir, "dados_clientes.json")
            assert os.path.exists(dados_file)
    
    def test_atualizar_dados_cliente(self):
        """Testa atualização de dados do cliente"""
        with patch('wa_core.whatsapp_client.SeleniumDriver'):
            client = WhatsAppClient(self.temp_dir)
            
            client.atualizar_dados_cliente("5511999999999", "João", "Olá!")
            
            assert "5511999999999" in client.dados_clientes
            dados = client.dados_clientes["5511999999999"]
            assert dados["numero"] == "5511999999999"
            assert dados["apelido"] == "João"
            assert dados["ultima_mensagem"] == "Olá!"
            assert dados["total_mensagens"] == 1
    
    def test_atualizar_dados_cliente_increment_count(self):
        """Testa incremento do contador de mensagens"""
        with patch('wa_core.whatsapp_client.SeleniumDriver'):
            client = WhatsAppClient(self.temp_dir)
            
            # Primeira mensagem
            client.atualizar_dados_cliente("5511999999999", "João", "Primeira")
            assert client.dados_clientes["5511999999999"]["total_mensagens"] == 1
            
            # Segunda mensagem
            client.atualizar_dados_cliente("5511999999999", "João", "Segunda")
            assert client.dados_clientes["5511999999999"]["total_mensagens"] == 2
    
    @patch('wa_core.whatsapp_client.SeleniumDriver')
    def test_close(self, mock_driver):
        """Testa fechamento do cliente"""
        mock_driver_instance = Mock()
        mock_driver.return_value = mock_driver_instance
        
        client = WhatsAppClient(self.temp_dir)
        client.close()
        
        mock_driver_instance.close.assert_called_once()
