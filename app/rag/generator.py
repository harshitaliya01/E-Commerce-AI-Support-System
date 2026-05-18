from langchain_openai import ChatOpenAI
from app.core.config import settings
from langchain_community.embeddings import JinaEmbeddings
from langchain_qdrant import QdrantVectorStore
from app.core.logging import get_logger

logger = get_logger(__name__)
embeddings = JinaEmbeddings(
    jina_api_key=settings.JINA_API_KEY,
    model_name="jina-embeddings-v3"
)

vectorstore = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="ecommerce_docs",
)

async def retrieve_documents(query: str):
    try:
        docs = await vectorstore.asimilarity_search(query, k=3)
        return docs
    except Exception as e:
        logger.error(f"Error retrieving documents for query '{query}': {e}", exc_info=True)
        return []

llm= ChatOpenAI(
    base_url= settings.BASE_URL,
    api_key= settings.OPENAI_API_KEY,
    model=settings.MODEL
)

async def generate_rag_response(user_query: str):
    try:
        docs = await retrieve_documents(user_query)
        context = "\n".join([doc.page_content for doc in docs])
        messages = f"""
            You are an ecommerce support AI.
            Answer ONLY using provided context.
            If answer is unavailable,
            say you don't know.
    
            Context:
            {context}
    
            User Question:
            {user_query}
        """
    
        response = await llm.ainvoke(messages)
        return response.content
    except Exception as e:
        logger.error(f"Error generating RAG response for query '{user_query}': {e}", exc_info=True)
        return "I am currently experiencing technical difficulties and cannot provide an answer right now. Please try again later."