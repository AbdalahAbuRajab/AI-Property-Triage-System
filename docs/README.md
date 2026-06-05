# 🏠 AI Property Triage System

## Overview

AI Property Triage System is an end-to-end AI-powered workflow for processing and evaluating real estate listings.

The platform automatically validates incoming property submissions, retrieves similar listings using Retrieval-Augmented Generation (RAG), analyzes property images, generates AI-powered recommendations, and routes listings to the correct business team.

This project demonstrates a production-style AI architecture using modern AI engineering tools and workflows.

---

## Features

### Property Submission Workflow

* Submit property listings through a Streamlit interface
* Upload property images
* Automatic workflow execution through n8n

### Guardrails

* Spam detection
* Off-topic detection
* Property-listing validation
* Output safety checks
* Unsafe claim prevention

### RAG + ChromaDB

* Vector similarity search
* Similar property retrieval
* Market comparison insights

### Image Analysis

* Room type detection
* Property condition scoring
* PyTorch EfficientNet-B0 training pipeline included

Supported room categories:

* Kitchen
* Bathroom
* Bedroom
* Living Room
* Exterior
* Other

### LangGraph Agent

Planner → Tool Execution → Synthesizer

The agent combines information from:

* Property description
* Retrieved listings
* Image analysis results

to generate structured recommendations.

### Real Estate Assistant

Powered by:

* Ollama
* Llama 3
* RAG-enhanced responses

Supports:

* Similar listing search
* Property advice
* Listing preparation
* Renovation suggestions

### Analytics Dashboard

Tracks:

* Total processed listings
* Residential vs Commercial routing
* Average condition score
* Average listing quality score
* Historical reports

---

## Architecture

User

↓

Streamlit WebUI

↓

n8n Workflow Orchestrator

↓

Input Guardrails

↓

Information Extraction

↓

RAG Service + ChromaDB

↓

Image Analyzer

↓

LangGraph Agent

↓

Output Guardrails

↓

Router

↓

Final Property Assessment Report

---

## Technology Stack

### Frontend

* Streamlit

### AI / ML

* Ollama
* Llama 3
* LangGraph
* LangChain
* ChromaDB
* PyTorch
* EfficientNet-B0

### Backend

* FastAPI
* Python

### Workflow Automation

* n8n

### Infrastructure

* Docker
* AWS EC2

---

## Services

### RAG Service

Port: 8001

Responsibilities:

* Similar listing retrieval
* Vector search
* Market insights

### Image Analyzer

Port: 8002

Responsibilities:

* Room classification
* Condition scoring

### Guardrails Service

Port: 8003

Responsibilities:

* Input validation
* Output validation

### LangGraph Agent

Port: 8004

Responsibilities:

* Planning
* Tool orchestration
* Recommendation generation

---

## Running the Project

### Start Services

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
uvicorn main:app --host 0.0.0.0 --port 8002
uvicorn main:app --host 0.0.0.0 --port 8003
uvicorn main:app --host 0.0.0.0 --port 8004
```

### Start n8n

```bash
docker run -it --rm \
-p 5678:5678 \
-v n8n_data:/home/node/.n8n \
n8nio/n8n
```

### Start Streamlit

```bash
streamlit run app.py
```

---

## Project Structure

```text
AI_Property_Triage/
│
├── code/
│   ├── services/
│   └── webui/
│
├── docs/
│   ├── architecture_diagram.png
│   ├── deployment_notes.md
│   └── prompt_engineering_log.md
│
├── n8n/
│   └── n8n_property_triage_workflow.json
│
├── demo/
│
└── README.md
```

---

## Future Improvements

* Real image inference model
* Full AWS deployment
* Managed vector database
* Multi-agent workflow
* Reviewer feedback loop
* Active learning pipeline

---

## Author

Abdallah Abu Rajab

B.Sc. Information Systems

University of Haifa
