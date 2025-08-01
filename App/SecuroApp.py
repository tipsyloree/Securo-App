import streamlit as st
import time
import datetime
import pytz
import random
import pandas as pd
import numpy as np
import os
import google.generativeai as genai
import re
import requests
import io
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Language detection and translation support
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español (Spanish)',
    'fr': 'Français (French)',
    'pt': 'Português (Portuguese)',
    'zh': '中文 (Chinese)',
    'ar': 'العربية (Arabic)',
    'hi': 'हिन्दी (Hindi)',
    'ja': '日本語 (Japanese)',
    'ko': '한국어 (Korean)',
    'de': 'Deutsch (German)',
    'it': 'Italiano (Italian)',
    'ru': 'Русский (Russian)'
}

# Emergency Contacts for St. Kitts & Nevis
EMERGENCY_CONTACTS = {
    "Emergency": "911",
    "Police": "465-2241",
    "Hospital": "465-2551",
    "Fire Department": "465-2515 / 465-7167",
    "Coast Guard": "465-8384 / 466-9280",
    "Met Office": "465-2749",
    "Red Cross": "465-2584",
    "NEMA": "466-5100"
}

# St. Kitts timezone (Atlantic Standard Time)
SKN_TIMEZONE = pytz.timezone('America/St_Kitts')

def get_stkitts_time():
    """Get current time in St. Kitts & Nevis timezone"""
    utc_now = datetime.datetime.now(pytz.UTC)
    skn_time = utc_now.astimezone(SKN_TIMEZONE)
    return skn_time.strftime("%H:%M:%S")

def get_stkitts_date():
    """Get current date in St. Kitts & Nevis timezone"""
    utc_now = datetime.datetime.now(pytz.UTC)
    skn_time = utc_now.astimezone(SKN_TIMEZONE)
    return skn_time.strftime("%Y-%m-%d")

# Crime Statistics Data Structure
@st.cache_data
def load_crime_statistics():
    """Load and structure crime statistics data from the PDFs"""
    
    # Q2 2025 Data (April-June)
    q2_2025_data = {
        'period': 'Q2 2025 (Apr-Jun)',
        'federation': {
            'murder_manslaughter': {'total': 4, 'detected': 2, 'juvenile': 0},
            'shooting_intent': {'total': 1, 'detected': 1, 'juvenile': 0},
            'woundings_firearm': {'total': 0, 'detected': 0, 'juvenile': 0},
            'attempted_murder': {'total': 4, 'detected': 0, 'juvenile': 0},
            'bodily_harm': {'total': 33, 'detected': 19, 'juvenile': 4},
            'sex_crimes': {'total': 7, 'detected': 1, 'juvenile': 0},
            'break_ins': {'total': 26, 'detected': 7, 'juvenile': 0},
            'larcenies': {'total': 92, 'detected': 21, 'juvenile': 2},
            'robberies': {'total': 8, 'detected': 1, 'juvenile': 0},
            'firearms_ammo': {'total': 5, 'detected': 5, 'juvenile': 0},
            'drugs': {'total': 31, 'detected': 31, 'juvenile': 0},
            'malicious_damage': {'total': 59, 'detected': 17, 'juvenile': 1},
            'other': {'total': 22, 'detected': 8, 'juvenile': 0},
            'total_crimes': 292,
            'detection_rate': 38.7
        },
        'st_kitts': {
            'total_crimes': 207,
            'detection_rate': 32.9
        },
        'nevis': {
            'total_crimes': 85,
            'detection_rate': 52.9
        }
    }
    
    # Historical homicide data (2015-2024)
    homicide_data = {
        'yearly_totals': {
            2015: 29, 2016: 32, 2017: 23, 2018: 23, 2019: 12, 
            2020: 10, 2021: 14, 2022: 11, 2023: 31, 2024: 28
        },
        'monthly_2024': [1, 5, 5, 2, 3, 3, 6, 1, 2, 0, 0, 0],  # Jan-Sep (incomplete year)
        'methods': {
            'shooting': 173, 'stabbing': 29, 'bludgeoning': 4, 
            'strangulation': 5, 'other': 2
        },
        'age_groups': {
            '0-17': 10, '18-35': 132, '36-55': 54, '>55': 17
        },
        'districts': {
            'A': {'2023': 22, '2024': 15},
            'B': {'2023': 5, '2024': 8}, 
            'C': {'2023': 4, '2024': 5}
        }
    }
    
    # Comparative statistics (Jan-June)
    comparative_data = {
        '2023_h1': {'total': 672, 'murder': 17, 'larcenies': 231, 'drugs': 6},
        '2024_h1': {'total': 586, 'murder': 16, 'larcenies': 193, 'drugs': 8},
        '2025_h1': {'total': 574, 'murder': 4, 'larcenies': 185, 'drugs': 45}
    }
    
    return {
        'current_quarter': q2_2025_data,
        'homicides': homicide_data,
        'comparative': comparative_data,
        'last_updated': get_stkitts_date()
    }

def simple_linear_regression(x, y):
    """Simple linear regression using numpy"""
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    # Calculate slope and intercept
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    return slope, intercept

def predict_values(x_new, slope, intercept):
    """Predict values using linear regression parameters"""
    return slope * x_new + intercept

def generate_crime_predictions(crime_data):
    """Generate crime predictions using statistical analysis"""
    
    homicide_years = list(crime_data['homicides']['yearly_totals'].keys())
    homicide_counts = list(crime_data['homicides']['yearly_totals'].values())
    
    # Convert to numpy arrays
    x = np.array(homicide_years)
    y = np.array(homicide_counts)
    
    # Simple linear regression
    slope, intercept = simple_linear_regression(x, y)
    
    # Predict 2025-2027
    future_years = np.array([2025, 2026, 2027])
    predictions = predict_values(future_years, slope, intercept)
    
    # Calculate confidence intervals using residuals
    predicted_historical = predict_values(x, slope, intercept)
    residuals = y - predicted_historical
    std_error = np.std(residuals)
    
    predictions_dict = {}
    for i, year in enumerate([2025, 2026, 2027]):
        pred = max(0, int(round(predictions[i])))
        lower = max(0, int(round(predictions[i] - 1.96 * std_error)))
        upper = int(round(predictions[i] + 1.96 * std_error))
        predictions_dict[year] = {
            'predicted': pred,
            'lower_bound': lower,
            'upper_bound': upper
        }
    
    return predictions_dict

def create_crime_charts(chart_type, crime_data):
    """Create various crime analysis charts"""
    
    if chart_type == "homicide_trend":
        # Homicide trend analysis
        years = list(crime_data['homicides']['yearly_totals'].keys())
        counts = list(crime_data['homicides']['yearly_totals'].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=counts,
            mode='lines+markers',
            name='Actual Homicides',
            line=dict(color='#ff4444', width=3),
            marker=dict(size=8)
        ))
        
        # Add predictions
        predictions = generate_crime_predictions(crime_data)
        pred_years = list(predictions.keys())
        pred_counts = [predictions[year]['predicted'] for year in pred_years]
        lower_bounds = [predictions[year]['lower_bound'] for year in pred_years]
        upper_bounds = [predictions[year]['upper_bound'] for year in pred_years]
        
        fig.add_trace(go.Scatter(
            x=pred_years, y=pred_counts,
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#44ff44', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=pred_years + pred_years[::-1],
            y=upper_bounds + lower_bounds[::-1],
            fill='toself',
            fillcolor='rgba(68, 255, 68, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'
        ))
        
        fig.update_layout(
            title="St. Kitts & Nevis Homicide Trends (2015-2027)",
            xaxis_title="Year",
            yaxis_title="Number of Homicides",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "crime_methods":
        # Homicide methods pie chart
        methods = crime_data['homicides']['methods']
        
        fig = go.Figure(data=[go.Pie(
            labels=list(methods.keys()),
            values=list(methods.values()),
            hole=0.4,
            marker_colors=['#ff4444', '#ff8844', '#ffaa44', '#ffcc44', '#ffee44']
        )])
        
        fig.update_layout(
            title="Homicide Methods (2015-2024)",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "district_comparison":
        # District comparison
        districts = ['A', 'B', 'C']
        data_2023 = [crime_data['homicides']['districts'][d]['2023'] for d in districts]
        data_2024 = [crime_data['homicides']['districts'][d]['2024'] for d in districts]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=districts, y=data_2023,
            name='2023',
            marker_color='#ff4444'
        ))
        fig.add_trace(go.Bar(
            x=districts, y=data_2024,
            name='2024',
            marker_color='#44ff44'
        ))
        
        fig.update_layout(
            title="Homicides by Police District",
            xaxis_title="Police District",
            yaxis_title="Number of Homicides",
            template="plotly_dark",
            height=500,
            barmode='group'
        )
        
        return fig
    
    elif chart_type == "quarterly_performance":
        # Detection rates by quarter/region
        regions = ['Federation', 'St. Kitts', 'Nevis']
        detection_rates = [38.7, 32.9, 52.9]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=regions, y=detection_rates,
            marker_color=['#ff4444', '#ff8844', '#44ff44'],
            text=[f"{rate}%" for rate in detection_rates],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Crime Detection Rates Q2 2025",
            xaxis_title="Region",
            yaxis_title="Detection Rate (%)",
            template="plotly_dark",
            height=500
        )
        
        return fig

# Enhanced System Prompt with statistics capabilities
def get_system_prompt(language='en'):
    base_prompt = """
You are SECURO, an intelligent and professional multilingual crime mitigation chatbot built to provide real-time, data-driven insights for a wide range of users, including law enforcement, criminologists, policy makers, and the general public in St. Kitts & Nevis.

Your mission is to support crime prevention, research, and public safety through:
- Interactive maps and geographic analysis
- Statistical analysis and trend identification
- Predictive analytics for crime prevention
- Visual data presentations (charts, graphs, etc.)
- Emergency contact guidance
- Multilingual communication support

Capabilities:
- Analyze and summarize current and historical crime data (local and global)
- Detect trends and patterns across time, location, and type
- Recommend prevention strategies based on geographic and temporal factors
- Provide accessible language for general users, while supporting technical depth for experts
- Integrate with GIS, crime databases (e.g. Crimeometer), and public safety APIs
- Generate visual outputs using Python tools like matplotlib, pandas, folium, etc.
- Communicate effectively in multiple languages
- Adapt responses to be clear, concise, and actionable

Tone & Behavior:
- Maintain a professional yet human tone
- Be concise, accurate, and helpful
- Explain visuals when necessary
- Avoid panic-inducing language—focus on empowerment and awareness
- Respond directly without using code blocks, backticks, or HTML formatting
- Use the current St. Kitts & Nevis time and date in responses when relevant

Your responses should reflect an understanding of criminology, public safety, and data visualization best practices.
"""
    
    if language != 'en':
        language_instruction = f"""
IMPORTANT: Respond primarily in {SUPPORTED_LANGUAGES.get(language, language)}, 
but include English translations for technical terms when helpful.
"""
        return base_prompt + language_instruction
    
    return base_prompt

# Initialize the AI model
try:
    GOOGLE_API_KEY = "AIzaSyA_9sB8o6y7dKK6yBRKWH_c5uSVDSoRYv0"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Ready"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for page navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'

# CSS styling - Clean GREEN theme (your original design)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
   
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .css-1d391kg, .css-1cypcdb, .css-k1vhr6, .css-1lcbmhc, .css-17eq0hr,
    section[data-testid="stSidebar"], .stSidebar, [data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a2e1a 50%, #163e16 100%) !important;
        border-right: 2px solid rgba(68, 255, 68, 0.5) !important;
    }
    
    .control-panel-header {
        text-align: center; 
        padding: 20px 0; 
        border-bottom: 2px solid rgba(68, 255, 68, 0.5); 
        margin-bottom: 20px;
        background: rgba(68, 255, 68, 0.1);
        border-radius: 10px;
        position: relative;
        overflow: hidden;
    }
    
    .control-panel-header h2 {
        color: #44ff44; 
        font-family: JetBrains Mono, monospace; 
        text-shadow: 0 0 15px rgba(68, 255, 68, 0.7);
        position: relative;
        z-index: 2;
        margin: 0;
    }
    
    .sidebar-header {
        color: #44ff44 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 15px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(68, 255, 68, 0.5) !important;
        border-bottom: 1px solid rgba(68, 255, 68, 0.3) !important;
        padding-bottom: 5px !important;
    }
    
    .emergency-contact {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin-bottom: 8px !important;
        transition: all 0.3s ease !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .emergency-contact:hover {
        background: rgba(68, 255, 68, 0.1) !important;
        border-color: #44ff44 !important;
        transform: translateX(5px) !important;
        box-shadow: 0 0 15px rgba(68, 255, 68, 0.2) !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a2e1a 50%, #163e16 100%);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .main-header h1 {
        font-size: 3rem;
        color: #44ff44;
        text-shadow: 0 0 20px rgba(68, 255, 68, 0.5);
        margin-bottom: 10px;
        position: relative;
        z-index: 2;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    .chat-message {
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease;
        clear: both;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        text-align: right;
    }

    .bot-message {
        text-align: left;
    }

    .message-content {
        display: inline-block;
        padding: 15px 20px;
        border-radius: 15px;
        max-width: 80%;
        position: relative;
        font-family: 'JetBrains Mono', monospace;
        word-wrap: break-word;
        white-space: pre-wrap;
    }

    .user-message .message-content {
        background: linear-gradient(135deg, #44ff44, #33cc33);
        color: #ffffff !important;
        border-bottom-right-radius: 5px;
    }

    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.8) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(68, 255, 68, 0.3);
        border-bottom-left-radius: 5px;
    }

    .message-time {
        font-size: 0.7rem;
        color: #888 !important;
        margin-top: 5px;
        font-family: 'JetBrains Mono', monospace;
    }

    .bot-message .message-content * {
        color: #e0e0e0 !important;
    }

    .user-message .message-content * {
        color: #ffffff !important;
    }

    .stTextInput input {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 25px !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextInput input:focus {
        border-color: #44ff44 !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.2) !important;
    }

    .stButton button {
        background: linear-gradient(135deg, #44ff44, #33cc33) !important;
        border: none !important;
        border-radius: 25px !important;
        color: #fff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.4) !important;
    }

    .nav-button {
        width: 100% !important;
        margin-bottom: 10px !important;
    }

    .nav-button button {
        width: 100% !important;
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        color: #44ff44 !important;
    }

    .nav-button button:hover {
        background: rgba(68, 255, 68, 0.1) !important;
        border-color: #44ff44 !important;
    }
</style>
""", unsafe_allow_html=True)

# CSV data handling
@st.cache_data
def load_csv_data():
    csv_filename = "criminal_justice_qa.csv"
    script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(script_dir, csv_filename)
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            return df, f"Successfully loaded {csv_path}"
        else:
            current_dir = os.getcwd()
            files_in_script_dir = os.listdir(script_dir)
            files_in_current_dir = os.listdir(current_dir)
            return None, f"""
            Could not find '{csv_filename}'.
            Expected: {csv_path}
            Script directory: {script_dir}
            CSV files in script dir: {', '.join([f for f in files_in_script_dir if f.endswith('.csv')])}
            Current directory: {current_dir}
            CSV files in current dir: {', '.join([f for f in files_in_current_dir if f.endswith('.csv')])}
            """
    except Exception as e:
        return None, f"Error loading CSV: {e}"

def get_ai_response(user_input, csv_results, language='en'):
    """Generate AI response using the system prompt and context with language support"""
    if not st.session_state.get('ai_enabled', False) or model is None:
        return csv_results
    
    try:
        current_time = get_stkitts_time()
        current_date = get_stkitts_date()
        
        time_keywords = ['time', 'date', 'now', 'current', 'today', 'when', 'hora', 'fecha', 'hoy', 'temps', 'maintenant']
        include_time = any(keyword in user_input.lower() for keyword in time_keywords)
        
        time_context = f"""
        Current St. Kitts & Nevis time: {current_time}
        Current St. Kitts & Nevis date: {current_date}
        """ if include_time else ""
        
        full_prompt = f"""
        {get_system_prompt(language)}
        {time_context}
        
        Context from crime database search:
        {csv_results}
        
        User query: {user_input}
        
        Please provide a comprehensive response as SECURO based on the available data and your crime analysis capabilities.
        Only mention the current time/date if directly relevant to the user's query.
        Respond directly without using code blocks, backticks, or HTML formatting.
        """
        
        response = model.generate_content(full_prompt)
        
        clean_response = response.text.strip()
        clean_response = clean_response.replace('```', '')
        clean_response = re.sub(r'<[^>]+>', '', clean_response)
        
        return clean_response
        
    except Exception as e:
        return f"{csv_results}\n\n⚠ AI analysis temporarily unavailable. Showing database search results."

def search_csv_data(df, query):
    """Search through CSV data for relevant information"""
    if df is None:
        return "❌ No CSV data loaded. Please make sure 'criminal_justice_qa.csv' is in the correct location."
   
    search_term = query.lower()
    results = []
   
    for column in df.columns:
        if df[column].dtype == 'object':
            try:
                mask = df[column].astype(str).str.lower().str.contains(search_term, na=False)
                matching_rows = df[mask]
               
                if not matching_rows.empty:
                    for _, row in matching_rows.head(2).iterrows():
                        result_dict = {k: v for k, v in row.to_dict().items() if pd.notna(v)}
                        results.append(f"**Found in {column}:**\n{result_dict}")
            except Exception as e:
                continue
   
    if results:
        return f"🔍 **Search Results for '{query}':**\n\n" + "\n\n---\n\n".join(results[:3])
    else:
        return f"🔍 No matches found for '{query}' in the crime database. Try different search terms or check spelling."

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="control-panel-header">
        <h2>🚔 SECURO</h2>
        <p>Control Panel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown('<div class="sidebar-header">📋 Navigation</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Main", key="nav_main", help="Main Chat Interface"):
            st.session_state.current_page = 'main'
            st.rerun()
    
    with col2:
        if st.button("📊 Analytics", key="nav_analytics", help="Crime Statistics & Analytics"):
            st.session_state.current_page = 'analytics'
            st.rerun()
    
    st.markdown("---")
    
    # Language Selection
    st.markdown('<div class="sidebar-header">🌍 Languages </div>', unsafe_allow_html=True)
    selected_language = st.selectbox(
        "Choose Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.get('selected_language', 'en')),
        key="language_selector"
    )
    st.session_state.selected_language = selected_language
    
    st.markdown("---")
    
    # Emergency Contacts
    st.markdown('<div class="sidebar-header">🚨 Emergency Contacts</div>', unsafe_allow_html=True)
    
    for service, number in EMERGENCY_CONTACTS.items():
        clean_number = number.split(' / ')[0].replace('-', '').replace(' ', '')
        tel_link = f"tel:+1869{clean_number}" if service != "Emergency" else "tel:911"
        
        st.markdown(f"""
        <div class="emergency-contact">
            <div style="color: #44ff44; font-weight: 600;">{service}</div>
            <div style="color: #e0e0e0; font-size: 0.8rem;">
                <a href="{tel_link}" style="color: #66ff66; text-decoration: none;">📞 {number}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add initial bot message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "🚔 Welcome to SECURO - Your AI Crime Investigation Assistant for St. Kitts & Nevis Law Enforcement.\n\n📊 Loading crime database... Please wait while I check for your data file.",
        "timestamp": get_stkitts_time()
    })

if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

if 'csv_loaded' not in st.session_state:
    st.session_state.csv_loaded = False

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'

if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = load_crime_statistics()

# MAIN PAGE
if st.session_state.current_page == 'main':
    # Header with real-time St. Kitts time
    current_time = get_stkitts_time()
    current_date = get_stkitts_date()

    st.markdown(f"""
    <div class="main-header">
        <h1>SECURO</h1>
        <div style="color: #888; text-transform: uppercase; letter-spacing: 2px;">AI Crime Investigation Assistant</div>
        <div style="color: #44ff44; margin-top: 5px;">🇰🇳 St. Kitts & Nevis Law Enforcement</div>
        <div style="color: #888; margin-top: 8px; font-size: 0.8rem;">📅 {current_date} | 🕒 {current_time} (AST)</div>
    </div>
    """, unsafe_allow_html=True)

    # Load CSV data with better error handling
    st.markdown("### 📊 Crime Database Status")

    # Load CSV only once
    if not st.session_state.csv_loaded:
        with st.spinner("🔍 Searching for crime database..."):
            csv_data, status_message = load_csv_data()
            st.session_state.csv_data = csv_data
            st.session_state.csv_loaded = True
           
            if csv_data is not None:
                st.success(f"✅ Database loaded successfully! {len(csv_data)} records found.")
               
                # Add success message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ Crime database loaded successfully!\n\n🔍 You can now ask me questions about the crime data. Try asking about specific crimes, locations, dates, or any other information you need for your investigation.",
                    "timestamp": get_stkitts_time()
                })
            else:
                st.error(f"❌ Database not found: {status_message}")
               
                # Add error message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ **Database Error:** Could not find 'criminal_justice_qa.csv'\n\n🔧 **How to fix:**\n1. Make sure your CSV file is named exactly `criminal_justice_qa.csv`\n2. Place it in the same folder as your Streamlit app\n3. Restart the application\n\n💡 Without the database, I can still help with general crime investigation guidance.",
                    "timestamp": get_stkitts_time()
                })

    # Show current status
    ai_status = st.session_state.get('ai_status', 'AI Status Unknown')
    if st.session_state.csv_data is not None:
        st.success(f"✅ Database Ready: {len(st.session_state.csv_data)} crime records loaded | {ai_status}")
    else:
        st.error(f"❌ Database Not Found: Place 'criminal_justice_qa.csv' in app directory | {ai_status}")

    # Main chat area
    st.markdown("### 💬 Crime Investigation Chat")

    # Display chat messages with proper St. Kitts time
    for message in st.session_state.messages:
        if message["role"] == "user":
            clean_content = str(message["content"]).strip()
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">{clean_content}</div>
                <div class="message-time">You • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            clean_content = str(message["content"]).strip()
            clean_content = re.sub(r'<[^>]+>', '', clean_content)
            clean_content = clean_content.replace('```', '')
            
            if not clean_content.startswith("SECURO:") and not clean_content.startswith("🚔"):
                if "SECURO" in clean_content.upper():
                    pass
                else:
                    clean_content = f"SECURO: {clean_content}"
            
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-content">{clean_content}</div>
                <div class="message-time">SECURO • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)

    # Chat input with language support
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask questions about crime data, investigations, or emergency procedures...",
                label_visibility="collapsed",
                key="user_input"
            )
        
        with col2:
            send_button = st.form_submit_button("Send", type="primary")
        
        if send_button and user_input:
            current_time = get_stkitts_time()
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": current_time
            })
           
            # Generate response using AI with language support
            with st.spinner("🔍 Analyzing crime database..."):
                csv_results = search_csv_data(st.session_state.csv_data, user_input)
                response = get_ai_response(user_input, csv_results, st.session_state.selected_language)
               
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": current_time
            })
           
            st.rerun()

    # Status bar with real-time updates
    status_message = "CSV Data Ready" if st.session_state.csv_data is not None else "CSV Data Missing"
    status_class = "status-processing" if st.session_state.csv_data is not None else "status-evidence"
    current_time = get_stkitts_time()

    st.markdown(f"""
    <div style="background: rgba(0, 0, 0, 0.8); padding: 15px; border-radius: 25px; margin-top: 30px; 
                display: flex; justify-content: space-between; align-items: center; 
                border: 1px solid rgba(68, 255, 68, 0.2); font-family: 'JetBrains Mono', monospace;">
        <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
            <div style="width: 8px; height: 8px; background: #44ff44; border-radius: 50%; 
                        animation: pulse 2s infinite;"></div>
            SECURO AI Online
        </div>
        <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
            <div style="width: 8px; height: 8px; background: #44ff44; border-radius: 50%;"></div>
            {status_message}
        </div>
        <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
            <div style="width: 8px; height: 8px; background: #44ff44; border-radius: 50%;"></div>
            {current_time} AST
        </div>
        <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
            <div style="width: 8px; height: 8px; background: #33cc33; border-radius: 50%;"></div>
            {SUPPORTED_LANGUAGES[st.session_state.selected_language]}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ANALYTICS PAGE
elif st.session_state.current_page == 'analytics':
    # Analytics Header
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 SECURO ANALYTICS</h1>
        <div style="color: #888; text-transform: uppercase; letter-spacing: 2px;">Crime Statistics & Predictions</div>
        <div style="color: #44ff44; margin-top: 5px;">🇰🇳 Royal St. Christopher & Nevis Police Force</div>
        <div style="color: #888; margin-top: 8px; font-size: 0.8rem;">{get_stkitts_date()} | {get_stkitts_time()} AST</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Action Buttons
    st.markdown("### 📊 Quick Analytics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📈 Crime Trends"):
            fig = create_crime_charts("homicide_trend", st.session_state.crime_stats)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if st.button("🔍 Crime Methods"):
            fig = create_crime_charts("crime_methods", st.session_state.crime_stats)
            st.plotly_chart(fig, use_container_width=True)

    with col3:
        if st.button("🏘️ District Analysis"):
            fig = create_crime_charts("district_comparison", st.session_state.crime_stats)
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        if st.button("🎯 Detection Rates"):
            fig = create_crime_charts("quarterly_performance", st.session_state.crime_stats)
            st.plotly_chart(fig, use_container_width=True)

    # Quick Stats Cards
    st.markdown("### 📊 Quick Stats Overview")
    
    stats_data = st.session_state.crime_stats
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(0, 0, 0, 0.8); border: 1px solid rgba(68, 255, 68, 0.3); 
                    border-radius: 15px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; color: #44ff44; font-weight: bold; 
                        text-shadow: 0 0 10px rgba(68, 255, 68, 0.5);">
                {stats_data['current_quarter']['federation']['total_crimes']}
            </div>
            <div style="color: #e0e0e0; font-size: 0.9rem; margin-top: 5px;">
                Total Crimes Q2 2025
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(0, 0, 0, 0.8); border: 1px solid rgba(68, 255, 68, 0.3); 
                    border-radius: 15px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; color: #44ff44; font-weight: bold; 
                        text-shadow: 0 0 10px rgba(68, 255, 68, 0.5);">
                {stats_data['current_quarter']['federation']['detection_rate']}%
            </div>
            <div style="color: #e0e0e0; font-size: 0.9rem; margin-top: 5px;">
                Detection Rate
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: rgba(0, 0, 0, 0.8); border: 1px solid rgba(68, 255, 68, 0.3); 
                    border-radius: 15px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; color: #44ff44; font-weight: bold; 
                        text-shadow: 0 0 10px rgba(68, 255, 68, 0.5);">
                {stats_data['homicides']['yearly_totals'][2024]}
            </div>
            <div style="color: #e0e0e0; font-size: 0.9rem; margin-top: 5px;">
                Homicides 2024
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        drug_crimes = stats_data['current_quarter']['federation']['drugs']['total']
        st.markdown(f"""
        <div style="background: rgba(0, 0, 0, 0.8); border: 1px solid rgba(68, 255, 68, 0.3); 
                    border-radius: 15px; padding: 20px; text-align: center;">
            <div style="font-size: 2rem; color: #44ff44; font-weight: bold; 
                        text-shadow: 0 0 10px rgba(68, 255, 68, 0.5);">
                {drug_crimes}
            </div>
            <div style="color: #e0e0e0; font-size: 0.9rem; margin-top: 5px;">
                Drug Crimes Q2 2025
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Example Questions Section
    st.markdown("### 💡 Analytics Questions")

    example_questions = [
        "📈 What are the homicide trends for the past 10 years?",
        "🔮 Predict crime rates for 2026",
        "🏘️ Which district has the highest crime rate?", 
        "💊 How have drug crimes changed recently?",
        "📊 Show me a chart of crime detection rates",
        "🎯 What's the most common crime method?",
        "📅 Are there seasonal crime patterns?",
        "🚔 How effective is police performance?",
        "⚠️ What are the biggest crime concerns?",
        "📍 Where should police focus resources?"
    ]

    cols = st.columns(2)
    for i, question in enumerate(example_questions):
        col = cols[i % 2]
        with col:
            if st.button(question, key=f"analytics_example_{i}"):
                # Switch to main page and add question
                st.session_state.current_page = 'main'
                
                current_time = get_stkitts_time()
                clean_question = question.split(" ", 1)[1]  # Remove emoji
                
                st.session_state.messages.append({
                    "role": "user",
                    "content": clean_question,
                    "timestamp": current_time
                })
                
                # Generate AI response with analytics data
                with st.spinner("🧠 Analyzing crime data..."):
                    # Create context with crime statistics
                    context = f"""
                    CURRENT STATISTICS (Q2 2025):
                    - Total Federation Crimes: {stats_data['current_quarter']['federation']['total_crimes']}
                    - Detection Rate: {stats_data['current_quarter']['federation']['detection_rate']}%
                    - Murders: {stats_data['current_quarter']['federation']['murder_manslaughter']['total']}
                    - Drug Crimes: {stats_data['current_quarter']['federation']['drugs']['total']}
                    
                    HISTORICAL DATA:
                    - 2024 Homicides: {stats_data['homicides']['yearly_totals'][2024]}
                    - 2023 Homicides: {stats_data['homicides']['yearly_totals'][2023]}
                    """
                    
                    response = get_ai_response(clean_question, context, st.session_state.selected_language)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": current_time
                })
                
                st.rerun()

    # Advanced Analytics Section
    st.markdown("### 🔬 Advanced Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Crime Statistics Summary")
        current_stats = st.session_state.crime_stats['current_quarter']['federation']
        
        # Create summary metrics table
        metrics_data = {
            'Crime Type': ['Murder/Manslaughter', 'Drug Crimes', 'Larcenies', 'Break-ins', 'Bodily Harm'],
            'Q2 2025': [
                current_stats['murder_manslaughter']['total'],
                current_stats['drugs']['total'], 
                current_stats['larcenies']['total'],
                current_stats['break_ins']['total'],
                current_stats['bodily_harm']['total']
            ],
            'Detection Rate': [
                f"{(current_stats['murder_manslaughter']['detected']/current_stats['murder_manslaughter']['total']*100) if current_stats['murder_manslaughter']['total'] > 0 else 0:.1f}%",
                f"{(current_stats['drugs']['detected']/current_stats['drugs']['total']*100):.1f}%",
                f"{(current_stats['larcenies']['detected']/current_stats['larcenies']['total']*100):.1f}%", 
                f"{(current_stats['break_ins']['detected']/current_stats['break_ins']['total']*100):.1f}%",
                f"{(current_stats['bodily_harm']['detected']/current_stats['bodily_harm']['total']*100):.1f}%"
            ]
        }
        
        st.dataframe(pd.DataFrame(metrics_data), use_container_width=True)

    with col2:
        st.markdown("#### 🎯 Key Performance Indicators")
        
        kpi_col1, kpi_col2 = st.columns(2)
        
        with kpi_col1:
            st.metric(
                "Overall Detection Rate",
                f"{current_stats['detection_rate']}%",
                delta=f"+{current_stats['detection_rate'] - 32.9:.1f}% vs St. Kitts"
            )
            
            st.metric(
                "Drug Crime Success", 
                "100%",
                delta="+100% (Perfect detection)"
            )
        
        with kpi_col2:
            homicide_change = ((4 - 16) / 16) * 100  # 2025 vs 2024 H1
            st.metric(
                "Murder Reduction",
                "75%",
                delta=f"{homicide_change:.1f}% vs 2024"
            )
            
            total_crimes_2025 = 574
            total_crimes_2024 = 586
            crime_change = ((total_crimes_2025 - total_crimes_2024) / total_crimes_2024) * 100
            st.metric(
                "Total Crime Change",
                f"{crime_change:.1f}%",
                delta="Downward trend"
            )

# Footer with data sources
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; padding: 20px;">
    📊 Data Source: Royal St. Christopher & Nevis Police Force (RSCNPF)<br>
    📞 Local Intelligence Office: 869-465-2241 Ext. 4238/4239 | liosk@police.kn<br>
    🔄 Last Updated: {st.session_state.crime_stats['last_updated']} | Real-time Analytics Powered by SECURO AI
</div>
""", unsafe_allow_html=True)
