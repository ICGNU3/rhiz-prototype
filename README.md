# OuRhizome - Contact Intelligence CRM

A goal-first intelligent contact management platform for early-stage founders with exclusive "Root Membership" model featuring lifetime access for "One Hundred Root Members".

## 🚀 Features

### Core Intelligence
- **AI-Powered Goal Matching**: Semantic analysis to connect your objectives with relevant contacts
- **Smart Contact Intelligence**: Natural language processing for relationship insights
- **Personalized Outreach**: AI-generated messages tailored to your goals and contact context
- **Network Analytics**: Comprehensive relationship mapping and success metrics

### CRM Capabilities
- **Pipeline Management**: Kanban-style relationship stages (Cold → Warm → Active → Contributor)
- **Interaction Tracking**: Complete history of all contact engagements
- **Contact Import**: LinkedIn CSV and bulk contact uploads
- **Email Integration**: Direct sending with SMTP auto-detection

### Advanced Features
- **Conference Mode**: Smart contact capture for networking events
- **Collective Actions**: Cohort-based collaboration system
- **Network Visualization**: Interactive relationship mapping
- **Gamification Engine**: Background XP system with contextual rewards
- **Shared AI Assistant**: Ambient intelligence for missed connections and micro-actions

## 🛠️ Technology Stack

- **Backend**: Python Flask with SQLite database
- **AI Integration**: OpenAI GPT-4o for embeddings and content generation
- **Email Service**: Resend API for transactional emails
- **Frontend**: Bootstrap 5.3 with glassmorphism design
- **Deployment**: Gunicorn WSGI server

## 📦 Installation

### Prerequisites
- Python 3.11+
- OpenAI API key
- Resend API key (for email functionality)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ourhizome-crm.git
cd ourhizome-crm
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=your_sender_email@domain.com
DATABASE_URL=sqlite:///db.sqlite3
SESSION_SECRET=your_secret_key
```

4. **Initialize the database**
```bash
python app.py
```

5. **Run the application**
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

Visit `http://localhost:5000` to access the application.

## 🏗️ Project Structure

```
ourhizome-crm/
├── main.py                    # Application entry point
├── app.py                     # Flask app configuration
├── routes.py                  # Main application routes
├── models.py                  # Database models
├── templates/                 # HTML templates
│   ├── landing.html          # Landing page
│   ├── application_success.html
│   └── monique/              # CRM templates
├── static/                    # CSS, JS, images
├── utils/                     # Utility modules
│   └── email.py              # Email service
├── ai_contact_matcher.py      # AI matching engine
├── analytics.py               # Network analytics
├── gamification.py            # XP and achievement system
└── schema.sql                 # Database schema
```

## 🎯 Key Features Explained

### Goal-First Approach
OuRhizome starts with your objectives and finds the right people to help achieve them. Create goals and let AI identify relevant contacts from your network.

### Root Membership Model
Exclusive access for "One Hundred Root Members" with lifetime platform access, emphasizing quality connections over scale.

### Ambient Intelligence
The AI assistant "Monique" provides:
- Missed connection discovery
- Daily micro-actions based on your goals
- Weekly collective insights from community patterns

### Network Intelligence
- Relationship health scoring
- Introduction opportunity identification
- Network gap analysis with expansion recommendations

## 🔐 Security & Privacy

- Magic link authentication (passwordless)
- Environment variable configuration for sensitive data
- Session-based user management
- Input sanitization and validation

## 📈 Analytics & Insights

- Outreach success rates and response tracking
- Contact effectiveness analysis by relationship type
- Goal performance metrics
- Network growth trends and pipeline analytics

## 🤝 Contributing

This project is designed for the exclusive Root Member community. For access requests or collaboration:

1. Apply through the Root Membership application
2. Join the founding community of ambitious entrepreneurs
3. Contribute to the collective intelligence platform

## 📧 Contact

Built for founders, by founders. Connect with us through the Root Membership application process.

## 📄 License

Private repository for Root Members. All rights reserved.

---

*OuRhizome - Connecting founders with the right people*