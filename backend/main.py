import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Load environment variables
load_dotenv()

# Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Create FastAPI application
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class Question(BaseModel):
    question: str


# Create embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Connect to existing ChromaDB
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)


@app.get("/")
def home():
    return {
        "message": "College Notes Chatbot API is running!"
    }


@app.post("/ask")
def ask_question(data: Question):

    # User's question
    query = data.question

    # Search relevant chunks
    results = vectorstore.similarity_search(
        query,
        k=3
    )

    # Combine retrieved chunks
    context = "\n\n".join(
        result.page_content
        for result in results
    )

    # Prompt for Gemini
    prompt = f"""
You are a college notes chatbot.

Answer the question using ONLY the information
provided in the context below.

If the answer is not present in the context,
say:
"The answer is not available in the provided notes."

Context:
{context}

Question:
{query}
"""

    # Generate answer
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return {
        "question": query,
        "answer": response.text
    }