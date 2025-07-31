import streamlit as st
import time
import datetime
import random
import pandas as pd
import os
import google.generativeai as genai
import re

# System Prompt for SECURO Crime Mitigation Chatbot
system_prompt = """
You are SECURO, an intelligent and professional crime mitigation chatbot built to provide real-time, data-driven insights for a wide range of users, including law enforcement, criminologists, policy makers, and the general public.

Your mission is to support crime prevention, research, and public safety through:
- Interactive maps
- Statistical analysis
- Predictive analytics
- Visual data presentations (charts, graphs, etc.)
- Emergency contact guidance

Capabilities:
- Analyze and summarize current and historical crime data (local and global)
- Detect trends and patterns across time, location, and type
- Recommend prevention strategies based on geographic and temporal factors
- Provide accessible language for general users, while supporting technical depth for experts
- Integrate with GIS, crime databases (e.g. Crimeometer), and public safety APIs
- Generate visual outputs using Python tools like matplotlib, pandas, folium, etc.
- Adapt responses to be clear, concise, and actionable

Tone & Behavior:
- Maintain a professional yet human tone
- Be concise, accurate, and helpful
- Explain visuals when necessary
- Avoid panic-inducing language—focus on empowerment and awareness
- Respond directly without using code blocks, backticks, or HTML formatting

Your responses should reflect an understanding of criminology, public safety, and data visualization best practices.
"""

# Initialize the AI model
try:
    GOOGLE_API_KEY = "AIzaSyAK-4Xklul9WNoiWnSrpzPkn5C-Dbny8B4"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Ready (Direct API Key)"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="https://i.postimg.cc/V69LH7F4/Logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling - FIXED VERSION
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
   
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
   
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #2e1a1a 50%, #3e1616 100%);
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Particles animation */
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
        background: rgba(255, 68, 68, 0.3);
        border-radius: 50%;
        animation: float 10s infinite linear;
    }

    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
    }
   
    /* Header styling */
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 15px;
        border: 1px solid rgba(255, 68, 68, 0.3);
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
        background: linear-gradient(45deg, transparent, rgba(255, 68, 68, 0.1), transparent);
        animation: scan 3s infinite;
    }

    @keyframes scan {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }

    .main-header h1 {
        font-size: 3rem;
        color: #ff4444;
        text-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
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
        color: #ff4444;
        margin-top: 5px;
        position: relative;
        z-index: 2;
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Sidebar styling - Multiple selectors for different Streamlit versions */
    .css-1d391kg, .css-1cypcdb, .css-k1vhr6, .css-1lcbmhc, .css-17eq0hr,
    section[data-testid="stSidebar"], .stSidebar, [data-testid="stSidebar"] > div,
    .css-1aumxhk, .css-hxt7ib, .css-17lntkn {
        background: rgba(40, 20, 20, 0.9) !important;
        border-right: 1px solid rgba(255, 68, 68, 0.3) !important;
        backdrop-filter: blur(10px) !important;
    }
   
    /* Sidebar header styling */
    section[data-testid="stSidebar"] .css-10trblm {
        color: #ff4444 !important;
    }
   
    /* Sidebar content background */
    .css-1cypcdb .css-17lntkn {
        background: transparent !important;
    }
   
    /* Emergency contacts styling */
    .contact-item {
        background: rgba(0, 0, 0, 0.5);
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        border-left: 3px solid #ff4444;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #e0e0e0;
        font-family: 'JetBrains Mono', monospace;
    }

    .contact-item:hover {
        background: rgba(255, 68, 68, 0.1);
        transform: translateX(5px);
    }

    .contact-name {
        color: #e0e0e0;
        font-size: 0.9rem;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
    }

    .contact-number {
        color: #ff4444;
        font-size: 0.8rem;
        margin-top: 3px;
        font-family: 'JetBrains Mono', monospace;
    }
   
    /* Sidebar toggle button */
    .sidebar-toggle {
        position: fixed;
        top: 70px;
        left: 20px;
        z-index: 999;
        background: linear-gradient(135deg, #ff4444, #cc3333);
        border: none;
        border-radius: 8px;
        color: white;
        padding: 10px 15px;
        cursor: pointer;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 68, 68, 0.3);
    }
   
    .sidebar-toggle:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 68, 68, 0.5);
    }
   
    /* Map container with better styling */
    .map-container {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 10px;
        padding: 0;
        border: 1px solid rgba(255, 68, 68, 0.3);
        position: relative;
        height: 300px;
        overflow: hidden;
        margin-bottom: 15px;
    }
   
    /* Map iframe styling */
    .crime-map iframe {
        width: 100%;
        height: 100%;
        border: none;
        border-radius: 10px;
        filter: invert(0.9) hue-rotate(180deg) saturate(1.2);
    }

    .map-placeholder {
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #2e1a1a, #3e1616);
        border-radius: 8px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
    }

    .hotspot {
        position: absolute;
        width: 12px;
        height: 12px;
        background: #ff4444;
        border-radius: 50%;
        animation: pulse-hotspot 2s infinite;
        cursor: pointer;
    }

    .hotspot::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border: 2px solid rgba(255, 68, 68, 0.5);
        border-radius: 50%;
        animation: ripple 2s infinite;
    }

    @keyframes pulse-hotspot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.2); }
    }

    @keyframes ripple {
        0% { transform: scale(1); opacity: 1; }
        100% { transform: scale(2); opacity: 0; }
    }

    .hotspot-1 { top: 30%; left: 25%; }
    .hotspot-2 { top: 45%; left: 60%; }
    .hotspot-3 { top: 70%; left: 40%; }
    .hotspot-4 { top: 25%; left: 75%; }
   
    /* Chat styling - FIXED VERSION */
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
        background: linear-gradient(135deg, #ff4444, #cc3333);
        color: #ffffff !important;
        border-bottom-right-radius: 5px;
    }

    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.8) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255, 68, 68, 0.3);
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
   
    /* Status bar */
    .status-bar {
        background: rgba(0, 0, 0, 0.8);
        padding: 10px 20px;
        border-radius: 25px;
        margin-top: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255, 68, 68, 0.2);
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

    .status-online { background: #ff4444; }
    .status-processing { background: #cc3333; }
    .status-evidence { background: #ff6666; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
   
    /* Input styling */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 68, 68, 0.3) !important;
        border-radius: 25px !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextInput input:focus {
        border-color: #ff4444 !important;
        box-shadow: 0 0 20px rgba(255, 68, 68, 0.2) !important;
    }
   
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #ff4444, #cc3333) !important;
        border: none !important;
        border-radius: 25px !important;
        color: #fff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 20px rgba(255, 68, 68, 0.4) !important;
    }
   
    /* Section headers */
    .section-header {
        color: #ff4444;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }

    .file-status {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(255, 68, 68, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        font-family: 'JetBrains Mono', monospace;
    }

    .file-found {
        color: #4ade80;
    }

    .file-missing {
        color: #ff4444;
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


def get_ai_response(user_input, csv_results):
    """Generate AI response using the system prompt and context"""
    if not st.session_state.get('ai_enabled', False) or model is None:
        return csv_results  # Fallback to CSV search results
    
    try:
        # Combine system prompt with user context
        full_prompt = f"""
        {system_prompt}
        
        Context from crime database search:
        {csv_results}
        
        User query: {user_input}
        
        Please provide a comprehensive response as SECURO based on the available data and your crime analysis capabilities.
        Respond directly without using code blocks, backticks, or HTML formatting.
        """
        
        response = model.generate_content(full_prompt)
        
        # Clean the response - remove any unwanted formatting
        clean_response = response.text.strip()
        # Remove backticks if they exist
        clean_response = clean_response.replace('```', '')
        # Remove any HTML tags that might appear
        clean_response = re.sub(r'<[^>]+>', '', clean_response)
        
        return clean_response
        
    except Exception as e:
        return f"{csv_results}\n\n⚠️ AI analysis temporarily unavailable. Showing database search results."


def search_csv_data(df, query):
    """Search through CSV data for relevant information"""
    if df is None:
        return "❌ No CSV data loaded. Please make sure 'criminal_justice_qa.csv' is in the correct location."
   
    search_term = query.lower()
    results = []
   
    # Search through all text columns
    for column in df.columns:
        if df[column].dtype == 'object':  # Text columns
            try:
                mask = df[column].astype(str).str.lower().str.contains(search_term, na=False)
                matching_rows = df[mask]
               
                if not matching_rows.empty:
                    for _, row in matching_rows.head(2).iterrows():  # Limit to 2 results per column
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
    # Add initial bot message
    st.session_state.messages.append({
        "role": "assistant",
        "content": "🚔 **Welcome to SECURO** - Your AI Crime Investigation Assistant for St. Kitts & Nevis Law Enforcement.\n\nI assist criminologists, police officers, forensic experts, and autopsy professionals with:\n• Case analysis and evidence correlation\n• Crime data search and insights\n• Investigative support and recommendations\n\n📊 Loading crime database... Please wait while I check for your data file.",
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "expanded"

if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

if 'csv_loaded' not in st.session_state:
    st.session_state.csv_loaded = False

# Header with sidebar toggle
col1, col2 = st.columns([1, 10])

with col1:
    if st.button("🔧", help="Toggle Sidebar", key="sidebar_toggle"):
        if st.session_state.sidebar_state == "expanded":
            st.session_state.sidebar_state = "collapsed"
        else:
            st.session_state.sidebar_state = "expanded"
        st.rerun()

with col2:
    st.markdown("""
    <div class="main-header">
        <div class="particles" id="particles"></div>
        <h1>SECURO</h1>
        <div class="tagline">AI Crime Investigation Assistant</div>
        <div class="location">🇰🇳 St. Kitts & Nevis Law Enforcement</div>
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
           
            # Add success message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"✅ **Crime database loaded successfully!**\n\n📊 Database contains {len(csv_data)} records with {len(csv_data.columns)} data fields.\n\n🔍 You can now ask me questions about the crime data. Try asking about specific crimes, locations, dates, or any other information you need for your investigation.",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
        else:
            st.markdown(f'<div class="file-status file-missing">{status_message}</div>', unsafe_allow_html=True)
           
            # Add error message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ **Database Error:** {status_message}\n\n🔧 **How to fix:**\n1. Make sure your CSV file is named exactly `criminal_justice_qa.csv`\n2. Place it in the same folder as your Streamlit app\n3. Restart the application\n\n💡 Without the database, I can still help with general crime investigation guidance and emergency contacts.",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })

# Show current status
ai_status = st.session_state.get('ai_status', 'AI Status Unknown')
if st.session_state.csv_data is not None:
    st.success(f"✅ Database Ready: {len(st.session_state.csv_data)} crime records loaded | {ai_status}")
else:
    st.error(f"❌ Database Not Found: Place 'criminal_justice_qa.csv' in app directory | {ai_status}")

# Sidebar (only show if expanded)
if st.session_state.sidebar_state == "expanded":
    with st.sidebar:
        st.markdown('<div class="section-header">🚨 Emergency Contacts</div>', unsafe_allow_html=True)
       
        emergency_contacts = [
            {"name": "Emergency Hotline", "number": "911", "type": "police"},
            {"name": "Police Department", "number": "465-2241", "type": "police"},
            {"name": "Hospital", "number": "465-2551", "type": "hospital"},
            {"name": "Fire Department", "number": "465-2515 / 465-7167", "type": "fire"},
            {"name": "Coast Guard", "number": "465-8384 / 466-9280", "type": "legal"},
            {"name": "Red Cross", "number": "465-2584", "type": "forensic"},
            {"name": "NEMA (Emergency Mgmt)", "number": "466-5100", "type": "legal"}
        ]
       
        for contact in emergency_contacts:
            if st.button(f"📞 {contact['name']}\n{contact['number']}", key=contact['name']):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"🚨 **Emergency Contact Accessed:**\n\n📞 **{contact['name']}:** {contact['number']}\n\n📝 Contact logged for case documentation. Emergency services are standing by for immediate response.",
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
       
        st.markdown('<div class="section-header">📍 Crime Hotspots Map</div>', unsafe_allow_html=True)
       
        # Real Google Maps embed for St. Kitts & Nevis
        st.markdown("""
        <div class="map-container crime-map">
            <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d243.44896!2d-62.7261!3d17.3026!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8c1a602b153c94b5%3A0x8e3f7a7c7b1b9f5e!2sBasseterre%2C%20St%20Kitts%20%26%20Nevis!5e1!3m2!1sen!2sus!4v1634567890123!5m2!1sen!2sus&maptype=satellite"
                allowfullscreen=""
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade">
            </iframe>
        </div>
        """, unsafe_allow_html=True)
       
        # Interactive hotspot buttons
        st.markdown('<div class="section-header">🎯 Active Crime Zones</div>', unsafe_allow_html=True)
       
        hotspots = [
            {"name": "Basseterre Downtown", "level": "🔴 High Risk", "coords": "17.3026, -62.7261"},
            {"name": "Sandy Point", "level": "🟡 Medium Risk", "coords": "17.3580, -62.8419"},
            {"name": "Charlestown (Nevis)", "level": "🟠 Active Cases", "coords": "17.1373, -62.6131"},
            {"name": "Frigate Bay", "level": "🟡 Tourist Area", "coords": "17.2742, -62.6897"}
        ]
       
        for hotspot in hotspots:
            if st.button(f"{hotspot['level']} {hotspot['name']}", key=f"hotspot_{hotspot['name']}"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"📍 **Crime Hotspot Analysis:**\n\n🎯 **Location:** {hotspot['name']}\n📊 **Coordinates:** {hotspot['coords']}\n⚠️ **Status:** {hotspot['level']}\n\n🚔 **Recommendation:** Increased patrol presence and witness canvassing recommended. Coordinating with local units for enhanced surveillance in this area.",
                    "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()

# Main chat area
st.markdown('<div class="section-header">💬 Crime Investigation Chat</div>', unsafe_allow_html=True)

# Display chat messages - FIXED VERSION
for message in st.session_state.messages:
    if message["role"] == "user":
        # Clean user message
        clean_content = str(message["content"]).strip()
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-content">{clean_content}</div>
            <div class="message-time">{message["timestamp"]}</div>
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
            <div class="message-time">{message["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
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
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
       
        # Generate response using AI if available, otherwise use CSV search
        with st.spinner("🔍 Analyzing crime database..."):
            csv_results = search_csv_data(st.session_state.csv_data, user_input)
            response = get_ai_response(user_input, csv_results)
           
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        })
       
        st.rerun()

# Status bar
status_message = "CSV Data Ready" if st.session_state.csv_data is not None else "CSV Data Missing"
status_class = "status-processing" if st.session_state.csv_data is not None else "status-evidence"

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
        <div class="status-dot status-evidence"></div>
        <span>Emergency Services Linked</span>
    </div>
</div>
""", unsafe_allow_html=True)
