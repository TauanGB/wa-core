# Configuração do Repositório GitHub

Este documento contém instruções para configurar o repositório `wa-core` no GitHub como um repositório independente.

## 🚀 Passos para Configuração

### 1. Criar Novo Repositório no GitHub

1. Acesse [GitHub](https://github.com) e faça login
2. Clique em "New repository" ou use o link: https://github.com/new
3. Configure o repositório:
   - **Repository name**: `wa-core`
   - **Description**: `Gerenciador funcional do WhatsApp para assistentes, bots e automações`
   - **Visibility**: Public (recomendado)
   - **Initialize**: Não marque nenhuma opção (já temos os arquivos)

### 2. Configurar Repositório Local

```bash
# Navegue para o diretório wa-core
cd wa-core

# Inicialize o git (se ainda não foi feito)
git init

# Adicione o remote do GitHub
git remote add origin https://github.com/SEU_USUARIO/wa-core.git

# Adicione todos os arquivos
git add .

# Faça o primeiro commit
git commit -m "feat: lançamento inicial do wa-core v1.0.0"

# Push para o GitHub
git push -u origin main
```

### 3. Configurar Branch Protection

1. Vá para **Settings** > **Branches**
2. Clique em **Add rule**
3. Configure:
   - **Branch name pattern**: `main`
   - ✅ **Require a pull request before merging**
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - ✅ **Restrict pushes that create files**

### 4. Configurar Secrets do GitHub

Vá para **Settings** > **Secrets and variables** > **Actions** e adicione:

#### Para PyPI (opcional - para publicação automática)
- **Name**: `PYPI_API_TOKEN`
- **Value**: Token do PyPI (crie em https://pypi.org/manage/account/)

### 5. Configurar GitHub Pages (opcional)

1. Vá para **Settings** > **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `gh-pages` (criar se necessário)

### 6. Configurar Issues e Discussions

1. **Settings** > **General**
2. ✅ **Issues** - Habilitar
3. ✅ **Discussions** - Habilitar (opcional)

### 7. Configurar Templates

Os templates já estão configurados em:
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`

### 8. Configurar Labels

Crie as seguintes labels no repositório:

- `bug` (vermelho) - Para bugs
- `enhancement` (verde) - Para melhorias
- `documentation` (azul) - Para documentação
- `good first issue` (roxo) - Para iniciantes
- `help wanted` (laranja) - Para ajuda
- `question` (amarelo) - Para perguntas
- `wontfix` (cinza) - Para issues que não serão corrigidas

### 9. Configurar Milestones

Crie milestones para organizar releases:
- `v1.1.0` - Próxima versão menor
- `v1.2.0` - Versão futura
- `v2.0.0` - Versão major futura

### 10. Configurar Code Owners

Crie o arquivo `.github/CODEOWNERS`:

```
# Global code owners
* @SEU_USUARIO

# Specific file owners
/wa_core/ @SEU_USUARIO
/examples/ @SEU_USUARIO
/tests/ @SEU_USUARIO
```

## 📋 Checklist de Configuração

- [ ] Repositório criado no GitHub
- [ ] Código enviado para o repositório
- [ ] Branch protection configurada
- [ ] Secrets configurados (se necessário)
- [ ] Issues e Discussions habilitados
- [ ] Templates de issue configurados
- [ ] Labels criados
- [ ] Milestones criados
- [ ] Code owners configurados
- [ ] README.md atualizado com badges
- [ ] Licença configurada
- [ ] Contributing.md configurado
- [ ] GitHub Actions funcionando

## 🔧 Comandos Úteis

### Atualizar README com Badges

Adicione estes badges no topo do README.md:

```markdown
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/wa-core.svg)](https://badge.fury.io/py/wa-core)
[![Build Status](https://github.com/SEU_USUARIO/wa-core/workflows/CI/badge.svg)](https://github.com/SEU_USUARIO/wa-core/actions)
[![Coverage](https://codecov.io/gh/SEU_USUARIO/wa-core/branch/main/graph/badge.svg)](https://codecov.io/gh/SEU_USUARIO/wa-core)
```

### Comandos Git Úteis

```bash
# Verificar status
git status

# Adicionar mudanças
git add .

# Commit com mensagem
git commit -m "feat: adiciona nova funcionalidade"

# Push para GitHub
git push origin main

# Criar nova branch
git checkout -b feature/nova-funcionalidade

# Voltar para main
git checkout main

# Merge branch
git merge feature/nova-funcionalidade

# Deletar branch local
git branch -d feature/nova-funcionalidade

# Deletar branch remota
git push origin --delete feature/nova-funcionalidade
```

## 🎯 Próximos Passos

1. **Teste o CI/CD**: Faça um commit e verifique se os workflows funcionam
2. **Configure Codecov**: Para relatórios de cobertura de testes
3. **Configure Dependabot**: Para atualizações automáticas de dependências
4. **Configure Stale Bot**: Para gerenciar issues antigas
5. **Publique no PyPI**: Configure publicação automática

## 📞 Suporte

Se precisar de ajuda com a configuração:
- Consulte a [documentação do GitHub](https://docs.github.com/)
- Abra uma issue no repositório
- Entre em contato: contact@whatsapp-assistant.com

---

**🎉 Parabéns!** Seu repositório `wa-core` está pronto para ser um gerenciador funcional do WhatsApp! 🚀
