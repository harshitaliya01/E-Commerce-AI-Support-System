from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import JinaEmbeddings

from langchain_qdrant import QdrantVectorStore 

from langchain_community.document_loaders import (
    TextLoader
)

from app.core.config import settings


def ingest_documents():

    loader = TextLoader(
        "app/rag/documents/policies.txt"
    )

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = splitter.split_documents(
        documents
    )

    embeddings = JinaEmbeddings(
        jina_api_key=settings.JINA_API_KEY,
        model_name="jina-embeddings-v3"
    )

    QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url="http://localhost:6333",
        collection_name="ecommerce_docs",
        force_recreate=True # Ensures the collection matches the embedding scheme
    )

    print("Documents ingested successfully")


if __name__ == "__main__":

    ingest_documents()