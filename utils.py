# utils.py
"""Utility functions used across the KrishiSahay platform."""

import streamlit as st

# simple multilingual support with hard‑coded texts
LANGUAGES = {
    "English": {
        "home_title": "KrishiSahay – Smart Farming Assistant",
        "nav_home": "Home",
        "nav_crop": "Crop Recommendation",
        "nav_disease": "Plant Disease Detection",
        "nav_fertilizer": "Fertilizer Guide",
        "nav_weather": "Weather",
        "nav_market": "Market Prices",
        "nav_schemes": "Government Schemes",
        "nav_chat": "Chatbot",
        "soil": "Soil Type",
        "season": "Season",
        "rainfall": "Rainfall (mm)",
        "recommend": "Recommend Crop",
        # ... add more keys as needed
    },
    "Hindi": {
        "home_title": "कृषिसहाय – स्मार्ट खेती सहायक",
        "nav_home": "होम",
        "nav_crop": "फसल सुझाव",
        "nav_disease": "रोग पहचान",
        "nav_fertilizer": "उर्वरक मार्गदर्शन",
        "nav_weather": "मौसम",
        "nav_market": "बाजार भाव",
        "nav_schemes": "सरकारी योजनाएँ",
        "nav_chat": "चैटबॉट",
        "soil": "मृदा प्रकार",
        "season": "मौसम",
        "rainfall": "वर्षा (मिमी)",
        "recommend": "फसल सुझाएँ",
    },
    "Telugu": {
        "home_title": "కృష్ణిసహాయ్ – స్మార్ట్ వ్యవసాయ సహాయకుడు",
        "nav_home": "హోమ్",
        "nav_crop": "పంట సిఫార్సు",
        "nav_disease": "రోగ గుర్తింపు",
        "nav_fertilizer": "రసాయనం మార్గదర్శనం",
        "nav_weather": "వాతావరణం",
        "nav_market": "మార్కెట్ ధరలు",
        "nav_schemes": "ప్రభుత్వ పథకాలు",
        "nav_chat": "చాట్బాట్",
        "soil": "మట్టిది రకం",
        "season": "కాలం",
        "rainfall": "వర్షపాతం (మిమీ)",
        "recommend": "పంట సిఫార్సు చేయండి",
    },
}


def t(key: str, lang: str = "English") -> str:
    """Translate a given message key according to the selected language."""
    return LANGUAGES.get(lang, LANGUAGES["English"]).get(key, key)


def load_css():
    """Inject custom CSS for improved UI/UX."""
    st.markdown(
        """
        <style>
        .stApp { 
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            font-family: 'Arial', sans-serif;
        }
        .hero {
            background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .card { 
            padding: 1.5rem; 
            border-radius: 12px; 
            background: white; 
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
            margin-bottom: 1.5rem;
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        h1, h2, h3 { 
            color: #1B5E20; 
            font-weight: bold;
        }
        .stButton>button {
            background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #388E3C 0%, #4CAF50 100%);
        }
        .sidebar .sidebar-content { 
            background-color: #4CAF50; 
            color: white; 
        }
        .metric {
            background: #f1f8e9;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
