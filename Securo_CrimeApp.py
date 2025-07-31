<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SECURO - St. Kitts & Nevis Crime AI Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #2e1a1a 50%, #3e1616 100%);
            font-family: 'JetBrains Mono', monospace;
            overflow-x: hidden;
            min-height: 100vh;
            position: relative;
        }

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
            border: 1px solid rgba(255, 68, 68, 0.3);
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
            background: linear-gradient(45deg, transparent, rgba(255, 68, 68, 0.1), transparent);
            animation: scan 3s infinite;
        }

        @keyframes scan {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }

        .header h1 {
            font-size: 3rem;
            color: #ff4444;
            text-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
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
            color: #ff4444;
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
            background: rgba(40, 20, 20, 0.8);
            border-radius: 15px;
            border: 1px solid rgba(255, 68, 68, 0.2);
            padding: 20px;
            backdrop-filter: blur(10px);
            overflow-y: auto;
        }

        /* Emergency Contacts */
        .emergency-contacts {
            margin-bottom: 25px;
        }

        .emergency-contacts h3 {
            color: #ff4444;
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
            background: rgba(255, 68, 68, 0.1);
            transform: translateX(5px);
        }

        .contact-police { border-left-color: #ff4444; }
        .contact-hospital { border-left-color: #ff6b6b; }
        .contact-fire { border-left-color: #ff8c00; }
        .contact-legal { border-left-color: #ff3333; }
        .contact-forensic { border-left-color: #cc3333; }

        .contact-info {
            flex: 1;
        }

        .contact-name {
            color: #e0e0e0;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .contact-number {
            color: #ff4444;
            font-size: 0.8rem;
            margin-top: 3px;
        }

        .contact-icon {
            width: 20px;
            height: 20px;
            opacity: 0.7;
            fill: #ff4444;
        }

        /* Crime Map */
        .crime-map-section {
            margin-bottom: 20px;
        }

        .crime-map-section h3 {
            color: #ff4444;
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
            border: 1px solid rgba(255, 68, 68, 0.2);
            position: relative;
            height: 200px;
            overflow: hidden;
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
        .low-crime { background: #ff9999; }

        /* Main chat area */
        .chat-main {
            background: rgba(40, 20, 20, 0.8);
            border-radius: 15px;
            border: 1px solid rgba(255, 68, 68, 0.2);
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(10px);
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: #ff4444 rgba(0, 0, 0, 0.3);
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
            background: #ff4444;
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
            background: linear-gradient(135deg, #ff4444, #cc3333);
            color: #fff;
            border-bottom-right-radius: 5px;
        }

        .message-bot .message-content {
            background: rgba(0, 0, 0, 0.6);
            color: #e0e0e0;
            border: 1px solid rgba(255, 68, 68, 0.3);
            border-bottom-left-radius: 5px;
        }

        .message-time {
            font-size: 0.7rem;
            color: #888;
            margin-top: 5px;
        }

        /* Input area */
        .chat-input {
            padding: 20px;
            border-top: 1px solid rgba(255, 68, 68, 0.2);
            background: rgba(0, 0, 0, 0.3);
            border-radius: 0 0 15px 15px;
        }

        .input-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        #messageInput {
            flex: 1;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 68, 68, 0.3);
            border-radius: 25px;
            padding: 12px 20px;
            color: #e0e0e0;
            font-family: 'JetBrains Mono', monospace;
            outline: none;
        }

        #messageInput:focus {
            border-color: #ff4444;
            box-shadow: 0 0 20px rgba(255, 68, 68, 0.2);
        }

        #sendButton {
            background: linear-gradient(135deg, #ff4444, #cc3333);
            border: none;
            border-radius: 25px;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 500;
            padding: 12px 24px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        #sendButton:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255, 68, 68, 0.4);
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
            border: 1px solid rgba(255, 68, 68, 0.2);
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
</head>
<body>
    <!-- Particles background -->
    <div class="particles" id="particles"></div>

    <div class="main-container">
        <!-- Header -->
        <div class="header">
            <h1>SECURO</h1>
            <div class="tagline">AI Crime Investigation Assistant</div>
            <div class="location">🇰🇳 St. Kitts & Nevis Law Enforcement</div>
        </div>

        <!-- Chat interface -->
        <div class="chat-container">
            <!-- Sidebar -->
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
                        <svg class="contact-icon" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                    </div>
                    
                    <div class="contact-item contact-police">
                        <div class="contact-info">
                            <div class="contact-name">Police Department</div>
                            <div class="contact-number">465-2241</div>
                        </div>
                        <svg class="contact-icon" viewBox="0 0 24 24">
                            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
                        </svg>
                    </div>
                    
                    <div class="contact-item contact-hospital">
                        <div class="contact-info">
                            <div class="contact-name">Hospital</div>
                            <div class="contact-number">465-2551</div>
                        </div>
                        <svg class="contact-icon" viewBox="0 0 24 24">
                            <path d="M19 8l-4 4h3c0 3.31-2.69 6-6 6-1.01 0-1.97-.25-2.8-.7l-1.46 1.46C8.97 19.54 10.43 20 12 20c4.42 0 8-3.58 8-8h3l-4-4zM6 12c0-3.31 2.69-6 6-6 1.01 0 1.97.25 2.8.7l1.46-1.46C15.03 4.46 13.57 4 12 4c-4.42 0-8 3.58-8 8H1l4 4 4-4H6z"/>
                        </svg>
                    </div>
                    
                    <div class="contact-item contact-fire">
                        <div class="contact-info">
                            <div class="contact-name">Fire Department</div>
                            <div class="contact-number">465-2515 / 465-7167</div>
                        </div>
                        <svg class="contact-icon" viewBox="0 0 24 24">
                            <path d="M12.71 2.96c-2.75 2.12-4.71 6.79-4.71 11.04 0 4.42 3.58 8 8 8s8-3.58 8-8c0-4.25-1.96-8.92-4.71-11.04-.44-.33-1.04-.33-1.48 0-.63.48-1.51 1.28-2.37 2.23-.86-.95-1.74-1.75-2.37-2.23-.44-.33-1.04-.33-1.48 0z"/>
                        </svg>
                    </div>
                    
                    <div class="contact-item contact-legal">
                        <div class="contact-info">
                            <div class="contact-name">Coast Guard</div>
                            <div class="contact-number">465-8384 / 466-9280</div>
                        </div>
                        <svg class="contact-icon" viewBox="0 0 24 24">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                        </svg>
                    </div>
                    
                    <div class="contact-item contact-forensic">
                        <div class="contact-info">
                            <div class="contact-name">Red Cross</div>
                            <div class="contact-number">465-2584</div>
                        </div>
                        <svg class="contact-icon" viewBox="0 0 24 24">
                            <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H9v-2h2v-2h2v2h2v2h-2v2h-2v-2z"/>
                        </svg>
                    </div>
                    
                    <div class="contact-item contact-legal">
                        <div class="contact-info">
                            <div class="contact-name">NEMA (Emergency Mgmt)</div>
                            <div class="contact-number">466-5100</div>
                        </div>
                        <svg class="contact-icon" viewBox="0 0 24 24">
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

            <!-- Main chat area -->
            <div class="chat-main">
                <div class="chat-messages" id="chatMessages">
                    <div class="message message-bot">
                        <div class="message-content">
                            Welcome to SECURO, your AI crime investigation assistant for St. Kitts & Nevis law enforcement.
                            <br><br>
                            I'm here to assist criminologists, police officers, forensic experts, and autopsy professionals with case analysis, evidence correlation, and investigative insights.
                            <br><br>
                            How can I assist with your investigation today?
                        </div>
                        <div class="message-time" id="currentTime"></div>
                    </div>
                </div>

                <div class="chat-input">
                    <div class="input-container">
                        <input type="text" id="messageInput" placeholder="Describe evidence, case details, or ask forensic questions..." maxlength="500">
                        <button id="sendButton">Send</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Status bar -->
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
    </div>

    <script>
        // Crime Q&A Database from CSV
        const crimeDatabase = [
            { category: "Victims", question: "What services are available for crime victims?", answer: "Counseling, financial assistance, and victim advocacy groups." },
            { category: "Journalists", question: "What are shield laws?", answer: "Laws protecting journalists from revealing confidential sources." },
            { category: "Witnesses", question: "What is a subpoena?", answer: "A legal document ordering someone to testify in court." },
            { category: "Lawyers", question: "What is double jeopardy?", answer: "A procedural defense that prevents an accused person from being tried again on the same charges." },
            { category: "General Public", question: "How do I check if someone has a criminal record?", answer: "Contact the local police department or use background check services." },
            { category: "Lawyers", question: "What is plea bargaining?", answer: "An agreement where the defendant pleads guilty for a reduced sentence." },
            { category: "Cybercrime Specialists", question: "What is phishing?", answer: "A cyber attack that tricks people into giving sensitive information." },
            { category: "General Public", question: "How do I get a restraining order?", answer: "File a petition with the court explaining why you need protection." },
            { category: "Cold Case Units", question: "What is a cold case?", answer: "A criminal investigation that remains unsolved after a long period." },
            { category: "Cold Case Units", question: "How are cold cases reopened?", answer: "Through new evidence, DNA technology, or witness testimony." },
            { category: "Criminologists", question: "What is the broken windows theory?", answer: "A theory that visible signs of disorder lead to more crime." },
            { category: "Criminologists", question: "What is white collar crime?", answer: "Financially motivated, nonviolent crime committed by businesses and government professionals." },
            { category: "Forensics", question: "How are fingerprints lifted?", answer: "Using powders, chemicals, or alternate light sources to make them visible." },
            { category: "Criminal Psychologists", question: "What is antisocial personality disorder?", answer: "A mental condition linked to disregard for others' rights, often found in criminals." },
            { category: "Victims", question: "What is victim impact statement?", answer: "A written or oral statement given at sentencing describing the crime's impact." },
            { category: "Journalists", question: "How do journalists cover crime ethically?", answer: "By verifying facts, respecting privacy, and avoiding sensationalism." },
            { category: "Investigators", question: "What is criminal profiling?", answer: "Inferring characteristics of an offender based on crime scene evidence." },
            { category: "Criminal Psychologists", question: "What is criminal insanity?", answer: "A legal term meaning the defendant was unable to understand their actions." },
            { category: "Cybercrime Specialists", question: "What is ransomware?", answer: "Malicious software that blocks access to data until a ransom is paid." },
            { category: "Investigators", question: "What is forensic entomology?", answer: "The study of insects to estimate time of death." },
            { category: "Police", question: "What is community policing?", answer: "A strategy that focuses on building ties and working closely with communities." },
            { category: "Police", question: "What is an arrest warrant?", answer: "A document issued by a judge authorizing the arrest of a person." },
            { category: "Forensics", question: "How is blood spatter analyzed?", answer: "By examining patterns to reconstruct a crime scene." },
            { category: "Witnesses", question: "Can I refuse to testify?", answer: "In some cases, but you may be held in contempt of court." },
            { category: "Police", question: "What does 'beyond reasonable doubt' mean?", answer: "The standard of evidence required to convict in a criminal trial." }
        ];

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

        // Search function for crime database
        function searchCrimeDatabase(query) {
            const searchTerm = query.toLowerCase();
            
            // Direct question match
            let match = crimeDatabase.find(item => 
                item.question.toLowerCase().includes(searchTerm) ||
                searchTerm.includes(item.question.toLowerCase().substring(0, 20))
            );
            
            if (match) {
                return match.answer;
            }
            
            // Keyword-based search
            const keywords = {
                'victim': ['What services are available for crime victims?', 'What is victim impact statement?'],
                'witness': ['What is a subpoena?', 'Can I refuse to testify?'],
                'police': ['What is community policing?', 'What is an arrest warrant?', "What does 'beyond reasonable doubt' mean?"],
                'forensic': ['How are fingerprints lifted?', 'How is blood spatter analyzed?', 'What is forensic entomology?'],
                'cyber': ['What is phishing?', 'What is ransomware?'],
                'legal': ['What is double jeopardy?', 'What is plea bargaining?'],
                'restraining': ['How do I get a restraining order?'],
                'cold case': ['What is a cold case?', 'How are cold cases reopened?'],
                'criminal record': ['How do I check if someone has a criminal record?'],
                'profiling': ['What is criminal profiling?'],
                'insanity': ['What is criminal insanity?'],
                'shield': ['What are shield laws?'],
                'journalism': ['How do journalists cover crime ethically?'],
                'white collar': ['What is white collar crime?'],
                'broken windows': ['What is the broken windows theory?'],
                'antisocial': ['What is antisocial personality disorder?']
            };
            
            for (const [keyword, questions] of Object.entries(keywords)) {
                if (searchTerm.includes(keyword)) {
                    const question = questions[0];
                    const answer = crimeDatabase.find(item => item.question === question);
                    if (answer) return answer.answer;
                }
            }
            
            // Default responses for St. Kitts & Nevis specific queries
            const sknResponses = [
                "Based on St. Kitts & Nevis criminal patterns, I recommend cross-referencing with the Royal St. Christopher and Nevis Police Force database.",
                "Crime analysis for the Caribbean region suggests this pattern. Coordinate with the Director of Public Prosecutions office.",
                "This case shows similarities to recent incidents in Basseterre. Consider interviewing witnesses near Independence Square.",
                "Forensic protocols for St. Kitts & Nevis require documentation per Caribbean Association of Police Chiefs standards.",
                "Evidence suggests connection to maritime activities between St. Kitts and Nevis. Contact Coast Guard unit 465-8384.",
                "Pattern matches recent cases in tourist areas. Recommend liaison with Ministry of National Security.",
                "This investigation may benefit from coordination with the Nevis Island Administration police division."
            ];
            
            return sknResponses[Math.floor(Math.random() * sknResponses.length)];
        }

        // Chat functionality
        function getCurrentTime() {
            return new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
        }

        function addMessage(content, isUser = false) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'message-user' : 'message-bot'}`;
            
            messageDiv.innerHTML = `
                <div class="message-content">${content}</div>
                <div class="message-time">${getCurrentTime()}</div>
            `;
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function handleSendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (message) {
                // Add user message
                addMessage(message, true);
                
                // Clear input
                messageInput.value = '';
                
                // Simulate AI thinking delay
                setTimeout(() => {
                    const response = searchCrimeDatabase(message);
                    addMessage(response);
                }, 1000);
            }
        }

        // Event listeners
        document.getElementById('sendButton').addEventListener('click', handleSendMessage);
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSendMessage();
            }
        });

        // Initialize
        document.getElementById('currentTime').textContent = getCurrentTime();
        createParticles();

        // Update time every second
        setInterval(() => {
            document.getElementById('currentTime').textContent = getCurrentTime();
        }, 1000);

        // Contact item click handlers
        document.querySelectorAll('.contact-item').forEach(item => {
            item.addEventListener('click', function() {
                const name = this.querySelector('.contact-name').textContent;
                const number = this.querySelector('.contact-number').textContent;
                
                // Create a flash effect
                this.style.background = 'rgba(255, 68, 68, 0.3)';
                setTimeout(() => {
                    this.style.background = 'rgba(0, 0, 0, 0.5)';
                }, 200);
                
                // Add message to chat about the contact
                addMessage(`Emergency contact information accessed: ${name} - ${number}. Contact has been logged for case documentation.`);
            });
        });

        // Hotspot click handlers
        document.querySelectorAll('.hotspot').forEach(hotspot => {
            hotspot.addEventListener('click', function() {
                const title = this.getAttribute('title');
                addMessage(`Crime hotspot analysis: ${title}. Recommend increased patrol presence and witness canvassing in this area.`);
            });
        });
    </script>
</body>
</html>
