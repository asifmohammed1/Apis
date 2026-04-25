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

### Features
- **AI Chatbot Integration:** Embedded AI assistant powered by `moonshotai/kimi-k2-instruct` via the NVIDIA API.
- **Smart Task Management:** Ask the AI to "create a task to study physics tomorrow" and it will automatically extract the details and add it to your dashboard.
- **Premium UI/UX:** Full-screen AI-generated carousel backgrounds, smooth glassmorphism modals, and highly responsive vanilla JavaScript interactions.
- **Secure Authentication:** Fully functional JWT-based user authentication.
- **Subtasks & Priority:** Deeply organize your life with subtasks, due dates, and priority tagging.

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
