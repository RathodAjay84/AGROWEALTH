import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# -------------------------------
# Page Config
# -------------------------------

st.set_page_config(
    page_title="KrishiSahay AI",
    page_icon="🌾",
    layout="wide"
)

# -------------------------------
# Load API Key
# -------------------------------
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("API key not found. Please add it in .env file")
    st.stop()

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-pro")

# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.title("🌾 KrishiSahay")
st.sidebar.subheader("Team AgroWealth")

language = st.sidebar.selectbox(
    "Choose Language",
    ["English", "Hindi", "Telugu"]
)

st.sidebar.markdown("---")

st.sidebar.info(
"""
KrishiSahay is an AI powered assistant for farmers.

Features:
• Crop Guidance  
• Pest Management  
• Fertilizer Advice  
• Government Schemes  
"""
)

# -------------------------------
# Load Knowledge Base
# -------------------------------

@st.cache_resource
def load_data():

    with open("knowledge.txt","r") as f:
        data = f.readlines()

    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    embeddings = embed_model.encode(data)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))

    return data, embed_model, index


data, embed_model, index = load_data()

# -------------------------------
# Title Section
# -------------------------------

st.title("🌾 KrishiSahay – AI Agricultural Assistant")
st.markdown("### Helping Farmers with Smart AI Advice")

st.markdown("---")

# -------------------------------
# Chat History
# -------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------
# User Input
# -------------------------------

user_question = st.chat_input("Ask any farming question...")

if user_question:

    st.session_state.messages.append({
        "role":"user",
        "content":user_question
    })

    with st.chat_message("user"):
        st.write(user_question)

    # -------------------------------
    # FAISS Search
    # -------------------------------

    query_vector = embed_model.encode([user_question])

    D, I = index.search(np.array(query_vector), k=3)

    context = ""

    for i in I[0]:
        context += data[i]

    # -------------------------------
    # Prompt
    # -------------------------------

    prompt = f"""
You are an expert agricultural advisor.

Use the following information to help the farmer.

Context:
{context}

Question:
{user_question}

Answer clearly and simply for farmers.
"""

    try:

        response = model.generate_content(prompt)

        answer = response.text

    except Exception as e:

        answer = "Sorry, AI service is temporarily unavailable."

    st.session_state.messages.append({
        "role":"assistant",
        "content":answer
    })

    with st.chat_message("assistant"):
        st.write(answer)

# -------------------------------
# Footer
# -------------------------------

st.markdown("---")

st.markdown(
"""
🌾 **KrishiSahay – AI for Farmers**  
Developed by **Team AgroWealth**

Hackathon Project
"""
)