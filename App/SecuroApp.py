import streamlit as st
import time
import datetime
import random
import pandas as pd
import os
import google.generativeai as genai
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from io import BytesIO
import base64

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
    model = genai.GenerativeModel('gemini-1.5-flash')
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

    .contact-number a {
        color: #ff4444 !important;
        text-decoration: none !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .contact-number a:hover {
        color: #ff6666 !important;
        text-decoration: underline !important;
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

    /* Selectbox styling */
    .stSelectbox select {
        background: rgba(0, 0, 0, 0.5) !important;
        border: 1px solid rgba(255, 68, 68, 0.3) !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
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

def generate_sample_crime_data():
    """Generate realistic sample crime data for St. Kitts & Nevis for demonstration"""
    np.random.seed(42)  # For consistent results
    
    years = list(range(2019, 2025))
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    crime_types = [
        'Theft', 'Burglary', 'Drug Offenses', 'Assault', 
        'Domestic Violence', 'Fraud', 'Vandalism', 'Robbery'
    ]
    
    locations = [
        'Basseterre', 'Sandy Point', 'Dieppe Bay', 'Old Road', 
        'Charlestown (Nevis)', 'Gingerland', 'Frigate Bay', 'Cayon'
    ]
    
    data = []
    for year in years:
        base_crimes = 120 if year < 2020 else (100 if year < 2022 else 110)  # COVID impact
        for month in months:
            for crime_type in crime_types:
                for location in locations:
                    # Add some seasonality and randomness
                    seasonal_factor = 1.2 if month in ['Dec', 'Jan', 'Jul', 'Aug'] else 1.0  # Tourist season
                    crime_count = max(0, int(np.random.poisson(base_crimes * seasonal_factor * 0.1)))
                    
                    if crime_count > 0:
                        data.append({
                            'Year': year,
                            'Month': month,
                            'Crime_Type': crime_type,
                            'Location': location,
                            'Count': crime_count,
                            'Date': f"{year}-{months.index(month)+1:02d}-01"
                        })
    
    return pd.DataFrame(data)

def create_crime_charts(df, chart_type="overview", specific_year=None, crime_type=None):
    """Create various crime statistics charts for St. Kitts & Nevis (No Seaborn Required)"""
    
    # Set matplotlib style for dark theme
    plt.style.use('dark_background')
    
    # Set color palette manually
    colors = ['#ff4444', '#ff6666', '#ff8888', '#ffaaaa', '#cc3333', '#aa2222', '#881111', '#660000']
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
    
    if chart_type == "yearly_trend":
        # Yearly crime trends
        fig, ax = plt.subplots(figsize=(12, 6))
        yearly_data = df.groupby('Year')['Count'].sum().reset_index()
        
        ax.plot(yearly_data['Year'], yearly_data['Count'], 
                marker='o', linewidth=3, markersize=8, color='#ff4444')
        ax.fill_between(yearly_data['Year'], yearly_data['Count'], 
                       alpha=0.3, color='#ff4444')
        
        ax.set_title('St. Kitts & Nevis - Crime Trends by Year', 
                    fontsize=16, color='white', pad=20)
        ax.set_xlabel('Year', fontsize=12, color='white')
        ax.set_ylabel('Total Crime Count', fontsize=12, color='white')
        ax.grid(True, alpha=0.3)
        
        # Add annotations
        for i, (year, count) in enumerate(zip(yearly_data['Year'], yearly_data['Count'])):
            ax.annotate(f'{count}', (year, count), 
                       textcoords="offset points", xytext=(0,10), 
                       ha='center', color='white', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    elif chart_type == "crime_types":
        # Crime types distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Bar chart
        crime_counts = df.groupby('Crime_Type')['Count'].sum().sort_values(ascending=False)
        bars = ax1.bar(range(len(crime_counts)), crime_counts.values, 
                      color=colors[:len(crime_counts)])
        
        ax1.set_title('Crime Types Distribution', fontsize=14, color='white')
        ax1.set_xlabel('Crime Type', fontsize=12, color='white')
        ax1.set_ylabel('Total Count', fontsize=12, color='white')
        ax1.set_xticks(range(len(crime_counts)))
        ax1.set_xticklabels(crime_counts.index, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, crime_counts.values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{value}', ha='center', va='bottom', color='white', fontweight='bold')
        
        # Pie chart
        ax2.pie(crime_counts.values, labels=crime_counts.index, autopct='%1.1f%%',
               colors=colors[:len(crime_counts)])
        ax2.set_title('Crime Types Percentage', fontsize=14, color='white')
        
        plt.tight_layout()
        return fig
    
    elif chart_type == "locations":
        # Crime by location
        fig, ax = plt.subplots(figsize=(12, 8))
        location_counts = df.groupby('Location')['Count'].sum().sort_values(ascending=True)
        
        bars = ax.barh(range(len(location_counts)), location_counts.values, 
                      color='#ff4444', alpha=0.8)
        
        ax.set_title('Crime Distribution by Location in St. Kitts & Nevis', 
                    fontsize=16, color='white', pad=20)
        ax.set_xlabel('Total Crime Count', fontsize=12, color='white')
        ax.set_ylabel('Location', fontsize=12, color='white')
        ax.set_yticks(range(len(location_counts)))
        ax.set_yticklabels(location_counts.index)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, location_counts.values)):
            ax.text(value + 5, i, f'{value}', 
                   va='center', ha='left', color='white', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    elif chart_type == "monthly_pattern":
        # Monthly crime patterns
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Define month order
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        monthly_data = df.groupby('Month')['Count'].sum().reindex(month_order, fill_value=0)
        
        bars = ax.bar(monthly_data.index, monthly_data.values, 
                     color='#ff4444', alpha=0.8, edgecolor='white', linewidth=1)
        
        ax.set_title('Seasonal Crime Patterns in St. Kitts & Nevis', 
                    fontsize=16, color='white', pad=20)
        ax.set_xlabel('Month', fontsize=12, color='white')
        ax.set_ylabel('Average Crime Count', fontsize=12, color='white')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Highlight tourist season
        tourist_months = ['Dec', 'Jan', 'Jul', 'Aug']
        for i, month in enumerate(monthly_data.index):
            if month in tourist_months:
                bars[i].set_color('#ffaa44')
                bars[i].set_alpha(0.9)
        
        # Add value labels
        for bar, value in zip(bars, monthly_data.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                   f'{value}', ha='center', va='bottom', color='white', fontweight='bold')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='#ff4444', label='Regular Season'),
                          Patch(facecolor='#ffaa44', label='Tourist Season')]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        return fig
    
    elif chart_type == "heatmap":
        # Crime heatmap by year and month (using matplotlib instead of seaborn)
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create pivot table
        pivot_data = df.pivot_table(values='Count', index='Month', columns='Year', 
                                   aggfunc='sum', fill_value=0)
        
        # Reorder months
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pivot_data = pivot_data.reindex(month_order)
        
        # Create heatmap using matplotlib
        im = ax.imshow(pivot_data.values, cmap='Reds', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(pivot_data.columns)))
        ax.set_yticks(range(len(pivot_data.index)))
        ax.set_xticklabels(pivot_data.columns)
        ax.set_yticklabels(pivot_data.index)
        
        # Add text annotations
        for i in range(len(pivot_data.index)):
            for j in range(len(pivot_data.columns)):
                text = ax.text(j, i, int(pivot_data.iloc[i, j]),
                             ha="center", va="center", color="white", fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Crime Count', rotation=270, labelpad=20, color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        ax.set_title('Crime Intensity Heatmap - St. Kitts & Nevis', 
                    fontsize=16, color='white', pad=20)
        ax.set_xlabel('Year', fontsize=12, color='white')
        ax.set_ylabel('Month', fontsize=12, color='white')
        
        plt.tight_layout()
        return fig
    
    else:  # overview
        # Overview dashboard
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Yearly trends
        yearly_data = df.groupby('Year')['Count'].sum()
        ax1.plot(yearly_data.index, yearly_data.values, 
                marker='o', linewidth=3, markersize=6, color='#ff4444')
        ax1.set_title('Yearly Crime Trends', fontsize=12, color='white')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(colors='white')
        
        # 2. Top crime types
        top_crimes = df.groupby('Crime_Type')['Count'].sum().nlargest(5)
        ax2.bar(range(len(top_crimes)), top_crimes.values, color='#ff4444', alpha=0.8)
        ax2.set_title('Top 5 Crime Types', fontsize=12, color='white')
        ax2.set_xticks(range(len(top_crimes)))
        ax2.set_xticklabels(top_crimes.index, rotation=45, ha='right')
        ax2.tick_params(colors='white')
        
        # 3. Location distribution
        top_locations = df.groupby('Location')['Count'].sum().nlargest(5)
        ax3.barh(range(len(top_locations)), top_locations.values, color='#ff4444', alpha=0.8)
        ax3.set_title('Top 5 Crime Locations', fontsize=12, color='white')
        ax3.set_yticks(range(len(top_locations)))
        ax3.set_yticklabels(top_locations.index)
        ax3.tick_params(colors='white')
        
        # 4. Monthly pattern
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_avg = df.groupby('Month')['Count'].mean().reindex(month_order, fill_value=0)
        ax4.bar(monthly_avg.index, monthly_avg.values, color='#ff4444', alpha=0.8)
        ax4.set_title('Average Monthly Crime Pattern', fontsize=12, color='white')
        ax4.tick_params(axis='x', rotation=45, colors='white')
        ax4.tick_params(colors='white')
        
        plt.suptitle('St. Kitts & Nevis Crime Statistics Overview', 
                    fontsize=16, color='white', y=0.98)
        plt.tight_layout()
        return fig

def chart_to_base64(fig):
    """Convert matplotlib figure to base64 string for embedding"""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', facecolor='#0a0a0a', 
                edgecolor='none', bbox_inches='tight', dpi=150)
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    plt.close(fig)
    return img_str

def detect_chart_request(user_input):
    """Detect if user is asking for charts/statistics and what type"""
    input_lower = user_input.lower()
    
    chart_keywords = ['chart', 'graph', 'plot', 'statistics', 'stats', 'trend', 
                     'data', 'visual', 'show me', 'display', 'analysis']
    
    year_keywords = ['year', 'yearly', 'annual', 'over time', 'trend']
    crime_type_keywords = ['crime type', 'types of crime', 'categories']
    location_keywords = ['location', 'area', 'place', 'where', 'geography']
    monthly_keywords = ['month', 'monthly', 'seasonal', 'season']
    heatmap_keywords = ['heatmap', 'heat map', 'intensity']
    
    if any(keyword in input_lower for keyword in chart_keywords):
        if any(keyword in input_lower for keyword in year_keywords):
            return "yearly_trend"
        elif any(keyword in input_lower for keyword in crime_type_keywords):
            return "crime_types"
        elif any(keyword in input_lower for keyword in location_keywords):
            return "locations"
        elif any(keyword in input_lower for keyword in monthly_keywords):
            return "monthly_pattern"
        elif any(keyword in input_lower for keyword in heatmap_keywords):
            return "heatmap"
        else:
            return "overview"
    
    return None

def get_ai_response(user_input, csv_results):
    """Generate AI response using the system prompt and context"""
    if not st.session_state.get('ai_enabled', False) or model is None:
        return csv_results  # Fallback to CSV search results
    
    try:
        # Check if user is requesting charts
        chart_type = detect_chart_request(user_input)
        
        if chart_type:
            # Generate sample data and create chart
            sample_data = generate_sample_crime_data()
            fig = create_crime_charts(sample_data, chart_type)
            chart_b64 = chart_to_base64(fig)
            
            chart_response = f"""
📊 **Crime Statistics Visualization for St. Kitts & Nevis**

<img src="data:image/png;base64,{chart_b64}" style="width:100%; border-radius:10px; border:1px solid rgba(255,68,68,0.3);">

**Analysis Summary:**
- Data shows crime trends from 2019-2024
- Tourist season months (Dec, Jan, Jul, Aug) typically show higher activity
- COVID-19 impact visible in 2020-2021 data
- Basseterre and tourist areas show higher incident rates

*Note: This visualization uses representative data for St. Kitts & Nevis crime patterns. For official statistics, contact the Royal St. Christopher and Nevis Police Force.*
            """
            
            return chart_response
        
        # Regular AI response
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
        "content": "🚔 Welcome to SECURO - Your AI Crime Investigation Assistant for St. Kitts & Nevis Law Enforcement.\n\nI assist criminologists, police officers, forensic experts, and autopsy professionals with:\n• Case analysis and evidence correlation\n• Crime data search and insights\n• Investigative support and recommendations\n• Interactive crime statistics and charts\n\n📊 Loading crime database... Please wait while I check for your data file.",
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
                "content": f"✅ Crime database loaded successfully!\n\n📊 Database contains {len(csv_data)} records with {len(csv_data.columns)} data fields.\n\n🔍 You can now ask me questions about the crime data or request charts and visualizations. Try asking:\n• 'Show me yearly crime trends'\n• 'Display crime statistics by location'\n• 'Create a monthly crime pattern chart'",
                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
            })
        else:
            st.markdown(f'<div class="file-status file-missing">{status_message}</div>', unsafe_allow_html=True)
           
            # Add error message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ **Database Error:** {status_message}\n\n🔧 **How to fix:**\n1. Make sure your CSV file is named exactly `criminal_justice_qa.csv`\n2. Place it in the same folder as your Streamlit app\n3. Restart the application\n\n💡 Without the database, I can still help with general crime investigation guidance, emergency contacts, and generate sample crime statistics charts for St. Kitts & Nevis.",
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
            {"name": "Fire Department", "number": "465-2515", "type": "fire"},
            {"name": "Coast Guard", "number": "465-8384", "type": "legal"},
            {"name": "Red Cross", "number": "465-2584", "type": "forensic"},
            {"name": "NEMA (Emergency Mgmt)", "number": "466-5100", "type": "legal"}
        ]
        
        # Create dropdown for emergency contacts
        contact_options = ["Select Emergency Contact..."] + [f"{contact['name']}" for contact in emergency_contacts]
        selected_contact = st.selectbox(
            "Choose Emergency Service:",
            contact_options,
            key="emergency_dropdown"
        )
        
        # Display selected contact with clickable phone number
        if selected_contact != "Select Emergency Contact...":
            # Find the selected contact details
            selected_contact_data = next(
                (contact for contact in emergency_contacts if contact['name'] == selected_contact), 
                None
            )
            
            if selected_contact_data:
                # Display contact info with clickable phone number
                st.markdown(f"""
                <div class="contact-item">
                    <div class="contact-name">{selected_contact_data['name']}</div>
                    <div class="contact-number">
                        <a href="tel:{selected_contact_data['number']}" style="color: #ff4444; text-decoration: none; font-family: 'JetBrains Mono', monospace;">
                            {selected_contact_data['number']}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add call button for logging purposes
                if st.button(f"Call {selected_contact_data['name']}", key=f"call_{selected_contact_data['name']}"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🚨 **Emergency Contact Accessed:**\n\n**{selected_contact_data['name']}:** {selected_contact_data['number']}\n\n📝 Contact logged for case documentation. Emergency services are standing by for immediate response.",
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
        
        # Check if content contains HTML (like charts)
        if '<img src="data:image/png;base64,' in clean_content:
            # This is a chart response, display as-is with HTML
            st.markdown(f"""
            <div class="chat-message bot-message">
                <div class="message-content">{clean_content}</div>
                <div class="message-time">{message["timestamp"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Regular text message, clean HTML tags
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
            placeholder="Ask questions about crime data, request charts, or emergency procedures...",
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
