# 🎓 CampusOS - Production-Ready Campus Management System

A secure, AI-powered full-stack application designed for college/university campus management with role-based access control, intelligent query resolution, and seamless student-faculty-admin workflows.

## 🌟 Features

### 🔐 Security
- **OAuth2 + JWT Authentication** - Secure login and session management
- **Role-Based Access Control (RBAC)** - STUDENT, FACULTY, ADMIN, SUPER_ADMIN
- **End-to-End Encryption** - bcrypt password hashing, SSL database connections
- **HTTPS & CSRF Protection** - Production-grade security
- **Audit Logs** - Track all admin/faculty actions
- **Input Validation** - Prevent injection attacks

### 🎓 Student Features
- Personalized dashboard with notices, deadlines, attendance, fees
- AI-powered Q&A with source citations (RAG pipeline)
- Admission guidance with step-by-step onboarding
- Automated credential generation
- Deadline reminders (email, push notifications)
- Problem resolver (lost ID, hall ticket, grievance reporting)

### 👨‍🏫 Faculty Features
- Upload exam timetables, notices, assignments
- Manage student queries
- Track student engagement

### 🛠️ Admin Features
- Document management (PDF, DOCX upload)
- Student registration and fee management
- Analytics dashboard (most asked questions, deadline compliance)
- Audit log viewer
- System-wide settings

### 🧠 AI & Intelligence
- Local LLM integration (Ollama - LLaMA 3, Mistral, Gemma)
- RAG (Retrieval-Augmented Generation) pipeline
- Document embeddings with pgvector
- Source-grounded answers with citations
- Auto-extract deadlines from notices

### 🗄️ Infrastructure
- PostgreSQL with pgvector for vector search
- Docker containerization
- GitHub Actions CI/CD pipeline
- Environment-based configuration
- Logging and monitoring ready

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose
- Ollama (for local LLM)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### Using Docker Compose
```bash
docker-compose up -d
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PgAdmin**: http://localhost:5050

## 📁 Project Structure

```
CampusOS/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── middleware/
│   │   ├── security/
│   │   └── database.py
│   ├── migrations/            # Alembic migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/                   # Next.js application
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── styles/
│   ├── .env.local.example
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/             # CI/CD pipelines
├── docs/                       # Documentation
└── README.md
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, React, Tailwind CSS, TypeScript |
| Backend | FastAPI, Python, Pydantic |
| Database | PostgreSQL, pgvector, SQLAlchemy |
| AI/ML | Ollama, LlamaIndex, LangChain |
| Authentication | OAuth2, JWT |
| DevOps | Docker, GitHub Actions, Render/Railway |
| Notifications | Email, Push Notifications |

## 📚 Documentation

- [Backend API Documentation](./docs/backend-setup.md)
- [Frontend Setup Guide](./docs/frontend-setup.md)
- [Database Schema](./docs/database-schema.md)
- [Security Guidelines](./docs/security.md)
- [Deployment Guide](./docs/deployment.md)
- [API Endpoints](./docs/api-endpoints.md)

## 🔒 Security Features

✅ OAuth2 + JWT authentication
✅ Role-based access control
✅ Password hashing with bcrypt
✅ SQL injection prevention
✅ CSRF protection
✅ Rate limiting
✅ Audit logging
✅ SSL/TLS encryption
✅ Input validation & sanitization
✅ Secure headers

## 📊 Database Schema

Key tables:
- `users` - Authentication & user profiles
- `admissions` - Student admission records
- `documents` - Uploaded PDFs, circulars
- `embeddings` - Vector embeddings for RAG
- `notices` - Campus notices with deadlines
- `deadlines` - Personalized deadline tracking
- `problem_reports` - Lost ID, hall ticket, grievances
- `audit_logs` - Action tracking

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 🚢 Deployment

### Using Docker
```bash
docker build -t campusos-backend ./backend
docker build -t campusos-frontend ./frontend
docker-compose up -d
```

### Cloud Deployment
Guides available for:
- Render
- Railway
- AWS
- Google Cloud
- DigitalOcean

See [Deployment Guide](./docs/deployment.md)

## 📞 Support & Contribution

- Report bugs via GitHub Issues
- Contribute via Pull Requests
- Join our community discussions

## 📄 License

MIT License - see LICENSE file

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Analytics dashboard
- [ ] Lecture notes AI summarization
- [ ] Multi-tenant SaaS model
- [ ] Advanced calendar integration
- [ ] SMS/WhatsApp notifications
- [ ] Multi-language support

---

**Built with ❤️ for campus excellence**
