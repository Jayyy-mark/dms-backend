# MOGE Enterprise Management & AI Document Intelligence System

[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20.svg?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.x-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash/Pro-4285F4.svg?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/Vector_Store-ChromaDB-FF6F00.svg?style=flat)](https://www.trychroma.com/)

> **Comprehensive Enterprise Management, Human Resources, Facility Tracking, and AI-Powered Document Intelligence Platform for Myanmar Oil and Gas Enterprise (MOGE).**

---

## 📖 Complete Documentation
For exhaustive technical details, database schema, AI/RAG pipeline design, API endpoint specifications, and architecture breakdowns, see **[DOCUMENTATION.md](file:///d:/Fifth%20year/MOGE/DOCUMENTATION.md)**.

---

## 🚀 Key Features

- **Document Management System (DMS):**
  - Multi-tier document lifecycle: Active ➔ Archive (`is_archived`) ➔ Recycle Bin (`is_recycled`) ➔ Permanent Purge.
  - Expiration date tracking and automated auditing.
  - Recursive tree categorization and administrative document types.
- **AI & Intelligent Document Search (RAG):**
  - **RAG Chatbot:** Conversational assistant powered by Google Gemini (2.5 Flash / 2.5 Pro) and ChromaDB vector embeddings. Provides answers with source document citations in Burmese (Myanmar Unicode) and English.
  - **Deep Search Engine:** Line-by-line Unicode-normalized PDF text search with exact line and page number detection.
- **Human Resources (HR) & Personnel:**
  - Staff profiles, ranks, roles, staff employment types, and departmental organization.
  - Tracking for promotions, transfers, training, overseas missions, awards, and disciplinary records.
- **Facilities & Geospatial Asset Registry:**
  - Building infrastructure and room allocations.
  - Field sites and GIS locations with GPS coordinates and photographic documentation.
- **Enterprise Security & Compliance:**
  - JWT authentication (Access & Refresh tokens) with Cookie/Bearer support.
  - Role-Based Access Control (Super Admin, Admin, Moderator, User, Guest).
  - Department-scoped data access control to prevent cross-department data leakage.
  - Comprehensive audit logging across all entities.
- **Bilingual Interface:** Instant toggling between English and Myanmar Unicode.

---

## 🏗️ Quick Start Guide

### Prerequisites
- Python 3.12+
- Node.js 18+ & npm
- MySQL 8.0+

### 1. Backend Setup
```bash
# Navigate to backend directory
cd project/backend

# Create & activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env)
# Create project/backend/.env with MySQL credentials & GEMINI_API_KEY

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create initial admin account
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### 2. Frontend Setup
```bash
# Open a new terminal and navigate to frontend directory
cd project/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Visit `http://localhost:5173` to log in and use the system.

---

## 🐳 Docker Deployment

To launch all services (MySQL, Django Backend, and React Frontend) using Docker Compose:
```bash
docker-compose up --build -d
```
- **Web Dashboard:** `http://localhost:3000`
- **REST API:** `http://localhost:8000`
- **MySQL Database:** `localhost:3306`

---

## 📁 Repository Overview
```
d:/Fifth year/MOGE/
├── DOCUMENTATION.md       # Master Technical Documentation (Complete Specifications)
├── README.md              # Project quick-start & overview
├── docker-compose.yml     # Multi-container deployment config
├── project/
│   ├── backend/           # Django 5.2 REST Framework API & AI/RAG Engine
│   │   ├── authentication/# Clean Architecture user auth & JWT
│   │   ├── common/        # Security, RBAC, audit logging & error handling
│   │   ├── features/      # HR, DMS, Chats, Facilities, Analytics, Logs
│   │   └── core/          # Settings, URLs, WSGI configuration
│   ├── frontend/          # React 19 + TypeScript + Tailwind UI Dashboard
│   └── nginx/             # Nginx reverse proxy configs
```

---
*For detailed developer guides, database schemas, and API documentation, please refer to [DOCUMENTATION.md](file:///d:/Fifth%20year/MOGE/DOCUMENTATION.md).*

######################

for https
Invoke-WebRequest -Uri "https://dl.filippo.io/mkcert/latest?for=windows/amd64" -OutFile "$env:windir\System32\mkcert.exe"
mkcert -install
mkcert -version
mkcert moge.local localhost 127.0.0.1 192.168.20.39

https://github.com/Jayyy-mark/demo1.git


#### SSL Certicficate generation

mkdir certs

openssl req -x509 -newkey rsa:2048 -keyout certs/localhost-key.pem -out certs/localhost.pem -days 365 -nodes -subj "/CN=localhost"