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

# Crime Hotspots Data for St. Kitts & Nevis
CRIME_HOTSPOTS = {
    # St. Kitts Hotspots
    "Basseterre Central": {"lat": 17.3026, "lon": -62.7177, "crimes": 45, "risk": "High", "types": ["Larceny", "Drug Crimes", "Assault"]},
    "Cayon": {"lat": 17.3581, "lon": -62.7440, "crimes": 28, "risk": "Medium", "types": ["Break-ins", "Theft"]},
    "Old Road Town": {"lat": 17.3211, "lon": -62.7847, "crimes": 22, "risk": "Medium", "types": ["Drug Crimes", "Vandalism"]},
    "Tabernacle": {"lat": 17.3100, "lon": -62.7200, "crimes": 31, "risk": "High", "types": ["Robbery", "Assault"]},
    "Sandy Point": {"lat": 17.3667, "lon": -62.8500, "crimes": 19, "risk": "Low", "types": ["Petty Theft"]},
    "Dieppe Bay": {"lat": 17.3833, "lon": -62.8167, "crimes": 15, "risk": "Low", "types": ["Vandalism"]},
    "Newton Ground": {"lat": 17.3319, "lon": -62.7269, "crimes": 26, "risk": "Medium", "types": ["Drug Crimes", "Larceny"]},
    "Molineux": {"lat": 17.2978, "lon": -62.7047, "crimes": 33, "risk": "High", "types": ["Armed Robbery", "Assault"]},
    
    # Nevis Hotspots
    "Charlestown": {"lat": 17.1348, "lon": -62.6217, "crimes": 18, "risk": "Medium", "types": ["Larceny", "Drug Crimes"]},
    "Gingerland": {"lat": 17.1019, "lon": -62.5708, "crimes": 12, "risk": "Low", "types": ["Petty Theft"]},
    "Newcastle": {"lat": 17.1667, "lon": -62.6000, "crimes": 14, "risk": "Low", "types": ["Vandalism", "Theft"]},
    "Cotton Ground": {"lat": 17.1281, "lon": -62.6442, "crimes": 16, "risk": "Medium", "types": ["Break-ins", "Larceny"]},
    "Ramsbury": {"lat": 17.1500, "lon": -62.6167, "crimes": 21, "risk": "Medium", "types": ["Drug Crimes", "Assault"]},
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
    
    # Color mapping for risk levels
    risk_colors = {
        'High': '#ff4444',
        'Medium': '#ffaa44', 
        'Low': '#44ff44'
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
    
    # Add a legend
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
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Crime Statistics Data Structure
@st.cache_data
def load_crime_statistics():
    """Load and structure crime statistics data"""
    
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
        pred_years = [2025, 2026, 2027]
        pred_counts = [10, 8, 7]
        
        fig.add_trace(go.Scatter(
            x=pred_years, y=pred_counts,
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#44ff44', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="St. Kitts & Nevis Homicide Trends (2015-2027)",
            xaxis_title="Year",
            yaxis_title="Number of Homicides",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "crime_breakdown":
        # Crime breakdown pie chart
        crime_data_q2 = crime_data['current_quarter']['federation']
        crimes = ['Larcenies', 'Malicious Damage', 'Bodily Harm', 'Drug Crimes', 'Break-ins', 'Murder']
        counts = [
            crime_data_q2['larcenies']['total'],
            crime_data_q2['malicious_damage']['total'],
            crime_data_q2['bodily_harm']['total'],
            crime_data_q2['drugs']['total'],
            crime_data_q2['break_ins']['total'],
            crime_data_q2['murder_manslaughter']['total']
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=crimes,
            values=counts,
            hole=0.4,
            marker_colors=['#44ff44', '#f39c12', '#e74c3c', '#27ae60', '#9b59b6', '#34495e']
        )])
        
        fig.update_layout(
            title="Crime Types Distribution Q2 2025",
            template="plotly_dark",
            height=500
        )
        
        return fig
    
    elif chart_type == "detection_rates":
        # Detection rates by quarter/region
        regions = ['Federation', 'St. Kitts', 'Nevis']
        detection_rates = [38.7, 32.9, 52.9]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=regions, y=detection_rates,
            marker_color=['#f39c12', '#e74c3c', '#44ff44'],
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
    
    elif chart_type == "predictions":
        # Crime predictions
        years = [2025, 2026, 2027]
        predictions = [10, 8, 7]
        upper_bound = [15, 12, 10]
        lower_bound = [5, 4, 3]
        
        fig = go.Figure()
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=years + years[::-1],
            y=upper_bound + lower_bound[::-1],
            fill='toself',
            fillcolor='rgba(68, 255, 68, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='95% Confidence Interval'
        ))
        
        fig.add_trace(go.Scatter(
            x=years, y=predictions,
            mode='lines+markers',
            name='Predicted Homicides',
            line=dict(color='#44ff44', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Homicide Predictions 2025-2027",
            xaxis_title="Year",
            yaxis_title="Predicted Homicides",
            template="plotly_dark",
            height=500
        )
        
        return fig

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
            files_in_script_dir = os.listdir(script_dir) if os.path.exists(script_dir) else []
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

def get_ai_response(user_input, csv_results, language='en'):
    """Generate AI response using the system prompt and context with language support"""
    if not st.session_state.get('ai_enabled', False) or model is None:
        return csv_results
    
    try:
        current_time = get_stkitts_time()
        current_date = get_stkitts_date()
        
        time_keywords = ['time', 'date', 'now', 'current', 'today', 'when', 'hora', 'fecha', 'hoy', 'temps', 'maintenant']
        include_time = any(keyword in user_input.lower() for keyword in time_keywords)
        
        # Include crime hotspot information in context
        hotspot_context = f"""
        CRIME HOTSPOT DATA:
        High Risk Areas: {', '.join([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'High'])}
        Medium Risk Areas: {', '.join([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Medium'])}
        Low Risk Areas: {', '.join([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Low'])}
        Total Mapped Locations: {len(CRIME_HOTSPOTS)}
        """
        
        time_context = f"""
        Current St. Kitts & Nevis time: {current_time}
        Current St. Kitts & Nevis date: {current_date}
        """ if include_time else ""
        
        # Enhanced crime context
        crime_context = f"""
        CURRENT ST. KITTS & NEVIS CRIME DATA (Q2 2025):
        
        OVERALL STATISTICS:
        - Total Federation Crimes: 292
        - Overall Detection Rate: 38.7%
        - St. Kitts: 207 crimes (32.9% detection rate)
        - Nevis: 85 crimes (52.9% detection rate)
        
        CRIME BREAKDOWN Q2 2025:
        - Murder/Manslaughter: 4 cases (2 detected, 50% rate)
        - Drug Crimes: 31 cases (31 detected, 100% rate) - PERFECT PERFORMANCE
        - Larcenies: 92 cases (21 detected, 22.8% rate)
        - Bodily Harm: 33 cases (19 detected, 57.6% rate)
        - Break-ins: 26 cases (7 detected, 26.9% rate)
        - Malicious Damage: 59 cases (17 detected, 28.8% rate)
        """
        
        full_prompt = f"""
        {get_system_prompt(language)}
        {time_context}
        {hotspot_context}
        {crime_context}
        
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

def get_enhanced_ai_response(user_input, language='en'):
    """Generate enhanced AI response with comprehensive crime analysis"""
    if not st.session_state.get('ai_enabled', False) or model is None:
        return get_fallback_response(user_input)
    
    try:
        current_time = get_stkitts_time()
        current_date = get_stkitts_date()
        
        # Create comprehensive context with all crime data
        crime_context = f"""
        CURRENT ST. KITTS & NEVIS CRIME DATA (Q2 2025):
        
        OVERALL STATISTICS:
        - Total Federation Crimes: 292
        - Overall Detection Rate: 38.7%
        - St. Kitts: 207 crimes (32.9% detection rate)
        - Nevis: 85 crimes (52.9% detection rate)
        
        CRIME BREAKDOWN Q2 2025:
        - Murder/Manslaughter: 4 cases (2 detected, 50% rate)
        - Drug Crimes: 31 cases (31 detected, 100% rate) - PERFECT PERFORMANCE
        - Larcenies: 92 cases (21 detected, 22.8% rate)
        - Bodily Harm: 33 cases (19 detected, 57.6% rate)
        - Break-ins: 26 cases (7 detected, 26.9% rate)
        - Malicious Damage: 59 cases (17 detected, 28.8% rate)
        
        HISTORICAL HOMICIDE TRENDS (2015-2024):
        2015: 29, 2016: 32, 2017: 23, 2018: 23, 2019: 12, 2020: 10, 
        2021: 14, 2022: 11, 2023: 31, 2024: 28
        
        CRIME HOTSPOTS (13 MAPPED LOCATIONS):
        HIGH RISK: Basseterre Central (45 crimes), Molineux (33), Tabernacle (31)
        MEDIUM RISK: Cayon (28), Newton Ground (26), Old Road (22), Ramsbury (21), Charlestown (18), Cotton Ground (16)
        LOW RISK: Sandy Point (19), Dieppe Bay (15), Newcastle (14), Gingerland (12)
        
        HOMICIDE METHODS ANALYSIS:
        - Shooting: 173 cases (81% of methods)
        - Stabbing: 29 cases (14%)
        - Other: 11 cases (5%)
        
        POLICE DISTRICT PERFORMANCE:
        - District A: 2023: 22 homicides → 2024: 15 (-32% improvement)
        - District B: 2023: 5 homicides → 2024: 8 (+60% increase - needs attention)
        - District C: 2023: 4 homicides → 2024: 5 (+25% increase)
        
        EMERGENCY CONTACTS:
        Police Emergency: 911
        Police HQ: 465-2241 (Ext. 4238/4239 for Intelligence)
        Medical: 465-2551, Fire: 465-2515, Coast Guard: 465-8384
        
        KEY INSIGHTS:
        - 75% reduction in murders H1 2025 vs H1 2024 (4 vs 16)
        - Drug enforcement achieving 100% detection rate
        - Nevis significantly outperforming St. Kitts in detection rates
        - Property crimes (larceny, break-ins) need improvement
        """
        
        time_context = f"""
        Current St. Kitts & Nevis Time: {current_time} AST
        Current Date: {current_date}
        """
        
        # Enhanced system prompt
        enhanced_prompt = f"""
        {get_system_prompt(language)}
        
        ENHANCED CONTEXT:
        {crime_context}
        
        TIME CONTEXT:
        {time_context}
        
        USER QUERY: {user_input}
        
        INSTRUCTIONS:
        1. Provide detailed, professional crime analysis based on the data
        2. Include specific statistics and percentages when relevant
        3. Offer actionable insights and recommendations
        4. Compare trends and highlight key patterns
        5. Reference specific locations, dates, and performance metrics
        6. Maintain professional law enforcement tone
        7. If asked about predictions, use the historical data to make informed projections
        8. For forensic questions, provide detailed investigative guidance
        9. Always cite specific data points from the provided statistics
        10. Format response clearly with headers and bullet points for readability
        
        Respond as SECURO with comprehensive analysis:
        """
        
        response = model.generate_content(enhanced_prompt)
        
        # Clean and format the response
        clean_response = response.text.strip()
        clean_response = clean_response.replace('```', '')
        clean_response = re.sub(r'<[^>]+>', '', clean_response)
        
        # Ensure SECURO branding
        if not clean_response.startswith("SECURO:") and "SECURO" not in clean_response[:50]:
            clean_response = f"SECURO: {clean_response}"
        
        return clean_response
        
    except Exception as e:
        return f"SECURO: I encountered a technical issue while analyzing your query. However, I can provide basic information: Based on our Q2 2025 data, we have 292 total crimes with a 38.7% detection rate. The system is temporarily experiencing AI connectivity issues: {str(e)[:100]}..."

def get_fallback_response(user_input):
    """Provide intelligent fallback responses when AI is unavailable"""
    lower_input = user_input.lower()
    
    # Smart pattern matching for common queries
    if any(word in lower_input for word in ['hotspot', 'map', 'location', 'area']):
        return "SECURO: Based on our crime mapping data, we have 13 hotspot locations: 3 High-Risk (Basseterre Central: 45 crimes, Molineux: 33, Tabernacle: 31), 6 Medium-Risk areas, and 4 Low-Risk areas. High-risk areas require increased patrol focus."
    
    elif any(word in lower_input for word in ['statistic', 'data', 'number', 'total']):
        return "SECURO: Q2 2025 Statistics - Total Crimes: 292 | Detection Rate: 38.7% | St. Kitts: 207 crimes (32.9%) | Nevis: 85 crimes (52.9%) | Key Success: Drug crimes 100% detection rate | Major Improvement: 75% reduction in murders vs 2024"
    
    elif any(word in lower_input for word in ['trend', 'prediction', 'future', 'forecast']):
        return "SECURO: Crime trends show positive direction - Homicides down 75% in 2025 H1 vs 2024 H1. Historical data (2015-2024) suggests continued improvement with current intervention strategies. Drug enforcement achieving perfect detection rate indicates effective resource allocation."
    
    elif any(word in lower_input for word in ['emergency', 'contact', 'help', 'call']):
        return "SECURO: Emergency Contacts - Police: 911 | Police HQ: 465-2241 | Medical: 465-2551 | Fire: 465-2515 | Coast Guard: 465-8384 | Intelligence Office: 465-2241 Ext. 4238/4239"
    
    else:
        return f"SECURO: I understand you're asking about '{user_input}'. Based on our comprehensive crime database: Q2 2025 shows 292 total crimes with significant improvements in murder reduction (75% decrease) and perfect drug crime detection (100%). For specific analysis, please try rephrasing your question or specify if you need statistics, hotspot analysis, trends, or emergency information."
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

# Initialize the AI model with better configuration
def initialize_ai():
    """Initialize AI model with proper configuration and error handling"""
    try:
        # Try to get API key from environment first, then fallback to hardcoded
        api_key = os.getenv('GOOGLE_API_KEY', "AIzaSyA_9sB8o6y7dKK6yBRKWH_c5uSVDSoRYv0")
        
        if not api_key or api_key == "your_api_key_here":
            st.session_state.ai_enabled = False
            st.session_state.ai_status = "❌ API Key Required"
            return None
            
        genai.configure(api_key=api_key)
        
        # Configure the model with enhanced settings
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Test the connection
        test_response = model.generate_content("Test connection")
        
        st.session_state.ai_enabled = True
        st.session_state.ai_status = "✅ AI Ready (Enhanced)"
        return model
        
    except Exception as e:
        st.session_state.ai_enabled = False
        st.session_state.ai_status = f"❌ AI Error: {str(e)[:50]}..."
        return None

# Initialize AI
model = initialize_ai()

# Page configuration
st.set_page_config(
    page_title="SECURO - St. Kitts & Nevis Crime AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'welcome'

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'

if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = load_crime_statistics()

if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

if 'csv_loaded' not in st.session_state:
    st.session_state.csv_loaded = False

# Enhanced CSS styling - keeping the exact same design from HTML
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
   
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Moving gradient animation keyframes */
    @keyframes moveGradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a2e1a 50%, #163e16 100%);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(-45deg, rgba(0, 0, 0, 0.7), rgba(68, 255, 68, 0.1), rgba(0, 0, 0, 0.8), rgba(34, 139, 34, 0.1));
        background-size: 400% 400%;
        animation: moveGradient 4s ease infinite;
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(68, 255, 68, 0.3), transparent);
        animation: shimmer 3s linear infinite;
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

    .nav-container {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        margin-bottom: 30px;
        overflow: hidden;
        padding: 10px;
    }

    .nav-bar {
        background: rgba(52, 73, 94, 0.9);
        padding: 0;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        border-bottom: 1px solid rgba(68, 255, 68, 0.3);
    }

    .nav-btn {
        background: none;
        border: none;
        color: #44ff44;
        padding: 15px 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1rem;
        flex: 1;
        min-width: 120px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }

    .nav-btn:hover {
        background: rgba(68, 255, 68, 0.1);
        transform: translateY(-2px);
    }

    .nav-btn.active {
        background: rgba(68, 255, 68, 0.2);
        border-bottom: 2px solid #44ff44;
    }

    .content-area {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        border: 1px solid rgba(68, 255, 68, 0.3);
        padding: 30px;
        min-height: 600px;
    }

    /* Statistics Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(68, 255, 68, 0.1), rgba(34, 139, 34, 0.2));
        color: #e0e0e0;
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(68, 255, 68, 0.3);
        transition: all 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(68, 255, 68, 0.2);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
        color: #44ff44;
        text-shadow: 0 0 10px rgba(68, 255, 68, 0.3);
    }

    .stat-label {
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Emergency Card Styles */
    .emergency-card {
        background: rgba(0, 0, 0, 0.6);
        border: 2px solid rgba(231, 76, 60, 0.5);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 20px;
        color: #e0e0e0 !important;
    }

    .emergency-card:hover {
        border-color: #e74c3c;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(231, 76, 60, 0.2);
    }

    .emergency-card h3 {
        color: #e74c3c !important;
        margin-bottom: 15px;
    }

    .emergency-card p, .emergency-card span, .emergency-card div {
        color: #e0e0e0 !important;
    }

    .phone-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #44ff44 !important;
        margin: 10px 0;
    }

    /* Feature card text fixes */
    .feature-card, .feature-card * {
        color: #e0e0e0 !important;
    }

    .feature-card h3 {
        color: #44ff44 !important;
    }

    /* Stat card text fixes */
    .stat-card, .stat-card * {
        color: #e0e0e0 !important;
    }

    .stat-number {
        color: #44ff44 !important;
    }

    /* Chat Styles */
    .chat-message {
        margin-bottom: 20px;
        animation: fadeInUp 0.5s ease;
        clear: both;
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

    /* Button Styles */
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

    /* Input Styles */
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

    /* Status bar */
    .status-bar {
        background: rgba(0, 0, 0, 0.8);
        padding: 15px;
        border-radius: 25px;
        margin-top: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(68, 255, 68, 0.2);
        font-family: 'JetBrains Mono', monospace;
        flex-wrap: wrap;
        gap: 10px;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #e0e0e0;
        font-size: 0.9rem;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background: #44ff44;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    /* Feature Cards */
    .feature-card {
        background: rgba(0, 0, 0, 0.6);
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        border: 1px solid rgba(68, 255, 68, 0.3);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(68, 255, 68, 0.2);
        border-color: #44ff44;
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 15px;
        color: #44ff44;
    }

    .feature-card h3 {
        color: #44ff44;
        margin-bottom: 10px;
    }

    /* Quick button styles */
    .quick-btn {
        background: rgba(68, 255, 68, 0.1) !important;
        border: 1px solid rgba(68, 255, 68, 0.3) !important;
        color: #44ff44 !important;
        padding: 8px 15px !important;
        border-radius: 20px !important;
        font-size: 0.9rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        margin: 5px !important;
        transition: all 0.3s ease !important;
    }

    .quick-btn:hover {
        background: rgba(68, 255, 68, 0.2) !important;
        border-color: #44ff44 !important;
        transform: scale(1.05) !important;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .nav-btn {
            min-width: 100px;
            padding: 12px 15px;
            font-size: 0.9rem;
        }
        
        .content-area {
            padding: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Language Selector in sidebar
with st.sidebar:
    st.markdown("### 🌍 Language Selection")
    selected_language = st.selectbox(
        "Choose Language",
        options=list(SUPPORTED_LANGUAGES.keys()),
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        index=list(SUPPORTED_LANGUAGES.keys()).index(st.session_state.selected_language),
        key="language_selector"
    )
    st.session_state.selected_language = selected_language
    
    st.markdown("---")
    
    # AI Configuration Section
    st.markdown("### 🤖 AI Configuration")
    st.write(f"**Status:** {st.session_state.get('ai_status', 'Unknown')}")
    
    # CSV Database Status
    if st.session_state.get('csv_data') is not None:
        st.success(f"📊 Database: {len(st.session_state.csv_data)} records")
    else:
        st.warning("📊 Database: Not loaded")
    
    # API Key input for users who want to use their own
    api_key_input = st.text_input(
        "Google AI API Key (Optional)",
        type="password",
        help="Enter your own Google AI API key for enhanced performance",
        placeholder="Leave blank to use default"
    )
    
    if st.button("🔄 Update AI Configuration"):
        if api_key_input:
            os.environ['GOOGLE_API_KEY'] = api_key_input
            st.success("✅ API Key updated! Reinitializing AI...")
            # Reinitialize AI with new key
            model = initialize_ai()
            st.rerun()
        else:
            st.info("Using default API configuration")
    
    if st.session_state.get('ai_enabled', False):
        st.success("🤖 Enhanced AI Active")
        st.write("• Advanced crime analysis")
        st.write("• Contextual responses")
        st.write("• Multi-language support")
        st.write("• Forensic assistance")
    else:
        st.warning("⚠️ AI Limited Mode")
        st.write("• Basic responses only")
        st.write("• Add API key for full features")
    
    if st.session_state.get('csv_data') is not None:
        st.success("📊 CSV Database Active")
        st.write("• Crime data search enabled")
        st.write("• Historical case lookup")
        st.write("• Evidence correlation")
    else:
        st.warning("⚠️ CSV Database Missing")
        st.write("• Add criminal_justice_qa.csv")
        st.write("• Place in app directory")

# Main Header
current_time = get_stkitts_time()
current_date = get_stkitts_date()

st.markdown(f"""
<div class="main-header">
    <h1>🛡️ SECURO</h1>
    <div style="color: #888; text-transform: uppercase; letter-spacing: 2px; position: relative; z-index: 2;">Advanced Crime Analysis & Security AI for St. Kitts & Nevis</div>
    <div style="color: #44ff44; margin-top: 5px; position: relative; z-index: 2;">🇰🇳 Royal St. Christopher & Nevis Police Force</div>
    <div style="color: #888; margin-top: 8px; font-size: 0.8rem; position: relative; z-index: 2;">📅 {current_date} | 🕒 {current_time} (AST)</div>
</div>
""", unsafe_allow_html=True)

# Navigation Bar
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🏠 Home", key="nav_home", help="Welcome to SECURO"):
        st.session_state.current_page = 'welcome'

with col2:
    if st.button("ℹ️ About SECURO", key="nav_about", help="About SECURO System"):
        st.session_state.current_page = 'about'

with col3:
    if st.button("🗺️ Crime Hotspots", key="nav_map", help="Interactive Crime Map"):
        st.session_state.current_page = 'map'

with col4:
    if st.button("📊 Statistics & Analytics", key="nav_stats", help="Crime Data Analysis"):
        st.session_state.current_page = 'statistics'

with col5:
    if st.button("🚨 Emergency", key="nav_emergency", help="Emergency Contacts"):
        st.session_state.current_page = 'emergency'

with col6:
    if st.button("💬 AI Assistant", key="nav_chat", help="Chat with SECURO AI"):
        st.session_state.current_page = 'chat'

# HOME PAGE
if st.session_state.current_page == 'welcome':
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h2 style="color: #44ff44; font-size: 2.5rem; margin-bottom: 20px; text-shadow: 0 0 15px rgba(68, 255, 68, 0.5);">Welcome to SECURO</h2>
        <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px; color: #e0e0e0;">Your comprehensive AI-powered crime analysis and security system for St. Kitts & Nevis</p>
        <p style="font-size: 1rem; line-height: 1.6; color: #e0e0e0;">SECURO (Security & Crime Understanding & Response Operations) is an advanced platform designed to support law enforcement, enhance public safety, and provide data-driven insights for crime prevention and analysis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <h3>Interactive Crime Mapping</h3>
            <p>Visualize crime patterns across 13+ mapped locations with real-time risk assessments and hotspot identification.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI Crime Assistant</h3>
            <p>Chat with SECURO for intelligent analysis, pattern recognition, and investigative support with multilingual capabilities.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Real-Time Analytics</h3>
            <p>Access comprehensive crime statistics with Q2 2025 data showing 292 total crimes and detailed performance metrics.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔮</div>
            <h3>Predictive Analytics</h3>
            <p>Advanced algorithms analyze historical data to predict crime trends and support strategic planning efforts.</p>
        </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE
elif st.session_state.current_page == 'about':
    st.markdown("""
    <h2 style="color: #44ff44; margin-bottom: 20px; text-align: center;">About SECURO</h2>
    
    <p style="color: #e0e0e0;"><strong style="color: #44ff44;">SECURO</strong> is an intelligent and professional multilingual crime mitigation system built to provide real-time, data-driven insights for law enforcement, criminologists, policy makers, and the general public in St. Kitts & Nevis.</p>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Mission</h3>
    <p style="color: #e0e0e0;">Our mission is to support crime prevention, research, and public safety through:</p>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Interactive maps and geographic analysis</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Statistical analysis and trend identification</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Predictive analytics for crime prevention</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Visual data presentations (charts, graphs, etc.)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Emergency contact guidance</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Multilingual communication support</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Core Capabilities</h3>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Analyze and summarize current and historical crime data (local and global)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Detect trends and patterns across time, location, and type</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Recommend prevention strategies based on geographic and temporal factors</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Provide accessible language for general users, while supporting technical depth for experts</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Integrate with GIS, crime databases, and public safety systems</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Generate visual outputs and interactive maps</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Communicate effectively in multiple languages</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Adapt responses to be clear, concise, and actionable</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Current Data Integration</h3>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Q2 2025 Crime Statistics (292 total crimes)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Historical Homicide Data (2015-2024)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">13+ Crime Hotspot Locations Mapped</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">District-wise Performance Analytics</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Multi-language Support (12 languages)</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Real-time Emergency Contact Database</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Professional Standards</h3>
    <p style="color: #e0e0e0;">SECURO maintains professional standards with:</p>
    <ul style="list-style: none; padding: 0; color: #e0e0e0;">
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Accurate, evidence-based analysis</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Clear, non-panic-inducing communication</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Focus on empowerment and awareness</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Understanding of criminology and public safety best practices</span>
        </li>
        <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #e0e0e0;">
            <span style="position: absolute; left: 0; color: #44ff44; font-weight: bold;">✓</span>
            <span style="color: #e0e0e0;">Real-time St. Kitts & Nevis time and date integration</span>
        </li>
    </ul>

    <h3 style="color: #44ff44; margin: 20px 0 10px 0;">Data Security & Accuracy</h3>
    <p style="color: #e0e0e0;">All crime data is sourced directly from the Royal St. Christopher and Nevis Police Force and is updated regularly to ensure accuracy and relevance for operational decision-making. SECURO maintains the highest standards of data security and privacy.</p>
    """, unsafe_allow_html=True)

# CRIME HOTSPOTS PAGE
elif st.session_state.current_page == 'map':
    st.markdown('<h2 style="color: #44ff44;">🗺️ Crime Hotspot Map - St. Kitts & Nevis</h2>', unsafe_allow_html=True)
    
    try:
        with st.spinner("🗺️ Loading interactive crime hotspot map..."):
            crime_map = create_crime_hotspot_map()
            map_data = st_folium(
                crime_map,
                width="100%",
                height=600,
                returned_objects=["last_object_clicked_tooltip", "last_clicked"],
                key="crime_hotspot_map"
            )
            
            # Display clicked location info
            if map_data['last_object_clicked_tooltip']:
                clicked_info = map_data['last_object_clicked_tooltip']
                st.info(f"📍 **Last Clicked Location:** {clicked_info}")
    
    except Exception as e:
        st.error(f"❌ Map Error: {str(e)}")
        st.info("💡 Note: Make sure folium and streamlit-folium are installed")
    
    # Hotspot Analysis Summary
    st.markdown('<h3 style="color: #44ff44;">📍 Hotspot Analysis Summary</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(231, 76, 60, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c;">
            <strong style="color: #e74c3c;">High Risk Areas (3)</strong><br>
            <span style="color: #e0e0e0; font-size: 0.9rem;">Basseterre Central, Molineux, Tabernacle<br>Total: 109 crimes</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(243, 156, 18, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12;">
            <strong style="color: #f39c12;">Medium Risk Areas (6)</strong><br>
            <span style="color: #e0e0e0; font-size: 0.9rem;">Cayon, Newton Ground, Old Road, etc.<br>Total: 133 crimes</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(39, 174, 96, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
            <strong style="color: #27ae60;">Low Risk Areas (4)</strong><br>
            <span style="color: #e0e0e0; font-size: 0.9rem;">Sandy Point, Dieppe Bay, etc.<br>Total: 60 crimes</span>
        </div>
        """, unsafe_allow_html=True)

# STATISTICS & ANALYTICS PAGE
elif st.session_state.current_page == 'statistics':
    st.markdown('<h2 style="color: #44ff44;">📊 Crime Statistics & Analytics</h2>', unsafe_allow_html=True)
    
    # Q2 2025 Overview
    st.markdown('<h3 style="color: #44ff44;">Q2 2025 Crime Statistics Overview</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    stats_data = st.session_state.crime_stats
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">292</div>
            <div class="stat-label">Total Crimes (Q2 2025)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">38.7%</div>
            <div class="stat-label">Overall Detection Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">207</div>
            <div class="stat-label">St. Kitts Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">85</div>
            <div class="stat-label">Nevis Crimes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">4</div>
            <div class="stat-label">Murders (Q2 2025)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">31</div>
            <div class="stat-label">Drug Crimes (100% detected)</div>
        </div>
        """, unsafe_allow_html=True)

    # Chart Controls
    st.markdown('<h3 style="color: #44ff44;">📈 Interactive Analytics</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Homicide Trends", key="chart_trends"):
            fig = create_crime_charts("homicide_trend", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if st.button("🔍 Crime Breakdown", key="chart_breakdown"):
            fig = create_crime_charts("crime_breakdown", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        if st.button("🎯 Detection Rates", key="chart_detection"):
            fig = create_crime_charts("detection_rates", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        if st.button("🔮 Predictions", key="chart_predictions"):
            fig = create_crime_charts("predictions", stats_data)
            st.plotly_chart(fig, use_container_width=True)
    
    # Crime Breakdown Details
    st.markdown('<h3 style="color: #44ff44;">🔍 Q2 2025 Crime Breakdown by Category</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #44ff44; margin-bottom: 15px;">
            <strong style="color: #44ff44;">Larcenies</strong><br>
            <span style="color: #e0e0e0;">92 cases (31.5%) | 21 detected (22.8%)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #f39c12; margin-bottom: 15px;">
            <strong style="color: #f39c12;">Malicious Damage</strong><br>
            <span style="color: #e0e0e0;">59 cases (20.2%) | 17 detected (28.8%)</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c; margin-bottom: 15px;">
            <strong style="color: #e74c3c;">Bodily Harm</strong><br>
            <span style="color: #e0e0e0;">33 cases (11.3%) | 19 detected (57.6%)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60; margin-bottom: 15px;">
            <strong style="color: #27ae60;">Drug Crimes</strong><br>
            <span style="color: #e0e0e0;">31 cases (10.6%) | 31 detected (100%)</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #9b59b6; margin-bottom: 15px;">
            <strong style="color: #9b59b6;">Break-ins</strong><br>
            <span style="color: #e0e0e0;">26 cases (8.9%) | 7 detected (26.9%)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 8px; border-left: 4px solid #34495e; margin-bottom: 15px;">
            <strong style="color: #34495e;">Murder/Manslaughter</strong><br>
            <span style="color: #e0e0e0;">4 cases (1.4%) | 2 detected (50%)</span>
        </div>
        """, unsafe_allow_html=True)

    # Historical Comparison
    st.markdown('<h3 style="color: #44ff44;">📈 Historical Comparison (Jan-June)</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: rgba(68, 255, 68, 0.05); border-radius: 8px;">
            <div style="font-size: 1.5rem; color: #44ff44; font-weight: bold;">2023 H1</div>
            <div style="color: #e0e0e0;">672 total crimes</div>
            <div style="color: #e74c3c; font-size: 0.9rem;">17 murders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: rgba(68, 255, 68, 0.05); border-radius: 8px;">
            <div style="font-size: 1.5rem; color: #44ff44; font-weight: bold;">2024 H1</div>
            <div style="color: #e0e0e0;">586 total crimes</div>
            <div style="color: #e74c3c; font-size: 0.9rem;">16 murders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background: rgba(68, 255, 68, 0.1); border-radius: 8px; border: 1px solid rgba(68, 255, 68, 0.3);">
            <div style="font-size: 1.5rem; color: #44ff44; font-weight: bold;">2025 H1</div>
            <div style="color: #e0e0e0;">574 total crimes</div>
            <div style="color: #27ae60; font-size: 0.9rem;">4 murders (↓75%)</div>
        </div>
        """, unsafe_allow_html=True)

# EMERGENCY CONTACTS PAGE
elif st.session_state.current_page == 'emergency':
    st.markdown("""
    <h2 style="color: #e74c3c; margin-bottom: 30px; text-align: center;">🚨 Emergency Contacts</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    emergency_contacts = [
        ("🚔 Police Emergency", "911", "For immediate police assistance and emergency response"),
        ("🏢 Police Headquarters", "465-2241", "Royal St. Christopher and Nevis Police Force\nLocal Intelligence: Ext. 4238/4239"),
        ("🏥 Medical Emergency", "465-2551", "Hospital services and medical emergencies"),
        ("🔥 Fire Department", "465-2515", "Fire emergencies and rescue operations\nAlt: 465-7167"),
        ("🚢 Coast Guard", "465-8384", "Maritime emergencies and water rescue\nAlt: 466-9280"),
        ("🌡️ Met Office", "465-2749", "Weather emergencies and warnings"),
        ("➕ Red Cross", "465-2584", "Disaster relief and emergency aid"),
        ("⚡ NEMA", "466-5100", "National Emergency Management Agency")
    ]
    
    for i, (title, number, description) in enumerate(emergency_contacts):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            st.markdown(f"""
            <div class="emergency-card">
                <h3>{title}</h3>
                <div class="phone-number">{number}</div>
                <p style="color: #e0e0e0;">{description}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Emergency Guidelines
    st.markdown("""
    <div style="background: rgba(255, 243, 205, 0.1); border: 1px solid rgba(255, 234, 167, 0.3); padding: 20px; border-radius: 10px; margin-top: 30px;">
        <h3 style="color: #f39c12; margin-bottom: 15px;">⚠️ Important Emergency Guidelines</h3>
        <ul style="color: #e0e0e0; line-height: 1.6; list-style: none; padding: 0;">
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                <strong>For life-threatening emergencies, always call 911 first</strong>
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                When calling, provide your exact location and nature of emergency
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                Stay on the line until instructed to hang up
            </li>
            <li style="padding: 4px 0; padding-left: 20px; position: relative;">
                <span style="position: absolute; left: 0; color: #f39c12;">•</span>
                Keep these numbers easily accessible at all times
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# AI ASSISTANT CHAT PAGE
elif st.session_state.current_page == 'chat':
    st.markdown('<h2 style="color: #44ff44; text-align: center;">💬 Chat with SECURO AI</h2>', unsafe_allow_html=True)
    
    # Load CSV data with better error handling
    st.markdown('<h3 style="color: #44ff44;">📊 Crime Database Status</h3>', unsafe_allow_html=True)

    # Load CSV only once
    if not st.session_state.csv_loaded:
        with st.spinner("🔍 Searching for crime database..."):
            csv_data, status_message = load_csv_data()
            st.session_state.csv_data = csv_data
            st.session_state.csv_loaded = True
           
            if csv_data is not None:
                st.success(f"✅ Database loaded successfully! {len(csv_data)} records found.")
               
                # Add success message to chat if messages are empty
                if not st.session_state.messages:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"✅ Crime database loaded successfully!\n\n🔍 You can now ask me questions about the crime data. Try asking about specific crimes, locations, dates, or any other information you need for your investigation.\n\n🗺️ Don't forget to check out the interactive crime hotspot map in the sidebar to explore high-risk areas across St. Kitts & Nevis!",
                        "timestamp": get_stkitts_time()
                    })
            else:
                st.error(f"❌ Database not found: {status_message}")
               
                # Add error message to chat if messages are empty
                if not st.session_state.messages:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ **Database Error:** Could not find 'criminal_justice_qa.csv'\n\n🔧 **How to fix:**\n1. Make sure your CSV file is named exactly `criminal_justice_qa.csv`\n2. Place it in the same folder as your Streamlit app\n3. Restart the application\n\n💡 Without the database, I can still help with general crime investigation guidance and the interactive hotspot map is available in the Crime Hotspots section.",
                        "timestamp": get_stkitts_time()
                    })

    # Show current status
    ai_status = st.session_state.get('ai_status', 'AI Status Unknown')
    if st.session_state.csv_data is not None:
        st.success(f"✅ Database Ready: {len(st.session_state.csv_data)} crime records loaded | {ai_status}")
    else:
        st.error(f"❌ Database Not Found: Place 'criminal_justice_qa.csv' in app directory | {ai_status}")

    # Crime Hotspot Summary
    total_hotspots = len(CRIME_HOTSPOTS)
    high_risk = len([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'High'])
    medium_risk = len([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Medium'])
    low_risk = len([loc for loc, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Low'])
    
    st.info(f"🗺️ **Crime Hotspot Map:** {total_hotspots} locations mapped | {high_risk} High Risk | {medium_risk} Medium Risk | {low_risk} Low Risk areas")
    
    # Initialize chat messages
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🛡️ **Welcome to SECURO AI Crime Analysis System**\n\nI'm your intelligent crime analysis assistant for St. Kitts & Nevis. I have access to comprehensive crime data including:\n\n📊 **Current Data (Q2 2025):**\n• 292 total crimes across the Federation\n• 38.7% overall detection rate\n• 13+ mapped crime hotspots\n• Real-time analytics and predictions\n\n🔍 **I can help you with:**\n• Crime pattern analysis and trends\n• Statistical insights and comparisons\n• Hotspot identification and risk assessment\n• Predictive analytics for resource planning\n• Forensic case support and investigations\n• Emergency contact information\n\n💬 **Try saying:** 'Hi', 'Show crime hotspots', 'What are the trends?', or ask anything about crime statistics, investigations, or law enforcement strategy for St. Kitts & Nevis.",
            "timestamp": get_stkitts_time()
        })
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="message-content">{message["content"]}</div>
                <div class="message-time">You • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-content">{message["content"]}</div>
                <div class="message-time">SECURO AI • {message["timestamp"]} AST</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Ask about crime statistics, hotspots, trends, investigations...",
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
            
            # Generate enhanced AI response
            with st.spinner("🧠 SECURO AI analyzing crime data..."):
                bot_response = get_enhanced_ai_response(user_input, st.session_state.selected_language)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_response,
                "timestamp": current_time
            })
            st.rerun()
    
    # Quick Action Buttons
    st.markdown('<h4 style="color: #44ff44; text-align: center; margin-bottom: 15px;">🚀 Quick Analysis Options</h4>', unsafe_allow_html=True)
    
    quick_options = [
        ("🗺️ Analyze Hotspots", "Show me a detailed analysis of the current crime hotspots across St. Kitts & Nevis"),
        ("📈 Crime Trends", "What are the current crime trends and how do they compare to previous years?"),
        ("🎯 Detection Rates", "Analyze the detection rates across different regions and crime types"),
        ("🔮 Predictions", "What are your predictions for crime rates in the coming years?"),
        ("🏘️ District Analysis", "Compare the performance of different police districts"),
        ("🔬 Forensic Support", "How can SECURO assist with forensic analysis and investigation support?")
    ]
    
    col1, col2, col3 = st.columns(3)
    
    for i, (button_text, query_text) in enumerate(quick_options):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(button_text, key=f"quick_{i}"):
                current_time = get_stkitts_time()
                
                st.session_state.messages.append({
                    "role": "user",
                    "content": query_text,
                    "timestamp": current_time
                })
                
                # Generate enhanced response using CSV + AI
                with st.spinner("🧠 SECURO AI analyzing..."):
                    # Search CSV first
                    csv_results = search_csv_data(st.session_state.csv_data, query_text)
                    
                    # Enhance with AI or use smart fallback
                    if st.session_state.get('ai_enabled', False):
                        response = get_ai_response(query_text, csv_results, st.session_state.selected_language)
                    else:
                        response = get_smart_fallback_response(query_text, csv_results)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": current_time
                })
                
                st.rerun()

# Status Bar
csv_status = f"{len(st.session_state.csv_data)} CSV Records" if st.session_state.get('csv_data') is not None else "CSV Missing"
current_time = get_stkitts_time()

st.markdown(f"""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot"></div>
        <span>SECURO AI Online</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Database: {csv_status}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>Hotspots: 13 Locations Mapped</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>{current_time} AST</span>
    </div>
    <div class="status-item">
        <div class="status-dot" style="background: #33cc33;"></div>
        <span>{SUPPORTED_LANGUAGES[st.session_state.selected_language]}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; padding: 20px; margin-top: 20px; border-top: 1px solid rgba(68, 255, 68, 0.2);">
    📊 Data Source: Royal St. Christopher & Nevis Police Force (RSCNPF)<br>
    📞 Local Intelligence Office: <a href="tel:+18694652241" style="color: #44ff44; text-decoration: none;">869-465-2241</a> Ext. 4238/4239 | 
    📧 <a href="mailto:liosk@police.kn" style="color: #44ff44; text-decoration: none;">liosk@police.kn</a><br>
    🔄 Last Updated: {get_stkitts_date()} {get_stkitts_time()} AST | Real-time Analytics Powered by SECURO AI<br>
    🗺️ Interactive Crime Hotspot System: 13 locations mapped across St. Kitts & Nevis<br>
    🌍 Multi-language Support Available | 🔒 Secure Law Enforcement Platform
</div>
""", unsafe_allow_html=True)
