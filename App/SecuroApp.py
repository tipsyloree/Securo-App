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
import folium
from streamlit_folium import st_folium
import warnings
import json
import uuid
from datetime import datetime as dt
import PyPDF2
import tempfile
import base64
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
    "Police Emergency": {"number": "911", "description": "For immediate police assistance and emergency response", "icon": "🚔"},
    "Police Headquarters": {"number": "465-2241", "description": "Royal St. Christopher and Nevis Police Force\nLocal Intelligence: Ext. 4238/4239", "icon": "🏢"},
    "Medical Emergency": {"number": "465-2551", "description": "Hospital services and medical emergencies", "icon": "🏥"},
    "Fire Department": {"number": "465-2515", "description": "Fire emergencies and rescue operations\nAlt: 465-7167", "icon": "🔥"},
    "Coast Guard": {"number": "465-8384", "description": "Maritime emergencies and water rescue\nAlt: 466-9280", "icon": "🚢"},
    "Met Office": {"number": "465-2749", "description": "Weather emergencies and warnings", "icon": "🌡️"},
    "Red Cross": {"number": "465-2584", "description": "Disaster relief and emergency aid", "icon": "➕"},
    "NEMA": {"number": "466-5100", "description": "National Emergency Management Agency", "icon": "⚡"}
}

# Crime Hotspots Data for St. Kitts & Nevis
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

# MacroTrends International Comparison Data
MACROTRENDS_DATA = {
    "homicide_rates_per_100k": {
        "2020": 20.99, "2019": 25.15, "2018": 48.16, "2017": 48.14,
        "2016": 42.50, "2015": 38.20, "2014": 35.80, "2013": 42.10,
        "2012": 33.60, "2011": 67.60
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
        "2024_total_crimes": 1146, "2023_total_crimes": 1280,
        "2022_total_crimes": 1360, "2024_homicides": 28,
        "2023_homicides": 31, "first_quarter_2025": "No homicides (first time in 23 years)"
    }
}

# Enhanced HISTORICAL CRIME DATABASE
HISTORICAL_CRIME_DATABASE = {
    "2025_Q2": {
        "period": "Q2 2025 (Apr-Jun)", "total_crimes": 292, "detection_rate": 38.7,
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
        "period": "2024 Full Year (Jan-Dec)", "total_crimes": 1146, "detection_rate": 41.8,
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
        "period": "2023 Full Year (Jan-Dec)", "total_crimes": 1280, "detection_rate": 44.6,
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
    }
}

# St. Kitts timezone
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

# Chat Management System
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'chat_counter' not in st.session_state:
    st.session_state.chat_counter = 1

if 'current_analytics_tab' not in st.session_state:
    st.session_state.current_analytics_tab = 'Crime Trends'

if 'statistical_database' not in st.session_state:
    st.session_state.statistical_database = {}

if 'main_view' not in st.session_state:
    st.session_state.main_view = 'ai-assistant'

if 'chat_active' not in st.session_state:
    st.session_state.chat_active = False

# Initialize auto-speak setting
if 'auto_speak_enabled' not in st.session_state:
    st.session_state.auto_speak_enabled = False

def clean_text_for_speech(text):
    """Clean text for better speech synthesis"""
    if not text:
        return ""
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', str(text))
    
    # Remove markdown formatting
    clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)  # Bold
    clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)      # Italic
    clean_text = re.sub(r'#{1,6}\s*', '', clean_text)           # Headers
    clean_text = re.sub(r'```[^`]*```', '', clean_text)         # Code blocks
    clean_text = re.sub(r'`([^`]+)`', r'\1', clean_text)        # Inline code
    
    # Clean up emojis and special characters that cause TTS issues
    clean_text = re.sub(r'[🚔🚨📊💬🤖🔥🏥➕⚡🌡️🚢🗺️📍⚠️🔍🟢🔴•]', '', clean_text)
    
    # Replace bullet points and lists with spoken equivalents
    clean_text = re.sub(r'^\s*•\s*', 'Point: ', clean_text, flags=re.MULTILINE)
    clean_text = re.sub(r'^\s*-\s*', 'Item: ', clean_text, flags=re.MULTILINE)
    clean_text = re.sub(r'^\s*\d+\.\s*', 'Number: ', clean_text, flags=re.MULTILINE)
    
    # Clean up whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text)
    clean_text = clean_text.strip()
    
    # Break into sentences and limit total length to prevent cutoffs
    sentences = re.split(r'[.!?]+', clean_text)
    limited_text = []
    total_chars = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and total_chars + len(sentence) < 800:  # Increased limit but still manageable
            limited_text.append(sentence)
            total_chars += len(sentence)
        elif total_chars > 0:
            break
    
    result = '. '.join(limited_text)
    if result and not result.endswith('.'):
        result += '.'
    
    return result

def create_male_voice_tts_script(text, element_id=""):
    """Create JavaScript for male voice TTS with voice selection"""
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return ""
    
    # Escape text for JavaScript
    escaped_text = clean_text.replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    
    return f"""
    <script>
    function speakWithMaleVoice_{element_id}() {{
        if ('speechSynthesis' in window) {{
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
            
            setTimeout(() => {{
                const utterance = new SpeechSynthesisUtterance('{escaped_text}');
                
                // Get available voices
                let voices = window.speechSynthesis.getVoices();
                
                // If voices aren't loaded yet, wait for them
                if (voices.length === 0) {{
                    window.speechSynthesis.onvoiceschanged = function() {{
                        voices = window.speechSynthesis.getVoices();
                        selectMaleVoice(voices, utterance);
                        window.speechSynthesis.speak(utterance);
                    }};
                }} else {{
                    selectMaleVoice(voices, utterance);
                    window.speechSynthesis.speak(utterance);
                }}
                
                function selectMaleVoice(voices, utterance) {{
                    // Preferred male voices (in order of preference)
                    const preferredMaleVoices = [
                        'Microsoft David - English (United States)',
                        'Google UK English Male',
                        'Alex',  // macOS male voice
                        'Daniel',  // macOS male voice
                        'Microsoft Mark - English (United States)',
                        'Microsoft George - English (United Kingdom)',
                        'Microsoft Richard - English (United Kingdom)',
                        'en-US-Wavenet-D',  // Google Cloud male voice
                        'en-US-Wavenet-A',  // Google Cloud male voice
                        'en-GB-Wavenet-D',  // Google Cloud UK male voice
                        'Chrome Male',
                        'Male'
                    ];
                    
                    // Find the best male voice
                    let selectedVoice = null;
                    
                    // First, try to find a preferred male voice
                    for (let preferred of preferredMaleVoices) {{
                        selectedVoice = voices.find(voice => 
                            voice.name.includes(preferred) || 
                            voice.name.toLowerCase().includes(preferred.toLowerCase())
                        );
                        if (selectedVoice) break;
                    }}
                    
                    // If no preferred voice found, look for any male voice
                    if (!selectedVoice) {{
                        selectedVoice = voices.find(voice => 
                            voice.name.toLowerCase().includes('male') ||
                            voice.name.toLowerCase().includes('man') ||
                            voice.name.toLowerCase().includes('david') ||
                            voice.name.toLowerCase().includes('alex') ||
                            voice.name.toLowerCase().includes('daniel') ||
                            voice.name.toLowerCase().includes('mark') ||
                            voice.name.toLowerCase().includes('george') ||
                            voice.name.toLowerCase().includes('richard') ||
                            voice.name.toLowerCase().includes('matthew') ||
                            voice.name.toLowerCase().includes('paul') ||
                            voice.name.toLowerCase().includes('tom') ||
                            (voice.name.includes('en-') && voice.name.includes('-D')) ||
                            (voice.name.includes('en-') && voice.name.includes('-A'))
                        );
                    }}
                    
                    // If still no male voice found, filter by language and try to avoid obviously female names
                    if (!selectedVoice) {{
                        const englishVoices = voices.filter(voice => 
                            voice.lang.startsWith('en') && 
                            !voice.name.toLowerCase().includes('female') &&
                            !voice.name.toLowerCase().includes('woman') &&
                            !voice.name.toLowerCase().includes('zira') &&
                            !voice.name.toLowerCase().includes('hazel') &&
                            !voice.name.toLowerCase().includes('susan') &&
                            !voice.name.toLowerCase().includes('karen') &&
                            !voice.name.toLowerCase().includes('moira') &&
                            !voice.name.toLowerCase().includes('tessa') &&
                            !voice.name.toLowerCase().includes('samantha') &&
                            !voice.name.toLowerCase().includes('victoria') &&
                            !voice.name.toLowerCase().includes('kate')
                        );
                        
                        if (englishVoices.length > 0) {{
                            // Try to pick the first non-female sounding voice
                            selectedVoice = englishVoices[0];
                        }}
                    }}
                    
                    // Apply the selected voice
                    if (selectedVoice) {{
                        utterance.voice = selectedVoice;
                        console.log('Selected voice:', selectedVoice.name);
                    }} else {{
                        console.log('No male voice found, using default voice');
                    }}
                    
                    // Voice settings optimized for male voice
                    utterance.rate = 0.85;      // Slightly slower for clarity
                    utterance.pitch = 0.8;     // Lower pitch for more masculine sound
                    utterance.volume = 0.9;    // Good volume level
                }}
            }}, 200);
        }} else {{
            console.error('Text-to-speech not supported in this browser');
        }}
    }}
    
    // Auto-execute if this is an auto-speak call
    if ('{element_id}' === 'auto') {{
        speakWithMaleVoice_{element_id}();
    }}
    </script>
    """

def get_current_chat():
    """Get current chat session"""
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        return st.session_state.chat_sessions[st.session_state.current_chat_id]
    else:
        # Only create new chat when actually needed, not during initialization
        if st.session_state.get('chat_active', False):
            return create_new_chat_session()
        else:
            # Return a temporary chat object for display purposes
            return {
                'id': 'temp',
                'name': 'New Chat',
                'messages': [],
                'created_at': get_stkitts_time(),
                'last_activity': get_stkitts_time()
            }

def create_new_chat_session():
    """Create a new chat session - renamed to avoid conflicts"""
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
    return st.session_state.chat_sessions[chat_id]

def add_message_to_chat(role, content):
    """Add message to current chat"""
    current_chat = get_current_chat()
    current_chat['messages'].append({
        "role": role,
        "content": content,
        "timestamp": get_stkitts_time()
    })
    current_chat['last_activity'] = get_stkitts_time()
    
    if role == "user" and len(current_chat['messages']) <= 2:
        chat_name = content[:30] + "..." if len(content) > 30 else content
        current_chat['name'] = chat_name

# Statistical Data Processing Functions
def fetch_and_process_statistics():
    """Fetch and process statistics from PDF URLs"""
    if st.session_state.statistical_database:
        return st.session_state.statistical_database
    
    # Use the enhanced database with complete data
    st.session_state.statistical_database = HISTORICAL_CRIME_DATABASE.copy()
    
    # Add MacroTrends and processed data from the PDF structure we saw
    st.session_state.statistical_database.update({
        "macrotrends_data": MACROTRENDS_DATA,
        "recent_trends": {
            "murder_trend": "75% decrease from 2024 to 2025 H1",
            "drug_crimes_trend": "463% increase in drug crimes 2024-2025",
            "detection_improvement": "Detection rates vary by crime type",
            "larceny_concern": "Larcenies remain highest volume crime"
        },
        "geographical_breakdown": {
            "st_kitts_districts_ab": "Higher crime volume but lower detection rate",
            "nevis_district_c": "Lower crime volume but higher detection rate",
            "federation_wide": "Overall crime trends showing mixed results"
        }
    })
    
    return st.session_state.statistical_database

def create_crime_hotspot_map():
    """Create an interactive crime hotspot map for St. Kitts and Nevis"""
    # Center the map on St. Kitts and Nevis
    center_lat = 17.25
    center_lon = -62.7
    
    # Create the base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap',
        attr='Crime Hotspot Analysis - SECURO'
    )
    
    # Add Google Satellite layer as an option
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Color mapping for risk levels (Updated with royal blue/red theme)
    risk_colors = {
        'High': '#dc2626',     # Red for high risk
        'Medium': '#1d4ed8',   # Royal blue for medium
        'Low': '#0f172a'       # Dark blue for low
    }
    
    # Add crime hotspots to the map
    for location, data in CRIME_HOTSPOTS.items():
        # Create popup content
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
        
        # Calculate marker size based on crime count
        marker_size = max(10, min(30, data['crimes'] * 0.8))
        
        # Add marker to map
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
        
        # Add text label for major hotspots
        if data['crimes'] > 25:
            folium.Marker(
                location=[data['lat'] + 0.01, data['lon']],
                icon=folium.DivIcon(
                    html=f"""<div style="font-size: 10px; font-weight: bold; 
                             color: white; text-shadow: 1px 1px 2px black;">
                             {location}</div>""",
                    icon_size=(100, 20),
                    icon_anchor=(50, 10)
                )
            ).add_to(m)
    
    # Add a legend (Updated with royal blue/red theme)
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 140px; 
                background-color: rgba(0, 0, 0, 0.9); 
                border: 2px solid #1d4ed8;
                border-radius: 10px; z-index:9999; 
                font-size: 12px; font-family: Arial;
                padding: 10px; color: white;">
    <h4 style="margin: 0 0 10px 0; color: #1d4ed8;">🗺️ Crime Risk Legend</h4>
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
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def create_macrotrends_comparison_charts(chart_type="homicide_trends"):
    """Create charts using MacroTrends international comparison data"""
    
    if chart_type == "homicide_trends":
        # Historical homicide rates per 100K population
        years = list(MACROTRENDS_DATA["homicide_rates_per_100k"].keys())
        rates = list(MACROTRENDS_DATA["homicide_rates_per_100k"].values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=years, y=rates,
            mode='lines+markers',
            name='Homicide Rate per 100K',
            line=dict(color='#dc2626', width=3),
            marker=dict(size=10, color='#dc
