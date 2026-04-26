from mcp.server.fastmcp import FastMCP
import chromadb
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from src.config import CHROMA_PATH, OLLAMA_BASE_URL
import os

mcp = FastMCP("EduKnowledge")

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_BASE_URL)


def ingest_documents():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="school_rules")

    vault_path = "data/vault"
    if not os.path.exists(vault_path):
        os.makedirs(vault_path)
        print(f"Please put your English rules in {vault_path}")
        return

    for filename in os.listdir(vault_path):
        file_path = os.path.join(vault_path, filename)

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif filename.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            continue

        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(docs)

        for i, chunk in enumerate(chunks):
            collection.add(
                ids=[f"{filename}_{i}"],
                documents=[chunk.page_content],
                metadatas=[{"source": filename}]
            )
    print("Indexing completed!")

@mcp.tool()
def search_regulations(query: str) -> str:
    """
    Searches the school regulations and returns relevant sections.
    Use this to answer questions about school policy, attendance, and behavior.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name="school_rules")

    results = collection.query(query_texts=[query], n_results=3)

    if not results['documents'][0]:
        return "No relevant information found in the regulations."

    formatted_results = "\n\n".join(results['documents'][0])
    return f"Relevant sections from regulations:\n{formatted_results}"


@mcp.tool()
def add_teacher_note(student_id: int, class_id: str, note_text: str, date: str) -> str:
    """
    Adds a note with both student and class metadata.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="school_knowledge")

    note_id = f"note_{student_id}_{date}_{hash(note_text) % 1000}"
    collection.add(
        ids=[note_id],
        documents=[note_text],
        metadatas=[{
            "student_id": student_id,
            "class_id": class_id,
            "type": "teacher_note",
            "date": date
        }]
    )
    return f"Note for student {student_id} in class {class_id} added."


@mcp.tool()
def search_knowledge(query: str, student_id: int = None, class_id: str = None) -> str:
    """
    Searches with strict filtering.
    If student_id is provided, only that student's notes + general rules are returned.
    If class_id is provided, all notes from that class are accessible.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(name="school_knowledge")

    where_filter = {}
    if student_id:
        where_filter = {"student_id": student_id}
    elif class_id:
        where_filter = {"class_id": class_id}

    results = collection.query(
        query_texts=[query],
        n_results=5,
        where=where_filter if where_filter else None
    )

    if not results['documents'][0]:
        return "No relevant information was found under the granted permissions."

    return "\n\n".join(results['documents'][0])

if __name__ == "__main__":
    ingest_documents()
    mcp.run()