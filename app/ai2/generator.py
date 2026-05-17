from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_community.embeddings import JinaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_community.vectorstores import (
    Qdrant
)

import os
from dotenv import load_dotenv
load_dotenv()

embeddings = JinaEmbeddings(
    jina_api_key=os.getenv("JINA_API_KEY"),
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
    base_url= os.getenv("BASE_URL"),
    api_key= os.getenv("API_KEY"),
    model=os.getenv("MODEL")
)


SYSTEM_PROMPT = """
You are an ecommerce support AI.

Answer ONLY using provided context.

If answer is unavailable,
say you don't know.
"""


def generate_rag_response(
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

    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    return response.content