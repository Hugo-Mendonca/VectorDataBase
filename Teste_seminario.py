from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# Se o Qdrant estiver rodando localmente via Docker, o URL é 'localhost' e a porta 6333(faz a conexão do codigo com o banco)
client = QdrantClient(host="localhost", port=6333)

# Este modelo converte texto em vetores de 384 dimensões(faz a manipulação de dados modelo SQL(estruturado) para o modelo de VectorDataBase(vetores que chamamos de embeddings))
model = SentenceTransformer('all-MiniLM-L6-v2')
vector_size = model.get_sentence_embedding_dimension()

# Defini o nome da coleção (equivalente a uma tabela em SQL)
collection_name = "documentos_ia"
#Criar uma coleção
# Se a coleção já existe, podemos ignorar a criação ou recriá-la
try:
    client.delete_collection(collection_name=collection_name)
    print(f"Coleção '{collection_name}' existente deletada para recriação.")
except Exception:
    pass # Coleção não existe, então não faz nada

client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
)
print(f"Coleção '{collection_name}' criada com sucesso!")

# Inserir dados (vetores e metadados)
#Criamos alguns documentos e seus embeddings
documents = [
    {"text": "A inteligência artificial está revolucionando a medicina.", "category": "tecnologia"},
    {"text": "Grandes modelos de linguagem (LLMs) são a base de muitos chatbots.", "category": "tecnologia"},
    {"text": "O aprendizado de máquina é um subcampo da IA.", "category": "tecnologia"},
    {"text": "A culinária italiana é famosa por suas massas e pizzas.", "category": "culinaria"},
    {"text": "Receitas saudáveis com vegetais frescos e orgânicos.", "category": "culinaria"},
    {"text": "Explorando a história da Roma Antiga e seus imperadores.", "category": "historia"},
    {"text": "Tutankhamon foi um faraó egípcio.", "category": "historia"},
]

points = []
for i, doc in enumerate(documents):
    # Gerar o embedding do texto
    embedding = model.encode(doc["text"]).tolist()
    points.append(
        models.PointStruct(
            id=i, # Um ID único para cada ponto
            vector=embedding,
            payload={
                "original_text": doc["text"],
                "category": doc["category"]
            } # Metadados
        )
    )

operation_info = client.upsert(
    collection_name=collection_name,
    wait=True, # Espera a operação ser concluída
    points=points,
)
print("\nDados inseridos:")
print(operation_info)

# 6. Consultar dados (Busca por Similaridade)

# Consulta 1: Busca semântica
query_text_1 = "modelos de IA para conversação"
query_embedding_1 = model.encode(query_text_1).tolist()

print(f"\n--- Busca por similaridade: '{query_text_1}' ---")
search_result_1 = client.search(
    collection_name=collection_name,
    query_vector=query_embedding_1,
    limit=3, # Retorna os 3 mais similares
    with_payload=True # Inclui os metadados nos resultados
)

for hit in search_result_1:
    print(f"ID: {hit.id}, Score (Similaridade): {hit.score:.4f}")
    print(f"  Texto Original: {hit.payload['original_text']}")
    print(f"  Categoria: {hit.payload['category']}")

# Consulta 2: Busca com filtro de metadados
query_text_2 = "comida boa"
query_embedding_2 = model.encode(query_text_2).tolist()

print(f"\n--- Busca por similaridade: '{query_text_2}' (apenas categoria 'culinaria') ---")
search_result_2 = client.search(
    collection_name=collection_name,
    query_vector=query_embedding_2,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="category",
                match=models.MatchValue(value="culinaria")
            )
        ]
    ),
    limit=1,
    with_payload=True
)

for hit in search_result_2:
    print(f"ID: {hit.id}, Score (Similaridade): {hit.score:.4f}")
    print(f"  Texto Original: {hit.payload['original_text']}")
    print(f"  Categoria: {hit.payload['category']}")

# 7. Obter um ponto específico por ID
print(f"\n--- Obtendo ponto com ID 0 ---")
point_id_to_retrieve = 0
retrieved_point = client.retrieve(
    collection_name=collection_name,
    ids=[point_id_to_retrieve],
    with_vectors=True, # Inclui o vetor no resultado
    with_payload=True
)
if retrieved_point:
    print(f"Ponto recuperado: {retrieved_point[0].payload['original_text']}")
else:
    print(f"Ponto com ID {point_id_to_retrieve} não encontrado.")

# 8. Deletar pontos (exemplo)
# client.delete(
#     collection_name=collection_name,
#     points_selector=models.PointIdsList(points=[0]) # Deleta o ponto com ID 0
# )
# print(f"\nPonto com ID 0 deletado (comentado no código).")

# 9. Contar pontos
count_result = client.count(
    collection_name=collection_name,
    exact=True # Retorna a contagem exata
)
print(f"\nTotal de pontos na coleção: {count_result.count}")