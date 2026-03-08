# app.py ── KrishiSahay Smart Farming Platform
# restructured for modularity, UI/UX and new features

import streamlit as st
from dotenv import load_dotenv
import os
import PIL.Image

# core business logic modules
from crop_model import recommend_crop
from disease_model import predict_disease
from fertilizer_model import recommend_fertilizer
from weather import fetch_weather, advice_from_weather
from market_price import get_current_price, predict_price_trend, available_crops, get_price_chart
from utils import t, load_css

# langchain imports for RAG
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# optional voice support
try:
    import speech_recognition as sr
    # check if PyAudio is available
    try:
        sr.Microphone()
        VOICE_AVAILABLE = True
    except AttributeError:
        VOICE_AVAILABLE = False
        sr = None
except ImportError:
    sr = None
    VOICE_AVAILABLE = False

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

load_dotenv()

# environment keys
GEMINI_API = os.getenv("GEMINI_API")
WEATHER_API = os.getenv("WEATHER_API")

# chatbot dependencies
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API)
    gemini_available = True
except:
    gemini_available = False

# Configure local LLM (no API needed)
@st.cache_resource
def load_llm():
    from transformers import pipeline
    return pipeline(
        "text-generation",
        model="microsoft/DialoGPT-small",
        max_length=200,
        truncation=True,
        temperature=0.7,
        do_sample=True,
        pad_token_id=50256,
    )

llm = load_llm()

@st.cache_resource

def create_vectorstore():
    knowledge = """
    Paddy in Telangana: NPK 120:60:60 kg/ha. Stem borer control: neem oil or carbofuran.
    Cotton: Pink bollworm – use pheromone traps + Profenofos spray.
    Chili: Thrips – Imidacloprid or neem-based spray.
    Government schemes: PM-KISAN ₹6000/year, Rythu Bandhu, PMFBY crop insurance.
    Save water: Use drip irrigation in dry districts like Mahabubnagar.
    Soil types: Black soil good for cotton, soybean, wheat. Red soil good for groundnut, millet. Sandy soil good for watermelon, sweet potato.
    
    Additional farming knowledge:
    - Organic farming: Use compost, vermiculture, and bio-fertilizers to improve soil health.
    - Pest management: Integrated Pest Management (IPM) combines cultural, biological, and chemical methods.
    - Irrigation: Drip irrigation saves 30-50% water compared to flood irrigation.
    - Climate change: Telangana faces droughts; focus on drought-resistant crops like sorghum and pearl millet.
    - Sustainable practices: Crop rotation prevents soil depletion and reduces pest buildup.
    - Market intelligence: Check MSP (Minimum Support Price) before selling crops.
    - Livestock: Integrate cattle rearing with crop farming for manure and additional income.
    - Women in farming: Many schemes support women farmers with training and subsidies.
    - Digital farming: Use apps for weather forecasts, pest alerts, and market prices.
    - Export potential: Telangana produces high-quality cotton, chili, and mangoes for export.
    """

    docs = [Document(page_content=knowledge, metadata={"source": "KrishiSahay"})]
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

vectorstore = create_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# --- UI components --------------------------------------------------------------

def show_dashboard(lang):
    st.header("Dashboard")
    
    # Weather Card
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='card'>
        <h4>🌤️ Current Weather</h4>
        """, unsafe_allow_html=True)
        try:
            weather = fetch_weather()
            if weather:
                st.metric("Temperature", f"{weather['temp']} °C")
                st.write(weather['desc'])
                st.write(advice_from_weather(weather))
            else:
                st.write("Weather data unavailable")
        except Exception as e:
            st.error(f"Weather error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card'>
        <h4>🌱 Crop Recommendation</h4>
        """, unsafe_allow_html=True)
        try:
            rec = recommend_crop('Black', 'Kharif', 500, 60, 30)
            st.success(f"Recommended: {rec}")
        except Exception as e:
            st.error(f"Crop rec error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='card'>
        <h4>📈 Market Trends</h4>
        """, unsafe_allow_html=True)
        try:
            crops = available_crops()
            crop = crops[0] if crops else "Rice"
            price = get_current_price(crop)
            st.metric(f"{crop} Price", f"₹{price}/qtl")
            chart = get_price_chart(crop)
            if chart:
                st.plotly_chart(chart, use_container_width=True, key="dashboard_chart")
        except Exception as e:
            st.error(f"Market error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='card'>
        <h4>💡 Farming Tips</h4>
        """, unsafe_allow_html=True)
        st.write("- Use drip irrigation to save water")
        st.write("- Rotate crops to maintain soil health")
        st.write("- Monitor for pests regularly")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Alerts
    st.subheader("🚨 Alerts & Notifications")
    st.info("Heavy rainfall expected tomorrow. Prepare for irrigation adjustments.")
    st.warning("Cotton prices are rising. Consider selling soon.")


def show_crop_recommendation(lang):
    st.header(t("nav_crop", lang))
    soil = st.selectbox(t("soil", lang), ["Black", "Red", "Sandy"])
    season = st.selectbox(t("season", lang), ["Kharif", "Rabi", "Zaid"])
    rain = st.number_input(t("rainfall", lang), min_value=0.0, max_value=10000.0, step=50.0)
    humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, step=5.0, value=50.0)
    temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=50.0, step=1.0, value=25.0)
    if st.button(t("recommend", lang)):
        try:
            result = recommend_crop(soil, season, rain, humidity, temperature)
            st.success(f"Recommended crop: **{result}**")
        except Exception as e:
            st.error(f"Error: {e}")


def show_disease_detection(lang):
    st.header(t("nav_disease", lang))
    uploaded = st.file_uploader("Upload leaf image", type=["jpg", "png", "jpeg"])
    if uploaded:
        img = PIL.Image.open(uploaded)
        st.image(img, use_column_width=True)
        if st.button("Detect Disease"):
            with st.spinner("Analyzing..."):
                try:
                    result = predict_disease(img)
                    st.success(f"Disease: **{result['disease']}**")
                    st.info(f"Treatment: {result['treatment']}")
                except Exception as e:
                    st.error(f"Error: {e}")


def show_fertilizer(lang):
    st.header(t("nav_fertilizer", lang))
    n = st.number_input("Nitrogen (N)", min_value=0.0, value=0.0)
    p = st.number_input("Phosphorus (P)", min_value=0.0, value=0.0)
    k = st.number_input("Potassium (K)", min_value=0.0, value=0.0)
    if st.button("Get Recommendation"):
        try:
            advice = recommend_fertilizer(n, p, k)
            st.write(advice)
        except Exception as e:
            st.error(f"Error: {e}")


def show_weather(lang):
    st.header(t("nav_weather", lang))
    try:
        weather = fetch_weather()
        if weather:
            st.image(weather["icon"], width=80)
            st.metric("Temp", f"{weather['temp']} °C", weather["desc"])
            st.write(advice_from_weather(weather))
        else:
            st.error("Weather information unavailable.")
    except Exception as e:
        st.error(f"Weather error: {e}")


def show_market(lang):
    st.header(t("nav_market", lang))
    try:
        crops = available_crops()
        crop = st.selectbox("Choose crop", crops)
        price = get_current_price(crop)
        pred = predict_price_trend(crop)
        st.metric("Current Price", f"₹{price}/qtl")
        st.metric("Predicted Next Month", f"₹{pred:.2f}/qtl")
        chart = get_price_chart(crop)
        if chart:
            st.plotly_chart(chart, key="market_chart")
        # Table
        st.subheader("Price Table")
        import pandas as pd
        data = {"Crop": crops, "Price (₹/qtl)": [get_current_price(c) for c in crops]}
        df = pd.DataFrame(data)
        st.table(df)
    except Exception as e:
        st.error(f"Market error: {e}")


def show_schemes(lang):
    st.header(t("nav_schemes", lang))
    st.markdown("""
    - **PM-KISAN:** ₹6000/year to farmers for cultivation. Apply online at pmkisan.gov.in
    - **Rythu Bandhu:** Investment support for Telangana farmers, up to ₹8000/ha.
    - **PMFBY:** Crop insurance scheme covering yield loss. Premium as low as 2%.
    - **Kisan Credit Card:** Easy loans for farmers at low interest.
    (Visit local agriculture office or agmarknet.gov.in for details.)
    """)


def show_chat(lang):
    st.header("💬 AI Farming Assistant")
    st.caption("Ask me anything about farming in Telangana! I have extensive knowledge about crops, weather, schemes, and best practices.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🌾 Hello! I'm KrishiSahay, your intelligent farming assistant for Telangana. I can help you with:\n\n• Crop recommendations and planning\n• Pest and disease management\n• Weather-based farming advice\n• Fertilizer and soil management\n• Government schemes and subsidies\n• Market prices and trends\n• Sustainable farming practices\n\nWhat would you like to know about farming today?"}
        ]
    
    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    prompt = None  # Initialize prompt
    
    # Voice input option
    if VOICE_AVAILABLE:
        if st.button("🎤 Voice Input"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening... Speak your question!")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    text = recognizer.recognize_google(audio)
                    st.success(f"You said: {text}")
                    prompt = text
                except Exception as e:
                    st.error(f"Voice error: {e}")
                    prompt = None
    else:
        st.info("Voice input disabled (PyAudio not installed)")

    if prompt is None:
        prompt = st.chat_input("Ask me about farming...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    answer, docs = generate_chat_response(prompt, lang)
                    st.markdown(answer)
                    if docs:
                        with st.expander("📚 Related Information"):
                            for doc in docs[:3]:  # Show top 3 references
                                st.caption(doc.page_content[:200] + "...")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = f"Chat error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def generate_chat_response(prompt: str, lang: str):
    try:
        answer = ""
        q = prompt.lower()
        if any(w in q for w in ["hello", "hi", "namaste"]):
            return "Namaste! मैं KrishiSahay हूं, आपका कृषि सहायक। मैं आपको फसल सलाह, मौसम अपडेट, और कृषि योजनाओं के बारे में मदद कर सकता हूं। आप क्या पूछना चाहेंगे? (Hello! I'm KrishiSahay, your farming assistant. I can help with crop advice, weather updates, and farming schemes. What would you like to ask?)", []
        
        if "weather" in q:
            w = fetch_weather()
            if w:
                return f"Current weather in Lal Bahadur Nagar, Telangana: {w['temp']}°C with {w['desc']}. Farming advice: {advice_from_weather(w)}", []
            else:
                return "Weather data unavailable. Please check local forecasts.", []
        
        if "crop" in q and ("recommend" in q or "suggest" in q):
            return f"Based on Telangana conditions: For Kharif season (June-Oct): Paddy, Cotton, Maize. For Rabi (Nov-March): Wheat, Chickpea. Consider soil type, rainfall, and market prices.", []
        
        # Use RAG with Gemini for detailed responses
        docs = retriever.invoke(prompt)
        context = "\n".join(d.page_content for d in docs)
        
        if gemini_available:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                full_prompt = f"""You are KrishiSahay, an expert AI farming assistant for Telangana farmers. 
                Provide detailed, helpful, and accurate farming advice based on the context provided.
                
                Context: {context}
                
                User Question: {prompt}
                
                Instructions:
                - Give comprehensive answers with practical farming tips
                - Include specific Telangana context when relevant
                - Suggest government schemes if applicable
                - Provide step-by-step guidance when needed
                - Be friendly and encouraging
                - Use simple language that farmers can understand
                - Include safety precautions for farming practices
                
                Answer:"""
                
                response = model.generate_content(full_prompt)
                answer = response.text.strip()
            except Exception as e:
                # Fallback to local LLM if Gemini fails
                full = f"Context: {context} Question: {prompt} Answer:"
                response = llm(full)
                answer = response[0]["generated_text"].split("Answer:")[-1].strip()
        else:
            # Fallback to local LLM
            full = f"Context: {context} Question: {prompt} Answer:"
            response = llm(full)
            answer = response[0]["generated_text"].split("Answer:")[-1].strip()
        
        return answer if answer else "I couldn't generate a response. Please try again.", docs
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question.", []

# ─── Page config & farmer-friendly green theme ──────────────────────────────
st.set_page_config(
    page_title="KrishiSahay",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌾 KrishiSahay")
    st.markdown("**Telangana Farmer AI Assistant**")
    st.markdown("Crops · Pests · Fertilizers · Schemes · Weather")
    st.markdown("Ask in English or Hindi")

    language = st.selectbox("Response Language", ["English", "Hindi", "Telugu"], index=0)

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Made for Rathod Ajay • Lal Bahadur Nagar • 2026")

# Hero Section
st.markdown("""
<div class='hero'>
<h1>🌾 KrishiSahay</h1>
<p>Empowering Farmers with Smart Agriculture Technology</p>
<p>Get personalized crop recommendations, detect plant diseases, access weather insights, fertilizer guidance, market trends, and government schemes all in one place.</p>
</div>
""", unsafe_allow_html=True)

language = st.selectbox("🌐 Language", ["English", "Hindi", "Telugu"], index=0, key="lang")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏠 " + t("nav_home", language),
    "🌱 " + t("nav_crop", language),
    "🔍 " + t("nav_disease", language),
    "🧪 " + t("nav_fertilizer", language),
    "🌤️ " + t("nav_weather", language),
    "📈 " + t("nav_market", language),
    "🏛️ " + t("nav_schemes", language),
    "💬 " + t("nav_chat", language),
])

with tab1:
    show_dashboard(language)
with tab2:
    show_crop_recommendation(language)
with tab3:
    show_disease_detection(language)
with tab4:
    show_fertilizer(language)
with tab5:
    show_weather(language)
with tab6:
    show_market(language)
with tab7:
    show_schemes(language)
with tab8:
    show_chat(language)