import streamlit as st
import time
import random

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with all styles properly formatted for Streamlit
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.main > div {
    padding: 0 !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    font-family: 'JetBrains Mono', monospace;
    overflow-x: hidden;
    min-height: 100vh;
    position: relative;
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Animated background particles */
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
    background: rgba(0, 255, 136, 0.3);
    border-radius: 50%;
    animation: float 10s infinite linear;
}

@keyframes float {
    0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
}

/* Main container */
.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    position: relative;
    z-index: 10;
}

/* Header */
.header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: rgba(0, 0, 0, 0.7);
    border-radius: 15px;
    border: 1px solid rgba(0, 255, 136, 0.3);
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}

.header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(0, 255, 136, 0.1), transparent);
    animation: scan 3s infinite;
}

@keyframes scan {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.header h1 {
    font-size: 3rem;
    color: #00ff88;
    text-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    margin-bottom: 10px;
    position: relative;
    z-index: 2;
    font-weight: 700;
}

.header .tagline {
    font-size: 1rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 2px;
    position: relative;
    z-index: 2;
}

.header .location {
    font-size: 0.9rem;
    color: #00ff88;
    margin-top: 5px;
    position: relative;
    z-index: 2;
}

/* Chat interface */
.chat-container {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 20px;
    height: 75vh;
}

/* Sidebar */
.sidebar {
    background: rgba(20, 20, 40, 0.8);
    border-radius: 15px;
    border: 1px solid rgba(0, 255, 136, 0.2);
    padding: 20px;
    backdrop-filter: blur(10px);
    overflow-y: auto;
}

/* Emergency Contacts */
.emergency-contacts {
    margin-bottom: 25px;
}

.emergency-contacts h3 {
    color: #00ff88;
    margin-bottom: 15px;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.contact-item {
    background: rgba(0, 0, 0, 0.5);
    padding: 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    border-left: 3px solid;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.contact-item:hover {
    background: rgba(0, 255, 136, 0.1);
    transform: translateX(5px);
}

.contact-police { border-left-color: #ff4444; }
.contact-hospital { border-left-color: #ff6b6b; }
.contact-fire { border-left-color: #ff8c00; }
.contact-legal { border-left-color: #4169e1; }
.contact-forensic { border-left-color: #9370db; }

.contact-info {
    flex: 1;
}

.contact-name {
    color: #e0e0e0;
    font-size: 0.9rem;
    font-weight: 500;
}

.contact-number {
    color: #00ff88;
    font-size: 0.8rem;
    margin-top: 3px;
}

.contact-icon {
    width: 20px;
    height: 20px;
    opacity: 0.7;
}

/* Crime Map */
.crime-map-section {
    margin-bottom: 20px;
}

.crime-map-section h3 {
    color: #00ff88;
    margin-bottom: 15px;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.map-container {
    background: rgba(0, 0, 0, 0.6);
    border-radius: 10px;
    padding: 15px;
    border: 1px solid rgba(0, 255, 136, 0.2);
    position: relative;
    height: 200px;
    overflow: hidden;
}

.map-placeholder {
    width: 100%;
    height: 100%;
    background: linear-gradient(45deg, #1a1a2e, #16213e);
    border-radius: 8px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    font-size: 0.8rem;
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

.legend {
    margin-top: 10px;
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    color: #888;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.legend-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}

.high-crime { background: #ff4444; }
.medium-crime { background: #ff8c00; }
.low-crime { background: #00ff88; }

/* Main chat area */
.chat-main {
    background: rgba(20, 20, 40, 0.8);
    border-radius: 15px;
    border: 1px solid rgba(0, 255, 136, 0.2);
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(10px);
}

.chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #00ff88 rgba(0, 0, 0, 0.3);
    max-height: 500px;
}

.chat-messages::-webkit-scrollbar {
    width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: #00ff88;
    border-radius: 3px;
}

.message {
    margin-bottom: 20px;
    animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.message-user {
    text-align: right;
}

.message-bot {
    text-align: left;
}

.message-content {
    display: inline-block;
    padding: 15px 20px;
    border-radius: 15px;
    max-width: 80%;
    position: relative;
}

.message-user .message-content {
    background: linear-gradient(135deg, #00ff88, #00cc6a);
    color: #000;
    border-bottom-right-radius: 5px;
}

.message-bot .message-content {
    background: rgba(0, 0, 0, 0.6);
    color: #e0e0e0;
    border: 1px solid rgba(0, 255, 136, 0.3);
    border-bottom-left-radius: 5px;
}

.message-time {
    font-size: 0.7rem;
    color: #888;
    margin-top: 5px;
}

/* Status indicators */
.status-bar {
    background: rgba(0, 0, 0, 0.8);
    padding: 10px 20px;
    border-radius: 25px;
    margin-top: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(0, 255, 136, 0.2);
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

.status-online { background: #00ff88; }
.status-processing { background: #00cc6a; }
.status-evidence { background: #ff4444; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Streamlit input styling */
.stTextInput > div > div > input {
    background: rgba(0, 0, 0, 0.5) !important;
    border: 1px solid rgba(0, 255, 136, 0.3) !important;
    border-radius: 25px !important;
    padding: 12px 20px !important;
    color: #e0e0e0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

.stTextInput > div > div > input:focus {
    border-color: #00ff88 !important;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #00ff88, #00cc6a) !important;
    border: none !important;
    border-radius: 25px !important;
    color: #000 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.4) !important;
}

/* Responsive design */
@media (max-width: 768px) {
    .chat-container {
        grid-template-columns: 1fr;
        height: auto;
    }
    
    .sidebar {
        order: 2;
        height: auto;
        max-height: 400px;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .chat-main {
        height: 60vh;
    }
}
</style>
""", unsafe_allow_html=True)

# Particles background
st.markdown("""
<div class="particles" id="particles"></div>

<script>
// Initialize particles
function createParticles() {
    const particlesContainer = document.getElementById('particles');
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

// Create particles when page loads
setTimeout(createParticles, 100);
</script>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-container">
    <div class="header">
        <h1>SECURO</h1>
        <div class="tagline">AI Crime Investigation Assistant</div>
        <div class="location">🇰🇳 St. Kitts & Nevis Law Enforcement</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for chat messages
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """Welcome to SECURO, your AI crime investigation assistant for St. Kitts & Nevis law enforcement.

I'm here to assist criminologists, police officers, forensic experts, and autopsy professionals with case analysis, evidence correlation, and investigative insights.

How can I assist with your investigation today?""",
            "time": time.strftime("%H:%M:%S")
        }
    ]

# Create columns for layout
col1, col2 = st.columns([1, 2])

# Sidebar with emergency contacts and crime map
with col1:
    st.markdown("""
    <div class="sidebar">
        <div class="emergency-contacts">
            <h3>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                </svg>
                Emergency Contacts
            </h3>
            
            <div class="contact-item contact-police">
                <div class="contact-info">
                    <div class="contact-name">Emergency Hotline</div>
                    <div class="contact-number">911</div>
                </div>
                <svg class="contact-icon" viewBox="0 0 24 24" fill="#ff4444">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
            </div>
            
            <div class="contact-item contact-police">
                <div class="contact-info">
                    <div class="contact-name">Police Department</div>
                    <div class="contact-number">465-2241</div>
                </div>
                <svg class="contact-icon" viewBox="0 0 24 24" fill="#ff4444">
                    <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
                </svg>
            </div>
            
            <div class="contact-item contact-hospital">
                <div class="contact-info">
                    <div class="contact-name">Hospital</div>
                    <div class="contact-number">465-2551</div>
                </div>
                <svg class="contact-icon" viewBox="0 0 24 24" fill="#ff6b6b">
                    <path d="M19 8l-4 4h3c0 3.31-2.69 6-6 6-1.01 0-1.97-.25-2.8-.7l-1.46 1.46C8.97 19.54 10.43 20 12 20c4.42 0 8-3.58 8-8h3l-4-4zM6 12c0-3.31 2.69-6 6-6 1.01 0 1.97.25 2.8.7l1.46-1.46C15.03 4.46 13.57 4 12 4c-4.42 0-8 3.58-8 8H1l4 4 4-4H6z"/>
                </svg>
            </div>
            
            <div class="contact-item contact-fire">
                <div class="contact-info">
                    <div class="contact-name">Fire Department</div>
                    <div class="contact-number">465-2515 / 465-7167</div>
                </div>
                <svg class="contact-icon" viewBox="0 0 24 24" fill="#ff8c00">
                    <path d="M12.71 2.96c-2.75 2.12-4.71 6.79-4.71 11.04 0 4.42 3.58 8 8 8s8-3.58 8-8c0-4.25-1.96-8.92-4.71-11.04-.44-.33-1.04-.33-1.48 0-.63.48-1.51 1.28-2.37 2.23-.86-.95-1.74-1.75-2.37-2.23-.44-.33-1.04-.33-1.48 0z"/>
                </svg>
            </div>
            
            <div class="contact-item contact-legal">
                <div class="contact-info">
                    <div class="contact-name">Coast Guard</div>
                    <div class="contact-number">465-8384 / 466-9280</div>
                </div>
                <svg class="contact-icon" viewBox="0 0 24 24" fill="#4169e1">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                </svg>
            </div>
            
            <div class="contact-item contact-forensic">
                <div class="contact-info">
                    <div class="contact-name">Red Cross</div>
                    <div class="contact-number">465-2584</div>
                </div>
                <svg class="contact-icon" viewBox="0 0 24 24" fill="#ff6b6b">
                    <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H9v-2h2v-2h2v2h2v2h-2v2h-2v-2z"/>
                </svg>
            </div>
            
            <div class="contact-item contact-legal">
                <div class="contact-info">
                    <div class="contact-name">NEMA (Emergency Mgmt)</div>
                    <div class="contact-number">466-5100</div>
                </div>
                <svg class="contact-icon" viewBox="0 0 24 24" fill="#9370db">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
            </div>
        </div>
        
        <div class="crime-map-section">
            <h3>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
                Crime Hotspots
            </h3>
            <div class="map-container">
                <div class="map-placeholder">
                    St. Kitts & Nevis Crime Map
                    <div class="hotspot hotspot-1" title="Basseterre Downtown - High Crime Area"></div>
                    <div class="hotspot hotspot-2" title="Sandy Point - Medium Risk"></div>
                    <div class="hotspot hotspot-3" title="Charlestown (Nevis) - Active Cases"></div>
                    <div class="hotspot hotspot-4" title="Frigate Bay - Tourist Area Incidents"></div>
                </div>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-dot high-crime"></div>
                        <span>High</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot medium-crime"></div>
                        <span>Medium</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-dot low-crime"></div>
                        <span>Low</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main chat area
with col2:
    st.markdown('<div class="chat-main">', unsafe_allow_html=True)
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message message-user">
                    <div class="message-content">{message["content"]}</div>
                    <div class="message-time">{message["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message message-bot">
                    <div class="message-content">{message["content"]}</div>
                    <div class="message-time">{message["time"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_button = st.columns([4, 1])
        
        with col_input:
            user_input = st.text_input(
                "Message",
                placeholder="Describe evidence, case details, or ask forensic questions...",
                label_visibility="collapsed"
            )
        
        with col_button:
            send_button = st.form_submit_button("Send")
    
    if send_button and user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": time.strftime("%H:%M:%S")
        })
        
        # Generate AI response
        responses = [
            "Analyzing case parameters against St. Kitts & Nevis criminal database... Found 3 similar patterns in recent cases.",
            "Cross-referencing forensic evidence with regional crime statistics. Unusual activity detected in Basseterre area.",
            "Based on autopsy protocols for the Caribbean region, I recommend examining toxicology results for common substances.",
            "Correlating witness statements with known criminal networks in St. Kitts & Nevis. 2 persons of interest identified.",
            "Crime pattern analysis suggests organized activity. Recommend coordination with Nevis division.",
            "Forensic timeline indicates premeditation. Checking financial records and travel patterns between islands.",
            "Evidence suggests connection to maritime criminal activity. Coast Guard coordination recommended."
        ]
        
        ai_response = random.choice(responses)
        
        # Add AI response
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "time": time.strftime("%H:%M:%S")
        })
        
        # Rerun to update the display
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Status bar
st.markdown("""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot status-online"></div>
        <span>SECURO AI Online</span>
    </div>
    <div class="status-item">
        <div class="status-dot status-processing"></div>
        <span>SKN Crime Database Connected</span>
    </div>
    <div class="status-item">
        <div class="status-dot status-evidence"></div>
        <span>Emergency Services Linked</span>
    </div>
</div>
""", unsafe_allow_html=True)
