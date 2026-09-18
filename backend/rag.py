import os
from dotenv import load_dotenv

from google import genai

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# 1. Load PDF
loader = PyPDFDirectoryLoader("documents")
documents = loader.load()

print("Number of pages:", len(documents))


# 2. Split PDF into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = text_splitter.split_documents(documents)

print("Number of chunks:", len(chunks))


# 3. Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# 4. Store in ChromaDB
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db"
)

print("Documents stored in ChromaDB!")


# 5. Ask a question
query = "What is Scrum?"


# 6. Retrieve relevant chunks
results = vectorstore.similarity_search(query, k=3)

context = "\n\n".join(
    result.page_content
    for result in results
)

print("\nRetrieved Context:")
print(context)


# 7. Send context to Gemini
prompt = f"""
You are a college notes chatbot.

Answer the question using ONLY the information provided
in the context below.

If the answer is not present in the context,
say: "The answer is not available in the provided notes."

Context:
{context}

Question:
{query}
"""


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)


# 8. Display final answer
print("\n===== CHATBOT ANSWER =====")
print(response.text)