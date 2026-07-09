import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore

# Load environment variables from .env file
load_dotenv()


def initialize_and_populate_vector_db(
    file_path: str,
    qdrant_url: str = "http://localhost:6333",
):

    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        raise ValueError("API Key is missing. Check your .env file.")

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []

    print(f"Processing PDF document: {file_path}")

    loader = PyPDFLoader(file_path=file_path, mode="page", extraction_mode="plain")
    pages_generator = loader.lazy_load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50, length_function=len
    )

    print("Splitting pages into smaller chunks lazily...")
    final_chunks = text_splitter.split_documents(pages_generator)
    print(f"Successfully created {len(final_chunks)} total chunks.")

    os.environ["GOOGLE_API_KEY"] = gemini_key

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview",
        output_dimensionality=768,
    )

    try:
        vector_store = QdrantVectorStore.from_documents(
            documents=final_chunks,
            embedding=embeddings_model,
            url=qdrant_url,
            collection_name="demo_collection",
        )
        print("🎉 Successfully populated your Qdrant Vector DB!")
        return vector_store
    except Exception as e:
        print(f"An error occurred while uploading to Qdrant: {e}")
        return None


if __name__ == "__main__":
    pdf_path = r"C:\Users\VNGkh\Downloads\NguyenDuyKhang-Fullstack Developer.pdf"
    store = initialize_and_populate_vector_db(
        pdf_path, qdrant_url="http://localhost:6333"
    )
