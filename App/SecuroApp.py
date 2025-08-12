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
            marker=dict(size=10, color='#dc2626')
        ))
        
        # Add global average line
        global_avg = MACROTRENDS_DATA["comparative_context"]["global_average_firearm_homicides"]
        fig.add_hline(y=global_avg, line_dash="dash", line_color="#1d4ed8",
                     annotation_text=f"Global Average: {global_avg}%")
        
        fig.update_layout(
            title="St. Kitts & Nevis Homicide Rate Trends (MacroTrends Data)",
            xaxis_title="Year",
            yaxis_title="Homicides per 100,000 Population",
            template="plotly_dark",
            height=500,
            paper_bgcolor='black',
            plot_bgcolor='#0f172a'
        )
        
        return fig
    
    elif chart_type == "recent_crime_totals":
        # Recent total crime trends
        years = ["2022", "2023", "2024"]
        crimes = [
            MACROTRENDS_DATA["recent_trends"]["2022_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2023_total_crimes"],
            MACROTRENDS_DATA["recent_trends"]["2024_total_crimes"]
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=years, y=crimes,
            marker_color='#1d4ed8',
            text=[f"{crime:,}" for crime in crimes],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Total Crime Trends 2022-2024 (RSCNPF Data)",
            xaxis_title="Year",
            yaxis_title="Total Crimes",
            template="plotly_dark",
            height=500,
            paper_bgcolor='black',
            plot_bgcolor='#0f172a'
        )
        
        return fig
    
    elif chart_type == "international_context":
        # International comparison chart
        categories = ["St. Kitts 2020", "St. Kitts 2019", "St. Kitts 2018", "Global Avg.", "St. Kitts Peak (2011)"]
        values = [
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2020"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2019"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2018"],
            MACROTRENDS_DATA["comparative_context"]["global_average_firearm_homicides"],
            MACROTRENDS_DATA["homicide_rates_per_100k"]["2011"]
        ]
        
        colors = ['#1d4ed8', '#3b82f6', '#dc2626', '#6b7280', '#b91c1c']
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=colors,
            text=[f"{val:.1f}" for val in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="International Context: Homicide Rates per 100K Population",
            xaxis_title="Comparison Points",
            yaxis_title="Rate per 100,000",
            template="plotly_dark",
            height=500,
            paper_bgcolor='black',
            plot_bgcolor='#0f172a'
        )
        
        return fig

def is_international_comparison_query(user_input):
    """Detect if user wants international comparison or historical trends"""
    comparison_keywords = ['international', 'global', 'worldwide', 'compare', 'comparison', 'trends', 'historical', 'macrotrends', 'world average', 'per 100k', 'rate', 'historical chart', 'long term', 'decade']
    return any(keyword in user_input.lower() for keyword in comparison_keywords)

def is_casual_greeting(user_input):
    """Detect if user input is a casual greeting"""
    casual_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'sup']
    return any(word in user_input.lower().strip() for word in casual_words) and len(user_input.strip()) < 25

def is_detailed_request(user_input):
    """Detect if user wants detailed information"""
    detail_keywords = ['detailed', 'detail', 'explain', 'comprehensive', 'thorough', 'in depth', 'breakdown', 'elaborate', 'more information', 'tell me more']
    return any(keyword in user_input.lower() for keyword in detail_keywords)

def is_statistics_query(user_input):
    """Detect if user is asking about statistics"""
    stats_keywords = ['statistics', 'stats', 'data', 'crime rate', 'trends', 'numbers', 'figures', 'analysis', 'murder', 'robbery', 'larceny', 'detection rate', 'quarterly', 'annual', 'breakdown', 'comparison']
    return any(keyword in user_input.lower() for keyword in stats_keywords)

def generate_enhanced_smart_response(user_input, conversation_history=None, language='en'):
    """Generate AI responses with statistical knowledge and conversation memory"""
    
    if not st.session_state.get('ai_enabled', False):
        return "🔧 AI system offline. Please check your API key configuration.", None
    
    try:
        # Load statistical data
        stats_data = fetch_and_process_statistics()
        
        # Check if user wants a chart
        chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show me', 'display', 'trends', 'comparison']
        wants_chart = any(keyword in user_input.lower() for keyword in chart_keywords)
        chart_to_show = None
        
        # Check if this is the first interaction after a greeting
        has_greeted_before = False
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'assistant' and any(greeting in msg['content'].lower() for greeting in ['good morning', 'good afternoon', 'good evening', 'hello', 'hi']):
                    has_greeted_before = True
                    break
        
        # Handle different query types
        if is_casual_greeting(user_input) and not has_greeted_before:
            # Simple greeting response - only if we haven't greeted before
            prompt = f"""
            You are SECURO, an AI assistant for St. Kitts & Nevis Police.
            
            User said: "{user_input}"
            
            Respond with a brief, friendly greeting (2-3 sentences max). Mention you're ready to help with questions about crime statistics or general assistance.
            Include the appropriate time-based greeting (good morning/afternoon/evening) based on the current time.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        elif is_casual_greeting(user_input) and has_greeted_before:
            # Don't repeat greeting, just acknowledge
            prompt = f"""
            You are SECURO, an AI assistant for St. Kitts & Nevis Police.
            
            User said: "{user_input}"
            The user has already been greeted earlier in this conversation.
            
            Respond with a brief acknowledgment WITHOUT repeating any greeting. Just ask how you can help or what they'd like to know about.
            Keep it to 1-2 sentences.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        elif is_statistics_query(user_input) or is_international_comparison_query(user_input) or wants_chart:
            # Statistics-focused response with actual data AND chart generation
            is_detailed = is_detailed_request(user_input)
            is_comparison = is_international_comparison_query(user_input)
            
            # Determine which chart to show
            if wants_chart:
                if 'international' in user_input.lower() or 'global' in user_input.lower() or 'world' in user_input.lower():
                    chart_to_show = "international"
                elif 'trend' in user_input.lower() or 'over time' in user_input.lower() or 'years' in user_input.lower():
                    chart_to_show = "trends"
                elif 'detection' in user_input.lower():
                    chart_to_show = "detection"
                elif 'breakdown' in user_input.lower() or 'types' in user_input.lower():
                    chart_to_show = "breakdown"
                elif 'manslaughter' in user_input.lower() or 'murder' in user_input.lower() or 'homicide' in user_input.lower():
                    chart_to_show = "homicide"
                else:
                    chart_to_show = "trends"  # Default to trends
            
            # Include conversation context
            context = ""
            if conversation_history and len(conversation_history) > 1:
                recent_messages = conversation_history[-4:]  # Last 4 messages for context
                context = "Recent conversation context:\n"
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content'][:100]}...\n"
                context += "\n"
            
            # Add MacroTrends data for comparison queries
            macrotrends_context = ""
            if is_comparison:
                macrotrends_context = f"""
                
                **MacroTrends International Data Available:**
                {json.dumps(MACROTRENDS_DATA, indent=2)}
                """
            
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force with access to comprehensive crime statistics AND international comparison data.
            
            {context}User query: "{user_input}"
            Detailed request: {is_detailed}
            International comparison requested: {is_comparison}
            Chart requested: {wants_chart}
            
            **Available Local Statistical Data:**
            {json.dumps(stats_data, indent=2)}
            {macrotrends_context}
            
            **Response Guidelines:**
            - NEVER say "Good morning", "Good afternoon", or "Good evening" in your response unless the user just greeted you for the first time
            - If detailed=False: Keep response concise (3-5 sentences) but data-rich
            - If detailed=True: Provide comprehensive statistical analysis
            - If comparison=True: Include international context, MacroTrends data
            - If chart requested: Say "I'll display the requested chart below" and provide data analysis
            - NEVER mention limitations about displaying charts - you CAN display interactive charts
            - Use specific numbers and percentages from the data above
            - Reference time periods (Q2 2025, H1 2024, etc.) when relevant
            - Include comparisons and trends when available
            - When discussing international comparisons, reference the MacroTrends data
            - Maintain professional law enforcement communication
            - Focus on actionable insights for police operations
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            
            Provide data-driven statistical analysis with specific figures and international context when relevant.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), chart_to_show
            
        else:
            # General query with conversation context
            is_detailed = is_detailed_request(user_input)
            
            # Include conversation context
            context = ""
            if conversation_history and len(conversation_history) > 1:
                recent_messages = conversation_history[-6:]  # Last 6 messages for context
                context = "Conversation history for context:\n"
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content'][:150]}...\n"
                context += "\n"
            
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force.
            
            {context}Current user query: "{user_input}"
            Detailed request: {is_detailed}
            
            **Response Guidelines:**
            - NEVER say "Good morning", "Good afternoon", or "Good evening" in your response unless the user just greeted you for the first time
            - If detailed=False: Keep response concise (3-5 sentences)
            - If detailed=True: Provide thorough explanation
            - Maintain conversation context and reference previous messages when relevant
            - Provide professional assistance suitable for law enforcement
            - Include practical recommendations when appropriate
            - You have access to crime statistics and can generate charts if asked
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            
            Provide helpful, context-aware assistance.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
            
    except Exception as e:
        return f"🚨 AI analysis error: {str(e)}\n\nI'm still here to help! Please try rephrasing your question or check your internet connection.", None

# Initialize AI model
try:
    GOOGLE_API_KEY = "AIzaSyBYRyEfONMUHdYmeFDkUGSTP1rNEy_p2L0"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Active with Statistical Knowledge"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - Modern AI Crime Intelligence System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize statistics on startup
fetch_and_process_statistics()

# Initialize chat system only if needed
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

# UPDATED CSS - Royal Blue, Red, Black Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Root styling - Royal Blue/Red/Black Theme */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #0f172a 30%, #1e293b 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Sidebar styling - Law Enforcement Professional */
    .css-1d391kg {
        background: linear-gradient(180deg, #000000 0%, #1e293b 50%, #000000 100%) !important;
        border-right: 3px solid transparent !important;
        background-clip: padding-box !important;
        position: relative !important;
    }
    
    .css-1d391kg::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #1d4ed8, #dc2626, #1d4ed8, #dc2626);
        background-size: 100% 400%;
        animation: sidebar-border-pulse 2s ease-in-out infinite;
    }
    
    @keyframes sidebar-border-pulse {
        0%, 100% { background-position: 0% 0%; }
        50% { background-position: 0% 100%; }
    }
    
    /* Sidebar navigation header */
    .sidebar-nav-header {
        background: linear-gradient(45deg, #1d4ed8, #dc2626, #1d4ed8);
        background-size: 300% 300%;
        animation: gradient-move 3s ease infinite;
        margin: -1rem -1rem 1rem -1rem;
        padding: 16px 20px;
        border-radius: 0 0 12px 12px;
        text-align: center;
        font-weight: 700;
        font-size: 18px;
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        letter-spacing: 2px;
        text-transform: uppercase;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    @keyframes gradient-move {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Main content area */
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
    }
    
    /* Enhanced Header bar - Professional law enforcement */
    .header-bar {
        background: linear-gradient(135deg, #000000 0%, #1e293b 50%, #000000 100%);
        border-bottom: 3px solid #1d4ed8;
        border-top: 3px solid #dc2626;
        padding: 16px 32px;
        margin: -1rem -2rem 2rem -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .logo-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(45deg, #1d4ed8, #dc2626);
        background-size: 300% 300%;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        animation: logo-pulse 2s ease-in-out infinite;
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 20px rgba(29, 78, 216, 0.3);
    }
    
    @keyframes logo-pulse {
        0%, 100% { 
            background-position: 0% 50%;
            box-shadow: 0 0 30px rgba(29, 78, 216, 0.4);
            transform: scale(1);
        }
        50% { 
            background-position: 100% 50%;
            box-shadow: 0 0 30px rgba(220, 38, 38, 0.4);
            transform: scale(1.05);
        }
    }
    
    .logo-text h1 {
        color: #ffffff !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: 3px;
        text-shadow: 0 2px 8px rgba(29, 78, 216, 0.5);
        animation: text-glow 3s ease-in-out infinite;
    }
    
    @keyframes text-glow {
        0%, 100% { 
            color: #ffffff !important;
            text-shadow: 0 2px 8px rgba(29, 78, 216, 0.5);
        }
        50% { 
            color: #ffffff !important;
            text-shadow: 0 2px 8px rgba(220, 38, 38, 0.5);
        }
    }
    
    .logo-text p {
        color: #9ca3af !important;
        font-size: 14px !important;
        margin: 0 !important;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    .status-section {
        display: flex;
        align-items: center;
        gap: 24px;
        font-size: 14px;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #d1d5db;
        font-weight: 500;
    }
    
    .status-dot {
        width: 10px;
        height: 10px;
        background: linear-gradient(45deg, #1d4ed8, #dc2626);
        border-radius: 50%;
        animation: dot-pulse 2s infinite;
        box-shadow: 0 0 10px rgba(29, 78, 216, 0.5);
    }
    
    @keyframes dot-pulse {
        0%, 100% { 
            background: linear-gradient(45deg, #1d4ed8, #dc2626);
            box-shadow: 0 0 10px rgba(29, 78, 216, 0.5);
        }
        50% { 
            background: linear-gradient(45deg, #dc2626, #1d4ed8);
            box-shadow: 0 0 10px rgba(220, 38, 38, 0.5);
        }
    }
    
    /* Enhanced Chat interface styling - Professional Police Theme */
    .chat-container {
        background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
        border: 2px solid #1d4ed8;
        border-radius: 20px;
        overflow: hidden;
        height: auto;
        display: flex;
        flex-direction: column;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .chat-header {
        background: linear-gradient(135deg, #1d4ed8 0%, #dc2626 100%);
        padding: 20px 24px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .chat-header h3 {
        color: #ffffff !important;
        margin: 0 !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .ai-status {
        color: #ffffff !important;
        font-size: 14px !important;
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        min-height: 300px;
        max-height: 600px;
        background: linear-gradient(180deg, #000000 0%, #0f172a 100%);
    }
    
    .message {
        display: flex;
        flex-direction: column;
        animation: messageSlide 0.4s ease-out;
        margin-bottom: 12px;
        width: auto;
        max-width: 85%;
    }
    
    @keyframes messageSlide {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* User messages - Royal Blue theme */
    .message.user {
        align-self: flex-end;
        margin-left: auto;
        width: fit-content;
        min-width: auto;
        max-width: 75%;
    }
    
    .message.user .message-bubble {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        color: white;
        border-radius: 20px 20px 4px 20px;
        padding: 12px 18px;
        font-size: 15px;
        line-height: 1.5;
        word-wrap: break-word;
        white-space: pre-wrap;
        box-shadow: 0 4px 16px rgba(29, 78, 216, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: inline-block;
        width: auto;
        min-width: 40px;
        max-width: 100%;
        font-weight: 500;
    }
    
    /* Assistant messages - Dark theme with Red accents */
    .message.assistant {
        align-self: flex-start;
        margin-right: auto;
        width: fit-content;
        min-width: auto;
        max-width: 85%;
    }
    
    .message.assistant .message-bubble {
        background: linear-gradient(135deg, #1e293b, #374151);
        color: #f9fafb;
        border-radius: 20px 20px 20px 4px;
        padding: 12px 18px;
        font-size: 15px;
        line-height: 1.5;
        word-wrap: break-word;
        white-space: pre-wrap;
        border: 2px solid #dc2626;
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.2);
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        width: auto;
        min-width: 80px;
        max-width: 100%;
        font-weight: 500;
    }
    
    .message-content {
        flex: 1;
        margin-right: 12px;
        text-align: left;
        line-height: 1.6;
        word-wrap: break-word;
        white-space: pre-wrap;
        text-indent: 0;
        padding-left: 0;
    }
    
    .message-time {
        font-size: 11px;
        color: #6b7280;
        margin-top: 6px;
        font-weight: 500;
    }
    
    .message.user .message-time {
        text-align: right;
        color: rgba(255, 255, 255, 0.8);
    }
    
    .message.assistant .message-time {
        text-align: left;
        color: #9ca3af;
    }
    
    /* Enhanced Speaker button styling */
    .speak-button {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 6px 8px !important;
        cursor: pointer !important;
        font-size: 12px !important;
        opacity: 0.8 !important;
        transition: all 0.3s ease !important;
        border-radius: 6px !important;
        position: relative !important;
        top: -2px !important;
        flex-shrink: 0 !important;
        margin-left: 12px !important;
        align-self: flex-start !important;
        color: #ffffff !important;
        min-width: 28px !important;
        text-align: center !important;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3) !important;
    }
    
    .speak-button:hover {
        opacity: 1 !important;
        background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
        border-color: #1d4ed8 !important;
        transform: scale(1.1) !important;
        box-shadow: 0 4px 12px rgba(29, 78, 216, 0.4) !important;
    }
    
    .speak-button:active {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
        transform: scale(0.95) !important;
    }
    
    .chat-input-area {
        background: linear-gradient(135deg, #1e293b 0%, #374151 100%);
        border-top: 2px solid #dc2626;
        padding: 20px 24px;
    }
    
    /* Enhanced Auto-speak toggle button */
    .auto-speak-toggle {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        border: none !important;
        color: white !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        margin-right: 12px !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    
    .auto-speak-toggle.disabled {
        background: linear-gradient(135deg, #6b7280, #4b5563) !important;
        box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3) !important;
    }
    
    .auto-speak-toggle:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4) !important;
    }
    
    .auto-speak-toggle.disabled:hover {
        box-shadow: 0 6px 16px rgba(107, 114, 128, 0.4) !important;
    }
    
    /* Enhanced Input styling */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 2px solid #1d4ed8 !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 14px 20px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
    }
    
    .stTextInput input:focus {
        border-color: #dc2626 !important;
        box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.2) !important;
    }
    
    /* Enhanced Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #dc2626) !important;
        border: none !important;
        color: white !important;
        padding: 12px 24px !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(29, 78, 216, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(220, 38, 38, 0.4) !important;
        background: linear-gradient(135deg, #dc2626, #1d4ed8) !important;
    }
    
    /* Enhanced Sidebar button styling */
    .sidebar-nav-button {
        width: 100% !important;
        background: linear-gradient(135deg, rgba(29, 78, 216, 0.15), rgba(220, 38, 38, 0.15)) !important;
        border: 2px solid rgba(29, 78, 216, 0.4) !important;
        color: #e5e7eb !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        text-align: left !important;
        margin-bottom: 10px !important;
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    
    .sidebar-nav-button:hover {
        background: linear-gradient(135deg, rgba(29, 78, 216, 0.3), rgba(220, 38, 38, 0.3)) !important;
        border-color: #dc2626 !important;
        color: #ffffff !important;
        transform: translateX(6px) !important;
        box-shadow: 0 6px 16px rgba(220, 38, 38, 0.3) !important;
    }
    
    .sidebar-nav-button.active {
        background: linear-gradient(135deg, #1d4ed8, #dc2626) !important;
        border-color: transparent !important;
        color: #ffffff !important;
        box-shadow: 0 6px 16px rgba(29, 78, 216, 0.4) !important;
    }
    
    /* Enhanced Card styling */
    .info-card {
        background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
        border: 2px solid #1d4ed8;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    
    .info-card:hover {
        border-color: #dc2626;
        box-shadow: 0 12px 32px rgba(220, 38, 38, 0.2);
        transform: translateY(-4px);
    }
    
    .info-card h3 {
        color: #1d4ed8 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        margin-bottom: 12px !important;
        text-shadow: 0 2px 4px rgba(29, 78, 216, 0.3);
    }
    
    .info-card p {
        color: #d1d5db !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        margin: 0 !important;
        font-weight: 500;
    }
    
    /* Enhanced Emergency card styling */
    .emergency-card {
        background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
        border: 2px solid #dc2626;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.2);
    }
    
    .emergency-card:hover {
        border-color: #1d4ed8;
        box-shadow: 0 12px 32px rgba(29, 78, 216, 0.3);
        transform: translateY(-2px);
    }
    
    .emergency-number {
        color: #dc2626 !important;
        font-size: 20px !important;
        font-weight: bold !important;
        margin: 10px 0 !important;
        text-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);
    }
    
    /* Enhanced Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
        border: 2px solid #1d4ed8;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #dc2626;
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(220, 38, 38, 0.2);
    }
    
    .metric-value {
        color: #1d4ed8 !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        margin-bottom: 6px !important;
        text-shadow: 0 2px 8px rgba(29, 78, 216, 0.4);
    }
    
    .metric-label {
        color: #9ca3af !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Enhanced Analytics cards */
    .analytics-card {
        background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
        border-left: 4px solid #1d4ed8;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .analytics-card:hover {
        transform: translateX(4px);
        box-shadow: 0 12px 32px rgba(29, 78, 216, 0.2);
    }
    
    .analytics-card.high-risk {
        border-left-color: #dc2626;
    }
    
    .analytics-card.high-risk:hover {
        box-shadow: 0 12px 32px rgba(220, 38, 38, 0.2);
    }
    
    .analytics-card.medium-risk {
        border-left-color: #1d4ed8;
    }
    
    .analytics-card.low-risk {
        border-left-color: #0f172a;
    }
    
    .analytics-title {
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }
    
    .analytics-value {
        color: #9ca3af !important;
        font-size: 13px !important;
        margin-bottom: 6px !important;
        font-weight: 500;
    }
    
    /* Enhanced Status bar */
    .status-bar {
        background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
        border-top: 3px solid #1d4ed8;
        padding: 16px 32px;
        margin: 2rem -2rem -1rem -2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .status-indicators {
        display: flex;
        gap: 24px;
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #9ca3af;
        font-weight: 500;
    }
    
    .status-indicator.active {
        color: #1d4ed8;
        font-weight: 600;
    }
    
    /* Enhanced Main content sections */
    .main-content-section {
        background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
        border: 2px solid #1d4ed8;
        border-radius: 20px;
        padding: 32px;
        margin-bottom: 32px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    
    .section-header {
        color: #1d4ed8 !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
        display: flex;
        align-items: center;
        gap: 16px;
        text-shadow: 0 2px 8px rgba(29, 78, 216, 0.3);
    }
    
    .section-content {
        color: #d1d5db !important;
        line-height: 1.7 !important;
        font-weight: 500;
    }
    
    /* Enhanced Responsive design */
    @media (max-width: 768px) {
        .header-bar {
            flex-direction: column;
            gap: 16px;
            padding: 16px;
        }
        
        .status-section {
            flex-direction: column;
            gap: 12px;
        }
        
        .chat-container {
            height: 600px;
        }
        
        .logo-text h1 {
            font-size: 24px !important;
        }
    }
    
    /* Enhanced Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #000000;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #1d4ed8, #dc2626);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #dc2626, #1d4ed8);
    }
    
    /* Enhanced Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    p, span, div, li {
        color: #d1d5db !important;
        font-weight: 500;
    }
    
    /* Enhanced Welcome screen styling */
    .welcome-container {
        background: linear-gradient(135deg, #000000 0%, #1e293b 50%, #000000 100%);
        border: 3px solid #1d4ed8;
        border-radius: 24px;
        padding: 48px 32px;
        text-align: center;
        margin: 32px 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
    }
    
    .welcome-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, 
            rgba(29, 78, 216, 0.1), 
            rgba(220, 38, 38, 0.1), 
            rgba(29, 78, 216, 0.1));
        z-index: -1;
        animation: gradient-shift 6s ease-in-out infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { 
            background: linear-gradient(45deg, 
                rgba(29, 78, 216, 0.1), 
                rgba(220, 38, 38, 0.1), 
                rgba(29, 78, 216, 0.1));
        }
        50% { 
            background: linear-gradient(45deg, 
                rgba(220, 38, 38, 0.1), 
                rgba(29, 78, 216, 0.1), 
                rgba(220, 38, 38, 0.1));
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Header Bar
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="header-bar">
    <div class="logo-section">
        <div class="logo-icon">🛡️</div>
        <div class="logo-text">
            <h1>SECURO</h1>
            <p>Crime Intelligence System</p>
        </div>
    </div>
    <div class="status-section">
        <div class="status-item">
            <div class="status-dot"></div>
            <span>Royal St. Christopher & Nevis Police Force</span>
        </div>
        <div class="status-item">
            <span>{current_date} | {current_time} AST</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    # Enhanced animated navigation header
    st.markdown("""
    <div class="sidebar-nav-header">
        🚔 NAVIGATION 🚔
    </div>
    """, unsafe_allow_html=True)
    
    # Main navigation buttons - now set main_view instead of sidebar_view
    if st.button("🏠 Home", key="nav_home", help="System Overview", use_container_width=True):
        st.session_state.main_view = 'home'
        st.rerun()
    
    if st.button("ℹ️ About", key="nav_about", help="About SECURO", use_container_width=True):
        st.session_state.main_view = 'about'
        st.rerun()
    
    if st.button("📊 Analytics", key="nav_analytics", help="Crime Analytics", use_container_width=True):
        st.session_state.main_view = 'analytics'
        st.rerun()
    
    if st.button("📝 History", key="nav_history", help="Chat History", use_container_width=True):
        st.session_state.main_view = 'history'
        st.rerun()
    
    if st.button("🗺️ Crime Map", key="nav_map", help="Crime Hotspots", use_container_width=True):
        st.session_state.main_view = 'hotspots'
        st.rerun()
    
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts", use_container_width=True):
        st.session_state.main_view = 'emergency'
        st.rerun()
    
    st.markdown("---")
    
    # Quick return to AI Assistant
    if st.session_state.main_view not in ['ai-assistant', 'hotspots']:
        if st.button("🤖 Back to AI Assistant", key="back_to_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    # Quick access to Crime Map from any view
    if st.session_state.main_view != 'hotspots':
        if st.button("🗺️ View Crime Map", key="quick_map_access", use_container_width=True):
            st.session_state.main_view = 'hotspots'
            st.rerun()
    
    st.markdown("---")
    
    # AI status section
    if st.session_state.get('ai_enabled', False):
        st.success("🟢 Enhanced AI Online")
        st.markdown("""
        **Capabilities:**
        - 🧠 Statistical knowledge integration
        - 💭 Conversation memory
        - 🎯 Context-aware responses
        - 📈 Crime data analysis
        - 👮 Professional assistance
        - 🔊 Text-to-Speech features
        """)
    else:
        st.error("🔴 AI Offline")
        st.write("Please check your API key configuration")
    
    st.markdown("---")
    
    # Enhanced quick stats with royal blue/red theme
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(29, 78, 216, 0.15), rgba(220, 38, 38, 0.15)); 
                border: 2px solid #dc2626; border-radius: 12px; padding: 16px;">
        <div style="color: #dc2626; font-weight: 700; margin-bottom: 12px; text-align: center; font-size: 16px;">
            🛡️ SYSTEM STATUS
        </div>
        <div style="color: #e5e7eb; font-size: 14px; line-height: 1.8;">
            <div>🟢 Active Chats: <strong style="color: #1d4ed8;">{len(st.session_state.chat_sessions)}</strong></div>
            <div>🟢 Database: <strong style="color: #10b981;">Loaded</strong></div>
            <div>🟢 API Status: <strong style="color: #10b981;">Online</strong></div>
            <div>🔊 Auto-Speak: <strong style="color: #{'#10b981' if st.session_state.get('auto_speak_enabled', False) else '#dc2626'};">{'ON' if st.session_state.get('auto_speak_enabled', False) else 'OFF'}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Content Area - Now handles all the different views
if st.session_state.main_view == 'home':
    # System Overview - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header">🏠 System Overview</h2>
        <div class="section-content">
            <p>Welcome to SECURO - the enhanced comprehensive crime analysis system with professional law enforcement colors, 
            statistical integration, conversation memory, and advanced AI capabilities built 
            specifically for the Royal St. Christopher and Nevis Police Force.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards in main area
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🤖 Enhanced AI</h3>
            <p>Statistical knowledge, memory, and context-aware responses with professional law enforcement styling.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Center the start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Conversation", key="start_chat", use_container_width=True):
                create_new_chat_session()
                st.session_state.chat_active = True
                st.success("✅ New chat session created! You can now start chatting with SECURO AI!")
                st.rerun()
        
        # Voice status indicator with browser check
        st.markdown(f"""
        <div style="text-align: center; margin-top: 32px;">
            <div style="display: inline-block; padding: 16px 32px; background: rgba(16, 185, 129, 0.15); 
                        border: 2px solid #10b981; border-radius: 12px;">
                <div style="color: #10b981; font-size: 16px; font-weight: 700;">🔊 TTS FEATURES AVAILABLE</div>
                <div style="color: #9ca3af; font-size: 13px; margin-top: 6px; font-weight: 500;">
                    Text-to-Speech • Auto-Speak: {'ON' if st.session_state.get('auto_speak_enabled', False) else 'OFF'} • Individual Message Speech
                </div>
            </div>
        </div>
        
        <script>
        // Check TTS support and notify user
        setTimeout(function() {{
            if (!('speechSynthesis' in window)) {{
                console.warn('Text-to-speech not supported in this browser');
            }} else {{
                console.log('Text-to-speech is supported');
            }}
        }}, 500);
        </script>
        """, unsafe_allow_html=True)
    
    else:
        # Chat interface - Enhanced with new theme
        st.markdown("""
        <div style="background: linear-gradient(135deg, #000000 0%, #1e293b 100%); 
                    border: 2px solid #1d4ed8; border-radius: 20px; padding: 20px; margin-bottom: 20px;
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h3 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 700;">🤖 SECURO AI</h3>
                    <div style="color: #10b981; font-size: 15px; margin-top: 6px; font-weight: 600;">
                        <span style="color: #10b981;">●</span>
                        Online with Statistical Knowledge & Enhanced TTS
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat controls with auto-speak toggle - Enhanced layout
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🆕 New Chat", key="new_chat_btn", use_container_width=True):
                create_new_chat_session()
                st.rerun()
        
        with col2:
            if st.button("← Welcome", key="back_welcome", use_container_width=True):
                st.session_state.chat_active = False
                st.rerun()
        
        with col3:
            # Auto-speak toggle button
            auto_speak_text = "🔊 Auto-Speak: ON" if st.session_state.get('auto_speak_enabled', False) else "🔇 Auto-Speak: OFF"
            if st.button(auto_speak_text, key="toggle_auto_speak", use_container_width=True):
                st.session_state.auto_speak_enabled = not st.session_state.get('auto_speak_enabled', False)
                if st.session_state.auto_speak_enabled:
                    st.success("🔊 Auto-speak enabled! New responses will be read aloud automatically.")
                else:
                    st.info("🔇 Auto-speak disabled. Use individual 🔊 buttons to hear messages.")
                st.rerun()
        
        # Current chat info - Enhanced
        current_chat = get_current_chat()
        auto_speak_status = "🔊 ON" if st.session_state.get('auto_speak_enabled', False) else "🔇 OFF"
        st.info(f"**Current Session:** {current_chat['name']} | **Auto-Speak:** {auto_speak_status}")
        
        # Display messages
        messages = current_chat['messages']
        
        # Initialize with welcome message if no messages
        if not messages:
            welcome_msg = {
                "role": "assistant",
                "content": "🛡️ Enhanced SECURO AI System Online!\n\nI now have access to comprehensive St. Kitts & Nevis crime statistics, international comparison data from MacroTrends, and can maintain conversation context. Ask me about:\n\n• Local crime trends and detection rates\n• International comparisons and global context\n• Historical data analysis with charts\n• Specific incidents or general questions\n\nI can show interactive charts for international comparisons! 🔊 Click the speaker buttons to hear any message read aloud.",
                "timestamp": get_stkitts_time()
            }
            messages.append(welcome_msg)
            current_chat['messages'] = messages
        
        # Messages container - Enhanced styling
        for i, message in enumerate(messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message user">
                    <div class="message-bubble">{message["content"]}</div>
                    <div class="message-time">You • {message["timestamp"]} AST</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                clean_content = str(message["content"]).strip()
                clean_content = re.sub(r'<[^>]+>', '', clean_content)
                clean_content = clean_content.replace('```', '')
                # Preserve bullet points but fix spacing issues
                clean_content = re.sub(r'  +', ' ', clean_content)
                clean_content = re.sub(r'\n +•', '\n•', clean_content)
                clean_content = re.sub(r'• +', '• ', clean_content)
                
                # Create message container with native Streamlit button
                col1, col2 = st.columns([6, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="message assistant">
                        <div class="message-bubble">
                            <div class="message-content">{clean_content}</div>
                        </div>
                        <div class="message-time">
                            SECURO • {message["timestamp"]} AST
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Use Streamlit's native button for TTS
                    if st.button("🔊", key=f"speak_{i}_{message['timestamp']}", help="Click to speak this message"):
                        # Simple JavaScript injection for immediate TTS
                        clean_speech_text = clean_text_for_speech(message["content"])
                        tts_script = f"""
                        <script>
                        if ('speechSynthesis' in window) {{
                            window.speechSynthesis.cancel();
                            setTimeout(() => {{
                                const utterance = new SpeechSynthesisUtterance('{clean_speech_text.replace("'", "\\'")}');
                                utterance.rate = 0.8;
                                utterance.volume = 0.9;
                                window.speechSynthesis.speak(utterance);
                            }}, 100);
                        }}
                        </script>
                        """
                        st.components.v1.html(tts_script, height=0)
        
        # Chat input - Enhanced
        st.markdown("---")
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Message Enhanced AI Assistant:",
                placeholder="Type your question about crime statistics, trends, or analysis...",
                label_visibility="collapsed",
                key="chat_input"
            )
            
            submitted = st.form_submit_button("📤 Send", type="primary")
            
            if submitted and user_input and user_input.strip():
                current_time = get_stkitts_time()
                
                # Add user message to current chat
                add_message_to_chat("user", user_input)
                
                # Generate response with conversation history and statistics
                with st.spinner("🧠 Generating enhanced AI response with statistical knowledge..."):
                    response, chart_type = generate_enhanced_smart_response(
                        user_input, 
                        conversation_history=current_chat['messages'],
                        language='en'
                    )
                
                # Add assistant response to current chat
                add_message_to_chat("assistant", response)
                
                # Store chart type in session state to persist after rerun
                if chart_type:
                    st.session_state.show_chart = chart_type
                
                # Store the response for auto-speak (only if enabled)
                if st.session_state.get('auto_speak_enabled', False):
                    st.session_state.last_response = response
                
                st.rerun()
        
        # Auto-speak the last response if enabled (Enhanced approach)
        if st.session_state.get('last_response') and st.session_state.get('auto_speak_enabled', False):
            clean_speech_text = clean_text_for_speech(st.session_state.last_response)
            if clean_speech_text:
                auto_speak_script = f"""
                <script>
                setTimeout(function() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        setTimeout(() => {{
                            const utterance = new SpeechSynthesisUtterance('{clean_speech_text.replace("'", "\\'")}');
                            utterance.rate = 0.8;
                            utterance.volume = 0.9;
                            window.speechSynthesis.speak(utterance);
                        }}, 200);
                    }}
                }}, 1000);
                </script>
                """
                st.components.v1.html(auto_speak_script, height=0)
            # Clear the response to avoid re-speaking
            st.session_state.last_response = None
        
        # Display charts after the rerun (Enhanced styling)
        if st.session_state.get('show_chart'):
            st.markdown("### 📊 Requested Chart")
            chart_type = st.session_state.show_chart
            
            if chart_type == "international":
                # Show international comparison charts
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fig = create_macrotrends_comparison_charts("homicide_trends")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = create_macrotrends_comparison_charts("international_context")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    fig = create_macrotrends_comparison_charts("recent_crime_totals")
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "trends":
                # Show crime trends
                st_kitts_data = []
                periods = []
                
                # Extract St. Kitts data from the database
                for period_key in ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']:
                    if period_key in HISTORICAL_CRIME_DATABASE:
                        period_data = HISTORICAL_CRIME_DATABASE[period_key]
                        periods.append(period_data["period"])
                        st_kitts_crimes = period_data.get('st_kitts', {}).get('crimes', 0)
                        st_kitts_data.append(st_kitts_crimes)
                
                # Create bar chart for St. Kitts crime trends
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=periods,
                    y=st_kitts_data,
                    marker_color='#1d4ed8',
                    text=[f"{crimes}" for crimes in st_kitts_data],
                    textposition='auto',
                    name='St. Kitts Crimes'
                ))
                
                fig.update_layout(
                    title="St. Kitts Crime Trends - Recent Years",
                    xaxis_title="Time Period",
                    yaxis_title="Number of Crimes",
                    template="plotly_dark",
                    height=500,
                    showlegend=False,
                    paper_bgcolor='black',
                    plot_bgcolor='#0f172a'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "homicide":
                # Show homicide trends
                fig = create_macrotrends_comparison_charts("homicide_trends")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Add button to clear the chart
            if st.button("🗑️ Clear Chart", key="clear_chart"):
                st.session_state.show_chart = None
                st.rerun()

elif st.session_state.main_view == 'hotspots':
    # Crime Hotspots Map - Enhanced
    st.markdown("""
    <div style="background: linear-gradient(135deg, #000000 0%, #1e293b 100%); 
                border: 2px solid #1d4ed8; border-radius: 20px; padding: 20px; margin-bottom: 20px;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);">
        <h3 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 700;">🗺️ Crime Hotspot Map - St. Kitts & Nevis</h3>
        <p style="color: #9ca3af; font-size: 15px; margin: 10px 0 0 0; font-weight: 500;">Interactive crime analysis with real-time data overlays</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        crime_map = create_crime_hotspot_map()
        map_data = st_folium(
            crime_map,
            width="100%",
            height=500,
            returned_objects=["last_object_clicked_tooltip", "last_clicked"],
            key="crime_hotspot_map"
        )
        
        if map_data['last_object_clicked_tooltip']:
            clicked_info = map_data['last_object_clicked_tooltip']
            st.info(f"📍 **Last Clicked Location:** {clicked_info}")
    
    except Exception as e:
        st.error(f"❌ Map Error: {str(e)}")
    
    # Hotspot summary metrics - Enhanced
    st.markdown("### 📊 Hotspot Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #000000 0%, #1e293b 100%); 
                    border-left: 4px solid #dc2626; border-radius: 12px; padding: 20px; text-align: center;
                    box-shadow: 0 8px 24px rgba(220, 38, 38, 0.2);">
            <div style="color: #dc2626; font-size: 28px; font-weight: 800; margin-bottom: 6px;">109</div>
            <div style="color: #9ca3af; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">High Risk Crimes</div>
            <div style="color: #9ca3af; font-size: 13px; margin-top: 6px; font-weight: 500;">3 Areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #000000 0%, #1e293b 100%); 
                    border-left: 4px solid #1d4ed8; border-radius: 12px; padding: 20px; text-align: center;
                    box-shadow: 0 8px 24px rgba(29, 78, 216, 0.2);">
            <div style="color: #1d4ed8; font-size: 28px; font-weight: 800; margin-bottom: 6px;">133</div>
            <div style="color: #9ca3af; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Medium Risk Crimes</div>
            <div style="color: #9ca3af; font-size: 13px; margin-top: 6px; font-weight: 500;">6 Areas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #000000 0%, #1e293b 100%); 
                    border-left: 4px solid #0f172a; border-radius: 12px; padding: 20px; text-align: center;
                    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);">
            <div style="color: #0f172a; font-size: 28px; font-weight: 800; margin-bottom: 6px;">60</div>
            <div style="color: #9ca3af; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Low Risk Crimes</div>
            <div style="color: #9ca3af; font-size: 13px; margin-top: 6px; font-weight: 500;">4 Areas</div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Default view - Enhanced Navigation prompts
    # Main navigation tabs
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("🤖 SECURO AI", key="main_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    with col2:
        if st.button("🗺️ Crime Hotspots", key="main_map", use_container_width=True):
            st.session_state.main_view = 'hotspots'
            st.rerun()
    
    # Welcome message if no specific view is selected - Enhanced
    st.markdown("""
    <div style="text-align: center; padding: 60px 32px; background: linear-gradient(135deg, #000000 0%, #1e293b 100%);
                border: 2px solid #1d4ed8; border-radius: 20px; margin: 32px 0;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);">
        <h2 style="color: #1d4ed8; font-size: 2.5rem; font-weight: 800; margin-bottom: 16px;">🛡️ Welcome to SECURO</h2>
        <p style="color: #9ca3af; font-size: 1.1rem; font-weight: 500;">Choose an option above to get started with the enhanced crime intelligence system</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Status Bar - Royal Blue/Red/Black theme
current_time = get_stkitts_time()
total_chats = len(st.session_state.chat_sessions)
auto_speak_status = "ON" if st.session_state.get('auto_speak_enabled', False) else "OFF"

st.markdown(f"""
<div class="status-bar">
    <div class="status-indicators">
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>🧠 Enhanced AI Active</span>
        </div>
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>🛡️ Professional Theme: Active</span>
        </div>
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>💭 Conversation Memory: Enabled</span>
        </div>
        <div class="status-indicator active">
            <div class="status-dot"></div>
            <span>🔊 TTS Available (Auto: {auto_speak_status})</span>
        </div>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span>💬 Chat Sessions: {total_chats}</span>
        </div>
    </div>
    <div class="status-indicator">
        <span>🕒 {current_time} AST</span>
    </div>
</div>
""", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>📊 Real-Time Statistics</h3>
            <p>Integrated crime data and international comparisons from MacroTrends.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>💭 Conversation Memory</h3>
            <p>Context preservation across chat sessions with full history management.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick access buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🤖 Start Chat", key="quick_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    with col2:
        if st.button("🗺️ View Crime Map", key="quick_map", use_container_width=True):
            st.session_state.main_view = 'hotspots'
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", key="quick_analytics", use_container_width=True):
            st.session_state.main_view = 'analytics'
            st.rerun()

elif st.session_state.main_view == 'about':
    # About SECURO - Main Screen
    st.markdown("## ℹ️ About SECURO")
    
    st.markdown("""
    **SECURO** is an enhanced comprehensive crime analysis system with professional law enforcement colors, 
    statistical integration, conversation memory, and advanced AI capabilities built 
    specifically for the Royal St. Christopher and Nevis Police Force.
    """)
    
    st.markdown("### 🌟 Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **💭 Conversation Memory:** Full context preservation across chat sessions
        - **📊 Statistical Knowledge Integration:** Real-time access to crime data  
        - **🧠 Context-Aware Responses:** Intelligent understanding of conversation flow
        - **💬 Multi-Chat Management:** Organize multiple conversation sessions
        - **📈 Real-time Crime Data:** Up-to-date statistics and analysis
        """)
    
    with col2:
        st.markdown("""
        - **🛡️ Professional Law Enforcement Theme:** Royal blue, red, and black aesthetics
        - **🔊 Text-to-Speech Features:** Audio accessibility and hands-free operation
        - **🗺️ Interactive Crime Maps:** Visual hotspot analysis
        - **🌍 International Comparisons:** Global context and trending
        - **📊 Advanced Analytics:** Charts, trends, and data visualization
        """)
    
    st.markdown("### 📊 Data Coverage")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Crime Statistics:**
        - 2022-2025 annual data
        - Quarterly reports
        - Detection rates
        - Crime type breakdowns
        """)
    
    with col2:
        st.markdown("""
        **International Data:**
        - MacroTrends comparisons
        - Global homicide rates
        - Regional analysis
        - Historical trends
        """)
    
    with col3:
        st.markdown("""
        **Geographic Data:**
        - 13 hotspot locations
        - Risk level mapping
        - St. Kitts & Nevis coverage
        - Interactive visualizations
        """)
    
    # Quick access buttons
    st.markdown("### 🚀 Quick Access")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🤖 SECURO AI", key="about_ai", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    
    with col2:
        if st.button("🗺️ Crime Map", key="about_map", use_container_width=True):
            st.session_state.main_view = 'hotspots'
            st.rerun()
    
    with col3:
        if st.button("📊 Analytics", key="about_analytics", use_container_width=True):
            st.session_state.main_view = 'analytics'
            st.rerun()
    
    with col4:
        if st.button("🚨 Emergency Info", key="about_emergency", use_container_width=True):
            st.session_state.main_view = 'emergency'
            st.rerun()

elif st.session_state.main_view == 'analytics':
    # Crime Analytics - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header">📊 Crime Analytics Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Analytics cards in main area
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="analytics-card high-risk">
            <div class="analytics-title">⚠️ High Risk Areas (3)</div>
            <div class="analytics-value">Basseterre Central, Molineux, Tabernacle</div>
            <div class="analytics-value"><strong>Total: 109 crimes</strong></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="analytics-card medium-risk">
            <div class="analytics-title">🔶 Medium Risk Areas (6)</div>
            <div class="analytics-value">Cayon, Newton Ground, Old Road</div>
            <div class="analytics-value"><strong>Total: 133 crimes</strong></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="analytics-card low-risk">
            <div class="analytics-title">✅ Low Risk Areas (4)</div>
            <div class="analytics-value">Sandy Point, Dieppe Bay</div>
            <div class="analytics-value"><strong>Total: 60 crimes</strong></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent trends section
    st.markdown("""
    <div class="main-content-section">
        <h3 class="section-header">📈 Recent Trends</h3>
        <div class="section-content">
            <ul>
                <li><strong>75% decrease in murders</strong> from 2024 to 2025 H1</li>
                <li><strong>Detection rates improving</strong> across most crime categories</li>
                <li><strong>Drug crimes up 463%</strong> indicating increased enforcement</li>
                <li><strong>Larcenies remain highest volume crime</strong> requiring focused attention</li>
                <li><strong>Federation-wide trends</strong> showing mixed but generally positive results</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive chart section
    st.markdown("### 📊 Interactive Analytics")
    
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["📈 Crime Trends", "🌍 International Comparison", "🎯 Detection Rates"])
    
    with chart_tab1:
        # Show crime trends
        st_kitts_data = []
        periods = []
        
        # Extract St. Kitts data from the database
        for period_key in ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']:
            if period_key in HISTORICAL_CRIME_DATABASE:
                period_data = HISTORICAL_CRIME_DATABASE[period_key]
                periods.append(period_data["period"])
                st_kitts_crimes = period_data.get('st_kitts', {}).get('crimes', 0)
                st_kitts_data.append(st_kitts_crimes)
        
        # Create bar chart for St. Kitts crime trends
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=periods,
            y=st_kitts_data,
            marker_color='#1d4ed8',
            text=[f"{crimes}" for crimes in st_kitts_data],
            textposition='auto',
            name='St. Kitts Crimes'
        ))
        
        fig.update_layout(
            title="St. Kitts Crime Trends - Recent Years",
            xaxis_title="Time Period",
            yaxis_title="Number of Crimes",
            template="plotly_dark",
            height=500,
            showlegend=False,
            paper_bgcolor='black',
            plot_bgcolor='#0f172a'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with chart_tab2:
        fig = create_macrotrends_comparison_charts("international_context")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with chart_tab3:
        # Detection rates chart
        periods = []
        detection_rates = []
        
        for period_key in ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']:
            if period_key in HISTORICAL_CRIME_DATABASE:
                period_data = HISTORICAL_CRIME_DATABASE[period_key]
                periods.append(period_data["period"])
                detection_rates.append(period_data["detection_rate"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=periods,
            y=detection_rates,
            mode='lines+markers',
            name='Detection Rate %',
            line=dict(color='#10b981', width=3),
            marker=dict(size=10, color='#10b981')
        ))
        
        fig.update_layout(
            title="Crime Detection Rate Trends",
            xaxis_title="Time Period",
            yaxis_title="Detection Rate (%)",
            template="plotly_dark",
            height=500,
            showlegend=False,
            paper_bgcolor='black',
            plot_bgcolor='#0f172a'
        )
        
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.main_view == 'history':
    # Chat History - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header">📝 Chat History Management</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("""
        <div class="info-card">
            <h3>💭 No Chat History Found</h3>
            <p>Start a conversation with the AI Assistant to create your first session! 
            All your conversations will be automatically saved and organized here.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick start button
        if st.button("🚀 Start Your First Chat", key="first_chat", use_container_width=True):
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
    else:
        st.markdown(f"**Total Chat Sessions:** {len(st.session_state.chat_sessions)}")
        st.markdown("---")
        
        # Display chat sessions in a nice grid
        for i, (chat_id, chat_data) in enumerate(st.session_state.chat_sessions.items()):
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                if st.button(f"💬 Chat: {chat_data['name']}", key=f"hist_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.session_state.main_view = 'ai-assistant'
                    st.session_state.chat_active = True
                    st.rerun()
            
            with col2:
                st.text(f"Messages: {len(chat_data['messages'])}")
                st.text(f"Created: {chat_data['created_at']} AST")
            
            with col3:
                st.text(f"Last Activity:")
                st.text(f"{chat_data['last_activity']} AST")
            
            st.markdown("---")

elif st.session_state.main_view == 'emergency':
    # Emergency Contacts - Main Screen
    st.markdown("""
    <div class="main-content-section">
        <h2 class="section-header">🚨 Emergency Contacts Directory</h2>
        <div class="section-content">
            <p><strong>Emergency Guidelines:</strong></p>
            <ul>
                <li>For life-threatening emergencies, call <strong>911</strong> immediately</li>
                <li>Provide exact location and nature of emergency</li>
                <li>Stay on the line until instructed to hang up</li>
                <li>Keep this directory accessible for quick reference</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Emergency contacts in a grid layout
    col1, col2 = st.columns(2)
    
    emergency_items = list(EMERGENCY_CONTACTS.items())
    mid_point = len(emergency_items) // 2
    
    with col1:
        for service, details in emergency_items[:mid_point]:
            st.markdown(f"""
            <div class="emergency-card">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="font-size: 28px;">{details['icon']}</span>
                    <div style="color: #ffffff; font-weight: 700; font-size: 18px;">{service}</div>
                </div>
                <div class="emergency-number">{details['number']}</div>
                <div style="color: #9ca3af; font-size: 14px; line-height: 1.5;">{details['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for service, details in emergency_items[mid_point:]:
            st.markdown(f"""
            <div class="emergency-card">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="font-size: 28px;">{details['icon']}</span>
                    <div style="color: #ffffff; font-weight: 700; font-size: 18px;">{service}</div>
                </div>
                <div class="emergency-number">{details['number']}</div>
                <div style="color: #9ca3af; font-size: 14px; line-height: 1.5;">{details['description']}</div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.main_view == 'ai-assistant':
    # AI Assistant interface (existing code)
    if not st.session_state.get('chat_active', False):
        # Chat welcome screen - Enhanced with new theme
        st.markdown("""
        <div class="welcome-container">
            <div style="width: 120px; height: 120px; margin: 0 auto 32px; border-radius: 50%; 
                       background: linear-gradient(45deg, #1d4ed8, #dc2626); display: flex; 
                       align-items: center; justify-content: center; font-size: 3.5rem; animation: logo-pulse 2s infinite;
                       border: 3px solid rgba(255, 255, 255, 0.2); box-shadow: 0 0 40px rgba(29, 78, 216, 0.4);">
                🛡️
            </div>
            <h1 style="color: #ffffff; font-size: 2.5rem; margin-bottom: 16px; font-weight: 800; text-shadow: 0 4px 12px rgba(29, 78, 216, 0.5);">SECURO AI</h1>
            <p style="color: #1d4ed8; font-size: 1.2rem; margin-bottom: 20px; font-weight: 700;">Enhanced Crime Intelligence</p>
            <p style="color: #d1d5db; max-width: 600px; margin: 0 auto 40px; line-height: 1.7; font-size: 16px; font-weight: 500;">
                Welcome! I'm your enhanced AI Crime Intelligence system with comprehensive St. Kitts & Nevis statistics, 
                international data, and conversation memory powered by professional law enforcement technology.
            </p>
            <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-bottom: 32px;">
                <div style="background: rgba(29, 78, 216, 0.15); border: 2px solid #1d4ed8; border-radius: 12px; 
                            padding: 16px 24px; color: #1d4ed8; font-size: 15px; font-weight: 600;">
                    📊 Statistical Knowledge
                </div>
                <div style="background: rgba(220, 38, 38, 0.15); border: 2px solid #dc2626; border-radius: 12px; 
                            padding: 16px 24px; color: #dc2626; font-size: 15px; font-weight: 600;">
                    💭 Conversation Memory
                </div>
                <div style="background: rgba(16, 185, 129, 0.15); border: 2px solid #10b981; border-radius: 12px; 
                            padding: 16px 24px; color: #10b981; font-size: 15px; font-weight: 600;">
                    🔊 Text-to-Speech
                </div>
            </div>
        </div>
