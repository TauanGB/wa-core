# wa-core

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/wa-core.svg)](https://badge.fury.io/py/wa-core)

**Gerenciador funcional do WhatsApp** - Uma biblioteca Python robusta para automação e gerenciamento do WhatsApp Web, perfeita para criar assistentes, bots e aplicações de automação.

## 🚀 Características

- ✅ **Automação completa do WhatsApp Web** usando Selenium
- ✅ **Gerenciamento de sessão persistente** - não precisa fazer login toda vez
- ✅ **Interface simples e intuitiva** para desenvolvedores
- ✅ **Suporte a múltiplos idiomas** (Português, Inglês, Espanhol)
- ✅ **Injeção de JavaScript** para melhor compatibilidade
- ✅ **Tratamento robusto de erros** com exceções customizadas
- ✅ **CLI integrada** para uso direto da linha de comando
- ✅ **Extensível** - fácil de integrar em qualquer aplicação

## 📦 Instalação

### Via pip (recomendado)

```bash
pip install wa-core
```

### Via GitHub (desenvolvimento)

```bash
git clone https://github.com/your-username/wa-core.git
cd wa-core
pip install -e .
```

### Dependências

- Python 3.8+
- Firefox (para o driver Selenium)
- geckodriver (instalado automaticamente)

## 🎯 Uso Rápido

### Exemplo Básico

```python
from wa_core import WhatsAppClient

# Inicializa o cliente
client = WhatsAppClient("minha_sessao")

# Verifica mensagens não lidas
if client.check_for_new_messages():
    # Clica na primeira mensagem não lida
    if client.click_unread_message():
        # Obtém informações
        contato = client.get_current_contact()
        mensagem = client.get_last_message()
        
        print(f"Mensagem de {contato}: {mensagem}")
        
        # Envia resposta
        client.send_message("Olá! Como posso ajudar?")
        
        # Fecha a conversa
        client.close_current_chat()

# Fecha o cliente
client.close()
```

### Uso via CLI

```bash
# Monitoramento contínuo
wa-core --monitor --interval 5

# Envio de mensagem específica
wa-core --send-message "Olá!" --contact "João"

# Verificação única
wa-core --session-path ./minha_sessao
```

## 📚 Exemplos Avançados

### 1. Bot de Resposta Automática

```python
import time
from wa_core import WhatsAppClient

class AutoReplyBot:
    def __init__(self, session_path="bot_session"):
        self.client = WhatsAppClient(session_path)
        self.responses = {
            "oi": "Olá! Como posso ajudar?",
            "ajuda": "Aqui estão as opções disponíveis...",
            "horario": "Nosso horário de funcionamento é..."
        }
    
    def process_message(self, message: str) -> str:
        """Processa a mensagem e retorna resposta apropriada"""
        message_lower = message.lower().strip()
        
        for keyword, response in self.responses.items():
            if keyword in message_lower:
                return response
        
        return "Desculpe, não entendi. Digite 'ajuda' para ver as opções."
    
    def run(self):
        """Executa o bot em loop contínuo"""
        print("Bot iniciado! Pressione Ctrl+C para parar.")
        
        try:
            while True:
                if self.client.check_for_new_messages():
                    if self.client.click_unread_message():
                        contato = self.client.get_current_contact()
                        mensagem = self.client.get_last_message()
                        
                        print(f"[{contato}] {mensagem}")
                        
                        # Processa e envia resposta
                        resposta = self.process_message(mensagem)
                        self.client.send_message(resposta)
                        
                        # Atualiza dados do cliente
                        self.client.atualizar_dados_cliente(
                            contato, contato, mensagem
                        )
                        
                        self.client.close_current_chat()
                
                time.sleep(2)  # Verifica a cada 2 segundos
                
        except KeyboardInterrupt:
            print("\nBot interrompido pelo usuário.")
        finally:
            self.client.close()

# Uso
if __name__ == "__main__":
    bot = AutoReplyBot()
    bot.run()
```

### 2. Assistente de Atendimento

```python
from wa_core import WhatsAppClient
from datetime import datetime
import json

class CustomerServiceAssistant:
    def __init__(self, session_path="atendimento_session"):
        self.client = WhatsAppClient(session_path)
        self.tickets = {}
        self.next_ticket_id = 1
    
    def create_ticket(self, customer_name: str, message: str) -> str:
        """Cria um novo ticket de atendimento"""
        ticket_id = f"TICKET-{self.next_ticket_id:04d}"
        self.tickets[ticket_id] = {
            "id": ticket_id,
            "customer": customer_name,
            "message": message,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "responses": []
        }
        self.next_ticket_id += 1
        return ticket_id
    
    def handle_customer_message(self):
        """Processa mensagens de clientes"""
        if self.client.check_for_new_messages():
            if self.client.click_unread_message():
                customer = self.client.get_current_contact()
                message = self.client.get_last_message()
                
                # Cria ticket
                ticket_id = self.create_ticket(customer, message)
                
                # Resposta automática
                response = f"""
🎫 *Ticket {ticket_id} criado com sucesso!*

Olá {customer}! Recebemos sua mensagem e criamos um ticket para acompanhamento.

*Sua mensagem:* {message}

Nosso time de atendimento entrará em contato em breve.
Obrigado pela preferência! 🙏
                """
                
                self.client.send_message(response)
                self.client.close_current_chat()
                
                # Salva dados
                self.save_tickets()
                
                return ticket_id
        return None
    
    def save_tickets(self):
        """Salva tickets em arquivo JSON"""
        with open("tickets.json", "w", encoding="utf-8") as f:
            json.dump(self.tickets, f, indent=2, ensure_ascii=False)
    
    def run(self):
        """Executa o assistente"""
        print("Assistente de atendimento iniciado!")
        
        try:
            while True:
                ticket_id = self.handle_customer_message()
                if ticket_id:
                    print(f"Novo ticket criado: {ticket_id}")
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\nAssistente interrompido.")
        finally:
            self.client.close()

# Uso
if __name__ == "__main__":
    assistant = CustomerServiceAssistant()
    assistant.run()
```

### 3. Monitor de Mensagens

```python
from wa_core import WhatsAppClient
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whatsapp_monitor.log'),
        logging.StreamHandler()
    ]
)

class MessageMonitor:
    def __init__(self, session_path="monitor_session"):
        self.client = WhatsAppClient(session_path)
        self.logger = logging.getLogger(__name__)
    
    def log_message(self, contact: str, message: str):
        """Registra mensagem no log"""
        self.logger.info(f"[{contact}] {message}")
    
    def monitor(self):
        """Monitora mensagens continuamente"""
        self.logger.info("Monitor de mensagens iniciado")
        
        try:
            while True:
                if self.client.check_for_new_messages():
                    if self.client.click_unread_message():
                        contact = self.client.get_current_contact()
                        message = self.client.get_last_message()
                        
                        self.log_message(contact, message)
                        
                        # Aqui você pode adicionar lógica adicional
                        # como notificações, análise de sentimento, etc.
                        
                        self.client.close_current_chat()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Monitor interrompido pelo usuário")
        finally:
            self.client.close()

# Uso
if __name__ == "__main__":
    monitor = MessageMonitor()
    monitor.monitor()
```

## 🔧 API Reference

### WhatsAppClient

Classe principal para interagir com o WhatsApp Web.

#### Métodos Principais

- `check_for_new_messages() -> bool`: Verifica se há mensagens não lidas
- `send_message(text: str) -> bool`: Envia uma mensagem
- `get_current_contact() -> str`: Obtém o nome do contato atual
- `click_unread_message() -> bool`: Clica na primeira mensagem não lida
- `get_last_message() -> str`: Obtém a última mensagem recebida
- `close_current_chat()`: Fecha a conversa atual
- `atualizar_dados_cliente(numero, nome, mensagem)`: Atualiza dados do cliente
- `close()`: Fecha o cliente e salva dados

### SeleniumDriver

Driver de baixo nível para automação do Selenium.

#### Métodos Principais

- `send_message(text: str) -> bool`: Envia mensagem
- `check_for_new_messages() -> bool`: Verifica mensagens não lidas
- `get_current_contact() -> str`: Obtém contato atual
- `click_unread_message() -> bool`: Clica em mensagem não lida
- `get_last_message() -> str`: Obtém última mensagem
- `inject_js_script() -> bool`: Injeta script JavaScript
- `load_session() -> bool`: Carrega sessão existente
- `save_session() -> bool`: Salva sessão atual

## 🛠️ Configuração

### Variáveis de Ambiente

```bash
# Caminho para a sessão do WhatsApp
export WA_SESSION_PATH="./whatsapp_session"

# Modo verboso
export WA_VERBOSE=true
```

### Arquivo de Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
WA_SESSION_PATH=./whatsapp_session
WA_VERBOSE=true
WA_BROWSER=firefox
```

## 🚨 Tratamento de Erros

O wa-core inclui exceções customizadas para melhor tratamento de erros:

```python
from wa_core import WhatsAppClient
from wa_core.exceptions import WhatsAppConnectionError, WhatsAppMessageError

try:
    client = WhatsAppClient()
    client.send_message("Teste")
except WhatsAppConnectionError as e:
    print(f"Erro de conexão: {e}")
except WhatsAppMessageError as e:
    print(f"Erro de mensagem: {e}")
```

## 📋 Requisitos do Sistema

- **Python**: 3.8 ou superior
- **Firefox**: Versão mais recente
- **Sistema Operacional**: Windows, macOS, Linux
- **Memória**: Mínimo 2GB RAM
- **Espaço em Disco**: 100MB para instalação

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📧 **Email**: contact@whatsapp-assistant.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/wa-core/issues)
- 📖 **Documentação**: [Documentação Completa](https://wa-core.readthedocs.io/)

## 🙏 Agradecimentos

- [Selenium](https://selenium.dev/) - Framework de automação web
- [Mozilla Firefox](https://www.mozilla.org/firefox/) - Navegador web
- Comunidade Python - Por todas as bibliotecas incríveis

---

**⚠️ Aviso Legal**: Este projeto é para fins educacionais e de automação pessoal. Respeite os Termos de Serviço do WhatsApp e use com responsabilidade.