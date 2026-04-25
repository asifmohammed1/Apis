# Multi-API Hub & Rising Star Todo Platform

Welcome to the **Multi-API Hub**, a sophisticated backend repository built by [Asif](https://asifportfolio123.web.app/). This project serves as a centralized platform containing various API integrations, Machine Learning model endpoints, and full-stack applications.

## 🌟 Overview

This repository is designed to host multiple diverse services. While it contains many different APIs and ML integrations, **Rising Star Todo** is currently the flagship application integrated into this ecosystem.

### Core Architecture
- **Backend:** FastAPI (Python 3.8+)
- **Database:** PostgreSQL (Hosted on Neon)
- **ORM:** SQLAlchemy
- **Containerization:** Docker & Docker Compose
- **Deployment:** Serverless deployment ready (Render & Vercel)

---

## 📝 Rising Star Todo (Flagship App)

The Todo application is a highly aesthetic, AI-powered productivity tool. It leverages state-of-the-art LLM capabilities via NVIDIA's API to help users manage their tasks seamlessly through a stunning dark-glassmorphism interface.

### ✨ Key Features
- **🤖 AI Intelligent Assistant:** Integrated chatbot powered by NVIDIA NIM (`moonshotai/kimi-k2-instruct`). Create tasks using natural language (e.g., "Remind me to call Mom at 6 PM tomorrow").
- **📅 Smart Date Parsing:** Automatically extracts dates and times from your task titles and chat messages.
- **⚡ Priority & Organization:** Color-coded priority levels (High, Medium, Low), subtask support, and real-time task status tracking.
- **🖼️ Immersive Visual Experience:** Full-screen AI-generated hero carousel, dynamic backgrounds, and a unified glassmorphic design system.
- **🔄 Real-time Persistence:** Seamless data synchronization with a PostgreSQL backend via FastAPI.
- **🔐 Secure Access:** Professional JWT-based authentication system for secure task management.

### 🛠️ Todo Tech Stack
- **Frontend:** Vanilla JavaScript (ES6+), Modern CSS3 (Grid/Flexbox), HTML5.
- **Backend:** FastAPI, Python 3.12, SQLAlchemy ORM.
- **AI/ML:** NVIDIA NIM API for LLM inference.
- **Database:** PostgreSQL (Neon).
- **Deployment:** Vercel (Frontend), Render (Backend).

---

## 🤖 ML Models & API Services

Beyond the Todo application, this repository is designed to be highly extensible. It serves as the foundation for:
- **Telegram Bot Webhooks:** Handling automated messaging and workflows.
- **LLM Integrations:** Generic LLM inference endpoints currently powered by NVIDIA APIs (previously OpenRouter).
- **Future ML Projects:** Structured to easily plug in computer vision or advanced data analysis models via FastAPI endpoints.

---

## 🚀 Running Locally

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Apis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Create a `.env` file and populate it with your PostgreSQL connection string and NVIDIA API key.

4. **Run the Server:**
   ```bash
   uvicorn main:app --reload
   ```
   The platform will be available at `http://127.0.0.1:8000`. Access the Todo application at `http://127.0.0.1:8000/todo`.

---

## 👨‍💻 Author & Copyright

**&copy; 2026 Asif. All rights reserved.**

This project was developed by Asif. For more information, projects, and contact details, please visit the official portfolio:
👉 **[View Portfolio](https://asifportfolio123.web.app/)**
