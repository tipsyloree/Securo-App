# SECUR0 - AI Crime Investigation Assistant

🛡️ **Enhanced AI Assistant & Crime Intelligence System for the Royal St. Christopher & Nevis Police Force**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Overview

SECUR0 is a comprehensive AI-powered crime analysis and investigation assistant designed specifically for the Royal St. Christopher & Nevis Police Force. It combines modern UI design with powerful AI capabilities, statistical analysis, and real-time crime data visualization.

### ✨ Key Features

- **🧠 Enhanced AI Assistant** - Powered by Google's Gemini AI with conversation memory and context awareness
- **📊 Statistical Integration** - Real crime data from 2022-2025 with MacroTrends international comparisons
- **🗺️ Interactive Crime Maps** - Visual hotspot analysis across St. Kitts & Nevis
- **💬 Multi-Chat Support** - Manage multiple conversation sessions with full history
- **📈 Data Visualization** - Interactive charts and analytics dashboards
- **🚨 Emergency Contacts** - Quick access to all emergency services
- **🌍 International Context** - Global crime rate comparisons and trends
- **🎨 Modern UI Design** - Professional dark theme with green accent colors

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Google AI API key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/secur0-app.git
   cd secur0-app
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   
   Create a `.streamlit/secrets.toml` file:
   ```toml
   GOOGLE_API_KEY = "your-api-key-here"
   ```
   
   Or set it directly in `app.py` (line ~97):
   ```python
   GOOGLE_API_KEY = "your-api-key-here"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 📱 Features in Detail

### AI Assistant
- Conversation memory across sessions
- Context-aware responses
- Statistical knowledge integration
- Chart generation on demand

### Crime Analytics
- Real-time crime statistics
- Detection rate analysis
- Geographical breakdowns
- Trend identification

### Interactive Maps
- 13 crime hotspot locations
- Risk level visualization
- Crime type breakdown
- Satellite view option

### Emergency System
- One-click access to all emergency contacts
- Police, Medical, Fire, Coast Guard, and more
- Quick reference guide

## 🛠️ Configuration

### Environment Variables
You can set these in `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your-google-ai-api-key"
```

### Customization
- **Colors**: Edit the CSS in `app.py` (main color: `#39ff14`)
- **Data**: Update crime statistics in the `HISTORICAL_CRIME_DATABASE` dictionary
- **Hotspots**: Modify locations in the `CRIME_HOTSPOTS` dictionary

## 🌐 Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add your API key in the Streamlit Cloud secrets:
   - Go to App Settings → Secrets
   - Add: `GOOGLE_API_KEY = "your-api-key"`
5. Deploy!

### Deploy to Heroku

1. Create a `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Create a `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]\nheadless = true\nport = $PORT\nenableCORS = false\n" > ~/.streamlit/config.toml
   ```

3. Deploy to Heroku:
   ```bash
   heroku create your-app-name
   heroku config:set GOOGLE_API_KEY=your-api-key
   git push heroku main
   ```

## 📊 Data Sources

- **Crime Statistics**: Royal St. Christopher & Nevis Police Force (RSCNPF)
- **International Data**: MacroTrends global crime database
- **Time Period**: 2022-2025 with quarterly updates
- **Coverage**: Complete federation-wide data

## 🔒 Security

- API keys should never be committed to version control
- Use environment variables or secrets management
- The app does not store personal data
- All chat sessions are stored locally in browser session

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- Royal St. Christopher & Nevis Police Force for data provision
- Google AI for the Gemini API
- Streamlit for the amazing framework
- The open-source community

## 📞 Support

For support, please contact:
- Local Intelligence Office: 869-465-2241 Ext. 4238/4239
- Email: lio@police.kn

## 🚨 Emergency Contacts

- **Emergency**: 911
- **Police**: 465-2241
- **Medical**: 465-2551
- **Fire**: 465-2515
- **Coast Guard**: 465-8384

---

**Note**: This is a demonstration system. For official police matters, please contact the appropriate authorities directly.
