import streamlit as st
import time
import datetime
import random
import pandas as pd
import os
# Commented out AI model imports since you don't have API key configured
# import google.generativeai as genai

# Initialize the AI model (API key should be set via environment variable or Streamlit secrets)
# genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  # Uncomment when you have API key configured
# model = genai.GenerativeModel('gemini-1.5-flash')

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="https://i.postimg.cc/V69LH7F4/Logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling - keeping the exact same design
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
   
    /* Chat styling */
    .chat-message {
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease;
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
    }

    .user-message .message-content {
        background: linear-gradient(135deg, #ff4444, #cc3333);
        color: #fff;
        border-bottom-right-radius: 5px;
    }

    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.6);
        color: #e0e0e0;
        border: 1px solid rgba(255, 68, 68, 0.3);
        border-bottom-left-radius: 5px;
    }

    .message-time {
        font-size: 0.7rem;
        color: #888;
        margin-top: 5px;
        font-family: 'JetBrains Mono', monospace;
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
            st.success(f"successfully load {csv_path}")
            st.info(f"loaded {len(df)} records with {len(df.columns)} columns")
            return df, csv_path
        else:
            current_dir = os.getcwd()
            files_in_script_dir = os.listdir(script_dir)
            files_in_current_dir = os.listdir(current_dir)
            return None, f"""
            could not find '{csv_filename}'.
            expected {csv_path}
            dir {script_dir}
            files: {', '.join([f for f in files_in_script_dir if f.endswith('.csv')])}
            current dir {current_dir}
            files in current directory {', '.join([f for f in files_in_current_dir if f.endswith('.csv')])}
            its not in the same folder chill
            """
    except Exception as e:
        return None, f" im not telling u what happened: {e}"


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
        return f"🔍 (results)
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
if st.session_state.csv_data is not None:
    st.success(f"✅ Database Ready: {len(st.session_state.csv_data)} crime records loaded")
else:
    st.error("❌ Database Not Found: Place 'criminal_justice_qa.csv' in app directory")

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

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-content">{message["content"]}</div>
            <div class="message-time">{message["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <div class="message-content">{message["content"]}</div>
            <div class="message-time">{message["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Ask questions about crime data, investigations, or emergency procedures...",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    if st.button("Send", type="primary"):
        if user_input:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
           
            # Generate response based on CSV data
            with st.spinner("🔍 Analyzing crime database..."):
                response = search_csv_data(st.session_state.csv_data, user_input)
                
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
