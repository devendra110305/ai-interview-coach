# rag.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import random
import re

def create_vector_store(pdf_file):
    loader = PyPDFLoader(pdf_file)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    return vectordb

def generate_question(vectordb, skills=None):
    if not skills:
        return "Could not detect skills. Please ensure your resume contains technical keywords."

    # Construct a highly targeted query based on extracted skills
    search_query = f"Technical interview questions about {', '.join(skills)}"
    
    # Retrieve relevant chunks
    docs = vectordb.similarity_search(search_query, k=15)

    questions = []
    for doc in docs:
        text = doc.page_content
        
        # Split text into sentences/fragments by question mark
        lines = text.split("?")
        for line in lines:
            line = line.strip()
            
            # --- CLEANING LOGIC ---
            # 1. Remove leading numbers (e.g., "1. What is..." -> "What is...")
            line = re.sub(r"^\d+[\.\)]\s*", "", line)
            
            # 2. Remove ALL UPPERCASE headers (e.g., "PYTHON INTERVIEW QUESTIONS")
            # This looks for 2 or more uppercase words followed by optional spaces
            line = re.sub(r"^[A-Z\s]{5,}", "", line).strip()
            
            # 3. Catch if the header is stuck to the end of the previous question
            # e.g. "What is a list? PYTHON INTERVIEW QUESTIONS"
            line = re.sub(r"[A-Z\s]{5,}$", "", line).strip()
            
            # 4. Clean up any extra spaces
            line = " ".join(line.split())

            if len(line) > 10:
                questions.append(line + "?")

    # Remove duplicates
    questions = list(set(questions))
    
    # Strict Filtering
    filtered_questions = []
    for q in questions:
        q_lower = q.lower()
        if any(skill.lower() in q_lower for skill in skills):
            filtered_questions.append(q)

    if len(filtered_questions) > 0:
        return random.choice(filtered_questions)
    
    if len(questions) > 0:
        return random.choice(questions)

    return "No relevant question found. Try adding more skills to your resume."