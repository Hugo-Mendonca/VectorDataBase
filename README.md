# VectorDataBase - Seminário de Banco de Dados

Projeto prático para a cadeira de Banco de Dados, apresentando um minicurso sobre a instalação, manipulação e uso de um Banco de Dados Vetorial (Qdrant).

---

## Pré-requisitos

Antes de iniciar, certifique-se de ter os seguintes softwares instalados em seu sistema:

- **Docker Desktop** (para Windows/macOS) ou **Docker Engine** (para Linux). Você pode fazer o download e seguir as instruções de instalação em https://www.docker.com/products/docker-desktop/.
- **Python 3.x** instalado.
- Um editor de código ou IDE, como o **VS Code**.

---

## Passo 1: Configurando o Ambiente do Banco de Dados (Qdrant)

O Qdrant, nosso banco de dados vetorial, será executado dentro de um contêiner Docker para facilitar a configuração e garantir a portabilidade.

### 1.1. Iniciando o Banco de Dados com Docker Compose

Para iniciar o banco de dados, certifique-se de que o Docker está em execução. Depois, abra seu terminal na raiz do projeto (na pasta `VectorDataBase`) e execute o seguinte comando:

```bash
docker-compose up -d
```

Este comando usará o arquivo `docker-compose.yml` para baixar a imagem do Qdrant e iniciar o serviço. As portas e volumes são configurados automaticamente.

- Solução de Problemas Comuns (Ex: Erro de GPG no Docker)
    
    Durante a configuração do Docker, alguns usuários podem encontrar um pop-up solicitando uma "Frase Secreta" relacionada ao GPG (GNU Privacy Guard).
    
    **Solução Rápida:**
    
    1. Edite o arquivo de configuração do Docker em `~/.docker/config.json`.
    2. Remova a linha `"credsStore": "desktop",` se ela estiver presente.
    3. Salve o arquivo e tente novamente.

### 1.2. Verificando o Dashboard

Para confirmar que o banco de dados está ativo, abra seu navegador e acesse a URL do dashboard do Qdrant:

[**http://localhost:6333/dashboard**](https://www.google.com/search?q=http://localhost:6333/dashboard&authuser=1)

Se a página de boas-vindas do Qdrant carregar, a configuração foi um sucesso.

---

## Passo 2: Preparando o Ambiente Python

Vamos configurar um ambiente Python isolado para nosso projeto.

### 2.1. Criando o Ambiente Virtual

No terminal, dentro da pasta `VectorDataBase`, execute:

Bash

`python -m venv venv`

### 2.2. Ativando o Ambiente Virtual

- **No Windows (PowerShell):**PowerShell
    
    `.\venv\Scripts\Activate.ps1`
    
- **No Linux ou macOS:**Bash
    
    `source venv/bin/activate`
    

Você saberá que o ambiente está ativo quando `(venv)` aparecer no início do seu prompt.

### 2.3. Instalando as Dependências

Com o ambiente virtual ativo, instale as bibliotecas necessárias:

Bash

`pip install -r requirements.txt`

---

## Passo 3: Entendendo e Executando o Código

O script `Teste_seminario.py` contém um exemplo completo de interação com o Qdrant. Abaixo está o código totalmente comentado, explicando cada passo.

Para executar, simplesmente rode o comando no seu terminal com o ambiente `venv` ativo:

Bash

`python Teste_seminario.py`

### Análise do Código Comentado

```python
# ==============================================================================
# 1. IMPORTAÇÕES E CONEXÃO INICIAL
# ==============================================================================
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer  # Biblioteca para gerar embeddings

# Se o Qdrant estiver rodando localmente via Docker, o URL é 'localhost' e a porta 6333.
# Esta linha faz a conexão do nosso código Python com o banco de dados.
client = QdrantClient(host="localhost", port=6333)

# ==============================================================================
# 2. PREPARAÇÃO DO MODELO DE EMBEDDING E DEFINIÇÃO DA COLEÇÃO
# ==============================================================================
# Carrega para o programa um modelo pré-treinado de Sentence Transformer.
# Este modelo converte texto em vetores de 384 dimensões. É aqui que transformamos
# dados não estruturados (texto) em dados que o Vector DB entende (vetores/embeddings).
model = SentenceTransformer('all-MiniLM-L6-v2')
vector_size = model.get_sentence_embedding_dimension()

# Define o nome da coleção (equivalente a uma tabela em SQL)
collection_name = "documentos_ia"

# ==============================================================================
# 3. CRIAÇÃO DA COLEÇÃO NO QDRANT
# ==============================================================================
# Para garantir que o script possa ser rodado várias vezes sem erros,
# primeiro tentamos deletar a coleção se ela já existir.
try:
    client.delete_collection(collection_name=collection_name)
    print(f"Coleção '{collection_name}' existente deletada para recriação.")
except Exception:
    pass  # Se a coleção não existe, um erro ocorre, mas nós o ignoramos.

# Agora, criamos a coleção.
client.create_collection(
    collection_name=collection_name,
    # Especifica o tamanho do vetor (384) e a métrica de distância.
    # A similaridade de cosseno (COSINE) é ideal para comparar a semelhança semântica de textos.
    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
)
print(f"Coleção '{collection_name}' criada com sucesso!")

# ==============================================================================
# 4. INSERÇÃO DE DADOS (VETORES E METADADOS)
# ==============================================================================
# Criamos uma lista de documentos de exemplo. Cada um é um dicionário
# com o texto principal e um metadado de "categoria".
documents = [
    {"text": "A inteligência artificial está revolucionando a medicina.", "category": "tecnologia"},
    {"text": "Grandes modelos de linguagem (LLMs) são a base de muitos chatbots.", "category": "tecnologia"},
    {"text": "O aprendizado de máquina é um subcampo da IA.", "category": "tecnologia"},
    {"text": "A culinária italiana é famosa por suas massas e pizzas.", "category": "culinaria"},
    {"text": "Receitas saudáveis com vegetais frescos e orgânicos.", "category": "culinaria"},
    {"text": "Explorando a história da Roma Antiga e seus imperadores.", "category": "historia"},
    {"text": "Tutankhamon foi um faraó egípcio.", "category": "historia"},
]

# Preparamos os "pontos" a serem inseridos no Qdrant.
points = []
# Loop para percorrer os documentos e transformá-los em pontos.
for i, doc in enumerate(documents):
    # Gerar o embedding: pega o texto e o transforma em um vetor numérico.
    embedding = model.encode(doc["text"]).tolist()
    # Cria a estrutura do ponto com ID, vetor e metadados (payload).
    points.append(
        models.PointStruct(
            id=i,  # Um ID único para cada ponto
            vector=embedding,
            payload={
                "original_text": doc["text"],
                "category": doc["category"]
            }
        )
    )

# Envia a lista de pontos para o Qdrant. A operação "upsert"
# insere se o ID não existir, ou atualiza se já existir.
operation_info = client.upsert(
    collection_name=collection_name,
    wait=True,  # Espera a operação ser concluída
    points=points,
)
print("\nDados inseridos:")
print(operation_info)

# ==============================================================================
# 5. CONSULTAS DE DADOS (BUSCA POR SIMILARIDADE)
# ==============================================================================
# --- 5.1 Consulta de Busca Semântica ---
query_text_1 = "modelos de IA para conversação"
# Para consultar, também precisamos converter a frase de busca em um vetor.
query_embedding_1 = model.encode(query_text_1).tolist()

print(f"\n--- Busca por similaridade: '{query_text_1}' ---")
# Comando para fazer a busca vetorial.
search_result_1 = client.search(
    collection_name=collection_name,
    query_vector=query_embedding_1,
    limit=3,  # Retorna os 3 mais similares
    with_payload=True  # Inclui os metadados nos resultados
)

# Itera sobre os resultados da busca para exibi-los.
for hit in search_result_1:
    print(f"ID: {hit.id}, Score (Similaridade): {hit.score:.4f}")
    print(f"  Texto Original: {hit.payload['original_text']}")
    print(f"  Categoria: {hit.payload['category']}")

# --- 5.2. Consulta com Filtro de Metadados ---
query_text_2 = "comida boa"
query_embedding_2 = model.encode(query_text_2).tolist()

print(f"\n--- Busca por similaridade: '{query_text_2}' (apenas categoria 'culinaria') ---")
search_result_2 = client.search(
    collection_name=collection_name,
    query_vector=query_embedding_2,
    # AQUI ESTÁ O FILTRO: buscamos apenas onde a "category" é "culinaria".
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="category",
                match=models.MatchValue(value="culinaria")
            )
        ]
    ),
    limit=2,
    with_payload=True
)

for hit in search_result_2:
    print(f"ID: {hit.id}, Score (Similaridade): {hit.score:.4f}")
    print(f"  Texto Original: {hit.payload['original_text']}")
    print(f"  Categoria: {hit.payload['category']}")

# ==============================================================================
# 6. OPERAÇÕES DE GERENCIAMENTO DE PONTOS
# ==============================================================================
# --- 6.1. Obtendo um Ponto Específico por ID ---
print(f"\n--- Obtendo ponto com ID 0 ---")
retrieved_point = client.retrieve(
    collection_name=collection_name,
    ids=[0], # Espera uma lista de IDs
    with_payload=True
)
print(f"Ponto recuperado: {retrieved_point[0].payload['original_text']}")

# --- 6.2. Deletando Pontos ---
client.delete(
    collection_name=collection_name,
    points_selector=models.PointIdsList(points=[0, 1]) # Deleta os pontos com ID 0 e 1
)
print(f"\nPontos com ID 0 e 1 deletados.")

# --- 6.3. Contagem de Pontos na Coleção ---
count_result = client.count(
    collection_name=collection_name,
    exact=True # Força uma contagem exata.
)
print(f"\nTotal de pontos na coleção agora: {count_result.count}")
```
