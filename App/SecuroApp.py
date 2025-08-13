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
import hashlib
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import tempfile

warnings.filterwarnings('ignore')

# Configuration
GOOGLE_API_KEY = "AIzaSyBYRyEfONMUHdYmeFDkUGSTP1rNEy_p2L0"  # Your API key
RECIPIENT_EMAIL = "lawszahir@gmail.com"  # Police email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Language support
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

# Emergency contacts
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

# Crime hotspots data
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

# Historical crime database
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

def get_greeting_time():
    """Get appropriate greeting based on current time"""
    utc_now = datetime.datetime.now(pytz.UTC)
    skn_time = utc_now.astimezone(SKN_TIMEZONE)
    hour = skn_time.hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good evening"

# ENHANCED ANONYMOUS CRIME REPORTING SYSTEM
class EnhancedAnonymousCrimeReporter:
    def __init__(self):
        self.recipient_email = RECIPIENT_EMAIL
        self.reports_storage = []
        
    def generate_report_id(self, report_text):
        """Generate secure anonymous report ID"""
        content_hash = hashlib.sha256(f"{report_text}_{time.time()}_{random.randint(1000,9999)}".encode()).hexdigest()[:12]
        return f"SKN-{content_hash.upper()}"
    
    def validate_report_data(self, report_data):
        """Validate report data before submission"""
        required_fields = ['crime_type', 'location', 'description']
        
        for field in required_fields:
            if not report_data.get(field) or report_data[field].strip() == "" or report_data[field] == f"Select {field.replace('_', ' ')}...":
                return False, f"Missing required field: {field.replace('_', ' ').title()}"
        
        if len(report_data['description']) < 10:
            return False, "Description must be at least 10 characters long"
        
        return True, "Valid"
    
    def create_report_email(self, report_data, report_id):
        """Create professional police report email"""
        timestamp = f"{get_stkitts_date()} {get_stkitts_time()} AST"
        
        # Determine priority based on urgency and crime type
        high_priority_crimes = ['murder', 'assault', 'robbery', 'firearms', 'domestic violence']
        urgency_level = report_data.get('urgency', '')
        crime_type = report_data.get('crime_type', '').lower()
        
        priority = "HIGH" if (
            "🔴 High" in urgency_level or 
            any(crime in crime_type for crime in high_priority_crimes)
        ) else "MEDIUM" if "🟡 Medium" in urgency_level else "LOW"
        
        email_subject = f"🚨 ANONYMOUS CRIME REPORT [{priority}] - {report_id}"
        
        email_body = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    ROYAL ST. CHRISTOPHER & NEVIS POLICE FORCE             ║
║                         ANONYMOUS CRIME REPORT SYSTEM                     ║
║                            CONFIDENTIAL DOCUMENT                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

REPORT DETAILS:
═══════════════════════════════════════════════════════════════════════════
Report ID:           {report_id}
Submission Time:     {timestamp}
Submission Method:   SECURO AI Anonymous System
Priority Level:      {priority}
Security Class.:     CONFIDENTIAL

INCIDENT INFORMATION:
═══════════════════════════════════════════════════════════════════════════
Crime Type:          {report_data['crime_type']}
Location:            {report_data['location']}
Incident Date/Time:  {report_data['incident_time']}
Urgency Assessment:  {report_data.get('urgency', 'Not specified')}

INCIDENT DESCRIPTION:
═══════════════════════════════════════════════════════════════════════════
{report_data['description']}

ADDITIONAL INFORMATION:
═══════════════════════════════════════════════════════════════════════════
{report_data.get('additional_info', 'None provided')}

REPORTER INFORMATION:
═══════════════════════════════════════════════════════════════════════════
Source Type:         Anonymous Citizen Report
Contact Method:      Digital Submission (Anonymous)
Identity Protection: FULL ANONYMITY MAINTAINED
Reliability Code:    CITIZEN-ANON-01

PRELIMINARY ASSESSMENT:
═══════════════════════════════════════════════════════════════════════════
Geographic Area:     {'St. Kitts' if any(area in report_data['location'] for area in ['Basseterre', 'Cayon', 'Sandy Point', 'Newton Ground']) else 'Nevis' if any(area in report_data['location'] for area in ['Charlestown', 'Gingerland', 'Newcastle']) else 'TBD'}
Crime Category:      {report_data['crime_type']}
Response Required:   {'IMMEDIATE' if priority == 'HIGH' else 'STANDARD'}

RECOMMENDED ACTIONS:
═══════════════════════════════════════════════════════════════════════════
☐ Initial Response Assessment
☐ Field Investigation Assignment
☐ Intelligence Database Check
☐ Area Patrol Enhancement
☐ Follow-up Investigation Plan
☐ Community Liaison Contact

PRIVACY & SECURITY NOTICE:
═══════════════════════════════════════════════════════════════════════════
This report was submitted through the SECURO Anonymous Crime Reporting System.
No personally identifiable information has been collected, stored, or transmitted.
Reporter identity remains completely anonymous and protected under data privacy laws.

For follow-up: Quote Report ID {report_id}
System Contact: SECURO AI Crime Intelligence System
Generated: {timestamp}

═══════════════════════════════════════════════════════════════════════════
        """
        
        return email_subject, email_body
    
    def send_report_via_smtp(self, report_data):
        """Send report via SMTP (fallback method)"""
        try:
            report_id = self.generate_report_id(report_data['description'])
            subject, body = self.create_report_email(report_data, report_id)
            
            # For demo purposes, we'll store the report locally
            # In production, you would configure SMTP settings
            self.store_report_locally(report_data, report_id, subject, body)
            
            return True, report_id
            
        except Exception as e:
            return False, f"SMTP Error: {str(e)}"
    
    def store_report_locally(self, report_data, report_id, subject, body):
        """Store report locally as backup"""
        report_entry = {
            'id': report_id,
            'timestamp': f"{get_stkitts_date()} {get_stkitts_time()} AST",
            'subject': subject,
            'body': body,
            'data': report_data,
            'status': 'submitted'
        }
        
        if 'anonymous_reports' not in st.session_state:
            st.session_state.anonymous_reports = []
        
        st.session_state.anonymous_reports.append(report_entry)
        
        # Also store in class instance
        self.reports_storage.append(report_entry)
    
    def submit_anonymous_report(self, report_data):
        """Main method to submit anonymous crime report"""
        # Validate data
        is_valid, validation_msg = self.validate_report_data(report_data)
        if not is_valid:
            return False, validation_msg
        
        # Submit via SMTP (or store locally for demo)
        success, result = self.send_report_via_smtp(report_data)
        
        if success:
            return True, result  # result is report_id
        else:
            return False, result  # result is error message
    
    def get_report_statistics(self):
        """Get statistics about submitted reports"""
        if not hasattr(st.session_state, 'anonymous_reports'):
            return {
                'total_reports': 0,
                'reports_today': 0,
                'high_priority': 0,
                'most_common_crime': 'No data'
            }
        
        reports = st.session_state.anonymous_reports
        today = get_stkitts_date()
        
        reports_today = len([r for r in reports if today in r['timestamp']])
        high_priority = len([r for r in reports if 'HIGH' in r['subject']])
        
        # Get most common crime type
        crime_types = [r['data']['crime_type'] for r in reports]
        most_common = max(set(crime_types), key=crime_types.count) if crime_types else 'No data'
        
        return {
            'total_reports': len(reports),
            'reports_today': reports_today,
            'high_priority': high_priority,
            'most_common_crime': most_common
        }

# Initialize session state variables
def initialize_session_state():
    """Initialize all session state variables"""
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {}
    
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = None
    
    if 'chat_counter' not in st.session_state:
        st.session_state.chat_counter = 1
    
    if 'main_view' not in st.session_state:
        st.session_state.main_view = 'ai-assistant'
    
    if 'chat_active' not in st.session_state:
        st.session_state.chat_active = False
    
    if 'show_report_form' not in st.session_state:
        st.session_state.show_report_form = False
    
    if 'crime_reporter' not in st.session_state:
        st.session_state.crime_reporter = EnhancedAnonymousCrimeReporter()
    
    if 'anonymous_reports' not in st.session_state:
        st.session_state.anonymous_reports = []

# Chat management functions
def get_current_chat():
    """Get current chat session"""
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        return st.session_state.chat_sessions[st.session_state.current_chat_id]
    else:
        if st.session_state.get('chat_active', False):
            return create_new_chat_session()
        else:
            return {
                'id': 'temp',
                'name': 'New Chat',
                'messages': [],
                'created_at': get_stkitts_time(),
                'last_activity': get_stkitts_time()
            }

def create_new_chat_session():
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

# Query detection functions
def is_report_crime_request(user_input):
    """Detect if user wants to report a crime"""
    report_keywords = [
        'report crime', 'report a crime', 'anonymous report', 'file report', 
        'submit report', 'crime report', 'report incident', 'report something',
        'witnessed', 'saw something', 'criminal activity', 'suspicious activity',
        'want to report', 'need to report', 'reporting', 'tip'
    ]
    return any(keyword in user_input.lower() for keyword in report_keywords)

def is_casual_greeting(user_input):
    """Detect if user input is a casual greeting"""
    casual_words = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you', 'what\'s up', 'sup']
    return any(word in user_input.lower().strip() for word in casual_words) and len(user_input.strip()) < 25

def is_statistics_query(user_input):
    """Detect if user is asking about statistics"""
    stats_keywords = ['statistics', 'stats', 'data', 'crime rate', 'trends', 'numbers', 'figures', 'analysis', 'murder', 'robbery', 'larceny', 'detection rate', 'quarterly', 'annual', 'breakdown', 'comparison']
    return any(keyword in user_input.lower() for keyword in stats_keywords)

# AI Response Generation
def generate_enhanced_smart_response(user_input, conversation_history=None, language='en'):
    """Generate AI responses with statistical knowledge and conversation memory"""
    
    try:
        # Check if user wants to report a crime
        if is_report_crime_request(user_input):
            st.session_state.show_report_form = True
            return """🚨 **Anonymous Crime Reporting System Activated**

I'll help you submit an anonymous crime report to the Royal St. Christopher & Nevis Police Force. Your identity will remain completely protected.

The anonymous reporting form will appear below. Please provide as much detail as possible to help the police investigate effectively.

**Important Reporting Guidelines:**
• 🛡️ Complete anonymity guaranteed
• 📧 Reports sent directly to police
• 🆔 Unique tracking ID provided
• ⚡ For emergencies, call 911 immediately
• 🔒 No personal information collected

Would you like to proceed with the anonymous report?""", "show_form"
        
        # Include conversation context
        context = ""
        if conversation_history and len(conversation_history) > 1:
            recent_messages = conversation_history[-4:]
            context = "Recent conversation:\n"
            for msg in recent_messages:
                context += f"{msg['role']}: {msg['content'][:100]}...\n"
            context += "\n"
        
        # Check for casual greeting
        has_greeted = False
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'assistant' and any(greeting in msg['content'].lower() for greeting in ['good morning', 'good afternoon', 'good evening', 'hello', 'hi']):
                    has_greeted = True
                    break
        
        if is_casual_greeting(user_input) and not has_greeted:
            greeting_time = get_greeting_time()
            prompt = f"""
            You are SECURO, an AI assistant for St. Kitts & Nevis Police with anonymous crime reporting capabilities.
            
            User said: "{user_input}"
            Current time: {greeting_time}
            
            Respond with a brief, friendly greeting using the appropriate time-based greeting. 
            Mention you can help with crime statistics, general police assistance, AND anonymous crime reporting.
            Keep it to 2-3 sentences maximum.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        elif is_casual_greeting(user_input) and has_greeted:
            return "How can I assist you today? I can help with crime statistics, general inquiries, or if you need to report something anonymously.", None
        
        elif is_statistics_query(user_input):
            # Statistics response
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force.
            
            {context}User query: "{user_input}"
            
            **Available Crime Statistics:**
            {json.dumps(HISTORICAL_CRIME_DATABASE, indent=2)}
            
            Provide a data-driven response using specific numbers and statistics from the database above.
            Include relevant crime trends, detection rates, and comparisons when appropriate.
            Be professional and informative.
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
        
        else:
            # General response
            prompt = f"""
            You are SECURO, an AI assistant for the Royal St. Christopher & Nevis Police Force with anonymous crime reporting.
            
            {context}User query: "{user_input}"
            
            Provide helpful, professional assistance. You can:
            - Answer general police-related questions
            - Provide crime statistics and analysis
            - Help with anonymous crime reporting
            - Offer guidance on safety and security
            
            Keep responses informative and professional.
            
            Current time: {get_stkitts_time()} AST
            Current date: {get_stkitts_date()}
            """
            
            response = model.generate_content(prompt)
            return response.text.strip(), None
            
    except Exception as e:
        return f"🚨 AI system error: {str(e)}\n\nI'm still available to help with anonymous crime reporting and basic assistance.", None

# Anonymous Crime Report Form
def show_anonymous_report_form():
    """Display the enhanced anonymous crime report form"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                border: 2px solid #ef4444; border-radius: 16px; padding: 24px; margin: 20px 0;
                animation: report-glow 3s ease-in-out infinite;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color: #ef4444; margin: 0;">🚨 Anonymous Crime Report</h2>
            <p style="color: #94a3b8; margin-top: 8px;">Royal St. Christopher & Nevis Police Force</p>
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; 
                        border-radius: 8px; padding: 12px; margin: 16px 0;">
                <p style="color: #fca5a5; font-size: 14px; margin: 0;">
                    🛡️ Complete anonymity guaranteed - No personal information collected
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("enhanced_anonymous_report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            crime_type = st.selectbox(
                "🚨 Type of Crime/Incident:",
                options=[
                    "Select crime type...",
                    "Drug Activity/Trafficking",
                    "Theft/Larceny", 
                    "Armed Robbery",
                    "Assault/Violence",
                    "Break-in/Burglary",
                    "Vandalism/Property Damage",
                    "Firearms Offense",
                    "Sexual Crime",
                    "Domestic Violence",
                    "Fraud/Scam",
                    "Suspicious Activity",
                    "Gang Activity",
                    "Corruption",
                    "Other Criminal Activity"
                ]
            )
            
            incident_date = st.date_input("📅 Date of Incident:")
            incident_time = st.time_input("🕐 Approximate Time:")
        
        with col2:
            location = st.text_input(
                "📍 Location (be as specific as possible):",
                placeholder="e.g., Basseterre Central Market, Old Road near gas station",
                help="Specific locations help police respond more effectively"
            )
            
            urgency = st.selectbox(
                "⚡ Urgency Level:",
                options=[
                    "Select urgency...",
                    "🔴 High - Immediate threat/ongoing criminal activity",
                    "🟡 Medium - Requires investigation soon",
                    "🟢 Low - General information/past incident"
                ]
            )
        
        st.markdown("### 📝 Incident Details")
        
        description = st.text_area(
            "Detailed Description of What You Witnessed/Know:",
            placeholder="""Please provide detailed information about:
- What exactly happened?
- Who was involved? (descriptions, not names)
- What did you see or hear?
- Any vehicles involved? (make, model, color, license if visible)
- Weapons or items used?
- Direction suspects went?
- Any other relevant details...""",
            height=150,
            help="The more details you provide, the better police can investigate"
        )
        
        additional_info = st.text_area(
            "🔍 Additional Information (Optional):",
            placeholder="""Any other relevant information:
- Is this part of a pattern you've noticed?
- Any previous incidents in the area?
- Times when activity usually occurs?
- Community impact or concerns?
- Any evidence that might still be available?""",
            height=100
        )
        
        # Anonymous contact preference
        st.markdown("### 📞 Follow-up (Optional & Anonymous)")
        contact_method = st.selectbox(
            "If police need clarification, how should they reach out? (Optional):",
            options=[
                "No follow-up needed",
                "Create anonymous email for this case only",
                "Post response in community board (anonymous)",
                "I will call back with Report ID if needed"
            ]
        )
        
        # Safety and legal notices
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; 
                    border-radius: 8px; padding: 12px; margin: 16px 0;">
            <p style="color: #34d399; font-size: 14px; margin: 0;">
                ⚠️ <strong>Emergency Reminder:</strong> If this is an emergency requiring immediate response, 
                please call <strong>911</strong> instead of using this form.
            </p>
        </div>
        
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; 
                    border-radius: 8px; padding: 12px; margin: 16px 0;">
            <p style="color: #60a5fa; font-size: 12px; margin: 0;">
                <strong>Legal Notice:</strong> This system is for reporting legitimate criminal activity. 
                False reports may be investigated. All submissions are logged for security purposes 
                but remain anonymous.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Form submission buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚨 Submit Anonymous Report",
                type="primary",
                use_container_width=True,
                help="Click to securely submit your anonymous report"
            )
        
        if submitted:
            # Validate form
            validation_errors = []
            
            if crime_type == "Select crime type...":
                validation_errors.append("Crime Type")
            if not location.strip():
                validation_errors.append("Location")
            if not description.strip():
                validation_errors.append("Description")
            if urgency == "Select urgency...":
                validation_errors.append("Urgency Level")
            if len(description.strip()) < 10:
                validation_errors.append("Description (minimum 10 characters)")
            
            if validation_errors:
                st.error(f"❌ Please complete the following required fields: {', '.join(validation_errors)}")
                return False
            
            # Prepare report data
            report_data = {
                'crime_type': crime_type,
                'location': location.strip(),
                'incident_time': f"{incident_date} at {incident_time}",
                'urgency': urgency,
                'description': description.strip(),
                'additional_info': additional_info.strip() if additional_info.strip() else "None provided",
                'contact_preference': contact_method
            }
            
            # Submit report
            with st.spinner("🔄 Submitting anonymous report securely..."):
                reporter = st.session_state.crime_reporter
                success, result = reporter.submit_anonymous_report(report_data)
                
                if success:
                    # Show success message
                    st.success(f"""
                    ✅ **Anonymous Report Submitted Successfully!**
                    
                    **Report ID:** `{result}`
                    **Timestamp:** {get_stkitts_date()} {get_stkitts_time()} AST
                    **Status:** Forwarded to RSCNPF
                    
                    Your anonymous report has been securely transmitted to the Royal St. Christopher & Nevis Police Force. 
                    
                    **Important:**
                    • Keep this Report ID for your records: `{result}`
                    • Your identity remains completely anonymous
                    • Police will investigate based on information provided
                    • Thank you for helping keep our community safe! 🛡️
                    """)
                    
                    # Add success message to chat
                    add_message_to_chat("assistant", f"""
                    ✅ **Anonymous Crime Report Submitted Successfully**
                    
                    **Report ID:** `{result}`
                    **Timestamp:** {get_stkitts_date()} {get_stkitts_time()} AST
                    
                    Your report has been securely forwarded to the Royal St. Christopher & Nevis Police Force. 
                    Thank you for your civic responsibility in helping keep our community safe! 🛡️
                    
                    Is there anything else I can help you with today?
                    """)
                    
                    # Hide the form and refresh
                    st.session_state.show_report_form = False
                    time.sleep(3)
                    st.rerun()
                    
                else:
                    st.error(f"""
                    ❌ **Report Submission Failed**
                    
                    **Error:** {result}
                    
                    Please try again or contact police directly:
                    • Emergency: 911
                    • Police Headquarters: 465-2241
                    • In person: Royal St. Christopher & Nevis Police Force
                    """)
            
            return True
    
    # Form control buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("❌ Cancel Report", key="cancel_report"):
            st.session_state.show_report_form = False
            st.rerun()
    
    with col3:
        if st.button("📞 Emergency Help", key="emergency_help"):
            st.markdown("""
            **🚨 Emergency Contacts:**
            - **Police Emergency:** 911
            - **Police HQ:** 465-2241
            - **Medical Emergency:** 465-2551
            - **Fire Department:** 465-2515
            """)

# Crime Hotspot Map Creation
def create_crime_hotspot_map():
    """Create an interactive crime hotspot map"""
    center_lat = 17.25
    center_lon = -62.7
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Risk level colors
    risk_colors = {'High': '#ff4444', 'Medium': '#1e90ff', 'Low': '#0066cc'}
    
    for location, data in CRIME_HOTSPOTS.items():
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px;">
            <h4 style="color: {risk_colors[data['risk']]}; margin: 0; text-align: center;">
                🚨 {location}
            </h4>
            <hr style="margin: 8px 0;">
            <p><strong>📊 Total Crimes:</strong> {data['crimes']}</p>
            <p><strong>⚠️ Risk Level:</strong> 
               <span style="color: {risk_colors[data['risk']]}; font-weight: bold;">{data['risk']}</span>
            </p>
            <p><strong>🔍 Common Types:</strong></p>
            <ul style="margin: 4px 0; padding-left: 20px;">
                {''.join([f'<li>{crime_type}</li>' for crime_type in data['types']])}
            </ul>
        </div>
        """
        
        marker_size = max(10, min(30, data['crimes'] * 0.8))
        
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
    
    return m

# Initialize AI model
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.ai_enabled = True
    st.session_state.ai_status = "✅ AI Active with Crime Reporting"
except Exception as e:
    st.session_state.ai_enabled = False
    st.session_state.ai_status = f"❌ AI Error: {str(e)}"
    model = None

# Main Application
def main():
    """Main application function"""
    
    # Page configuration
    st.set_page_config(
        page_title="SECURO - Enhanced AI Crime Intelligence & Reporting",
        page_icon="🚔",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Enhanced CSS styling
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        /* Modern app styling */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            color: #ffffff;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Report form glow animation */
        @keyframes report-glow {
            0%, 100% { 
                border-color: #ef4444;
                box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
            }
            50% { 
                border-color: #3b82f6;
                box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            }
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #1e293b 0%, #334155 50%, #1e293b 100%) !important;
        }
        
        /* Chat message styling */
        .chat-message {
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 12px;
            max-width: 80%;
        }
        
        .user-message {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            margin-left: auto;
        }
        
        .assistant-message {
            background: linear-gradient(135deg, #374151, #4b5563);
            color: #f9fafb;
        }
        
        /* Form styling */
        .stSelectbox > div > div, .stTextInput > div > div, .stTextArea > div > div {
            background: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
            color: #ffffff !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #1d4ed8, #1e40af);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }
        
        /* Emergency button */
        .emergency-button {
            background: linear-gradient(135deg, #ef4444, #dc2626) !important;
            animation: emergency-pulse 2s infinite;
        }
        
        @keyframes emergency-pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); 
                padding: 16px; margin: -1rem -1rem 2rem -1rem; 
                border-bottom: 2px solid #3b82f6;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="background: linear-gradient(45deg, #3b82f6, #ef4444); 
                           padding: 12px; border-radius: 12px; font-size: 24px;">🚔</div>
                <div>
                    <h1 style="color: #3b82f6; margin: 0; font-size: 28px; font-weight: 700;">SECURO</h1>
                    <p style="color: #94a3b8; margin: 0; font-size: 14px;">Enhanced AI Crime Intelligence & Anonymous Reporting</p>
                </div>
            </div>
            <div style="color: #94a3b8; font-size: 14px; text-align: right;">
                <div>🕐 {get_stkitts_time()} AST</div>
                <div>📅 {get_stkitts_date()}</div>
                <div style="color: #10b981;">🟢 System Online</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-nav-header">🚔 SECURO Navigation</div>', unsafe_allow_html=True)
        
        # Quick report button
        if st.button("📝 Submit Anonymous Report", key="quick_report", help="Report crime anonymously"):
            st.session_state.show_report_form = True
            st.session_state.main_view = 'ai-assistant'
            st.rerun()
        
        # Navigation
        view_options = {
            'ai-assistant': '🤖 AI Assistant & Reporting',
            'crime-map': '🗺️ Crime Hotspot Map',
            'statistics': '📊 Crime Statistics',
            'emergency': '🚨 Emergency Contacts'
        }
        
        selected_view = st.selectbox(
            "Choose View:",
            options=list(view_options.keys()),
            format_func=lambda x: view_options[x],
            index=0
        )
        st.session_state.main_view = selected_view
        
        # Report statistics
        if st.session_state.anonymous_reports:
            stats = st.session_state.crime_reporter.get_report_statistics()
            st.markdown("### 📈 Report Statistics")
            st.metric("Total Reports", stats['total_reports'])
            st.metric("Reports Today", stats['reports_today'])
            st.metric("High Priority", stats['high_priority'])
        
        # Emergency contacts
        st.markdown("### 🚨 Emergency Contacts")
        st.markdown("**Police Emergency:** 911")
        st.markdown("**Police HQ:** 465-2241")
        st.markdown("**Medical:** 465-2551")
        
        # System status
        st.markdown("### 🔧 System Status")
        st.markdown(f"**AI Status:** {st.session_state.ai_status}")
        st.markdown("**Anonymous Reporting:** ✅ Active")
        st.markdown("**Data Security:** 🔒 Encrypted")
    
    # Main content area
    if st.session_state.main_view == 'ai-assistant':
        show_ai_assistant()
    elif st.session_state.main_view == 'crime-map':
        show_crime_map()
    elif st.session_state.main_view == 'statistics':
        show_crime_statistics()
    elif st.session_state.main_view == 'emergency':
        show_emergency_contacts()

def show_ai_assistant():
    """Show AI assistant interface with anonymous reporting"""
    st.markdown("## 🤖 AI Assistant & Anonymous Crime Reporting")
    
    # Show anonymous report form if requested
    if st.session_state.show_report_form:
        show_anonymous_report_form()
        st.markdown("---")
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        current_chat = get_current_chat()
        
        if current_chat['messages']:
            for message in current_chat['messages']:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    st.caption(f"🕐 {message['timestamp']}")
        else:
            # Welcome message
            with st.chat_message("assistant"):
                greeting = get_greeting_time()
                st.markdown(f"""
                {greeting}! 👋 I'm SECURO, your AI assistant for the Royal St. Christopher & Nevis Police Force.
                
                I can help you with:
                • 📊 **Crime statistics and analysis**
                • 🗺️ **Crime hotspot information**
                • 📝 **Anonymous crime reporting**
                • 🚨 **Emergency contact information**
                • ❓ **General police assistance**
                
                How can I assist you today?
                """)
    
    # Chat input
    if prompt := st.chat_input("Type your message or ask to report a crime anonymously..."):
        # Activate chat and create session if needed
        if not st.session_state.chat_active:
            st.session_state.chat_active = True
            create_new_chat_session()
        
        # Add user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕐 {get_stkitts_time()}")
        
        add_message_to_chat("user", prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, action = generate_enhanced_smart_response(
                    prompt, 
                    current_chat['messages']
                )
            
            st.markdown(response)
            st.caption(f"🕐 {get_stkitts_time()}")
        
        add_message_to_chat("assistant", response)
        
        # Handle special actions
        if action == "show_form":
            time.sleep(1)
            st.rerun()

def show_crime_map():
    """Display crime hotspot map"""
    st.markdown("## 🗺️ Crime Hotspot Map - St. Kitts & Nevis")
    
    st.markdown("""
    This interactive map shows crime hotspots across St. Kitts & Nevis based on recent incident data.
    Click on markers for detailed information about each area.
    """)
    
    # Create and display map
    crime_map = create_crime_hotspot_map()
    st_folium(crime_map, width=700, height=500)
    
    # Legend and statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Hotspot Summary")
        high_risk = len([area for area, data in CRIME_HOTSPOTS.items() if data['risk'] == 'High'])
        medium_risk = len([area for area, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Medium'])
        low_risk = len([area for area, data in CRIME_HOTSPOTS.items() if data['risk'] == 'Low'])
        
        st.metric("High Risk Areas", high_risk)
        st.metric("Medium Risk Areas", medium_risk)
        st.metric("Low Risk Areas", low_risk)
    
    with col2:
        st.markdown("### 🔍 Risk Levels")
        st.markdown("🔴 **High Risk:** 25+ crimes reported")
        st.markdown("🔵 **Medium Risk:** 15-24 crimes reported")
        st.markdown("🟢 **Low Risk:** Less than 15 crimes reported")

def show_crime_statistics():
    """Display crime statistics"""
    st.markdown("## 📊 Crime Statistics - St. Kitts & Nevis")
    
    # Display statistics from database
    data = HISTORICAL_CRIME_DATABASE
    
    # 2024 vs 2025 comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 2024 Annual Report")
        st.metric("Total Crimes", data['2024_ANNUAL']['total_crimes'])
        st.metric("Detection Rate", f"{data['2024_ANNUAL']['detection_rate']:.1f}%")
        st.metric("Murders", data['2024_ANNUAL']['federation']['murder_manslaughter']['total'])
    
    with col2:
        st.markdown("### 2025 Q2 Report")
        st.metric("Total Crimes", data['2025_Q2']['total_crimes'])
        st.metric("Detection Rate", f"{data['2025_Q2']['detection_rate']:.1f}%")
        st.metric("Murders", data['2025_Q2']['federation']['murder_manslaughter']['total'])
    
    # Detailed breakdown
    st.markdown("### Crime Type Breakdown (2024)")
    
    crime_data_2024 = data['2024_ANNUAL']['federation']
    crime_names = []
    crime_counts = []
    detection_rates = []
    
    for crime_type, stats in crime_data_2024.items():
        crime_names.append(crime_type.replace('_', ' ').title())
        crime_counts.append(stats['total'])
        detection_rates.append(stats['rate'])
    
    # Create bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=crime_names,
        y=crime_counts,
        marker_color='#3b82f6',
        text=crime_counts,
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Crime Types by Frequency (2024)",
        xaxis_title="Crime Type",
        yaxis_title="Number of Cases",
        template="plotly_dark",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_emergency_contacts():
    """Display emergency contacts"""
    st.markdown("## 🚨 Emergency Contacts - St. Kitts & Nevis")
    
    for contact_name, info in EMERGENCY_CONTACTS.items():
        with st.expander(f"{info['icon']} {contact_name} - {info['number']}"):
            st.markdown(f"**Phone:** {info['number']}")
            st.markdown(f"**Description:** {info['description']}")
    
    # Emergency tips
    st.markdown("### ⚠️ Emergency Guidelines")
    st.markdown("""
    - **Call 911** for immediate life-threatening emergencies
    - **Call Police HQ (465-2241)** for non-emergency police matters
    - **Use Anonymous Reporting** for tips and non-urgent crime information
    - **Stay calm** and provide clear location information
    - **Don't approach** dangerous situations - let professionals handle it
    """)

if __name__ == "__main__":
    main()

