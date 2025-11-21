!pip install -q google-genai chromadb

from google import genai
import chromadb

# Set your API key
client = genai.Client(api_key="AIzaSyA6UrAY4g3fTEjM48rQinrajD-6ifOcU")

college_text = """
Artificial Intelligence (AI) is a field of computer science focused on creating systems 
that can perform tasks requiring human intelligence such as reasoning and learning.

Machine Learning (ML) is a subset of AI that helps computers learn patterns from data
without being explicitly programmed.

Deep Learning is a subset of ML that uses neural networks with many layers.
"""
with open("college_notes.txt", "w") as f:
    f.write(college_text)

def split_text(text, chunk_size=200):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

chunks = split_text(college_text)
print(f"Created {len(chunks)} chunks")

def embed_text(text):
    """Generate embeddings using Gemini API with error handling."""
    try:
        if isinstance(text, str):
            text = [text]  # Convert single string to list
            
        result = client.models.embed_content(
            model="models/embedding-001",  # Updated model name
            contents=text
        )
        
        # Return all embeddings if multiple texts were provided
        if len(text) > 1:
            return [embedding.values for embedding in result.embeddings]
        else:
            return result.embeddings[0].values
            
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

# -------------------------
# INITIALIZE VECTOR DATABASE
# -------------------------
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="college_rag")

# -------------------------
# ADD DOCUMENTS TO COLLECTION
# -------------------------
print("Adding documents to vector database...")
for i, chunk in enumerate(chunks):
    emb = embed_text(chunk)
    if emb is not None:
        collection.add(
            ids=[f"chunk_{i}"],
            documents=[chunk],
            embeddings=[emb]
        )
        print(f"Added chunk {i}")

print("All documents added to collection!")

# -------------------------
# RAG QUERY FUNCTION
# -------------------------
def rag_query(question):
    q_emb = embed_text(question)
    if q_emb is None:
        return "Error: Failed to generate embedding for question"
    
    result = collection.query(query_embeddings=[q_emb], n_results=2)
    retrieved = result['documents'][0]
    
    prompt = f"""
Answer using ONLY this context:
{retrieved}

Question: {question}
"""
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text

# -------------------------
# TEST THE RAG SYSTEM
# -------------------------
print("\nTesting RAG system...")
result = rag_query("What is Machine Learning?")
print("Answer:", result)
