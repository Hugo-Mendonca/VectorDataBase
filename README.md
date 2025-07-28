# VectorDataBase - Seminário de Banco de Dados

Projeto prático para a cadeira de Banco de Dados, apresentando um minicurso sobre a instalação, manipulação e uso de um Banco de Dados Vetorial (**Qdrant**) e demonstrando um caso de uso real com uma aplicação web interativa.

## Estrutura do Projeto

- `docker-compose.yml`: Arquivo de configuração para iniciar o banco de dados Qdrant com Docker de forma simples.
- `requirements.txt`: Lista de todas as dependências Python necessárias para executar o projeto.
- `/notebooks`: Contém o minicurso prático em formato de Jupyter Notebook.
    - `minicurso_qdrant.ipynb`: Aula interativa, com explicações detalhadas e código passo a passo.
- `/src`: Contém o código-fonte da aplicação final.
    - `app.py`: Aplicação web interativa construída com Streamlit que demonstra o caso de uso.

## Como Executar o Projeto

Siga os passos abaixo para configurar e executar todas as partes do projeto.

### 1. Pré-requisitos

- **Docker Desktop** (para Windows/macOS) ou **Docker Engine** (para Linux)
- **Python 3.8+**

### 2. Iniciar o Banco de Dados (Docker)

Com o Docker em execução, abra o terminal na raiz do projeto e execute:

```bash
docker-compose up -d
```

Isso iniciará o container do Qdrant.

Para verificar se está funcionando, acesse:

```bash
http://localhost:6333/dashboard
```

### 3. Configurar o Ambiente Python

É altamente recomendado usar um ambiente virtual.

```bash
# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# No Linux/macOS
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 4. Executar o Minicurso Prático (Jupyter Notebook)

O notebook é uma aula interativa que explica os conceitos passo a passo.

Você pode usá-lo no VS Code (com extensão Python) ou no Jupyter Lab.

- Navegue até a pasta `/notebooks/`
- Abra o arquivo `minicurso_qdrant.ipynb`
- Execute todas as células em ordem

> A etapa de inserção (`cliente.upsert`) populando o banco de dados Qdrant é essencial para o funcionamento da aplicação web.
> 

### 5. Executar a Aplicação Final (Streamlit)

Com o ambiente virtual ativo e na raiz do projeto, execute:

```bash
streamlit run src/app.py
```

Uma aba será aberta automaticamente no navegador com a aplicação interativa.

Ela demonstra um motor de busca semântica usando embeddings de texto e o Qdrant como banco de dados vetorial.
