# FinanceOS

Projeto pessoal para análise financeira baseado em histórico de gastos.

## Objetivo

O objetivo deste projeto é transformar uma planilha financeira em uma plataforma de análise capaz de:

- Consolidar automaticamente as transações
- Classificar despesas por categoria
- Comparar cartões de crédito
- Simular cashback
- Gerar dashboards financeiros

## Estrutura

- `src/` - Código do projeto
- `rules/` - Regras dos cartões
- `docs/` - Documentação
- `tests/` - Testes unitários do projeto
- `run.py` - Script unificado de execução do pipeline completo
- `requirements.txt` - Gerenciamento de dependências

## Instalação e Configuração

### Pré-requisitos
Certifique-se de ter o **Python 3.8+** instalado em sua máquina.

### Instalação de Dependências
Instale as dependências necessárias executando o seguinte comando a partir da raiz do repositório:

```bash
pip install -r requirements.txt
```

## Como Executar

### 1. Preparação dos Dados
Para rodar o pipeline completo, coloque a planilha original de gastos nomeada como **`Contas Pedro.xlsx`** no diretório raiz do projeto.

### 2. Execução do Pipeline Completo
Rode o script unificado `run.py` a partir da raiz do repositório para executar todas as etapas sequencialmente (extração, validação, normalização, base de conhecimento, classificação semântica e cálculo de cashback):

```bash
python run.py
```

### 3. Execução dos Testes Automatizados
Para rodar a suíte de testes unitários com o `pytest`, execute:

```bash
PYTHONPATH=src pytest
```

## Status

- ✅ Sprint 1 - Ingestão de dados (Pronto)
- ✅ Sprint 2 - Classificação automática (Pronto)
- ✅ Sprint 3 - Motor de cashback e Portabilidade (Pronto)
