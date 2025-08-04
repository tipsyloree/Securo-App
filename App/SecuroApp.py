import streamlit as st
import time
import datetime
import pytz
import pandas as pd
import numpy as np
import json
import re
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="SECUR0 - AI Crime Investigation Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONSTANTS AND DATA
# ============================================

# St. Kitts timezone
SKN_TIMEZONE = pytz.timezone('America/St_Kitts')

# Emergency Contacts
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

# Crime Hotspots Data
CRIME_HOTSPOTS = {
    "Basseterre Central": {"lat": 17.3026, "lon": -62.7177, "crimes": 45, "risk": "High", "types": ["Larceny", "Drug Crimes", "Assault"]},
    "Cayon": {"lat": 17.3581, "lon": -62.7440, "crimes": 28, "risk": "Medium", "types": ["Break-ins", "Theft"]},
    "Old Road Town": {"lat": 17.3211, "lon": -62.7847, "crimes": 22, "risk": "Medium", "types": ["Drug Crimes", "Vandalism"]},
    "Tabernacle": {"lat": 17.3100, "lon": -62.7200, "crimes": 31, "risk": "High", "types": ["Robbery", "Assault"]},
    "Sandy Point": {"lat": 17.3667, "lon": -62.8500, "crimes": 19, "risk": "Low", "types": ["Petty Theft"]},
    "Dieppe Bay": {"lat": 17.3833, "lon": -62.8167, "crimes": 15, "risk": "Low", "types": ["Vandalism"]},
    "Newton Ground": {"lat": 17.3319, "lon": -62.7269, "crimes": 26, "risk": "Medium", "types": ["Drug Crimes", "Larceny"]},
    "Molineux": {"lat": 17.2978, "lon": -62.7047, "crimes": 33, "risk": "High", "types": ["Armed Robbery", "Assault"]},
    "Charlestown": {"lat": 17.1348, "lon": -62.6217, "crimes": 18, "risk": "Medium", "types": ["Larceny", "Drug Crimes"]},
    "Gingerland": {"lat": 17.1019, "lon": -62.5708, "crimes": 12, "risk": "Low", "types": ["Petty Theft"]},
    "Newcastle": {"lat": 17.1667, "lon": -62.6000, "crimes": 14, "risk": "Low", "types": ["Vandalism", "Theft"]},
    "Cotton Ground": {"lat": 17.1281, "lon": -62.6442, "crimes": 16, "risk": "Medium", "types": ["Break-ins", "Larceny"]},
    "Ramsbury": {"lat": 17.1500, "lon": -62.6167, "crimes": 21, "risk": "Medium", "types": ["Drug Crimes", "Assault"]},
}

# MacroTrends Data
MACROTRENDS_DATA = {
    "homicide_rates_per_100k": {
        "2020": 20.99,
        "2019": 25.15,
        "2018": 48.16,
        "2017": 48.14,
        "2016": 42.50,
        "2015": 38.20,
        "2014": 35.80,
        "2013": 42.10,
        "2012": 33.60,
        "2011": 67.60
    },
    "comparative_context": {
        "global_average_firearm_homicides": 42.0,
        "skn_firearm_homicides_2010": 85.0,
        "skn_firearm_homicides_2003": 63.6,
        "basseterre_2011_rate": 131.6,
        "world_ranking_2012": 8,
        "world_ranking_2005_2014": 7
    },
    "recent_trends": {
        "2024_total_crimes": 1146,
        "2023_total_crimes": 1280,
        "2022_total_crimes": 1360,
        "2024_homicides": 28,
        "2023_homicides": 31,
        "first_quarter_2025": "No homicides (first time in 23 years)"
    }
}

# Historical Crime Database
HISTORICAL_CRIME_DATABASE = {
    "2025_Q2": {
        "period": "Q2 2025 (Apr-Jun)",
        "total_crimes": 292,
        "detection_rate": 38.7,
        "federation": {
            "murder_manslaughter": {"total": 4, "detected": 2, "rate": 50.0},
            "attempted_murder": {"total": 4, "detected": 0, "rate": 0.0},
            "bodily_harm": {"total": 33, "detected": 19, "rate": 57.6},
            "sex_crimes": {"total": 7, "detected": 1, "rate": 14.3},
            "break_ins": {"total": 26, "detected": 7, "rate": 26.9},
            "larcenies": {"total": 92, "detected": 21, "rate": 22.8},
            "robberies": {"total": 8, "detected": 1, "rate": 12.5},
            "firearms_offences": {"total": 5, "detected": 5, "rate": 100.0},
            "drug_crimes": {"total": 31, "detected": 31, "rate": 100.0},
            "malicious_damage": {"total": 59, "detected": 17, "rate": 28.8},
        },
        "st_kitts": {"crimes": 207, "detection_rate": 32.9},
        "nevis": {"crimes": 85, "detection_rate": 52.9}
    },
    "2024_ANNUAL": {
        "period": "2024 Full Year (Jan-Dec)",
        "total_crimes": 1146,
        "detection_rate": 41.8,
        "federation": {
            "murder_manslaughter": {"total": 28, "detected": 16, "rate": 57.0},
            "shooting_intent": {"total": 6, "detected": 0, "rate": 0.0},
            "attempted_murder": {"total": 18, "detected": 5, "rate": 28.0},
            "bodily_harm": {"total": 145, "detected": 115, "rate": 79.0},
            "sex_crimes": {"total": 72, "detected": 33, "rate": 46.0},
            "break_ins": {"total": 134, "detected": 36, "rate": 27.0},
            "larcenies": {"total": 395, "detected": 119, "rate": 30.0},
            "robberies": {"total": 42, "detected": 5, "rate": 12.0},
            "firearms_offences": {"total": 21, "detected": 19, "rate": 90.0},
            "drug_crimes": {"total": 20, "detected": 20, "rate": 100.0},
            "malicious_damage": {"total": 191, "detected": 72, "rate": 38.0},
            "other_crimes": {"total": 74, "detected": 39, "rate": 53.0}
        },
        "st_kitts": {"crimes": 965, "detection_rate": 40.7},
        "nevis": {"crimes": 181, "detection_rate": 47.5}
    },
    "2023_ANNUAL": {
        "period": "2023 Full Year (Jan-Dec)",
        "total_crimes": 1280,
        "detection_rate": 44.6,
        "federation": {
            "murder_manslaughter": {"total": 31, "detected": 11, "rate": 35.0},
            "shooting_intent": {"total": 6, "detected": 3, "rate": 50.0},
            "woundings_firearm": {"total": 24, "detected": 19, "rate": 79.0},
            "attempted_murder": {"total": 9, "detected": 2, "rate": 22.0},
            "bodily_harm": {"total": 161, "detected": 126, "rate": 78.0},
            "sex_crimes": {"total": 68, "detected": 38, "rate": 56.0},
            "break_ins": {"total": 136, "detected": 32, "rate": 24.0},
            "larcenies": {"total": 446, "detected": 118, "rate": 26.0},
            "robberies": {"total": 39, "detected": 19, "rate": 49.0},
            "firearms_offences": {"total": 34, "detected": 32, "rate": 94.0},
            "drug_crimes": {"total": 21, "detected": 21, "rate": 100.0},
            "malicious_damage": {"total": 274, "detected": 131, "rate": 48.0},
            "other_crimes": {"total": 31, "detected": 19, "rate": 61.0}
        },
        "st_kitts": {"crimes": 1093, "detection_rate": 44.8},
        "nevis": {"crimes": 187, "detection_rate": 43.3}
    },
    "2022_ANNUAL": {
        "period": "2022 Full Year (Jan-Dec)",
        "total_crimes": 1360,
        "detection_rate": 31.4,
        "federation": {
            "murder_manslaughter": {"total": 11, "detected": 7, "rate": 64.0},
            "shooting_intent": {"total": 3, "detected": 1, "rate": 33.0},
            "attempted_murder": {"total": 6, "detected": 1, "rate": 17.0},
            "bodily_harm": {"total": 172, "detected": 116, "rate": 67.0},
            "sex_crimes": {"total": 58, "detected": 10, "rate": 17.0},
            "break_ins": {"total": 183, "detected": 28, "rate": 15.0},
            "larcenies": {"total": 525, "detected": 114, "rate": 22.0},
            "robberies": {"total": 38, "detected": 7, "rate": 18.0},
            "firearms_offences": {"total": 17, "detected": 17, "rate": 100.0},
            "drug_crimes": {"total": 26, "detected": 26, "rate": 100.0},
            "malicious_damage": {"total": 268, "detected": 71, "rate": 26.0},
            "other_crimes": {"total": 53, "detected": 29, "rate": 55.0}
        },
        "st_kitts": {"crimes": 1183, "detection_rate": 32.1},
        "nevis": {"crimes": 177, "detection_rate": 26.6}
    }
}

# ============================================
# INITIALIZE SESSION STATE
# ============================================

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'chat_counter' not in st.session_state:
    st.session_state.chat_counter = 1

if 'statistical_database' not in st.session_state:
    st.session_state.statistical_database = {}

if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = HISTORICAL_CRIME_DATABASE

# Initialize Google AI
try:
    # IMPORTANT: Replace with your actual API key or use Streamlit secrets
    GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.model = model
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.model = None

# ============================================
# UTILITY FUNCTIONS
# ============================================

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

# ============================================
# CHAT MANAGEMENT FUNCTIONS
# ============================================

def create_new_chat():
    """Create a new chat session"""
    chat_id = f"chat_{st.session_state.chat_counter}_{int(time.time())}"
    st.session_state.chat_sessions[chat_id] = {
        'id': chat_id,
        'name': f"Chat {st.session_state.chat_counter}",
        'messages': [],
        'created_at': get_stkitts_time(),
        'last_activity': get_stkitts_time()
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.chat_counter += 1
    
    # Add welcome message
    welcome_msg = {
        "role": "assistant",
        "content": "🔒 Enhanced SECURO AI System Online!\n\nI now have access to comprehensive St. Kitts & Nevis crime statistics, international comparison data from MacroTrends, and can maintain conversation context. Ask me about:\n\n• Local crime trends and detection rates\n• International comparisons and global context\n• Historical data analysis with charts\n• Specific incidents or general questions\n\nHow can I assist you today?",
        "timestamp": get_stkitts_time()
    }
    st.session_state.chat_sessions[chat_id]['messages'].append(welcome_msg)
    
    return chat_id

def get_current_chat():
    """Get current chat session"""
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        return st.session_state.chat_sessions[st.session_state.current_chat_id]
    else:
        create_new_chat()
        return st.session_state.chat_sessions[st.session_state.current_chat_id]

def add_message_to_chat(role, content):
    """Add message to current chat"""
    current_chat = get_current_chat()
    current_chat['messages'].append({
        "role": role,
        "content": content,
        "timestamp": get_stkitts_time()
    })
    current_chat['last_activity'] = get_stkitts_time()
    
    # Update chat name based on first user message
    if role == "user" and len(current_chat['messages']) <= 2:
        chat_name = content[:30] + "..." if len(content) > 30 else content
        current_chat['name'] = chat_name

def switch_to_chat(chat_id):
    """Switch to a specific chat session"""
    if chat_id in st.session_state.chat_sessions:
        st.session_state.current_chat_id = chat_id

# ============================================
# DATA PROCESSING FUNCTIONS
# ============================================

def fetch_and_process_statistics():
    """Fetch and process statistics"""
    if st.session_state.statistical_database:
        return st.session_state.statistical_database
    
    st.session_state.statistical_database = HISTORICAL_CRIME_DATABASE.copy()
    st.session_state.statistical_database.update({
        "macrotrends_data": MACROTRENDS_DATA,
        "recent_trends": {
            "murder_trend": "75% decrease from 2024 to 2025 H1",
            "drug_crimes_trend": "463% increase in drug crimes 2024-2025",
            "detection_improvement": "Detection rates vary by crime type",
            "larceny_concern": "Larcenies remain highest volume crime"
        }
    })
    
    return st.session_state.statistical_database

# ============================================
# MAP CREATION
# ============================================

def create_crime_hotspot_map():
    """Create an interactive crime hotspot map"""
    center_lat = 17.25
    center_lon = -62.7
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap',
        attr='Crime Hotspot Analysis - SECURO'
    )
    
    # Add satellite layer
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    risk_colors = {
        'High': '#ff4444',
        'Medium': '#ffaa44', 
        'Low': '#44ff44'
    }
    
    for location, data in CRIME_HOTSPOTS.items():
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="color: {risk_colors[data['risk']]}; margin: 0; text-align: center;">
                🚨 {location}
            </h4>
            <hr style="margin: 8px 0;">
            <p style="margin: 4px 0;"><strong>📊 Total Crimes:</strong> {data['crimes']}</p>
            <p style="margin: 4px 0;"><strong>⚠️ Risk Level:</strong> 
               <span style="color: {risk_colors[data['risk']]}; font-weight: bold;">{data['risk']}</span>
            </p>
            <p style="margin: 4px 0;"><strong>🔍 Common Types:</strong></p>
            <ul style="margin: 4px 0; padding-left: 20px;">
                {''.join([f'<li>{crime_type}</li>' for crime_type in data['types']])}
            </ul>
            <small style="color: #666;">📍 Lat: {data['lat']:.4f}, Lon: {data['lon']:.4f}</small>
        </div>
        """
        
        marker_size = max(10, min(30, data['crimes'] * 0.8))
        
        folium.CircleMarker(
            location=[data['lat'], data['lon']],
            radius=marker_size,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{location}: {data['crimes']} crimes ({data['risk']} risk)",
            color='black',
            fillColor=risk_colors[data['risk']],
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # Add legend
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 140px; 
                background-color: rgba(0, 0, 0, 0.8); 
                border: 2px solid rgba(68, 255, 68, 0.5);
                border-radius: 10px; z-index:9999; 
                font-size: 12px; font-family: Arial;
                padding: 10px; color: white;">
    <h4 style="margin: 0 0 10px 0; color: #44ff44;">🗺️ Crime Risk Legend</h4>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['High']};">●</span> High Risk (25+ crimes)
    </div>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['Medium']};">●</span> Medium Risk (15-24 crimes)  
    </div>
    <div style="margin: 5px 0;">
        <span style="color: {risk_colors['Low']};">●</span> Low Risk (<15 crimes)
    </div>
    <small style="color: #888;">Marker size = Crime frequency</small>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    folium.LayerControl().add_to(m)
    
    return m

# ============================================
# CHART CREATION FUNCTIONS
# ============================================

def create_macrotrends_comparison_charts(chart_type="homicide_trends"):
    """Create charts using MacroTrends data"""
    
    if chart_type == "homicide_trends":
        years = list(MACROTRENDS_DATA["homicide_rates_per_100k"].keys())
        rates = list(MACROTRENDS_DATA["homicide_rates_per_100k"].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=rates,
            mode='lines+markers',
            name='Homicide Rate per 100K',
            line=dict(color='#ff4444', width=3),
            marker=dict(size=10, color='#ff4444')
        ))
        
        global_avg = MACROTRENDS_DATA["comparative_context"]["global_average_firearm_homicides"]
        fig.add_hline(y=global_avg, line_dash="dash", line_color="#888888",
                     annotation_text=f"Global Average: {global_avg}%")
        
        fig.update_layout(
            title="St. Kitts & Nevis Homicide Rate Trends (MacroTrends Data)",
            xaxis_title="Year",
            yaxis_title="Homicides per 100,000 Population",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "recent_crime_totals":
        years = ["2022", "2023", "2024"]
        crimes = [
            MACROTRENDS_DATA["recent_trends"]["2022_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2023_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2024_total_crimes"]
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=years, y=crimes,
            marker_color='#44ff44',
            text=[f"{crime:,}" for crime in crimes],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Total Crime Trends 2022-2024 (RSCNPF Data)",
            xaxis_title="Year",
            yaxis_title="Total Crimes",
            template="plotly_dark",
            height=500
        )
        
        return fig

# ============================================
# AI RESPONSE GENERATION
# ============================================

def generate_enhanced_smart_response(user_input, conversation_history=None):
    """Generate AI responses with statistical knowledge"""
    
    if not st.session_state.get('ai_enabled', False):
        return "🔧 AI system offline. Please check your API key configuration.", None
    
    try:
        model = st.session_state.model
        stats_data = fetch_and_process_statistics()
        
        # Check if user wants a chart
        chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show me', 'display', 'trends']
        wants_chart = any(keyword in user_input.lower() for keyword in chart_keywords)
        chart_to_show = None
        
        if wants_chart:
            if 'homicide' in user_input.lower() or 'murder' in user_input.lower():
                chart_to_show = "homicide"
            elif 'recent' in user_input.lower() or 'total' in user_input.lower():
                chart_to_show = "recent"
            else:
                chart_to_show = "homicide"
        
        # Build conversation context
        context = ""
        if conversation_history and len(conversation_history) > 1:
            recent_messages = conversation_history[-4:]
            context = "Recent conversation context:\n"
            for msg in recent_messages:
                content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                context += f"{msg['role']}: {content_preview}\n"
            context += "\n"
        
        # Generate prompt
        prompt = f"""
        You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force with access to comprehensive crime statistics.
        
        {context}User query: "{user_input}"
        
        **Available Statistical Data:**
        {json.dumps(stats_data, indent=2)}
        
        **Response Guidelines:**
        - Use specific numbers and percentages from the data above
        - Reference time periods when relevant
        - Include comparisons and trends when available
        - Maintain professional law enforcement communication
        - If a chart is requested, acknowledge it
        
        Current time: {get_stkitts_time()} AST
        Current date: {get_stkitts_date()}
        
        Provide a helpful, data-driven response.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip(), chart_to_show
        
    except Exception as e:
        return f"🚨 AI analysis error: {str(e)}\n\nPlease try rephrasing your question.", None

# ============================================
# CUSTOM CSS
# ============================================

st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://remixicon.com/font/remixicon.css');
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app styling */
    .stApp {
        background-color: #0a0f1b;
        font-family: 'Inter', sans-serif;
        color: #e0e0e0;
    }
    
    /* Header styling */
    .main-header {
        background-color: #0d1117;
        border-bottom: 2px solid rgba(57, 255, 20, 0.5);
        padding: 1rem 2rem;
        margin: -1rem -1rem 1rem -1rem;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .header-title {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .header-title h1 {
        color: #39ff14;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.1em;
    }
    
    .header-subtitle {
        color: #8b949e;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .header-info {
        text-align: right;
        color: #8b949e;
        font-size: 0.875rem;
    }
    
    /* Navigation buttons */
    .stButton > button {
        background-color: transparent !important;
        color: #e0e0e0 !important;
        border: none !important;
        border-radius: 2rem !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: rgba(57, 255, 20, 0.1) !important;
        color: #fff !important;
    }
    
    /* Panel styling */
    .panel {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Feature cards */
    .feature-card {
        background-color: #0d1117;
        border: 2px solid #30363d;
        border-radius: 0.5rem;
        padding: 1.5rem;
        text-align: left;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .feature-card:hover {
        border-color: rgba(57, 255, 20, 0.5);
        transform: translateY(-2px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        color: #39ff14;
        margin-bottom: 1rem;
    }
    
    .feature-card h3 {
        color: #39ff14;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .feature-card p {
        color: #8b949e;
        font-size: 0.875rem;
        line-height: 1.5;
    }
    
    /* Statistics cards */
    .stat-card {
        background-color: rgba(13, 17, 23, 0.5);
        border: 1px solid #30363d;
        border-radius: 0.5rem;
        padding: 1.25rem;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #39ff14;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Chat messages */
    .message {
        margin-bottom: 1rem;
        display: flex;
        gap: 1rem;
    }
    
    .message-user {
        flex-direction: row-reverse;
    }
    
    .message-content {
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
    }
    
    .message-user .message-content {
        background-color: rgba(59, 130, 246, 0.2);
        color: #93bbfe;
    }
    
    .message-assistant .message-content {
        background-color: rgba(30, 41, 59, 0.5);
        color: #e0e0e0;
    }
    
    .message-timestamp {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 0.25rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: #0a0f1b !important;
        border: 1px solid #30363d !important;
        border-radius: 0.5rem !important;
        color: #e0e0e0 !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* Footer */
    .footer {
        background-color: #000;
        border-top: 2px solid #000;
        margin-top: 2rem;
        padding: 1rem;
        text-align: center;
    }
    
    .footer-content {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1rem;
        color: #6b7280;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# UI COMPONENTS
# ============================================

def render_header():
    """Render the main header"""
    current_time = get_stkitts_time()
    current_date = get_stkitts_date()
    
    st.markdown(f"""
    <div class="main-header">
        <div class="header-content">
            <div class="header-title">
                <i class="ri-shield-check-line" style="font-size: 2.5rem; color: #39ff14;"></i>
                <div>
                    <h1>SECUR0</h1>
                    <div class="header-subtitle">ENHANCED AI ASSISTANT & CRIME INTELLIGENCE SYSTEM</div>
                </div>
            </div>
            <div class="header-info">
                <div><i class="ri-flag-line" style="color: #39ff14;"></i> Royal St. Christopher & Nevis Police Force</div>
                <div><i class="ri-time-line" style="color: #39ff14;"></i> {current_date} | {current_time} (AST)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    """Render navigation buttons"""
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    nav_items = [
        ("home", "🏠 Home", col1),
        ("about", "ℹ️ About SECURO", col2),
        ("hotspots", "📍 Crime Hotspots", col3),
        ("analytics", "📊 Statistics & Analytics", col4),
        ("emergency", "🚨 Emergency", col5),
        ("ai_assistant", "🤖 AI Assistant", col6)
    ]
    
    for page_id, label, col in nav_items:
        with col:
            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()

# ============================================
# PAGE RENDERERS
# ============================================

def render_home_page():
    """Render the home page"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #fff; font-size: 2rem; margin-bottom: 1rem;">Welcome to Enhanced SECURO</h2>
        <p style="color: #8b949e; font-size: 1.125rem;">
            Your comprehensive AI assistant with statistical knowledge, conversation memory, 
            and crime analysis capabilities for St. Kitts & Nevis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>Enhanced AI with Memory</h3>
            <p>Conversation memory, statistical knowledge integration, and context-aware responses powered by real crime data.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card" style="margin-top: 1rem;">
            <div class="feature-icon">💾</div>
            <h3>Conversation Management</h3>
            <p>Multiple chat sessions with memory, chat history, and context preservation across conversations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Integrated Statistics</h3>
            <p>Real-time access to local crime statistics PLUS MacroTrends international comparison data.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card" style="margin-top: 1rem;">
            <div class="feature-icon">📈</div>
            <h3>Statistical Analysis</h3>
            <p>Advanced crime data analysis with detection rates, trend identification, and actionable insights.</p>
        </div>
        """, unsafe_allow_html=True)

def render_about_page():
    """Render the about page"""
    st.markdown("""
    <div class="panel">
        <h1 style="color: #fff; text-align: center; margin-bottom: 2rem;">About Enhanced SECURO</h1>
        <p style="text-align: center; color: #8b949e; font-size: 1.125rem; margin-bottom: 2rem;">
            SECURO is an enhanced comprehensive crime analysis system with statistical integration, 
            conversation memory, and advanced AI capabilities built specifically for the 
            Royal St. Christopher and Nevis Police Force.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="panel">
            <h2 style="color: #39ff14;">🧠 Enhanced AI Capabilities</h2>
            <ul style="color: #e0e0e0; line-height: 1.8;">
                <li>Conversation Memory - Maintains context across entire chat sessions</li>
                <li>Statistical Knowledge Integration - Real access to crime data</li>
                <li>Context-Aware Responses - Understands conversation flow</li>
                <li>Multi-Chat Management - Multiple conversation sessions</li>
                <li>Statistical Query Processing - Answers with actual data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="panel">
            <h2 style="color: #39ff14;">📊 Statistical Database</h2>
            <ul style="color: #e0e0e0; line-height: 1.8;">
                <li>Real PDF Integration - Official police reports</li>
                <li>2022-2025 Crime Data - Complete statistics</li>
                <li>Detection Rate Analysis - Performance metrics</li>
                <li>Geographical Breakdown - St. Kitts vs. Nevis</li>
                <li>MacroTrends Integration - Global comparisons</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_hotspots_page():
    """Render the crime hotspots page"""
    st.markdown("""
    <h1 style="color: #fff;">📍 Crime Hotspot Map - St. Kitts & Nevis</h1>
    """, unsafe_allow_html=True)
    
    # Map container
    with st.container():
        try:
            crime_map = create_crime_hotspot_map()
            map_data = st_folium(
                crime_map,
                width="100%",
                height=600,
                returned_objects=["last_object_clicked_tooltip"],
                key="crime_hotspot_map"
            )
            
            if map_data['last_object_clicked_tooltip']:
                st.info(f"📍 **Last Clicked Location:** {map_data['last_object_clicked_tooltip']}")
        except Exception as e:
            st.error(f"Map loading error: {str(e)}")
    
    # Summary cards
    st.markdown('<h2 style="color: #fff; margin-top: 2rem;">📍 Hotspot Analysis Summary</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-card" style="border-left: 4px solid #ef4444;">
            <h4 style="color: #ef4444;">High Risk Areas (3)</h4>
            <p style="color: #8b949e;">Basseterre, Molineux, Tabernacle</p>
            <div class="stat-value" style="color: #ef4444;">109</div>
            <div class="stat-label">Total Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card" style="border-left: 4px solid #f59e0b;">
            <h4 style="color: #f59e0b;">Medium Risk Areas (6)</h4>
            <p style="color: #8b949e;">Cayon, Newton Ground, etc.</p>
            <div class="stat-value" style="color: #f59e0b;">133</div>
            <div class="stat-label">Total Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card" style="border-left: 4px solid #10b981;">
            <h4 style="color: #10b981;">Low Risk Areas (4)</h4>
            <p style="color: #8b949e;">Sandy Point, Dieppe Bay, etc.</p>
            <div class="stat-value" style="color: #10b981;">60</div>
            <div class="stat-label">Total Crimes</div>
        </div>
        """, unsafe_allow_html=True)

def render_analytics_page():
    """Render the analytics page"""
    st.markdown('<h1 style="color: #fff;">📊 Crime Statistics & Analytics</h1>', unsafe_allow_html=True)
    
    # Quick analytics buttons
    if st.button("📈 Show Homicide Trends", key="show_homicide"):
        fig = create_macrotrends_comparison_charts("homicide_trends")
        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("📊 Show Recent Crime Totals", key="show_recent"):
        fig = create_macrotrends_comparison_charts("recent_crime_totals")
        st.plotly_chart(fig, use_container_width=True)
    
    # Crime statistics summary
    st.markdown('<h2 style="color: #fff; margin-top: 2rem;">📊 Q2 2025 Crime Summary</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">292</div>
            <div class="stat-label">Total Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">38.7%</div>
            <div class="stat-label">Detection Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">207</div>
            <div class="stat-label">St. Kitts Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">85</div>
            <div class="stat-label">Nevis Crimes</div>
        </div>
        """, unsafe_allow_html=True)

def render_emergency_page():
    """Render the emergency page"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <i class="ri-alarm-warning-fill" style="font-size: 3rem; color: #ef4444;"></i>
        <h1 style="color: #fff; margin-top: 0.5rem;">Emergency Contacts</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency contacts grid
    emergency_data = [
        ("🚔", "Police Emergency", "911", "For immediate police assistance"),
        ("🏢", "Police Headquarters", "465-2241", "RSCNPF - Local Intelligence: Ext. 4238/4239"),
        ("🏥", "Medical Emergency", "465-2551", "Hospital services and medical emergencies"),
        ("🔥", "Fire Department", "465-2515", "Fire emergencies - Alt: 465-7167"),
        ("🚢", "Coast Guard", "465-8384", "Maritime emergencies - Alt: 466-9280"),
        ("🌡️", "Met Office", "465-2749", "Weather emergencies and warnings"),
        ("➕", "Red Cross", "465-2584", "Disaster relief and emergency aid"),
        ("⚡", "NEMA", "466-5100", "National Emergency Management Agency")
    ]
    
    cols = st.columns(4)
    for i, (icon, title, number, desc) in enumerate(emergency_data):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="panel" style="border: 2px solid rgba(239, 68, 68, 0.5); text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <h3 style="color: #ef4444;">{title}</h3>
                <div style="font-size: 1.875rem; font-weight: 700; color: #39ff14;">{number}</div>
                <p style="color: #8b949e; font-size: 0.875rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

def render_ai_assistant_page():
    """Render the AI assistant page"""
    if not st.session_state.chat_sessions:
        create_new_chat()
    
    current_chat = get_current_chat()
    
    # Header
    st.markdown("""
    <div class="panel" style="display: flex; align-items: center; gap: 1rem;">
        <i class="ri-robot-2-line" style="font-size: 4rem; color: #39ff14;"></i>
        <div>
            <h1 style="color: #fff; margin: 0;">SECUR0</h1>
            <p style="color: #8b949e; margin: 0;">Enhanced AI Assistant & Crime Intelligence System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ New Chat", use_container_width=True):
            create_new_chat()
            st.rerun()
    
    with col2:
        if st.button("📚 Chat History", use_container_width=True):
            st.session_state.show_history = not st.session_state.get('show_history', False)
            st.rerun()
    
    with col3:
        st.markdown(f"<p style='color: #8b949e;'>Current: {current_chat['name']}</p>", unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"<p style='color: #8b949e;'>Chats: {len(st.session_state.chat_sessions)}</p>", unsafe_allow_html=True)
    
    # Chat history
    if st.session_state.get('show_history', False):
        st.markdown('<h3 style="color: #39ff14;">Chat History</h3>', unsafe_allow_html=True)
        for chat_id, chat_data in st.session_state.chat_sessions.items():
            if st.button(f"💬 {chat_data['name']}", key=f"hist_{chat_id}", use_container_width=True):
                switch_to_chat(chat_id)
                st.session_state.show_history = False
                st.rerun()
    
    # Display messages
    chat_container = st.container()
    with chat_container:
        for msg in current_chat['messages']:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="message message-user">
                    <div class="message-content">
                        {msg['content']}
                        <div class="message-timestamp">You • {msg.get('timestamp', '')} AST</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message message-assistant">
                    <div class="message-content">
                        {msg['content']}
                        <div class="message-timestamp">SECUR0 • {msg.get('timestamp', '')} AST</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Message",
            placeholder="Ask about crime statistics, trends, or request charts...",
            label_visibility="collapsed"
        )
        
        submitted = st.form_submit_button("Send", use_container_width=True)
        
        if submitted and user_input:
            add_message_to_chat("user", user_input)
            
            with st.spinner("SECUR0 is typing..."):
                response, chart_type = generate_enhanced_smart_response(
                    user_input,
                    conversation_history=current_chat['messages']
                )
            
            add_message_to_chat("assistant", response)
            
            # Display chart if requested
            if chart_type:
                if chart_type == "homicide":
                    fig = create_macrotrends_comparison_charts("homicide_trends")
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == "recent":
                    fig = create_macrotrends_comparison_charts("recent_crime_totals")
                    st.plotly_chart(fig, use_container_width=True)
            
            st.rerun()

def render_footer():
    """Render the footer"""
    st.markdown(f"""
    <div class="footer">
        <div class="footer-content">
            <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 2rem;">
                <span><span style="color: #39ff14;">●</span> Enhanced AI Active</span>
                <span><span style="color: #39ff14;">●</span> MacroTrends Integration: Active</span>
                <span><span style="color: #39ff14;">●</span> Memory: Enabled</span>
                <span><span style="color: #39ff14;">●</span> Sessions: {len(st.session_state.chat_sessions)}</span>
                <span><span style="color: #39ff14;">●</span> {get_stkitts_time()} AST</span>
            </div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #30363d;">
                <p><i class="ri-database-2-line" style="color: #39ff14;"></i> Data Source: Royal St. Christopher & Nevis Police Force</p>
                <p><i class="ri-building-line" style="color: #39ff14;"></i> Local Intelligence: 869-465-2241 Ext. 4238/4239</p>
                <p><i class="ri-mail-line" style="color: #39ff14;"></i> lio@police.kn</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN APP
# ============================================

def main():
    # Initialize statistics
    if 'initialized' not in st.session_state:
        fetch_and_process_statistics()
        st.session_state.initialized = True
    
    # Render header
    render_header()
    
    # Render navigation
    render_navigation()
    
    # Render current page
    if st.session_state.current_page == 'home':
        render_home_page()
    elif st.session_state.current_page == 'about':
        render_about_page()
    elif st.session_state.current_page == 'hotspots':
        render_hotspots_page()
    elif st.session_state.current_page == 'analytics':
        render_analytics_page()
    elif st.session_state.current_page == 'emergency':
        render_emergency_page()
    elif st.session_state.current_page == 'ai_assistant':
        render_ai_assistant_page()
    
    # Render footer
    render_footer()
    
    # Emergency button
    if st.session_state.current_page != 'emergency':
        if st.button("🚨", key="emergency_float", help="Emergency Contacts"):
            st.session_state.current_page = 'emergency'
            st.rerun()

# Run the app
if __name__ == "__main__":
    main()
