import streamlit as st
import time
import datetime
import pytz
import random
import pandas as pd
import os
import google.generativeai as genai
import re

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

# Enhanced System Prompt with multilingual support
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
IMPORTANT: The user has selected {SUPPORTED_LANGUAGES.get(language, language)} as their preferred language. 
Please respond primarily in {SUPPORTED_LANGUAGES.get(language, language)}, but you may include English translations for technical terms when helpful for clarity.
If you're not completely fluent in the requested language, do your best and indicate that you're providing assistance in that language.
"""
        return base_prompt + language_instruction
    
    return base_prompt

# Initialize the AI model
try:
    GOOGLE_API_KEY = "AIzaSyAK-4Xklul9WNoiWnSrpzPkn5C-Dbny8B4"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Ready (Direct API Key)"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration - With sidebar enabled
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="https://i.postimg.cc/V69LH7F4/Logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling WITH sidebar - GREEN THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
   
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom sidebar styling - GREEN theme */
    .css-1d391kg, .css-1cypcdb, .css-k1vhr6, .css-1lcbmhc, .css-17eq0hr,
    section[data-testid="stSidebar"], .stSidebar, [data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a2e1a 50%, #163e16 100%) !important;
        border-right: 2px solid rgba(68, 255, 68, 0.5) !important;
    }
    
    /* Sidebar toggle button styling */
    .sidebar-toggle {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 999;
        background: linear-gradient(135deg, #44ff44, #33cc33) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        color: white !important;
        font-size: 1.2rem !important;
        cursor: pointer !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.4) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Control panel header with green theme */
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
    
    .control-panel-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(68, 255, 68, 0.1), transparent);
        animation: scan 4s infinite;
    }
    
    .control-panel-header h2 {
        color: #44ff44; 
        font-family: JetBrains Mono, monospace; 
        text-shadow: 0 0 15px rgba(68, 255, 68, 0.7);
        position: relative;
        z-index: 2;
        margin: 0;
    }
    
    .control-panel-header p {
        color: #66ff66; 
        font-size: 0.8rem; 
        font-family: JetBrains Mono, monospace; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        position: relative;
        z-index: 2;
        margin: 5px 0 0 0;
    }
    
    /* Sidebar content styling */
    .css-1d391kg .css-1v0mbdj, .stSidebar .element-container {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Sidebar headers */
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
    
    /* Sidebar selectbox styling */
    .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(68, 255, 68, 0.4) !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #44ff44 !important;
        box-shadow: 0 0 15px rgba(68, 255, 68, 0.3) !important;
    }
    
    /* Emergency contact styling */
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
    
    .emergency-title {
        color: #44ff44 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 4px !important;
    }
    
    .emergency-number {
        color: #e0e0e0 !important;
        font-size: 0.8rem !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    .emergency-link {
        color: #66ff66 !important;
        text-decoration: none !important;
        font-weight: 500 !important;
    }
    
    .emergency-link:hover {
        color: #44ff44 !important;
        text-shadow: 0 0 5px rgba(68, 255, 68, 0.5) !important;
    }
    
    /* Map container styling */
    .map-container {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        margin-top: 10px !important;
    }
    
    /* Sidebar text styling */
    .stSidebar .stMarkdown p, .stSidebar .stMarkdown div {
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
   
    /* Main app background - Green theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a2e1a 50%, #163e16 100%);
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Particles animation - Green particles */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    }

    .particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(68, 255, 68, 0.3);
        border-radius: 50%;
        animation: float 10s infinite linear;
    }

    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
    }
   
    /* Header styling - Green theme */
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

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(68, 255, 68, 0.1), transparent);
        animation: scan 3s infinite;
    }

    @keyframes scan {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
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

    .main-header .tagline {
        font-size: 1rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 2px;
        position: relative;
        z-index: 2;
        font-family: 'JetBrains Mono', monospace;
    }

    .main-header .location {
        font-size: 0.9rem;
        color: #44ff44;
        margin-top: 5px;
        position: relative;
        z-index: 2;
        font-family: 'JetBrains Mono', monospace;
    }

    .main-header .datetime {
        font-size: 0.8rem;
        color: #888;
        margin-top: 8px;
        position: relative;
        z-index: 2;
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Chat styling - Green theme */
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

    /* Override any conflicting Streamlit styles */
    .bot-message .message-content * {
        color: #e0e0e0 !important;
    }

    .user-message .message-content * {
        color: #ffffff !important;
    }
   
    /* Status bar - Green theme */
    .status-bar {
        background: rgba(0, 0, 0, 0.8);
        padding: 10px 20px;
        border-radius: 25px;
        margin-top: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(68, 255, 68, 0.2);
        font-family: 'JetBrains Mono', monospace;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.8rem;
        color: #e0e0e0;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    .status-online { background: #44ff44; }
    .status-processing { background: #33cc33; }
    .status-evidence { background: #66ff66; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
   
    /* Input styling - Green theme */
    .stTextInput input, .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        border-radius: 25px !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextInput input:focus, .stSelectbox > div > div:focus {
        border-color: #44ff44 !important;
        box-shadow: 0 0 20px rgba(68, 255, 68, 0.2) !important;
    }
   
    /* Button styling - Green theme */
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
   
    /* Section headers - Green theme */
    .section-header {
        color: #44ff44;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }

    .file-status {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(68, 255, 68, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        font-family: 'JetBrains Mono', monospace;
    }

    .file-found {
        color: #4ade80;
    }

    .file-missing {
        color: #44ff44;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR IMPLEMENTATION
with st.sidebar:
    # SECURO Logo/Header with GREEN theme
    st.markdown("""
    <div class="control-panel-header">
        <h2>🚔 SECURO</h2>
        <p>Control Panel</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Emergency Contacts Section
    st.markdown('<div class="sidebar-header">🚨 Emergency Contacts</div>', unsafe_allow_html=True)
    
    for service, number in EMERGENCY_CONTACTS.items():
        # Clean the number for tel: link (remove extra numbers and formatting)
        clean_number = number.split(' / ')[0].replace('-', '').replace(' ', '')
        tel_link = f"tel:+1869{clean_number}" if service != "Emergency" else "tel:911"
        
        st.markdown(f"""
        <div class="emergency-contact">
            <div class="emergency-title">{service}</div>
            <div class="emergency-number">
                <a href="{tel_link}" class="emergency-link">📞 {number}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Crime Hotspots Map Section - INTERACTIVE
    st.markdown('<div class="sidebar-header">🗺️ Crime Hotspots Map</div>', unsafe_allow_html=True)
    
    # Interactive Google Maps with crime hotspots for St. Kitts & Nevis
    st.markdown("""
    <div class="map-container">
        <iframe 
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d61440.47289881779!2d-62.759765!3d17.302606!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8c0498a6c7d7ac0d%3A0x40b9ba03c4b0b0!2sSt%20Kitts%20and%20Nevis!5e0!3m2!1sen!2sus!4v1640995200000!5m2!1sen!2sus&output=embed" 
            width="100%" 
            height="250" 
            style="border:1px solid rgba(68, 255, 68, 0.3); border-radius: 8px;" 
            allowfullscreen="" 
            loading="lazy" 
            referrerpolicy="no-referrer-when-downgrade"
            title="St. Kitts & Nevis Crime Hotspots Map">
        </iframe>
        <div style="margin-top: 8px; font-size: 0.7rem; color: #66ff66; font-family: 'JetBrains Mono', monospace;">
            🔴 Basseterre Downtown - High Risk<br>
            🟠 Industrial Areas - Medium Risk<br>
            🟡 Residential Areas - Low Risk<br>
            <br>
            <a href="https://www.google.com/maps/@17.302606,-62.759765,12z" target="_blank" style="color: #44ff44; text-decoration: none; font-weight: bold;">📍 Open Full Map</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Status
    st.markdown('<div class="sidebar-header">⚡ System Status</div>', unsafe_allow_html=True)
    
    current_time = get_stkitts_time()
    ai_status = "🟢 Online" if st.session_state.get('ai_enabled', False) else "🔴 Offline"
    db_status = "🟢 Loaded" if st.session_state.get('csv_data') is not None else "🔴 Missing"
    
    st.markdown(f"""
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #e0e0e0;">
        <div style="margin-bottom: 5px; color: #66ff66;">🤖 AI: {ai_status}</div>
        <div style="margin-bottom: 5px; color: #66ff66;">💾 Database: {db_status}</div>
        <div style="margin-bottom: 5px; color: #66ff66;">🕒 Time: {current_time} AST</div>
        <div style="margin-bottom: 5px; color: #66ff66;">🌐 Language: {SUPPORTED_LANGUAGES[selected_language][:8]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh Status", key="sidebar_refresh"):
        st.rerun()

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
        # Get current St. Kitts time for context (but don't always mention it)
        current_time = get_stkitts_time()
        current_date = get_stkitts_date()
        
        # Only include time context if user asks about time or current events
        time_keywords = ['time', 'date', 'now', 'current', 'today', 'when', 'hora', 'fecha', 'hoy', 'temps', 'maintenant']
        include_time = any(keyword in user_input.lower() for keyword in time_keywords)
        
        time_context = f"""
        Current St. Kitts & Nevis time: {current_time}
        Current St. Kitts & Nevis date: {current_date}
        """ if include_time else ""
        
        # Combine system prompt with user context
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
        
        # Clean the response
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
   
    # Search through all text columns
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

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    # Add initial bot message without excessive time mentions
    st.session_state.messages.append({
        "role": "assistant",
        "content": "🚔 Welcome to SECURO - Your AI Crime Investigation Assistant for St. Kitts & Nevis Law Enforcement.\n\n\n\n\n\n📊 Loading crime database... Please wait while I check for your data file.",
        "timestamp": get_stkitts_time()
    })

if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

if 'csv_loaded' not in st.session_state:
    st.session_state.csv_loaded = False

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = True

# Sidebar toggle functionality
col1, col2 = st.columns([1, 10])
with col1:
    if st.button("☰", key="sidebar_toggle", help="Toggle Sidebar"):
        st.session_state.sidebar_state = not st.session_state.sidebar_state
        st.rerun()

# Apply CSS to hide/show sidebar based on state
if not st.session_state.sidebar_state:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            transform: translateX(-100%) !important;
            transition: transform 0.3s ease !important;
        }
        .main .block-container {
            margin-left: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Header with real-time St. Kitts time
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="main-header">
    <div class="particles" id="particles"></div>
    <h1>SECURO</h1>
    <div class="tagline">AI Crime Investigation Assistant</div>
    <div class="location">🇰🇳 St. Kitts & Nevis Law Enforcement</div>
    <div class="datetime">📅 {current_date} | 🕒 {current_time} (AST)</div>
</div>
""", unsafe_allow_html=True)

# Particles animation script
st.markdown("""
<script>
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        const particleCount = 40;
       
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 15) + 's';
            particlesContainer.appendChild(particle);
        }
    }
}
createParticles();
</script>
""", unsafe_allow_html=True)

# Load CSV data with better error handling
st.markdown('<div class="section-header">📊 Crime Database Status</div>', unsafe_allow_html=True)

# Load CSV only once
if not st.session_state.csv_loaded:
    with st.spinner("🔍 Searching for crime database..."):
        csv_data, status_message = load_csv_data()
        st.session_state.csv_data = csv_data
        st.session_state.csv_loaded = True
       
        if csv_data is not None:
            st.markdown(f'<div class="file-status file-found">{status_message}</div>', unsafe_allow_html=True)
           
            # Add success message to chat without time spam
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ Crime database loaded successfully!\n\n\n\n🔍 You can now ask me questions about the crime data. Try asking about specific crimes, locations, dates, or any other information you need for your investigation.",
                "timestamp": get_stkitts_time()
            })
        else:
            st.markdown(f'<div class="file-status file-missing">{status_message}</div>', unsafe_allow_html=True)
           
            # Add error message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ **Database Error:** {status_message}\n\n🔧 **How to fix:**\n1. Make sure your CSV file is named exactly `criminal_justice_qa.csv`\n2. Place it in the same folder as your Streamlit app\n3. Restart the application\n\n💡 Without the database, I can still help with general crime investigation guidance.",
                "timestamp": get_stkitts_time()
            })

# Show current status
ai_status = st.session_state.get('ai_status', 'AI Status Unknown')
if st.session_state.csv_data is not None:
    st.success(f"✅ Database Ready: {len(st.session_state.csv_data)} crime records loaded | {ai_status}")
else:
    st.error(f"❌ Database Not Found: Place 'criminal_justice_qa.csv' in app directory | {ai_status}")

# Main chat area
st.markdown('<div class="section-header">💬 Crime Investigation Chat</div>', unsafe_allow_html=True)

# Display chat messages with proper St. Kitts time
for message in st.session_state.messages:
    if message["role"] == "user":
        # Clean user message
        clean_content = str(message["content"]).strip()
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-content">{clean_content}</div>
            <div class="message-time">You • {message["timestamp"]} AST</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Clean bot message and ensure proper formatting
        clean_content = str(message["content"]).strip()
        # Remove any unwanted HTML or formatting
        clean_content = re.sub(r'<[^>]+>', '', clean_content)
        clean_content = clean_content.replace('```', '')
        
        # Format with SECURO prefix if it doesn't already have it
        if not clean_content.startswith("SECURO:") and not clean_content.startswith("🚔"):
            if "SECURO" in clean_content.upper():
                # If SECURO is mentioned but not at start, leave as is
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
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot status-online"></div>
        <span>SECURO AI Online</span>
    </div>
    <div class="status-item">
        <div class="status-dot {status_class}"></div>
        <span>{status_message}</span>
    </div>
    <div class="status-item">
        <div class="status-dot status-online"></div>
        <span>{current_time} AST</span>
    </div>
    <div class="status-item">
        <div class="status-dot status-processing"></div>
        <span>{SUPPORTED_LANGUAGES[st.session_state.selected_language]}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Auto-refresh time every 30 seconds
if st.button("🔄 Refresh Time", help="Update current St. Kitts time"):
    st.rerun()
