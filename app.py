import streamlit as st
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline
import numpy as np

st.title("Website Q&A (Faster + Accurate)")

# -------------------------------
# Load models (cached)
# -------------------------------
@st.cache_resource
def load_models():
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    # Generative Q&A for accuracy
    qa_gen = pipeline("text2text-generation", model="google/flan-t5-small")# Question suggestions
    q_gen = pipeline("text2text-generation", model="google/flan-t5-small")
    return embed_model, qa_gen, q_gen

embed_model, qa_gen, q_gen = load_models()

# -------------------------------
# User input
# -------------------------------
url = st.text_input("Enter Website URL:")

if url:
    try:
        # -------------------------------
        # Scrape website
        # -------------------------------
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ')
        st.success("Website loaded!")

        # -------------------------------
        # Split text into chunks
        # -------------------------------
        chunk_size = 800
        overlap = 100
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]

        # -------------------------------
        # Create embeddings & FAISS index
        # -------------------------------
        embeddings = embed_model.encode(chunks, convert_to_numpy=True)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        st.success("Embeddings indexed!")

        # -------------------------------
        # Generate suggested questions
        # -------------------------------
        try:
            q_prompt = f"Generate 5 relevant questions based on this text:\n{text[:2000]}"
            suggestions_text = q_gen(q_prompt, max_length=150)[0]['generated_text']
            suggested_questions = [q.strip() for q in suggestions_text.replace("\n", ",").split(",") if q.strip()]
        except Exception as e:
            st.warning(f"Question suggestion failed: {e}")
            suggested_questions = []

        st.sidebar.subheader("Suggested Questions")
        selected_question = st.sidebar.radio("Click a question:", [""] + suggested_questions[:5])

        # -------------------------------
        # Ask question
        # -------------------------------
        user_query = st.text_input("Or type your own question:")
        final_query = selected_question if selected_question else user_query

        if final_query:
            # Top 3 chunks
            q_emb = embed_model.encode([final_query], convert_to_numpy=True)
            D, I = index.search(q_emb, k=3)
            context = " ".join([chunks[idx] for idx in I[0]])

            # Generative Q&A (accurate answer)
            qa_input = f"Answer the question based on the context:\nContext: {context}\nQuestion: {final_query}"
            answer = qa_gen(qa_input, max_length=150)[0]['generated_text']

            st.subheader("Answer:")
            st.write(answer)

    except Exception as e:
        st.error(f"Error loading website: {e}")
