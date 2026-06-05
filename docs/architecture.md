# AI Property Triage Architecture

User
→ Streamlit WebUI
→ n8n Workflow

Workflow:
1. Input Guardrails
2. Information Extractor
3. RAG Service
4. Image Analyzer
5. LangGraph Agent
6. Output Guardrails
7. Router
8. Final Report

Services:
- Guardrails Service (8003)
- RAG Service (8001)
- Image Analyzer (8002)
- LangGraph Agent (8004)

Technologies:
- FastAPI
- Streamlit
- Ollama
- ChromaDB
- n8n
- Docker
- PyTorch