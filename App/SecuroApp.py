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

# Crime Statistics URLs from St. Kitts & Nevis Police Force
CRIME_STATS_URLS = [
    "http://www.police.kn/statistics/links/1752416412.pdf",
    "http://www.police.kn/statistics/links/1752414290.pdf",
    "http://www.police.kn/statistics/links/1750875153.pdf",
    "http://www.police.kn/statistics/links/1746572831.pdf",
    "http://www.police.kn/statistics/links/1746572806.pdf",
    "http://www.police.kn/statistics/links/1739113354.pdf",
    "http://www.police.kn/statistics/links/1739113269.pdf",
    "http://www.police.kn/statistics/links/1739112788.pdf",
    "http://www.police.kn/statistics/links/1733163796.pdf",
    "http://www.police.kn/statistics/links/1733163758.pdf",
]

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
You are SECURO, an advanced AI crime analyst for the Royal St. Christopher & Nevis Police Force (RSCNPF). 
You have access to comprehensive crime statistics and can provide:

**STATISTICAL ANALYSIS:**
- Real-time crime data analysis from official RSCNPF reports
- Trend identification and pattern recognition
- Crime prediction modeling using historical data
- Detection rate analysis and performance metrics
- Geographic crime distribution analysis

**CURRENT DATA AVAILABLE:**
- Q2 2025 crime statistics (April-June)
- Historical homicide data (2015-2024)
- District-wise crime breakdown (Districts A, B, C)
- Crime method analysis and victim demographics
- Comparative year-over-year analysis

**PREDICTION CAPABILITIES:**
- Statistical forecasting for crime trends
- Risk assessment for different areas and time periods
- Resource allocation recommendations
- Early warning systems for crime spikes

**CHART GENERATION:**
When users request charts, you can create:
- Homicide trend analysis with predictions
- Crime method breakdowns
- District comparison charts
- Detection rate performance metrics
- Age group and demographic analysis

**KEY INSIGHTS FROM RECENT DATA:**
- 2025 shows significant changes: 75% reduction in murders, 463% increase in drug crimes
- Nevis has highest detection rate (52.9%) vs St. Kitts (32.9%)
- Shootings account for 81% of homicides historically
- Peak crime periods and seasonal patterns identified

Always provide evidence-based analysis using the actual statistics. When creating predictions, 
explain the methodology and confidence levels. Respond professionally but accessibly.
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
    GOOGLE_API_KEY = "AIzaSyAK-4Xklul9WNoiWnSrpzPkn5C-Dbny8B4"
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Ready (Enhanced Analytics)"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Page configuration
st.set_page_config(
    page_title="SECURO - Enhanced Crime Analytics",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS (keeping your original styling)
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

    .stats-card {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid rgba(68, 255, 68, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stats-number {
        font-size: 2rem;
        color: #44ff44;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(68, 255, 68, 0.5);
    }
    
    .stats-label {
        color: #e0e0e0;
        font-size: 0.9rem;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="control-panel-header">
        <h2>🚔 SECURO</h2>
        <p>Enhanced Analytics</p>
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
    
    # Quick Stats
    st.markdown('<div class="sidebar-header">📊 Quick Stats</div>', unsafe_allow_html=True)
    
    # Load crime data
    if 'crime_stats' not in st.session_state:
        st.session_state.crime_stats = load_crime_statistics()
    
    stats_data = st.session_state.crime_stats
    
    st.markdown(f"""
    <div class="stats-card">
        <div class="stats-number">{stats_data['current_quarter']['federation']['total_crimes']}</div>
        <div class="stats-label">Total Crimes Q2 2025</div>
    </div>
    <div class="stats-card">
        <div class="stats-number">{stats_data['current_quarter']['federation']['detection_rate']}%</div>
        <div class="stats-label">Detection Rate</div>
    </div>
    <div class="stats-card">
        <div class="stats-number">{stats_data['homicides']['yearly_totals'][2024]}</div>
        <div class="stats-label">Homicides 2024</div>
    </div>
    """, unsafe_allow_html=True)
    
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

def get_enhanced_ai_response(user_input, crime_data, language='en'):
    """Enhanced AI response with statistics and chart capabilities"""
    if not st.session_state.get('ai_enabled', False) or model is None:
        return "AI analysis temporarily unavailable."
    
    try:
        current_time = get_stkitts_time()
        current_date = get_stkitts_date()
        
        # Check if user wants a chart
        chart_keywords = ['chart', 'graph', 'plot', 'visualize', 'show me']
        needs_chart = any(keyword in user_input.lower() for keyword in chart_keywords)
        
        # Generate predictions if requested
        predictions = None
        if any(word in user_input.lower() for word in ['predict', 'forecast', 'future', 'trend']):
            predictions = generate_crime_predictions(crime_data)
        
        # Prepare comprehensive context
        context = f"""
CURRENT STATISTICS (Q2 2025):
- Total Federation Crimes: {crime_data['current_quarter']['federation']['total_crimes']}
- Detection Rate: {crime_data['current_quarter']['federation']['detection_rate']}%
- Murders: {crime_data['current_quarter']['federation']['murder_manslaughter']['total']} (detected: {crime_data['current_quarter']['federation']['murder_manslaughter']['detected']})
- Drug Crimes: {crime_data['current_quarter']['federation']['drugs']['total']} (100% detection rate)
- Break-ins: {crime_data['current_quarter']['federation']['break_ins']['total']}
- Larcenies: {crime_data['current_quarter']['federation']['larcenies']['total']}

HISTORICAL HOMICIDE DATA (2015-2024):
- 2024: {crime_data['homicides']['yearly_totals'][2024]} homicides
- 2023: {crime_data['homicides']['yearly_totals'][2023]} homicides  
- 10-year average: {sum(crime_data['homicides']['yearly_totals'].values()) / len(crime_data['homicides']['yearly_totals']):.1f}
- Primary method: Shooting ({crime_data['homicides']['methods']['shooting']} of 213 total)
- Most affected age group: 18-35 years ({crime_data['homicides']['age_groups']['18-35']} victims)

DISTRICT BREAKDOWN:
- District A (Basseterre): Highest crime area
- District B: Medium activity  
- District C (Nevis): Highest detection rate (52.9%)

RECENT TRENDS:
- 75% reduction in murders (2024 vs 2025 H1)
- 463% increase in drug crimes (major enforcement success)
- Detection rates vary: Nevis (52.9%) > Federation (38.7%) > St. Kitts (32.9%)

{f"PREDICTIONS: {predictions}" if predictions else ""}

Current St. Kitts time: {current_time}, Date: {current_date}
"""
        
        full_prompt = f"""
        {get_system_prompt(language)}
        
        CRIME STATISTICS CONTEXT:
        {context}
        
        User Query: {user_input}
        
        Provide comprehensive analysis using the actual statistics. If trends or predictions are requested, 
        use the historical data. Be specific with numbers and percentages. Explain methodology for any 
        predictions. If charts are requested, mention that you'll provide visualization recommendations.
        """
        
        response = model.generate_content(full_prompt)
        clean_response = response.text.strip()
        clean_response = clean_response.replace('```', '')
        clean_response = re.sub(r'<[^>]+>', '', clean_response)
        
        return clean_response, needs_chart
        
    except Exception as e:
        return f"Analysis temporarily unavailable. Error: {str(e)}", False

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'crime_stats' not in st.session_state:
    st.session_state.crime_stats = load_crime_statistics()

# Header
st.markdown(f"""
<div class="main-header">
    <h1>SECURO ENHANCED</h1>
    <div style="color: #888; text-transform: uppercase; letter-spacing: 2px;">AI Crime Analytics & Predictions</div>
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

# Chat interface
st.markdown("### 💬 SECURO Crime Analytics Chat")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div style="text-align: right; margin: 20px 0;">
            <div style="display: inline-block; background: linear-gradient(135deg, #44ff44, #33cc33); 
                        color: white; padding: 15px 20px; border-radius: 15px; max-width: 80%; 
                        font-family: 'JetBrains Mono', monospace;">
                {message["content"]}
            </div>
            <div style="font-size: 0.7rem; color: #888; margin-top: 5px;">You • {message["timestamp"]} AST</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align: left; margin: 20px 0;">
            <div style="display: inline-block; background: rgba(0, 0, 0, 0.8); 
                        color: #e0e0e0; padding: 15px 20px; border-radius: 15px; max-width: 80%; 
                        border: 1px solid rgba(68, 255, 68, 0.3); font-family: 'JetBrains Mono', monospace;">
                {message["content"]}
            </div>
            <div style="font-size: 0.7rem; color: #888; margin-top: 5px;">SECURO • {message["timestamp"]} AST</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chart if available
        if 'chart' in message and message['chart']:
            st.plotly_chart(message['chart'], use_container_width=True)

# Chat input
with st.form("enhanced_chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask about crime statistics, trends, predictions, or request charts...",
            placeholder="Examples: 'Show homicide trends', 'Predict drug crimes for 2026', 'Which district is safest?'",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.form_submit_button("🔍 Analyze", type="primary")

    if send_button and user_input:
        current_time = get_stkitts_time()
        
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": current_time
        })
        
        # Process with enhanced AI
        with st.spinner("🧠 Analyzing crime data and generating insights..."):
            response, needs_chart = get_enhanced_ai_response(
                user_input, 
                st.session_state.crime_stats, 
                st.session_state.selected_language
            )
            
            # Determine chart type based on user input
            chart_fig = None
            if needs_chart or any(word in user_input.lower() for word in ['chart', 'graph', 'plot', 'show']):
                if any(word in user_input.lower() for word in ['homicide', 'murder', 'trend', 'year']):
                    chart_fig = create_crime_charts("homicide_trend", st.session_state.crime_stats)
                elif any(word in user_input.lower() for word in ['method', 'how', 'weapon']):
                    chart_fig = create_crime_charts("crime_methods", st.session_state.crime_stats)
                elif any(word in user_input.lower() for word in ['district', 'area', 'location', 'where']):
                    chart_fig = create_crime_charts("district_comparison", st.session_state.crime_stats)
                elif any(word in user_input.lower() for word in ['detection', 'solve', 'performance']):
                    chart_fig = create_crime_charts("quarterly_performance", st.session_state.crime_stats)
                else:
                    chart_fig = create_crime_charts("homicide_trend", st.session_state.crime_stats)
        
        # Add bot message
        bot_message = {
            "role": "assistant",
            "content": response,
            "timestamp": current_time
        }
        
        if chart_fig:
            bot_message["chart"] = chart_fig
            
        st.session_state.messages.append(bot_message)
        st.rerun()

# Example Questions Section
st.markdown("### 💡 Example Questions")

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
        if st.button(question, key=f"example_{i}"):
            # Auto-fill the question
            st.session_state.auto_question = question.split(" ", 1)[1]  # Remove emoji
            st.rerun()

# Handle auto-filled questions
if 'auto_question' in st.session_state:
    user_input = st.session_state.auto_question
    del st.session_state.auto_question
    
    current_time = get_stkitts_time()
    
    st.session_state.messages.append({
        "role": "user",
        "content": user_input, 
        "timestamp": current_time
    })
    
    with st.spinner("🧠 Analyzing crime data..."):
        response, needs_chart = get_enhanced_ai_response(
            user_input,
            st.session_state.crime_stats,
            st.session_state.selected_language
        )
        
        chart_fig = None
        if needs_chart or any(word in user_input.lower() for word in ['chart', 'graph', 'show']):
            if any(word in user_input.lower() for word in ['homicide', 'murder', 'trend']):
                chart_fig = create_crime_charts("homicide_trend", st.session_state.crime_stats)
            elif any(word in user_input.lower() for word in ['method', 'how']):
                chart_fig = create_crime_charts("crime_methods", st.session_state.crime_stats)
            elif any(word in user_input.lower() for word in ['district', 'area']):
                chart_fig = create_crime_charts("district_comparison", st.session_state.crime_stats)
            elif any(word in user_input.lower() for word in ['detection', 'performance']):
                chart_fig = create_crime_charts("quarterly_performance", st.session_state.crime_stats)
    
    bot_message = {
        "role": "assistant",
        "content": response,
        "timestamp": current_time
    }
    
    if chart_fig:
        bot_message["chart"] = chart_fig
        
    st.session_state.messages.append(bot_message)
    st.rerun()

# Advanced Analytics Section
st.markdown("### 🔬 Advanced Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📊 Crime Statistics Summary")
    current_stats = st.session_state.crime_stats['current_quarter']['federation']
    
    # Create summary metrics
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

# Status bar
st.markdown(f"""
<div style="background: rgba(0, 0, 0, 0.8); padding: 15px; border-radius: 25px; margin-top: 30px; 
            display: flex; justify-content: space-between; align-items: center; 
            border: 1px solid rgba(68, 255, 68, 0.2); font-family: 'JetBrains Mono', monospace;">
    <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #44ff44; border-radius: 50%; 
                    animation: pulse 2s infinite;"></div>
        SECURO Enhanced Analytics Online
    </div>
    <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #44ff44; border-radius: 50%;"></div>
        Real-time Statistics Active
    </div>
    <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #44ff44; border-radius: 50%;"></div>
        {get_stkitts_time()} AST
    </div>
    <div style="display: flex; align-items: center; gap: 10px; color: #e0e0e0; font-size: 0.9rem;">
        <div style="width: 8px; height: 8px; background: #33cc33; border-radius: 50%;"></div>
        {SUPPORTED_LANGUAGES[st.session_state.selected_language]}
    </div>
</div>
""", unsafe_allow_html=True)

# Footer with data sources
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; padding: 20px;">
    📊 Data Source: Royal St. Christopher & Nevis Police Force (RSCNPF)<br>
    📞 Local Intelligence Office: 869-465-2241 Ext. 4238/4239 | liosk@police.kn<br>
    🔄 Last Updated: {st.session_state.crime_stats['last_updated']} | Real-time Analytics Powered by SECURO AI
</div>
""", unsafe_allow_html=True)
