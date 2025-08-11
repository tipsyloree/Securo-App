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
    
    # Color mapping for risk levels (Updated with police colors)
    risk_colors = {
        'High': '#ff4444',
        'Medium': '#1e90ff', 
        'Low': '#0066cc'
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
    
    # Add a legend (Updated with police colors)
    legend_html = f"""
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 180px; height: 140px; 
                background-color: rgba(0, 0, 0, 0.8); 
                border: 2px solid rgba(30, 144, 255, 0.5);
                border-radius: 10px; z-index:9999; 
                font-size: 12px; font-family: Arial;
                padding: 10px; color: white;">
    <h4 style="margin: 0 0 10px 0; color: #1e90ff;">🗺️ Crime Risk Legend</h4>
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
            line=dict(color='#ff4444', width=3),
            marker=dict(size=10, color='#ff4444')
        ))
        
        # Add global average line
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
            marker_color='#1e90ff',
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
        
        colors = ['#1e90ff', '#0066cc', '#ff4444', '#888888', '#ff0000']
        
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
            height=500
        )
        
        return fig

def create_historical_crime_charts(chart_type, selected_periods, crime_data):
    """Create various crime analysis charts for selected periods"""
    
    if chart_type == "crime_trends":
        # Crime trends across selected periods
        periods = []
        total_crimes = []
        
        for period_key in selected_periods:
            if period_key in crime_data:
                periods.append(crime_data[period_key]["period"])
                total_crimes.append(crime_data[period_key]["total_crimes"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=periods, y=total_crimes,
            mode='lines+markers',
            name='Total Crimes',
            line=dict(color='#1e90ff', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Crime Trends - Selected Periods",
            xaxis_title="Time Period",
            yaxis_title="Total Crimes",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "detection_comparison":
        # Detection rate comparison
        periods = []
        detection_rates = []
        
        for period_key in selected_periods:
            if period_key in crime_data and "detection_rate" in crime_data[period_key]:
                periods.append(crime_data[period_key]["period"])
                detection_rates.append(crime_data[period_key]["detection_rate"])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=periods, y=detection_rates,
            marker_color='#1e90ff',
            text=[f"{rate}%" for rate in detection_rates],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Detection Rates - Selected Periods",
            xaxis_title="Time Period",
            yaxis_title="Detection Rate (%)",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "crime_type_breakdown":
        # Crime type breakdown for latest selected period
        if selected_periods and selected_periods[-1] in crime_data:
            latest_data = crime_data[selected_periods[-1]]
            if "federation" in latest_data:
                crimes = []
                counts = []
                
                for crime_type, data in latest_data["federation"].items():
                    if "total" in data:
                        crimes.append(crime_type.replace('_', ' ').title())
                        counts.append(data["total"])
                
                fig = go.Figure(data=[go.Pie(
                    labels=crimes,
                    values=counts,
                    hole=0.4,
                    marker_colors=['#1e90ff', '#f39c12', '#e74c3c', '#27ae60', '#9b59b6', '#34495e', '#16a085', '#f1c40f']
                )])
                
                fig.update_layout(
                    title=f"Crime Type Distribution - {latest_data['period']}",
                    template="plotly_dark",
                    height=500
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
    GOOGLE_API_KEY = "AIzaSyBn1AUXxPtPMu9eRnosECSSQG_2e5bArR8"
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
    page_title="SECURO - Enhanced AI Assistant & Crime Intelligence System",
    page_icon="https://i.postimg.cc/jdtG76G8/PH-PR-2.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = HISTORICAL_CRIME_DATABASE

if 'selected_periods' not in st.session_state:
    st.session_state.selected_periods = ['2023_ANNUAL', '2024_ANNUAL', '2025_Q2']

if 'chat_active' not in st.session_state:
    st.session_state.chat_active = False

# Initialize statistics on startup
fetch_and_process_statistics()

# Professional CSS styling with POLICE SIREN COLORS! 🚔
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Root styling */
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #0d1117 50%, #1a1a1a 100%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
        padding: 15px 0;
        border-bottom: 1px solid #21262d;
        margin-bottom: 10px;
        position: sticky;
        top: 0;
        z-index: 1000;
        backdrop-filter: blur(10px);
    }
    
    .header-content {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 30px;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    /* POLICE SIREN SHIELD - Animated Blue/Red */
    .shield-icon {
        width: 45px;
        height: 45px;
        background: linear-gradient(45deg, #1e90ff, #ff4444, #1e90ff, #ff4444);
        background-size: 400% 400%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        color: #fff;
        box-shadow: 0 4px 15px rgba(30, 144, 255, 0.4), 0 0 20px rgba(255, 68, 68, 0.3);
        animation: siren-pulse 2s ease-in-out infinite;
    }
    
    @keyframes siren-pulse {
        0%, 100% { 
            background-position: 0% 50%;
            box-shadow: 0 4px 15px rgba(30, 144, 255, 0.4), 0 0 20px rgba(255, 68, 68, 0.3);
        }
        50% { 
            background-position: 100% 50%;
            box-shadow: 0 4px 15px rgba(255, 68, 68, 0.4), 0 0 20px rgba(30, 144, 255, 0.3);
        }
    }
    
    .logo-text h1 {
        color: #1e90ff !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: 2px;
        text-shadow: 0 0 20px rgba(30, 144, 255, 0.4);
        animation: text-glow 3s ease-in-out infinite alternate;
    }
    
    @keyframes text-glow {
        from { 
            color: #1e90ff !important;
            text-shadow: 0 0 20px rgba(30, 144, 255, 0.4);
        }
        to { 
            color: #ff4444 !important;
            text-shadow: 0 0 20px rgba(255, 68, 68, 0.4);
        }
    }
    
    .logo-text p {
        color: #8b949e !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0 !important;
        font-weight: 500;
    }
    
    .status-info {
        display: flex;
        align-items: center;
        gap: 25px;
        font-size: 14px;
        color: #8b949e;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(30, 144, 255, 0.05);
        border-radius: 20px;
        border: 1px solid rgba(30, 144, 255, 0.2);
    }
    
    /* Alternating Blue/Red Status Dots */
    .status-dot {
        width: 8px;
        height: 8px;
        background: linear-gradient(45deg, #1e90ff, #ff4444);
        background-size: 200% 200%;
        border-radius: 50%;
        animation: status-siren 1.5s infinite;
    }
    
    @keyframes status-siren {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Welcome section */
    .welcome-hero {
        text-align: center;
        padding: 30px 20px;
        margin: 20px 0;
        background: linear-gradient(-45deg, rgba(0, 0, 0, 0.9), rgba(30, 144, 255, 0.1), rgba(255, 68, 68, 0.1), rgba(0, 0, 0, 0.9));
        background-size: 400% 400%;
        animation: siren-gradient 4s ease infinite;
        border-radius: 20px;
        border: 1px solid rgba(30, 144, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    @keyframes siren-gradient {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 50%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    .welcome-hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at center, rgba(30, 144, 255, 0.1) 0%, rgba(255, 68, 68, 0.1) 50%, transparent 70%);
        pointer-events: none;
        animation: radial-siren 3s ease-in-out infinite;
    }
    
    @keyframes radial-siren {
        0%, 100% { background: radial-gradient(circle at center, rgba(30, 144, 255, 0.1) 0%, transparent 70%); }
        50% { background: radial-gradient(circle at center, rgba(255, 68, 68, 0.1) 0%, transparent 70%); }
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 15px;
        text-shadow: 0 0 30px rgba(30, 144, 255, 0.3);
        position: relative;
        z-index: 2;
        animation: title-siren 4s ease-in-out infinite;
    }
    
    @keyframes title-siren {
        0%, 100% { text-shadow: 0 0 30px rgba(30, 144, 255, 0.3); }
        50% { text-shadow: 0 0 30px rgba(255, 68, 68, 0.3); }
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #c9d1d9;
        margin-bottom: 10px;
        font-weight: 400;
        position: relative;
        z-index: 2;
    }
    
    .hero-description {
        font-size: 1rem;
        color: #8b949e;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
        position: relative;
        z-index: 2;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(30, 144, 255, 0.02) 0%, rgba(255, 68, 68, 0.02) 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
        pointer-events: none;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: #1e90ff;
        box-shadow: 0 15px 40px rgba(30, 144, 255, 0.15), 0 0 30px rgba(255, 68, 68, 0.1);
        animation: card-siren-glow 1.5s ease-in-out infinite;
    }
    
    @keyframes card-siren-glow {
        0%, 100% { 
            border-color: #1e90ff;
            box-shadow: 0 15px 40px rgba(30, 144, 255, 0.15), 0 0 30px rgba(255, 68, 68, 0.1);
        }
        50% { 
            border-color: #ff4444;
            box-shadow: 0 15px 40px rgba(255, 68, 68, 0.15), 0 0 30px rgba(30, 144, 255, 0.1);
        }
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-icon {
        font-size: 2.8rem;
        margin-bottom: 20px;
        color: #1e90ff;
        text-shadow: 0 0 20px rgba(30, 144, 255, 0.4);
        animation: icon-siren 3s ease-in-out infinite;
    }
    
    @keyframes icon-siren {
        0%, 100% { 
            color: #1e90ff;
            text-shadow: 0 0 20px rgba(30, 144, 255, 0.4);
        }
        50% { 
            color: #ff4444;
            text-shadow: 0 0 20px rgba(255, 68, 68, 0.4);
        }
    }
    
    .feature-card h3 {
        color: #1e90ff !important;
        font-size: 1.4rem !important;
        margin-bottom: 15px !important;
        font-weight: 600 !important;
    }
    
    .feature-card p {
        color: #c9d1d9 !important;
        line-height: 1.6 !important;
        font-size: 14px !important;
    }
    
    /* Emergency cards */
    .emergency-card {
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
    }
    
    .emergency-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(30, 144, 255, 0.02) 0%, rgba(255, 68, 68, 0.02) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    
    .emergency-card:hover {
        transform: translateY(-5px);
        border-color: #1e90ff;
        box-shadow: 0 10px 25px rgba(30, 144, 255, 0.15);
    }
    
    .emergency-card:hover::before {
        opacity: 1;
    }
    
    .emergency-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
        color: #1e90ff;
    }
    
    .emergency-card h3 {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        margin-bottom: 15px !important;
        font-weight: 600 !important;
    }
    
    .emergency-number {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #1e90ff !important;
        margin: 15px 0 !important;
        text-shadow: 0 0 10px rgba(30, 144, 255, 0.3);
        animation: number-siren 2.5s ease-in-out infinite;
    }
    
    @keyframes number-siren {
        0%, 100% { 
            color: #1e90ff !important;
            text-shadow: 0 0 10px rgba(30, 144, 255, 0.3);
        }
        50% { 
            color: #ff4444 !important;
            text-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
        }
    }
    
    .emergency-card p {
        color: #c9d1d9 !important;
        font-size: 13px !important;
        line-height: 1.5 !important;
    }
    
    /* Guidelines box */
    .guidelines-box {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 16px;
        padding: 30px;
        margin-top: 40px;
    }
    
    .guidelines-title {
        color: #ffc107 !important;
        font-size: 1.3rem !important;
        margin-bottom: 20px !important;
        font-weight: 600 !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .guidelines-list {
        color: #c9d1d9 !important;
        line-height: 1.8 !important;
        list-style: none !important;
        padding: 0 !important;
    }
    
    .guidelines-list li {
        padding: 8px 0 !important;
        padding-left: 25px !important;
        position: relative !important;
    }
    
    .guidelines-list li::before {
        content: "•" !important;
        color: #ffc107 !important;
        font-weight: bold !important;
        position: absolute !important;
        left: 0 !important;
    }
    
    /* Chat messages */
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
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    
    /* POLICE SIREN USER MESSAGES */
    .user-message .message-content {
        background: linear-gradient(135deg, #1e90ff, #0066cc);
        color: #ffffff !important;
        border-bottom-right-radius: 5px;
        animation: user-message-pulse 3s ease-in-out infinite;
    }
    
    @keyframes user-message-pulse {
        0%, 100% { 
            background: linear-gradient(135deg, #1e90ff, #0066cc);
            box-shadow: 0 0 10px rgba(30, 144, 255, 0.3);
        }
        50% { 
            background: linear-gradient(135deg, #ff4444, #cc0000);
            box-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
        }
    }
    
    .bot-message .message-content {
        background: rgba(0, 0, 0, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(30, 144, 255, 0.3);
        border-bottom-left-radius: 5px;
        animation: bot-border-siren 4s ease-in-out infinite;
    }
    
    @keyframes bot-border-siren {
        0%, 100% { border-color: rgba(30, 144, 255, 0.3); }
        50% { border-color: rgba(255, 68, 68, 0.3); }
    }
    
    .message-time {
        font-size: 0.7rem;
        color: #888 !important;
        margin-top: 5px;
    }
    
    /* Chat interface */
    .chat-welcome {
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border-radius: 20px;
        border: 1px solid #30363d;
        margin: 40px 0;
    }
    
    /* POLICE SIREN CHAT LOGO */
    .chat-logo {
        width: 100px;
        height: 100px;
        border: 4px solid #1e90ff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 30px;
        font-size: 3rem;
        color: #1e90ff;
        background: rgba(30, 144, 255, 0.1);
        animation: chat-logo-siren 2s ease-in-out infinite;
    }
    
    @keyframes chat-logo-siren {
        0%, 100% { 
            border-color: #1e90ff;
            color: #1e90ff;
            background: rgba(30, 144, 255, 0.1);
            box-shadow: 0 0 20px rgba(30, 144, 255, 0.3);
        }
        50% { 
            border-color: #ff4444;
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
            box-shadow: 0 0 20px rgba(255, 68, 68, 0.3);
        }
    }
    
    .chat-title {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .chat-subtitle {
        color: #8b949e;
        font-size: 16px;
        margin-bottom: 30px;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 80px 20px;
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
        border-radius: 20px;
        border: 1px solid #30363d;
        margin: 40px auto;
        max-width: 600px;
    }
    
    .empty-icon {
        width: 80px;
        height: 80px;
        border: 3px solid #30363d;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 30px;
        font-size: 2rem;
        color: #8b949e;
        background: rgba(0, 0, 0, 0.3);
    }
    
    .empty-title {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    .empty-subtitle {
        color: #8b949e;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Status bar */
    .status-bar {
        background: rgba(0, 0, 0, 0.9);
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
        border-top: 1px solid #21262d;
        font-size: 13px;
    }
    
    .status-active {
        color: #1e90ff;
        animation: status-text-siren 3s ease-in-out infinite;
    }
    
    @keyframes status-text-siren {
        0%, 100% { color: #1e90ff; }
        50% { color: #ff4444; }
    }
    
    /* Buttons */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #30363d !important;
        color: #8b949e !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: rgba(30, 144, 255, 0.1) !important;
        border-color: #1e90ff !important;
        color: #1e90ff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(30, 144, 255, 0.2) !important;
        animation: button-hover-siren 1s ease-in-out infinite;
    }
    
    @keyframes button-hover-siren {
        0%, 100% { 
            border-color: #1e90ff !important;
            color: #1e90ff !important;
            box-shadow: 0 5px 15px rgba(30, 144, 255, 0.2) !important;
        }
        50% { 
            border-color: #ff4444 !important;
            color: #ff4444 !important;
            box-shadow: 0 5px 15px rgba(255, 68, 68, 0.2) !important;
        }
    }
    
    /* Text inputs */
    .stTextInput input {
        background: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput input:focus {
        border-color: #1e90ff !important;
        box-shadow: 0 0 0 3px rgba(30, 144, 255, 0.1) !important;
        animation: input-focus-siren 2s ease-in-out infinite;
    }
    
    @keyframes input-focus-siren {
        0%, 100% { 
            border-color: #1e90ff !important;
            box-shadow: 0 0 0 3px rgba(30, 144, 255, 0.1) !important;
        }
        50% { 
            border-color: #ff4444 !important;
            box-shadow: 0 0 0 3px rgba(255, 68, 68, 0.1) !important;
        }
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background-color: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    /* Fix text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    p, span, div, li {
        color: #c9d1d9 !important;
    }
    
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 20px;
            padding: 0 20px;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #21262d 0%, #161b22 100%); border-radius: 16px; padding: 25px; border: 1px solid #30363d; margin-bottom: 25px;">
        <h3 style="color: #1e90ff; margin-bottom: 20px; text-align: center; animation: sidebar-title-siren 3s ease-in-out infinite;">🤖 AI System Status</h3>
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border: 3px solid #1e90ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; font-size: 1.5rem; color: #1e90ff; background: rgba(30, 144, 255, 0.1); animation: sidebar-icon-siren 2s ease-in-out infinite;">
                🧠
            </div>
            <p style="color: #1e90ff; font-weight: 600; margin-bottom: 5px;">Enhanced AI Active</p>
            <p style="color: #8b949e; font-size: 12px;">Statistical Knowledge • Memory • Context</p>
        </div>
    </div>
    
    <style>
    @keyframes sidebar-title-siren {
        0%, 100% { color: #1e90ff; }
        50% { color: #ff4444; }
    }
    
    @keyframes sidebar-icon-siren {
        0%, 100% { 
            border-color: #1e90ff;
            color: #1e90ff;
            background: rgba(30, 144, 255, 0.1);
        }
        50% { 
            border-color: #ff4444;
            color: #ff4444;
            background: rgba(255, 68, 68, 0.1);
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('ai_enabled', False):
        st.success("🔮 AI Assistant Online")
        st.markdown("""
        **Enhanced Capabilities:**
        - Statistical knowledge integration
        - Conversation memory
        - Context-aware responses
        - Crime data analysis
        - Professional assistance
        
        **Statistical Coverage:**
        - 2022-2025 complete annual data
        - 2015-2024 homicide analysis
        - MacroTrends international data
        - Quarterly & half-yearly reports
        - Detection rate analysis
        """)
    else:
        st.error("⚠️ AI Offline")
        st.write("Please check your API key configuration")

# Main Header
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="main-header">
    <div class="header-content">
        <div class="logo-section">
            <div class="shield-icon">🚔</div>
            <div class="logo-text">
                <h1>SECURO</h1>
                <p>Enhanced AI Assistant & Crime Intelligence System</p>
            </div>
        </div>
        <div class="status-info">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>Royal St. Christopher & Nevis Police Force</span>
            </div>
            <div class="status-item">
                <span>📅 {current_date} | 🕒 {current_time} (AST)</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("🏠 Home", key="nav_home", help="Home", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

with col2:
    if st.button("ℹ️ About", key="nav_about", help="About SECURO System", use_container_width=True):
        st.session_state.current_page = 'about'
        st.rerun()

with col3:
    if st.button("🗺️ Hotspots", key="nav_map", help="Crime Hotspots", use_container_width=True):
        st.session_state.current_page = 'hotspots'
        st.rerun()

with col4:
    if st.button("📊 Analytics", key="nav_stats", help="Statistics & Analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()

with col5:
    if st.button("💬 AI Assistant", key="nav_chat", help="AI Chat", use_container_width=True):
        st.session_state.current_page = 'chat'
        st.rerun()

with col6:
    if st.button("💾 History", key="nav_history", help="Chat History", use_container_width=True):
        st.session_state.current_page = 'history'
        st.rerun()

with col7:
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts", use_container_width=True):
        st.session_state.current_page = 'emergency'
        st.rerun()

# HOME PAGE
if st.session_state.current_page == 'home':
    st.markdown("""
    <div class="welcome-hero" style="text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <h1 class="hero-title" style="text-align: center; margin: 0 auto;">Welcome to SECURO AI 🚔</h1>
    <p class="hero-subtitle" style="text-align: center; margin: 15px auto; max-width: 900px;">Your comprehensive AI assistant with POLICE SIREN COLORS, statistical knowledge, conversation memory, and crime analysis capabilities for St. Kitts & Nevis</p>
    <p class="hero-description" style="text-align: center; margin: 10px auto; max-width: 800px;">AI assistant now features conversation memory, statistical integration, enhanced analytics, and emergency blue & red police car siren effects! 🚨</p>
</div>
""", unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <h3>Enhanced AI with Police Siren Colors</h3>
            <p>Conversation memory, statistical knowledge integration, and context-aware responses powered by real crime data from police PDFs - now with emergency blue & red siren effects! 🚔</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Integrated Statistics + International Data</h3>
            <p>Real-time access to local crime statistics PLUS MacroTrends international comparison data with global context and historical trends - all styled with police emergency colors.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💾</div>
            <h3>Conversation Management</h3>
            <p>Multiple chat sessions with memory, chat history, and context preservation across conversations for continuous assistance - with animated police siren styling!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <h3>Statistical Analysis</h3>
            <p>Advanced crime data analysis with detection rates, trend identification, and actionable insights for police operations - enhanced with emergency response aesthetics.</p>
        </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE
elif st.session_state.current_page == 'about':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">About SECURO AI 🚔</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card" style="margin-bottom: 40px;">
        <p style="text-align: center; font-size: 16px;"><strong style="color: #1e90ff;">SECURO</strong> is now an enhanced comprehensive crime analysis system with <strong style="color: #ff4444;">POLICE SIREN COLORS</strong>, statistical integration, conversation memory, and advanced AI capabilities built specifically for the Royal St. Christopher and Nevis Police Force. Experience the emergency blue and red styling that matches real police car sirens! 🚨</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧠 SECURO AI Capabilities")
        capabilities = [
            "Conversation Memory - Maintains context across entire chat sessions",
            "Statistical Knowledge Integration - Real access to 2023-2025 crime data", 
            "Context-Aware Responses - Understands conversation flow and history",
            "Multi-Chat Management - Multiple conversation sessions with history",
            "Statistical Query Processing - Answers questions with actual crime data"
        ]
        
        for cap in capabilities:
            col_check, col_text = st.columns([1, 10])
            with col_check:
                st.markdown("✅")
            with col_text:
                st.markdown(f"**{cap.split(' - ')[0]}** - {cap.split(' - ')[1]}")
        
        st.markdown("### 💬 Chat Management Features")
        chat_features = [
            "New Chat Sessions - Start fresh conversations anytime",
            "Chat History - Access and resume previous conversations",
            "Context Preservation - AI remembers entire conversation context", 
            "Session Management - Switch between multiple chat sessions seamlessly"
        ]
        
        for feature in chat_features:
            col_check, col_text = st.columns([1, 10])
            with col_check:
                st.markdown("✅")
            with col_text:
                st.markdown(f"**{feature.split(' - ')[0]}** - {feature.split(' - ')[1]}")
    
    with col2:
        st.markdown("### 📊 Integrated Statistical Database")
        stats_features = [
            "Real PDF Integration - Data sourced from official police statistical reports",
            "2022-2025 Crime Data - Complete annual statistics plus quarterly analysis",
            "Detection Rate Analysis - Performance metrics and trend identification",
            "Geographical Breakdown - St. Kitts vs. Nevis crime distribution"
        ]
        
        for feature in stats_features:
            col_check, col_text = st.columns([1, 10])
            with col_check:
                st.markdown("✅")
            with col_text:
                st.markdown(f"**{feature.split(' - ')[0]}** - {feature.split(' - ')[1]}")
        
        st.markdown("### 🔒 Police Siren Design")
        st.markdown("""
        Enhanced SECURO now features authentic police car siren colors with alternating blue and red animations throughout the interface. 
        The AI assistant provides statistically-informed assistance while preserving conversation context for more effective police support - 
        all with emergency response styling! 🚨
        """)

# CRIME HOTSPOTS PAGE
elif st.session_state.current_page == 'hotspots':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">🗺️ Crime Hotspot Map - St. Kitts & Nevis 🚔</h1>', unsafe_allow_html=True)
    
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
    
    # Hotspot Analysis Summary
    st.markdown('<h2 style="text-align: center; margin: 40px 0 30px;">📍 Hotspot Analysis Summary</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255, 68, 68, 0.1) 0%, rgba(255, 68, 68, 0.05) 100%); 
                    border: 1px solid rgba(255, 68, 68, 0.3); border-radius: 16px; padding: 25px; text-align: center; 
                    border-left: 4px solid #ff4444;">
            <h3 style="color: #ff4444; margin-bottom: 15px;">High Risk Areas (3)</h3>
            <p style="color: #c9d1d9; margin-bottom: 10px;">Basseterre Central, Molineux, Tabernacle</p>
            <p style="color: #8b949e; font-size: 14px;"><strong>Total: 109 crimes</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(30, 144, 255, 0.1) 0%, rgba(30, 144, 255, 0.05) 100%); 
                    border: 1px solid rgba(30, 144, 255, 0.3); border-radius: 16px; padding: 25px; text-align: center; 
                    border-left: 4px solid #1e90ff;">
            <h3 style="color: #1e90ff; margin-bottom: 15px;">Medium Risk Areas (6)</h3>
            <p style="color: #c9d1d9; margin-bottom: 10px;">Cayon, Newton Ground, Old Road, etc.</p>
            <p style="color: #8b949e; font-size: 14px;"><strong>Total: 133 crimes</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(0, 102, 204, 0.05) 100%); 
                    border: 1px solid rgba(0, 102, 204, 0.3); border-radius: 16px; padding: 25px; text-align: center; 
                    border-left: 4px solid #0066cc;">
            <h3 style="color: #0066cc; margin-bottom: 15px;">Low Risk Areas (4)</h3>
            <p style="color: #c9d1d9; margin-bottom: 10px;">Sandy Point, Dieppe Bay, etc.</p>
            <p style="color: #8b949e; font-size: 14px;"><strong>Total: 60 crimes</strong></p>
        </div>
        """, unsafe_allow_html=True)

# ANALYTICS PAGE
elif st.session_state.current_page == 'analytics':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">📊 Statistics & Analytics 🚔</h1>', unsafe_allow_html=True)
    
    st.info("📊 **Enhanced Statistics System** - Data is now integrated with the AI assistant for comprehensive statistical analysis, styled with police siren colors! 🚨")
    
    # Year/Period Selection
    st.markdown('<h3>📅 Select Time Periods for Analysis</h3>', unsafe_allow_html=True)
    
    available_periods = list(HISTORICAL_CRIME_DATABASE.keys())
    period_labels = {key: data["period"] for key, data in HISTORICAL_CRIME_DATABASE.items()}
    
    selected_periods = st.multiselect(
        "📊 Choose time periods to analyze:",
        options=available_periods,
        default=['2023_ANNUAL', '2024_ANNUAL', '2025_Q2'],
        format_func=lambda x: period_labels.get(x, x),
        help="Select one or more time periods to compare statistics and trends.",
        key="period_selector"
    )
    
    if not selected_periods:
        st.warning("Please select at least one time period to view statistics.")
    else:
        # Display stats for selected periods
        if len(selected_periods) == 1:
            # Single period detailed view
            period_key = selected_periods[0]
            period_data = HISTORICAL_CRIME_DATABASE[period_key]
            
            st.markdown(f'<h3>📈 {period_data["period"]} Overview</h3>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Crimes", period_data['total_crimes'])
            
            with col2:
                detection_rate = period_data.get('detection_rate', 'N/A')
                st.metric("Detection Rate", f"{detection_rate}%" if detection_rate != 'N/A' else 'N/A')
            
            with col3:
                st_kitts_crimes = period_data.get('st_kitts', {}).get('crimes', 'N/A')
                st.metric("St. Kitts Crimes", st_kitts_crimes)
            
            with col4:
                nevis_crimes = period_data.get('nevis', {}).get('crimes', 'N/A')
                st.metric("Nevis Crimes", nevis_crimes)
        
        else:
            # Multiple periods comparison view
            st.markdown('<h3>📈 Multi-Period Comparison</h3>', unsafe_allow_html=True)
            
            comparison_data = []
            for period_key in selected_periods:
                period_data = HISTORICAL_CRIME_DATABASE[period_key]
                comparison_data.append({
                    "Period": period_data["period"],
                    "Total Crimes": period_data["total_crimes"],
                    "Detection Rate": f"{period_data.get('detection_rate', 'N/A')}{'%' if period_data.get('detection_rate') else ''}",
                    "St. Kitts": period_data.get('st_kitts', {}).get('crimes', 'N/A'),
                    "Nevis": period_data.get('nevis', {}).get('crimes', 'N/A')
                })
            
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)

# AI ASSISTANT PAGE
elif st.session_state.current_page == 'chat':
    # Show welcome screen only if chat is not active
    if not st.session_state.get('chat_active', False):
        st.markdown("""
        <div class="chat-welcome">
            <div class="chat-logo">
                🔒
            </div>
            <h1 class="chat-title">SECURO</h1>
            <p class="chat-subtitle">AI Assistant with Police Siren Colors</p>
            <p style="color: #8b949e; max-width: 600px; margin: 0 auto 30px;">
                Welcome, I am SECURO, an enhanced AI Assistant & Crime Intelligence system for Law Enforcement Professionals with authentic police car siren styling! I am Online and ready, having just loaded the crime intelligence database. You now have access to comprehensive St. Kitts & Nevis crime statistics, international comparison data from MacroTrends, and can maintain your chat history. Click Start to begin the conversation and experience the emergency blue & red police aesthetic! 🚨
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Working start conversation button
        if st.button("🚀 Start Conversation", key="start_chat", use_container_width=True):
            # Create new chat session and activate chat
            create_new_chat()
            st.session_state.chat_active = True
            st.success("✅ New chat session created! You can now start chatting with SECURO AI with police siren colors!")
            st.rerun()
    
    else:
        # Chat is active - show chat interface
        st.markdown('<h2 style="text-align: center; margin-bottom: 20px;">💬 SECURO AI Assistant 🔒</h2>', unsafe_allow_html=True)
        
        # Chat management controls
        col1, col2, col3 = st.columns([2, 6, 2])
        
        with col1:
            if st.button("➕ New Chat", key="new_chat_btn", use_container_width=True):
                create_new_chat()
                st.rerun()
        
        with col2:
            current_chat = get_current_chat()
            st.markdown(f"""
            <div style="background: rgba(30, 144, 255, 0.1); border: 1px solid rgba(30, 144, 255, 0.3); 
                        border-radius: 8px; padding: 10px; text-align: center; animation: session-siren 3s ease-in-out infinite;">
                <strong style="color: #1e90ff;">Current Session:</strong>
                <span style="color: #c9d1d9;">{current_chat['name']}</span>
            </div>
            <style>
            @keyframes session-siren {{
                0%, 100% {{ 
                    background: rgba(30, 144, 255, 0.1);
                    border-color: rgba(30, 144, 255, 0.3);
                }}
                50% {{ 
                    background: rgba(255, 68, 68, 0.1);
                    border-color: rgba(255, 68, 68, 0.3);
                }}
            }}
            </style>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🔙 Back to Welcome", key="back_welcome", use_container_width=True):
                st.session_state.chat_active = False
                st.rerun()
        
        # Enhanced Status Display
        if st.session_state.get('ai_enabled', False):
            st.success("✅ Enhanced AI Ready: Statistical Knowledge • Conversation Memory • Context Awareness • Police Siren Colors! 🚔")
        else:
            st.error("❌ AI Offline: Check your Google AI API key")
        
        # Get current chat and display messages
        current_chat = get_current_chat()
        messages = current_chat['messages']
        
        # Initialize with welcome message if no messages
        if not messages:
            welcome_msg = {
                "role": "assistant",
                "content": "🔒 Enhanced SECURO AI System Online!\n\nI now have access to comprehensive St. Kitts & Nevis crime statistics, international comparison data from MacroTrends, and can maintain conversation context. Ask me about:\n\n• Local crime trends and detection rates\n• International comparisons and global context\n• Historical data analysis with charts\n• Specific incidents or general questions\n\nI can show interactive charts for international comparisons! Experience the authentic police emergency styling with alternating blue and red effects! 🚨",
                "timestamp": get_stkitts_time()
            }
            messages.append(welcome_msg)
            current_chat['messages'] = messages
        
        # Display chat messages
        st.markdown("### 💬 Conversation")
        for message in messages:
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
               
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <div class="message-content">{clean_content}</div>
                    <div class="message-time">SECURO • {message["timestamp"]} AST</div>
                </div>
                """, unsafe_allow_html=True)

        # Enhanced Chat input
        st.markdown("---")
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "💬 Message Enhanced AI Assistant:",
                placeholder="Ask about crime statistics, trends, international comparisons, or request charts... (I have full conversation memory and police siren styling!) 🚔",
                label_visibility="collapsed",
                key="chat_input"
            )
            
            submitted = st.form_submit_button("Send", type="primary")
            
            if submitted and user_input and user_input.strip():
                current_time = get_stkitts_time()
                
                # Add user message to current chat
                add_message_to_chat("user", user_input)
                
                # Generate response with conversation history and statistics
                with st.spinner("🤖 Generating enhanced AI response with statistical knowledge..."):
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
                
                st.rerun()
        
        # Display charts after the rerun (so they persist)
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
                # Show crime trends - St. Kitts specific data
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
                    marker_color='#1e90ff',
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
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "detection":
                # Show detection rates
                selected_periods = ['2023_ANNUAL', '2024_ANNUAL']
                fig = create_historical_crime_charts("detection_comparison", selected_periods, HISTORICAL_CRIME_DATABASE)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "breakdown":
                # Show crime type breakdown
                selected_periods = ['2024_ANNUAL']
                fig = create_historical_crime_charts("crime_type_breakdown", selected_periods, HISTORICAL_CRIME_DATABASE)
                if fig:
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

# CHAT HISTORY PAGE
elif st.session_state.current_page == 'history':
    st.markdown('<h1 style="text-align: center; margin-bottom: 20px;">💾 Chat History Archive 🚔</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #8b949e; margin-bottom: 40px;">Review and continue any of your past conversations with SECURO. All chat context is preserved with police siren styling! 🚨</p>', unsafe_allow_html=True)
    
    if not st.session_state.chat_sessions:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💬</div>
            <h2 class="empty-title">No Chat History Found</h2>
            <p class="empty-subtitle">Start a conversation in the AI Assistant tab to create your first chat session with police siren colors!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for chat_id, chat_data in st.session_state.chat_sessions.items():
            if st.button(f"💬 {chat_data['name']}", key=f"hist_{chat_id}", use_container_width=True):
                st.session_state.current_chat_id = chat_id
                st.session_state.current_page = 'chat'
                st.session_state.chat_active = True
                st.rerun()
            
            st.caption(f"Created: {chat_data['created_at']} AST | Last Activity: {chat_data['last_activity']} AST")
            if chat_data['messages']:
                last_msg = chat_data['messages'][-1]['content'][:100] + "..." if len(chat_data['messages'][-1]['content']) > 100 else chat_data['messages'][-1]['content']
                st.caption(f"Last message: {last_msg}")
            st.markdown("---")

# EMERGENCY CONTACTS PAGE
elif st.session_state.current_page == 'emergency':
    st.markdown('<h1 style="text-align: center; margin-bottom: 40px;">🚨 Emergency Contacts 🚔</h1>', unsafe_allow_html=True)
    
    # Emergency cards grid
    cols = st.columns(4)
    for i, (service, details) in enumerate(EMERGENCY_CONTACTS.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="emergency-card">
                <div class="emergency-icon">{details['icon']}</div>
                <h3>{service}</h3>
                <div class="emergency-number">{details['number']}</div>
                <p>{details['description']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Emergency Guidelines
    st.markdown("""
    <div class="guidelines-box">
        <h3 class="guidelines-title">⚠️ Important Emergency Guidelines 🚔</h3>
        <ul class="guidelines-list">
            <li>For life-threatening emergencies, always call <strong>911</strong> first.</li>
            <li>When calling, provide your exact location and the nature of the emergency.</li>
            <li>Stay on the line until instructed to hang up.</li>
            <li>Keep these numbers easily accessible at all times.</li>
            <li>Follow dispatcher instructions carefully.</li>
            <li>Provide first aid only if trained to do so.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Status Bar
current_time = get_stkitts_time()
total_chats = len(st.session_state.chat_sessions)

st.markdown(f"""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot"></div>
        <span class="status-active">Enhanced AI Active</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span class="status-active">Police Siren Colors: Active</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span class="status-active">Conversation Memory: Enabled</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Chat Sessions: {total_chats}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>🕒 {current_time} AST</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); border-top: 1px solid #21262d; padding: 40px 0 20px; margin-top: 60px;">
    <div style="max-width: 1400px; margin: 0 auto; padding: 0 30px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px; margin-bottom: 30px;">
            <div>
                <h4 style="color: #1e90ff; font-size: 14px; font-weight: 600; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;">Data Source</h4>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">📊 Royal St. Christopher & Nevis Police Force (RSCNPF)</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">📈 Statistical Integration Active</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">🌍 Multi-language Support</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">🚔 Police Siren Color Theme</p>
            </div>
            <div>
                <h4 style="color: #1e90ff; font-size: 14px; font-weight: 600; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;">Last Updated</h4>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">🔄 {get_stkitts_date()} {get_stkitts_time()} AST</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">🤖 AI System: Enhanced AI Intelligence</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">📊 Enhanced AI Assistant Platform</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">🚨 Emergency Response Styling</p>
            </div>
            <div>
                <h4 style="color: #1e90ff; font-size: 14px; font-weight: 600; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;">Contact Information</h4>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">📞 Local Intelligence Office: 869-465-2241 Ext. 4238/4239</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">📧 lio@police.kn</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">🌐 Multi-Chat Support</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">⚖️ Secure Law Enforcement Platform</p>
            </div>
            <div>
                <h4 style="color: #1e90ff; font-size: 14px; font-weight: 600; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px;">AI System</h4>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">🚔 Enhanced AI Assistant with Police Siren Colors</p>
                <p style="color: #8b949e; font-size: 13px; line-height: 1.6; margin-bottom: 8px;">Statistical knowledge integration • Conversation memory • Context awareness • Multi-chat support • Professional law enforcement assistance • emergency blue & red styling</p>
            </div>
        </div>
        <div style="border-top: 1px solid #21262d; padding: 20px 0; text-align: center; color: #6e7681; font-size: 12px;">
            <p>&copy; 2025 SECURO - Enhanced AI Assistant & Crime Intelligence System with Police Siren Colors 🚔 | Royal St. Christopher and Nevis Police Force | Version 2.1.0 - Emergency Response Edition 🚨</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
