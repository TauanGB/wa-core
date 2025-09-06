# Guia de Contribuição

Obrigado por considerar contribuir com o wa-core! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Processo de Desenvolvimento](#processo-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Testes](#testes)
- [Documentação](#documentação)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

## 🤝 Código de Conduta

Este projeto segue um código de conduta para garantir um ambiente acolhedor para todos os contribuidores. Ao participar, você concorda em manter este código.

### Nossos Compromissos

- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista e experiências
- Aceitar críticas construtivas graciosamente
- Focar no que é melhor para a comunidade
- Demonstrar empatia com outros membros da comunidade

## 🚀 Como Contribuir

### Tipos de Contribuição

1. **🐛 Reportar Bugs**
2. **💡 Sugerir Melhorias**
3. **📝 Melhorar Documentação**
4. **🧪 Adicionar Testes**
5. **⚡ Implementar Features**
6. **🔧 Melhorar Performance**

### Processo de Contribuição

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature
4. **Faça** suas mudanças
5. **Teste** suas mudanças
6. **Commit** suas mudanças
7. **Push** para sua branch
8. **Abra** um Pull Request

## 🛠️ Configuração do Ambiente

### Pré-requisitos

- Python 3.8+
- Firefox
- Git
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/your-username/wa-core.git
cd wa-core

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -e .[dev]

# Instale geckodriver
# Linux/Mac
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
tar -xzf geckodriver-v0.33.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/

# Windows
# Baixe geckodriver.exe e adicione ao PATH
```

## 🔄 Processo de Desenvolvimento

### Estrutura do Projeto

```
wa-core/
├── wa_core/           # Código principal
├── examples/          # Exemplos de uso
├── tests/            # Testes
├── docs/             # Documentação
├── .github/          # GitHub Actions
└── README.md
```

### Workflow Git

```bash
# 1. Atualize sua branch principal
git checkout main
git pull origin main

# 2. Crie uma nova branch
git checkout -b feature/nova-funcionalidade

# 3. Faça suas mudanças
# ... código ...

# 4. Teste suas mudanças
pytest tests/
flake8 wa_core/
black --check wa_core/

# 5. Commit suas mudanças
git add .
git commit -m "feat: adiciona nova funcionalidade"

# 6. Push para sua branch
git push origin feature/nova-funcionalidade

# 7. Abra um Pull Request no GitHub
```

## 📏 Padrões de Código

### Python

- **PEP 8**: Siga o guia de estilo PEP 8
- **Black**: Use Black para formatação automática
- **Type Hints**: Use type hints sempre que possível
- **Docstrings**: Documente todas as funções e classes

### Formatação

```bash
# Formatação automática
black wa_core/

# Verificação de estilo
flake8 wa_core/

# Verificação de tipos
mypy wa_core/
```

### Convenções de Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adiciona nova funcionalidade
fix: corrige bug
docs: atualiza documentação
style: formatação de código
refactor: refatoração de código
test: adiciona testes
chore: tarefas de manutenção
```

### Exemplos

```python
def send_message(self, text: str) -> bool:
    """
    Envia uma mensagem no WhatsApp.
    
    Args:
        text: Texto da mensagem a ser enviada
        
    Returns:
        True se enviou com sucesso, False caso contrário
        
    Raises:
        WhatsAppMessageError: Se houver erro ao enviar mensagem
    """
    try:
        return self.driver.send_message(text)
    except Exception as e:
        raise WhatsAppMessageError(f"Erro ao enviar mensagem: {e}") from e
```

## 🧪 Testes

### Executando Testes

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/test_whatsapp_client.py

# Com cobertura
pytest --cov=wa_core --cov-report=html

# Testes de integração
pytest tests/integration/ -m integration
```

### Escrevendo Testes

```python
import pytest
from wa_core import WhatsAppClient
from wa_core.exceptions import WhatsAppConnectionError

class TestWhatsAppClient:
    def test_send_message_success(self):
        """Testa envio de mensagem com sucesso"""
        client = WhatsAppClient("test_session")
        result = client.send_message("Teste")
        assert result is True
    
    def test_send_message_failure(self):
        """Testa falha no envio de mensagem"""
        client = WhatsAppClient("test_session")
        with pytest.raises(WhatsAppMessageError):
            client.send_message("")
```

### Marcadores de Teste

```python
@pytest.mark.slow
def test_long_running_operation():
    """Teste que demora para executar"""
    pass

@pytest.mark.integration
def test_whatsapp_integration():
    """Teste de integração com WhatsApp"""
    pass
```

## 📚 Documentação

### Atualizando Documentação

- **README.md**: Documentação principal
- **Docstrings**: Documentação inline do código
- **Exemplos**: Exemplos práticos em `examples/`
- **CHANGELOG.md**: Histórico de mudanças

### Padrões de Documentação

```python
def complex_function(param1: str, param2: int = 10) -> bool:
    """
    Descrição breve da função.
    
    Descrição mais detalhada se necessário.
    
    Args:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro (padrão: 10)
        
    Returns:
        Descrição do valor de retorno
        
    Raises:
        ValueError: Quando param1 é inválido
        ConnectionError: Quando não consegue conectar
        
    Example:
        >>> result = complex_function("test", 20)
        >>> print(result)
        True
        
    Note:
        Informações adicionais importantes.
    """
    pass
```

## 🐛 Reportando Bugs

### Antes de Reportar

1. Verifique se o bug já foi reportado
2. Teste com a versão mais recente
3. Verifique a documentação

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do bug.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Comportamento Atual**
O que está acontecendo.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
- OS: [ex: Windows 10]
- Python: [ex: 3.9.0]
- wa-core: [ex: 1.0.0]
- Firefox: [ex: 95.0]

**Informações Adicionais**
Qualquer outra informação relevante.
```

## 💡 Sugerindo Melhorias

### Template de Feature Request

```markdown
**Funcionalidade Solicitada**
Descrição clara da funcionalidade.

**Problema que Resolve**
Qual problema esta funcionalidade resolve.

**Solução Proposta**
Como você imagina que deveria funcionar.

**Alternativas Consideradas**
Outras soluções que você considerou.

**Contexto Adicional**
Qualquer outro contexto sobre a solicitação.
```

## 📞 Suporte

- **GitHub Issues**: Para bugs e feature requests
- **Discussions**: Para perguntas e discussões
- **Email**: contact@whatsapp-assistant.com

## 🏆 Reconhecimento

Contribuidores serão reconhecidos no README e em releases. Obrigado por contribuir! 🙏

---

**Lembre-se**: Contribuir é sobre colaboração, não competição. Seja respeitoso e construtivo! 😊
