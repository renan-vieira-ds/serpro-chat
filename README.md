# Sistema de Perguntas e Respostas sobre Edital SERPRO 2023

## Índice

1. [Objetivo do Projeto](#1-objetivo-do-projeto)
2. [Estrutura do Projeto](#2-estrutura-do-projeto)
3. [Setup do Projeto](#3-setup-do-projeto)
   - 3.1. [Pré-requisitos](#31-pré-requisitos)
   - 3.2. [Instalação de Dependências](#32-instalação-de-dependências)
   - 3.3. [Configuração do Ambiente](#33-configuração-do-ambiente)
4. [Funcionamento do Projeto](#4-funcionamento-do-projeto)
   - 4.1. [Fluxo de Execução](#41-fluxo-de-execução)
   - 4.2. [Descrição dos Módulos](#42-descrição-dos-módulos)
5. [Docker Compose](#5-docker-compose)
   - 5.1. [Serviços e Portas](#51-serviços-e-portas)
   - 5.2. [Interação entre Serviços](#52-interação-entre-serviços)
6. [Usage](#6-usage)
   - 6.1. [Inicialização do Banco de Dados](#61-inicialização-do-banco-de-dados)
   - 6.2. [Ingestão de Documentos](#62-ingestão-de-documentos)
   - 6.3. [Execução do Chat](#63-execução-do-chat)
7. [Trabalhos Futuros](#7-trabalhos-futuros)

## 1. Objetivo do Projeto

Este projeto implementa um sistema de perguntas e respostas baseado em Retrieval-Augmented Generation (RAG) para consultar informações do edital do concurso SERPRO 2023. O sistema utiliza processamento de documentos PDF, armazenamento vetorial em PostgreSQL com extensão pgvector e geração de respostas contextualizadas através de modelos de linguagem da OpenAI.

## 2. Estrutura do Projeto

```
.
├── docker-compose.yml          # Configuração dos serviços Docker
├── requirements.txt             # Dependências Python do projeto
├── .gitignore                  # Arquivos ignorados pelo Git
├── .env                        # Variáveis de ambiente (não versionado)
├── edital-serpro-2023.pdf      # Documento fonte para ingestão
└── src/
    ├── ingest.py               # Script de ingestão de documentos
    ├── search.py               # Módulo de busca e geração de respostas
    └── chat.py                 # Interface de chat interativa
```

## 3. Setup do Projeto

### 3.1. Pré-requisitos

- Python 3.12 ou superior
- Docker e Docker Compose instalados
- Conta OpenAI com API key válida
- Arquivo PDF do edital SERPRO 2023

### 3.2. Instalação de Dependências

1. Crie um ambiente virtual Python:

```bash
python -m venv env
```

2. Ative o ambiente virtual:

```bash
# macOS/Linux
source env/bin/activate

# Windows
env\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

### 3.3. Configuração do Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# OpenAI Configuration
OPENAI_API_KEY=sua-chave-api-openai
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Database Configuration
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=edital_serpro_2023

# Document Path
PDF_PATH=edital-serpro-2023.pdf
```

## 4. Funcionamento do Projeto

### 4.1. Fluxo de Execução

O projeto segue uma arquitetura RAG em três etapas principais:

1. **Ingestão**: O documento PDF é carregado, dividido em chunks e convertido em embeddings que são armazenados no banco vetorial.
2. **Busca**: Quando uma pergunta é feita, o sistema busca os chunks mais relevantes usando similaridade vetorial.
3. **Geração**: Os chunks encontrados são usados como contexto para gerar uma resposta através de um modelo de linguagem.

### 4.2. Descrição dos Módulos

#### 4.2.1. `ingest.py`

Este módulo é responsável pela ingestão inicial dos documentos no banco de dados vetorial.

**Funcionalidades:**
- Carrega o arquivo PDF especificado em `PDF_PATH` usando `PyPDFLoader`
- Divide o documento em chunks de 1000 caracteres com sobreposição de 150 caracteres usando `RecursiveCharacterTextSplitter`
- Remove metadados vazios ou nulos dos documentos
- Gera embeddings usando o modelo especificado em `OPENAI_EMBEDDING_MODEL`
- Armazena os documentos e embeddings no PostgreSQL através do `PGVector`
- Atribui IDs sequenciais no formato `doc-{i}` para cada chunk

**Variáveis de ambiente utilizadas:**
- `PDF_PATH`: Caminho para o arquivo PDF
- `OPENAI_API_KEY`: Chave de API da OpenAI
- `OPENAI_EMBEDDING_MODEL`: Modelo de embeddings a ser utilizado
- `DATABASE_URL`: String de conexão com o banco de dados
- `PG_VECTOR_COLLECTION_NAME`: Nome da coleção no banco vetorial

#### 4.2.2. `search.py`

Este módulo implementa a lógica de busca e geração de respostas.

**Funcionalidades:**
- Conecta-se ao banco vetorial usando as mesmas credenciais da ingestão
- Realiza busca por similaridade vetorial retornando os 10 chunks mais relevantes (`k=10`)
- Constrói um prompt estruturado que inclui:
  - Contexto extraído dos chunks encontrados
  - Regras para resposta baseada exclusivamente no contexto
  - Tratamento de perguntas fora do escopo do documento
- Gera resposta usando `ChatOpenAI` com temperatura 0.7
- Utiliza `StrOutputParser` para formatar a saída final

**Prompt Template:**
O template garante que o modelo responda apenas com base no contexto fornecido, retornando uma mensagem padrão quando a informação não estiver disponível no documento.

#### 4.2.3. `chat.py`

Interface de linha de comando para interação com o sistema.

**Funcionalidades:**
- Solicita entrada do usuário via `input()`
- Invoca a função `search_prompt` do módulo `search`
- Exibe a resposta gerada no console

**Limitações atuais:**
- Execução única por pergunta (não mantém histórico de conversação)
- Não possui loop de conversação contínua

## 5. Docker Compose

### 5.1. Serviços e Portas

O arquivo `docker-compose.yml` define dois serviços:

#### 5.1.1. Serviço `postgres`

- **Imagem**: `pgvector/pgvector:pg17`
- **Container**: `postgres_rag`
- **Porta**: `5432:5432` (host:container)
- **Variáveis de ambiente**:
  - `POSTGRES_USER`: postgres
  - `POSTGRES_PASSWORD`: postgres
  - `POSTGRES_DB`: rag
- **Volume**: `postgres_data` mapeado para `/var/lib/postgresql/data`
- **Healthcheck**: Verifica se o PostgreSQL está pronto para conexões
- **Restart**: `unless-stopped`

#### 5.1.2. Serviço `bootstrap_vector_ext`

- **Imagem**: `pgvector/pgvector:pg17`
- **Dependência**: Aguarda o serviço `postgres` estar saudável
- **Função**: Cria a extensão `vector` no banco de dados
- **Restart**: `no` (executa uma vez e encerra)

### 5.2. Interação entre Serviços

1. O serviço `postgres` inicia e aguarda estar pronto (healthcheck)
2. Após confirmação de saúde, o serviço `bootstrap_vector_ext` executa
3. `bootstrap_vector_ext` conecta-se ao PostgreSQL e cria a extensão `vector` se não existir
4. Após a criação da extensão, o container `bootstrap_vector_ext` encerra
5. O serviço `postgres` permanece rodando, expondo a porta 5432 para conexões externas

A extensão `vector` é essencial para armazenar e realizar buscas por similaridade vetorial no PostgreSQL.

## 6. Usage

### 6.1. Inicialização do Banco de Dados

Inicie os serviços Docker:

```bash
docker compose up -d
```

Verifique se os containers estão rodando:

```bash
docker compose ps
```

Confirme que a extensão vector foi criada:

```bash
docker exec postgres_rag psql -U postgres -d rag -c "\dx"
```

### 6.2. Ingestão de Documentos

Execute o script de ingestão para processar o PDF e popular o banco vetorial:

```bash
python src/ingest.py
```

Este comando:
- Carrega o PDF especificado em `PDF_PATH`
- Divide em chunks e gera embeddings
- Armazena no banco de dados
- Exibe o número de documentos inseridos

**Nota**: Executar novamente o script de ingestão atualiza os documentos existentes (upsert) se os IDs forem os mesmos, evitando duplicação.

### 6.3. Execução do Chat

Execute a interface de chat:

```bash
python src/chat.py
```

O sistema solicitará uma pergunta relacionada ao edital SERPRO 2023. Digite sua pergunta e pressione Enter para receber a resposta baseada no contexto do documento.

**Exemplo de uso:**

```
Digite sua pergunta relativa ao concurso SERPRO 2023: 
Qual é o prazo de inscrição?
```

## 7. Trabalhos Futuros

### 7.1. Agente Conversacional com Memória

Expandir o sistema para um chat contínuo que:
- Mantém histórico de conversação entre perguntas
- Permite múltiplas interações sem reiniciar o processo
- Encerra apenas com indicação explícita do usuário
- Implementa memória de curto prazo (últimas N mensagens) e opcionalmente memória de longo prazo persistida

### 7.2. Expansão da Base de Conhecimento

Incluir documentos adicionais relacionados ao concurso SERPRO:
- Documentos complementares ao edital principal
- FAQ oficial do concurso
- Atualizações e retificações publicadas
- Informações sobre cargos, requisitos e processos seletivos

### 7.3. Melhorias na Ingestão

- **Processamento de múltiplos documentos**: Suporte para ingestão de vários PDFs em lote
- **Detecção de duplicatas**: Identificar e evitar chunks duplicados ou muito similares
- **Metadados enriquecidos**: Extrair e armazenar informações estruturadas (seções, páginas, datas)
- **Reingestão incremental**: Mecanismo para atualizar apenas documentos modificados

### 7.4. Otimização de Busca

- **Ajuste de parâmetros de busca**: Permitir configuração do número de chunks retornados (`k`)
- **Busca híbrida**: Combinar busca vetorial com busca por palavras-chave
- **Filtragem por metadados**: Permitir filtros por seção, página ou tipo de documento
- **Re-ranking**: Aplicar modelo de re-ranking para melhorar a relevância dos resultados

### 7.5. Interface e Experiência do Usuário

- **Interface web**: Desenvolver interface gráfica web para substituir a CLI
- **Streaming de respostas**: Exibir respostas de forma incremental enquanto são geradas
- **Citações e referências**: Mostrar de qual parte do documento a resposta foi extraída
- **Feedback do usuário**: Sistema para coletar feedback sobre qualidade das respostas

### 7.6. Monitoramento e Avaliação

- **Logging estruturado**: Registrar todas as interações para análise
- **Métricas de qualidade**: Implementar avaliação automática de respostas (RAGAS ou similar)
- **Dashboard de uso**: Visualização de perguntas mais frequentes e taxa de sucesso
- **Alertas**: Notificações para perguntas sem resposta adequada no contexto

### 7.7. Segurança e Performance

- **Validação de entrada**: Sanitização de perguntas do usuário
- **Rate limiting**: Controle de taxa de requisições para evitar abuso
- **Cache de respostas**: Armazenar respostas frequentes para reduzir custos de API
- **Otimização de embeddings**: Avaliar modelos de embeddings mais eficientes ou específicos para português
