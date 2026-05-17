from langchain_openai import ChatOpenAI
from app.core.config import settings
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_community.embeddings import JinaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.vectorstores import (
    Qdrant
)

from app.core.config import settings


embeddings = JinaEmbeddings(
    jina_api_key=settings.JINA_API_KEY,
    model_name="jina-embeddings-v3"
)

vectorstore = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="ecommerce_docs",
)


def retrieve_documents(query: str):

    docs = vectorstore.similarity_search(
        query,
        k=3,
    )

    return docs



llm= ChatOpenAI(
    base_url= settings.BASE_URL,
    api_key= settings.OPENAI_API_KEY,
    model=settings.OPENAI_MODEL
)

SYSTEM_PROMPT = """
You are an ecommerce support AI.

Answer ONLY using provided context.

If answer is unavailable,
say you don't know.
"""


async def generate_rag_response(
    user_query: str,
):

    docs = retrieve_documents(
        user_query
    )

    context = "\n".join([
        doc.page_content
        for doc in docs
    ])

    prompt = f"""
    Context:
    {context}

    User Question:
    {user_query}
    """

    response = await llm(
        SYSTEM_PROMPT,
        prompt,
    )

    return response