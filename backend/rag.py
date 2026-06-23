import uuid
from pinecone import Pinecone
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("ai-teacher")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Splits the input text into chunks of specified size with optional overlap.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): The size of each chunk in characters. Default is 500.
        overlap (int): The number of characters to overlap between chunks. Default is 50.

    Returns:
        list: A list of text chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if overlap < 0:
        raise ValueError("overlap must be a non-negative integer.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size.")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks

def embed_chunks(chunks: list) -> list:
    """
    Placeholder function for embedding text chunks.

    Args:
        chunks (list): A list of text chunks to be embedded.
    Returns:
        list: A list of embedded vectors corresponding to the input chunks. 
    """

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks  # list of strings
    )

    vectors = [item.embedding for item in response.data]
    return vectors


def store_chunks(chunks: list, embeddings: list, collection_name= "student_docs") -> None:
    """
    Stores the chunks and their corresponding embeddings in a vector database.

    Args:
        chunks (list): A list of text chunks.
        embeddings (list): A list of embeddings corresponding to each chunk.

    Returns:
        None
    """
    if collection_name == "student_docs":
        index.delete(filter={"source": "student_docs"})

    index.upsert(vectors=[
    {
        "id": str(uuid.uuid4()),
        "values": embedding,
        "metadata": {"text": chunk, "source": collection_name}
    }
    for chunk, embedding in zip(chunks, embeddings)
])

       

def index_document(text:str, collection_name: str = "student_docs") -> int:
    """
    Indexes a document by chunking the text, generating embeddings, and storing them in a vector database.

    Args:
        text (str): The input text to be indexed.
        collection_name (str): The name of the collection to store the indexed document.
    Returns:
        int: The number of chunks the document was split into.
    """

    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    store_chunks(chunks, embeddings, collection_name)

    return len(chunks)


def search(query: str, n_results: int = 3) -> list:
    # embed the query (single string, not a list)
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    query_embedding = response.data[0].embedding
    
    try:
        results= index.query(
            vector=query_embedding,
            top_k=n_results,
            include_metadata=True  # we need the text back from metadata
        )
        results = [match["metadata"]["text"] for match in results["matches"]]
        return results
    except:
        return []  # student hasn't uploaded anything yet
    
