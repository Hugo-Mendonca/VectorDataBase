from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer #bliblioteca para gerar embeddings

# Se o Qdrant estiver rodando localmente via Docker, o URL é 'localhost' e a porta 6333(faz a conexão do codigo com o banco)
client = QdrantClient(host="localhost", port=6333)

# Este modelo converte texto em vetores de 384 dimensões(faz a manipulação de dados modelo SQL(estruturado) para o modelo de VectorDataBase(vetores que chamamos de embeddings))
model = SentenceTransformer('all-MiniLM-L6-v2') #Carrega para o programa um modelo pré-treinado de Sentence Transformer que converte frases em embeddings
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
    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),#Especifica o tamnho do vetor que nesse caso é 384 pq é a dimensão usada pelo
    #qdrant e  Define a métrica de similaridade que o Qdrant usará para comparar vetores nesta coleção que no caso de dados textuais/semanticos a similaridade de
    #cosseno é a melhor.
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
#declara o vetores de textos que usaremos como teste por meio de um dicionario em python com o text(conteudo principal) e category(metadado).

points = []
#loop para percorrer o dicionario e transformar esses textos em embbedings
for i, doc in enumerate(documents):
    # Gerar o embedding do texto
    embedding = model.encode(doc["text"]).tolist()  #pega o texto de cada documento e o transforma em um vetor numérico (o embedding).
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

#enviar as operações para o QDrANT
operation_info = client.upsert(
    collection_name=collection_name,
    wait=True, # Espera a operação ser concluída
    points=points,
)
print("\nDados inseridos:")
print(operation_info)

#Consultar dados (Busca por Similaridade)

# Consulta 1: Busca semântica
query_text_1 = "modelos de IA para conversação"#Frase que o usuario está pesquisando
query_embedding_1 = model.encode(query_text_1).tolist()#Para que a consulta seja bem feita temos que converter a frase de busca em um vetor tbm, visto que 
#no banco está salvo como vetor, então essa função serve para transformar a frase do usuário em vetor.

print(f"\n--- Busca por similaridade: '{query_text_1}' ---")
#Comando para fazer a busca
search_result_1 = client.search(
    collection_name=collection_name, #coleção onde faremos a busca.
    query_vector=query_embedding_1,
    limit=3, # Retorna os 3 mais similares
    with_payload=True # Inclui os metadados nos resultados
)

#itera sobre os resultados da busca, cada hit será um objeto
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
    #agora vamos filtrar para o tipo de metadado que queremos
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
point_id_to_retrieve = 0 #variavel para armazenar o ID
#Método da bliblioteca Qdrant para buscar por ID especificos
retrieved_point = client.retrieve(
    collection_name=collection_name,#refenrencia qual tabela(coleção) procurar o ponto
    ids=[point_id_to_retrieve],#Aspecifica quais IDs de pontos você deseja recuperar, é importante notar que ele espera uma lista de IDs
    with_vectors=True, # Inclui o vetor no resultado
    with_payload=True
)
#O método retrieve retorna uma lista de Record objects. 
# #Se a lista não estiver vazia (ou seja, se o ponto com o ID especificado foi encontrado), a condição é verdadeira.
if retrieved_point:
    print(f"Ponto recuperado: {retrieved_point[0].payload['original_text']}")
else:
    print(f"Ponto com ID {point_id_to_retrieve} não encontrado.")

# 8. Deletar pontos (exemplo)
client.delete( # <--- Removido o #
    collection_name=collection_name,
    points_selector=models.PointIdsList(points=[0]) # Deleta o ponto com ID 0
)
print(f"\nPonto com ID 0 deletado.") # <--- Removido o #

# 9. Contar pontos
count_result = client.count(
    collection_name=collection_name,# A coleção a ser contada
    exact=True                      # Parâmetro opcional: Se True, o Qdrant fará uma contagem exata.
                                    # Se False, ele pode retornar uma contagem aproximada para melhorar a performance em coleções muito grandes.
)
print(f"\nTotal de pontos na coleção: {count_result.count}")