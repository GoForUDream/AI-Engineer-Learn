import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)
from langchain_classic.chains import create_retrieval_chain

load_dotenv()


def start_chat(collection_name: str = "demo_collection"):
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        raise ValueError("API Key is missing. Check your .env file.")

    # 1. Guarantee the Google SDK can read the key globally
    os.environ["GOOGLE_API_KEY"] = gemini_key

    # 2. Re-initialize the same Embedding model setup used during ingestion
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview",
        output_dimensionality=768,
    )

    # 3. Reference your EXISTING running Qdrant collection
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings_model,
        url="http://localhost:6333",
        collection_name=collection_name,
    )

    # Transform our vector store into a search retriever tool
    # k=3 tells it to retrieve the top 3 closest matching text chunks from the PDF
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 4. Instantiate the Chat model (using gemini-2.5-flash for speed and reasoning precision)
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=gemini_key,
        temperature=0.2,
    )

    # 5. Build the Prompt layout instructing the AI how to act
    system_prompt = (
        "You are an expert document assistant. Answer the user's question using strictly "
        "the provided context sections retrieved from the database below. If you don't know the "
        "answer, say that you cannot find it in the document. Keep your answers concise.\n\n"
        "Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{input}"),
        ]
    )

    # 6. Assemble the Chain components
    # The document chain handles wrapping the text chunks into the prompt context parameter
    question_answer_chain = create_stuff_documents_chain(llm=model, prompt=prompt)

    # The retrieval chain automatically searches Qdrant first, then fires the LLM
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    print("\n🚀 RAG Chat System Ready! Ask anything about your uploaded data.")
    print("Type 'exit' to quit.\n" + "=" * 50)

    while True:
        user_query = input("\nYou: ")
        if user_query.strip().lower() == "exit":
            print("Shutting down chat. Goodbye!")
            break

        if not user_query.strip():
            continue

        try:
            print("Searching database and thinking...")

            # Fire the entire combined execution pipeline
            response = rag_chain.invoke({"input": user_query})

            print(f"\nAI: {response['answer']}\n")

            # Optional Debug: Show exactly which pages the AI extracted information from
            print("📌 Sources referenced:")
            for doc in response.get("context", []):
                source_file = os.path.basename(
                    doc.metadata.get("source", "Unknown File")
                )
                page_num = (
                    doc.metadata.get("page", 0) + 1
                )  # Standardizing 0-index to Human counting
                print(f" - File: {source_file} (Page {page_num})")
            print("=" * 50)

        except Exception as e:
            print(f"An error occurred during retrieval: {e}")


if __name__ == "__main__":
    start_chat(collection_name="demo_collection")
