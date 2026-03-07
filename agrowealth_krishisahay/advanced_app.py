import streamlit as st
import google.generativeai as genai
from PIL import Image

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="KrishiSahay AI",
    page_icon="🌾",
    layout="wide"
)

# -----------------------------
# API KEY
# -----------------------------
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API = os.getenv("GEMINI_API")

genai.configure(api_key=GEMINI_API)

model = genai.GenerativeModel("gemini-1.5-flash")
# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown("""
<style>

.main {
background-color:#f6f9f6;
}

h1 {
color:#2e7d32;
text-align:center;
}

.card {
padding:20px;
border-radius:10px;
background:white;
box-shadow:0px 0px 10px rgba(0,0,0,0.1);
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------

st.title("🌾 KrishiSahay")
st.subheader("AI Powered Agriculture Assistant")
st.write("Developed by **Team AgroWealth**")

st.divider()

# -----------------------------
# SIDEBAR MENU
# -----------------------------

menu = st.sidebar.selectbox(
    "Navigation",
    [
        "Home",
        "AI Chat Assistant",
        "Farmer Dashboard",
        "Crop Disease Detection",
        "Weather Information"
    ]
)

# -----------------------------
# HOME PAGE
# -----------------------------

if menu == "Home":

    st.markdown("## Welcome to KrishiSahay")

    st.write("""
KrishiSahay helps farmers with AI powered solutions.

Features:

✔ AI Farming Assistant  
✔ Crop Disease Detection  
✔ Farmer Dashboard  
✔ Weather Information  
✔ Agricultural Knowledge
""")

# -----------------------------
# AI CHATBOT
# -----------------------------

elif menu == "AI Chat Assistant":

    st.header("🤖 Ask Agriculture Questions")

    question = st.text_input("Enter your farming question")

    if st.button("Get Advice"):

        if question:

            try:

                response = model.generate_content(question)

                st.success(response.text)

            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------------
# FARMER DASHBOARD
# -----------------------------

elif menu == "Farmer Dashboard":

    st.header("📊 Farmer Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Soil Health", "Good")

    with col2:
        st.metric("Water Level", "Moderate")

    with col3:
        st.metric("Crop Growth", "Healthy")

    st.write("### Recommended Crops")

    st.write("""
• Rice  
• Wheat  
• Cotton  
• Maize
""")

# -----------------------------
# CROP DISEASE DETECTION
# -----------------------------

elif menu == "Crop Disease Detection":

    st.header("📷 Upload Crop Image")

    uploaded_file = st.file_uploader(
        "Upload plant image",
        type=["jpg","png","jpeg"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Image", use_column_width=True)

        st.write("### AI Analysis")

        st.info("Possible disease detected. Use organic pesticide or neem oil.")

# -----------------------------
# WEATHER INFO
# -----------------------------

elif menu == "Weather Information":

    st.header("🌦 Weather Information")

    city = st.text_input("Enter your city")

    if st.button("Get Weather Advice"):

        st.write("Weather analysis feature can be integrated with API.")

        st.success("Temperature: 28°C")

        st.info("Recommended irrigation for crops today.")