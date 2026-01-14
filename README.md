# 🩺 Post Discharge Medical AI Assistant (POC)

---

## 📘 Project Overview

The **Post Discharge Medical AI Assistant** is a **multi-agent GenAI system** designed to assist patients after hospital discharge.  
It uses **Retrieval-Augmented Generation (RAG)**, **LangGraph-based multi-agent orchestration**, and **medical data retrieval** to simulate intelligent patient support for **nephrology (kidney-related)** conditions.

> ⚕️ _This system is for **educational and demonstration purposes only**. Always consult a healthcare professional for medical advice._

---

## 🎯 Objectives

- Manage and retrieve 25+ dummy post-discharge reports  
- Use RAG over nephrology reference materials (PDF/text)  
- Implement **two intelligent agents**:
  1. 🧾 **Receptionist Agent** – handles patient identification, retrieves reports, and routes queries  
  2. 🧑‍⚕️ **Clinical Agent** – provides RAG-based medical responses with citations and web search fallback  
- Maintain complete **logging** of agent communications  
- Provide a simple **Streamlit web interface**

---

## ⚙️ Tech Stack

| Component | Technology Used |
|------------|----------------|
| **Frontend** | Streamlit |
| **Backend** | FastAPI |
| **Multi-Agent Framework** | LangGraph (with LangChain tools) |
| **Vector Database** | ChromaDB |
| **Embeddings Model** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Web Search API** | Google Generative AI / Serper API |
| **Database / Data Storage** | SQLite / JSON files |
| **Logging** | Python logging module with timestamped logs |

---

## 🧩 System Architecture

User (Patient)
│
▼
Receptionist Agent ──► Patient Data Retrieval Tool ──► Database (JSON / SQLite)
│
▼
Clinical Agent ──► RAG over Nephrology Reference ──► ChromaDB (Embeddings)
│
├──► Web Search (for latest medical info)
▼
Response with Citations + Log Entry


---

## 🧠 Multi-Agent Roles

### 🤖 Receptionist Agent
- Greets patient and asks for their name  
- Retrieves discharge summary using the **Patient Data Retrieval Tool**  
- Asks follow-up health questions  
- Routes clinical queries to **Clinical AI Agent**

### 🩺 Clinical AI Agent
- Uses **RAG** over nephrology documents for clinical responses  
- Provides **citations** from the reference book  
- Uses **Web Search** for latest or external information  
- Logs all interactions for traceability  

---

## 📂 Folder Structure

PostDischargeAI/
├── backend/
│ ├── main.py
│ ├── routers/
│ │ └── agents.py
│ ├── services/
│ │ ├── rag_engine.py
│ │ ├── patient_lookup.py
│ │ └── web_search.py
│ ├── data/
│ │ ├── patients.json
│ │ └── nephrology_reference.pdf
│ ├── core/
│ │ └── logger.py
│ ├── requirements.txt
│ └── .env
├── frontend/
│ └── streamlit_app.py
├── scripts/
│ ├── prepare_data.py
│ ├── build_embeddings.py
│ └── test_agents.py
└── README.md


---

## 🧱 Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/<your-username>/PostDischargeAI-GenAI-POC-Roobii.git
cd PostDischargeAI

**2️⃣ Setup Python Environment**
cd backend
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3️⃣ Configure Environment Variables

Create a .env file in backend/ with your API keys:
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_gemini_api_key


4️⃣ Run Backend Server
uvicorn main:app --reload

Backend will start at http://127.0.0.1:8000
5️⃣ Run Frontend (React.js)
cd frontend
npm run dev
npm run host--

📚 Features

✅ 25+ dummy discharge reports stored in JSON
✅ Nephrology reference book processed into vector embeddings
✅ RAG-enabled Clinical Agent with citations
✅ Web search integration for latest medical data
✅ Comprehensive logging of all actions
✅ Simple chat-based Streamlit UI


🧮 Example Patient Report
{
  "patient_name": "John Smith",
  "discharge_date": "2024-01-15",
  "primary_diagnosis": "Chronic Kidney Disease Stage 3",
  "medications": ["Lisinopril 10mg daily", "Furosemide 20mg twice daily"],
  "dietary_restrictions": "Low sodium (2g/day), fluid restriction (1.5L/day)",
  "follow_up": "Nephrology clinic in 2 weeks",
  "warning_signs": "Swelling, shortness of breath, decreased urine output",
  "discharge_instructions": "Monitor blood pressure daily, weigh yourself daily"
}


🔍 Sample Interaction Flow

System:

Hello! I’m your post-discharge care assistant. What’s your name?

Patient:

John Smith

Receptionist Agent:

Hi John! I found your discharge report from January 15th for Chronic Kidney Disease.
How are you feeling today? Are you following your medication schedule?

Patient:

I'm having swelling in my legs. Should I be worried?

Clinical Agent:

Based on your CKD diagnosis and nephrology guidelines, leg swelling may indicate fluid retention.
Please monitor your weight and consult your doctor if it persists.
(Source: Comprehensive Clinical Nephrology, 6th Edition, Page 412)

🧾 Logging

Each interaction (user + agent) is logged in /backend/logs/system_log.txt

Includes timestamps, agent names, and response sources (RAG / Web / DB)

| Component          | Choice               | Justification                                    |
| ------------------ | -------------------- | ------------------------------------------------ |
| **LLM**            | Gemini / OpenAI GPT  | Reliable text understanding & generation         |
| **Vector DB**      | ChromaDB             | Lightweight, open-source, ideal for local POC    |
| **RAG**            | LangChain pipeline   | Efficient document chunking + semantic retrieval |
| **Agents**         | LangGraph            | Modular orchestration of multi-agent workflow    |
| **Web Search**     | Google Generative AI | For real-time research updates                   |
| **Data Retrieval** | SQLite / JSON        | Simple structured query access for demo          |
| **Logging**        | Python logging       | Transparent debugging and traceability           |


traceability
🧪 Testing

To test agents individually:

python scripts/test_agents.py

To rebuild embeddings:
python scripts/build_embeddings.py


📜 Disclaimer

⚕️ This AI assistant is for educational and demonstration purposes only.
It is not a substitute for professional medical advice, diagnosis, or treatment.
Always consult qualified healthcare professionals for any medical concerns.

📹 Demo Video

🎥 Watch the project demo here:
Demo Video Link: https://drive.google.com/drive/folders/17Ns_InCF0B2JIUHf0oYv0BFMSLZpKQTk?usp=sharing



