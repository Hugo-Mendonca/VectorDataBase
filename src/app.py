import streamlit as st
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# --- Configuração da Página e Cache ---
st.set_page_config(
    page_title="Busca Semântica com Qdrant",
    page_icon="🔎",
    layout="centered"
)

# A anotação @st.cache_resource é um recurso poderoso do Streamlit.
# Ela garante que o modelo de IA e a conexão com o banco sejam carregados
# apenas uma vez, na primeira execução, tornando a aplicação muito mais rápida.
@st.cache_resource
def load_model():
    """Carrega o modelo de embedding SentenceTransformer."""
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def get_qdrant_client():
    """Inicia e retorna o cliente Qdrant."""
    return QdrantClient(host="localhost", port=6333)

# --- Carregamento dos Recursos ---
try:
    model = load_model()
    client = get_qdrant_client()
    collection_name = "documentos_ia"
    # Testa a conexão para garantir que o Qdrant está acessível
    client.get_collection(collection_name=collection_name)
    qdrant_is_ready = True
except Exception as e:
    qdrant_is_ready = False


# --- Interface Gráfica da Aplicação ---
st.title("🔎 Motor de Busca Semântica")
st.write(
    "Este é um exemplo de um caso de uso de um Banco de Dados Vetorial. "
    "O Qdrant armazena vetores de textos sobre tecnologia, culinária e história. "
    "Faça uma pergunta ou digite um termo para buscar os documentos mais relevantes em significado."
)

if not qdrant_is_ready:
    st.error(
        "❌ Não foi possível conectar ao Qdrant. "
        "Verifique se o Docker está rodando com o comando 'docker-compose up -d' "
        "e se o notebook do minicurso já foi executado para criar e popular a coleção."
    )
else:
    # --- Input do Usuário ---
    query_text = st.text_input(
        "O que você gostaria de saber?",
        placeholder="Ex: Como funciona a inteligência artificial?"
    )

    # --- Lógica de Busca ---
    if st.button("Buscar"):
        if query_text:
            # 1. Converte a busca do usuário em um vetor
            query_embedding = model.encode(query_text).tolist()

            # 2. Executa a busca no Qdrant
            search_result = client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=3
            )

            # 3. Exibe os resultados
            st.subheader("Resultados Encontrados:")
            if not search_result:
                st.warning("Nenhum resultado encontrado. Tente uma busca diferente.")
            
            for hit in search_result:
                # Usamos st.container com borda para separar visualmente os resultados
                with st.container(border=True):
                    st.metric(
                        label="Score de Similaridade (Quanto mais alto, melhor)", 
                        value=f"{hit.score:.4f}"
                    )
                    st.write(f"**Texto Original:** {hit.payload['original_text']}")
                    st.info(f"**Categoria:** {hit.payload['category']}")
        else:
            st.warning("Por favor, digite algo para buscar.")