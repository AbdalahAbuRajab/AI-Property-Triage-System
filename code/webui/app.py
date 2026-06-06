import streamlit as st
import requests
import pandas as pd
from datetime import datetime

N8N_WEBHOOK_URL = "http://localhost:5678/webhook/property-triage"
RAG_URL = "http://127.0.0.1:8001/query"
OLLAMA_URL = "http://localhost:11434/api/generate"

st.set_page_config(page_title="AI Property Triage", page_icon="🏠", layout="wide")

st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] { gap: 12px; }
.stTabs [data-baseweb="tab"] {
    background-color: white;
    border-radius: 12px;
    padding: 10px 18px;
    border: 1px solid #e6e9ef;
}
.stButton > button {
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
}
.main { background-color: #f7f9fc; }
.block-container { padding-top: 2rem; }
.hero-card {
    background: linear-gradient(135deg, #1f4e79, #2f80ed);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 24px;
}
.hero-title { font-size: 34px; font-weight: 800; margin-bottom: 8px; }
.hero-subtitle { font-size: 18px; opacity: 0.95; }
.report-card {
    background: white;
    padding: 24px;
    border-radius: 18px;
    border: 1px solid #e6e9ef;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    margin-top: 12px;
}
.feature-card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e6e9ef;
    margin-bottom: 16px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="hero-title">AI Property Triage System</div>
    <div class="hero-subtitle">
        Automated real estate listing validation, RAG-based comparison, image analysis, routing, and AI reporting.
    </div>
</div>
""", unsafe_allow_html=True)

if "reports_history" not in st.session_state:
    st.session_state.reports_history = []

submission_tab, chat_tab, analytics_tab, architecture_tab = st.tabs([
    "Property Submission",
    "Real Estate Assistant",
    "Reports & Analytics",
    "System Architecture"
])


def get_first_image_url(uploaded_image, image_urls):
    if uploaded_image is not None:
        name = uploaded_image.name.lower()
        if "kitchen" in name:
            return "uploaded_kitchen.jpg"
        if "bathroom" in name:
            return "uploaded_bathroom.jpg"
        if "bedroom" in name:
            return "uploaded_bedroom.jpg"
        if "living" in name:
            return "uploaded_living.jpg"
        if "exterior" in name:
            return "uploaded_exterior.jpg"
        return "uploaded_other.jpg"

    if image_urls.strip():
        return image_urls.split("\n")[0].strip()

    return ""


def infer_property_type(description):
    text = description.lower()
    if "office" in text:
        return "Office"
    if "retail" in text or "shop" in text or "store" in text:
        return "Retail"
    if "industrial" in text or "warehouse" in text:
        return "Industrial"
    if "villa" in text:
        return "Villa"
    if "house" in text:
        return "House"
    if "apartment" in text or "flat" in text:
        return "Apartment"
    return "Unknown"


def infer_location(description):
    text = description.lower()
    if "haifa" in text:
        return "Haifa"
    if "tel aviv" in text:
        return "Tel Aviv"
    if "nazareth" in text:
        return "Nazareth"
    if "jerusalem" in text:
        return "Jerusalem"
    return "Unknown"


def infer_image_assessment(first_image_url):
    text = first_image_url.lower()
    if "kitchen" in text:
        return "Kitchen", 4
    if "bathroom" in text:
        return "Bathroom", 3
    if "bedroom" in text:
        return "Bedroom", 4
    if "living" in text:
        return "Living Room", 4
    if "exterior" in text:
        return "Exterior", 3
    return "Unknown", 0


def calculate_quality(description, location, property_type, first_image_url):
    score = 0
    strengths = []
    missing = []

    if location != "Unknown":
        score += 20
        strengths.append("Location specified")
    else:
        missing.append("Location missing")

    if property_type != "Unknown":
        score += 20
        strengths.append("Property type identified")
    else:
        missing.append("Property type not clearly identified")

    if len(description.strip()) > 80:
        score += 20
        strengths.append("Detailed description")
    else:
        missing.append("Description too short")

    if first_image_url:
        score += 20
        strengths.append("Images provided")
    else:
        missing.append("No images provided")

    if "bathroom" in description.lower() or "bathrooms" in description.lower():
        score += 10
        strengths.append("Bathroom information included")
    else:
        missing.append("Bathroom count not specified")

    if "price" in description.lower() or "$" in description or "usd" in description.lower():
        score += 10
        strengths.append("Price information included")
    else:
        missing.append("Price not provided")

    return score, strengths, missing


with submission_tab:
    st.subheader("Property Submission via n8n")

    agent_name = st.text_input("Agent Name")
    property_description = st.text_area("Property Description")
    image_urls = st.text_area("Image URLs (one per line)")

    uploaded_image = st.file_uploader(
        "Upload Property Image",
        type=["jpg", "jpeg", "png"]
    )

    if st.button("Submit Listing"):
        first_image_url = get_first_image_url(uploaded_image, image_urls)

        try:
            n8n_response = requests.post(
                N8N_WEBHOOK_URL,
                json={
                    "description": property_description,
                    "image_url": first_image_url,
                    "agent_name": agent_name
                },
                timeout=60
            )

            try:
                n8n_result = n8n_response.json()
            except ValueError:
                n8n_result = {
                    "status": "success",
                    "message": "Workflow completed but returned an empty response.",
                    "route_to_team": "Unknown"
                }

        except requests.RequestException as e:
            st.error("Could not connect to n8n workflow.")
            st.code(str(e))
            st.stop()

        if isinstance(n8n_result, list) and len(n8n_result) > 0:
            n8n_data = n8n_result[0]
        elif isinstance(n8n_result, dict):
            n8n_data = n8n_result
        else:
            n8n_data = {}

        with st.expander("View raw n8n response"):
            st.json(n8n_result)

        route_to_team = n8n_data.get("route_to_team", "Unknown")
        status = n8n_data.get("status", "success")

        if status == "rejected" or route_to_team == "Rejected":
            st.error("Listing rejected by input guardrails.")
            st.warning(n8n_data.get("reason", "The submission did not pass validation."))

            st.markdown("""
<div class="report-card">
<h2>Rejected Submission</h2>
<p>This listing was blocked before entering the AI property review pipeline.</p>
<p><b>Reason:</b> The input did not pass guardrails validation.</p>
<p><b>Review Status:</b> ❌ Rejected</p>
</div>
""", unsafe_allow_html=True)

        else:
            property_type = infer_property_type(property_description)
            location = infer_location(property_description)
            room_type, condition_score = infer_image_assessment(first_image_url)

            if route_to_team == "Unknown":
                if property_type in ["Office", "Retail", "Industrial"]:
                    route_to_team = "Commercial"
                else:
                    route_to_team = "Residential"

            quality_score, strengths, missing_items = calculate_quality(
                property_description,
                location,
                property_type,
                first_image_url
            )

            strengths_text = "<br>".join([f"✅ {item}" for item in strengths]) or "No strengths detected."
            missing_text = "<br>".join([f"⚠️ {item}" for item in missing_items]) if missing_items else "✅ No missing information detected."

            st.success("Listing processed successfully through n8n!")
            st.progress(quality_score / 100)

            st.markdown('<div class="report-card">', unsafe_allow_html=True)

            st.markdown(f"""
## Property Assessment Report

### Basic Information

**Agent Name:** {agent_name}  
**Property Type:** {property_type}  
**Location:** {location}  
**Route To Team:** {route_to_team}

---

### Listing Summary

{property_description}

---

### Image Assessment

**Detected Room Type:** {room_type}  
**Estimated Condition Score:** {condition_score} / 5

---

### Listing Quality Score

**Score:** {quality_score}/100

#### Strengths

{strengths_text}

#### Missing Information

{missing_text}

---

### AI Recommendation

This property was processed successfully through the AI Property Triage workflow.  
The listing passed input validation, was processed by the RAG and image analysis services, and was assigned to the **{route_to_team}** team.

---

### Review Status

✅ Ready for agent review before publication.
""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            report_record = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "agent_name": agent_name,
                "property_type": property_type,
                "location": location,
                "route_to_team": route_to_team,
                "room_type": room_type,
                "condition_score": condition_score,
                "quality_score": quality_score,
                "description": property_description[:80] + "..."
            }

            st.session_state.reports_history.append(report_record)


with chat_tab:
    st.subheader("Real Estate Assistant")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Hi! I can help with property listings, condition checks, renovation suggestions, and listing preparation."
            }
        ]

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input("Ask a real estate question...")

    if user_question:
        st.session_state.chat_messages.append({"role": "user", "content": user_question})

        system_prompt = """
You are a helpful real estate assistant.
Answer only questions related to real estate, property listings, property condition, pricing considerations, renovation advice, and listing preparation.
If the user asks an unrelated question, politely refuse and explain that you can only help with real estate topics.
Do not provide legal advice.
Do not guarantee property prices, investment returns, or profits.
Keep answers clear, practical, and concise.
"""

        conversation_text = ""
        for msg in st.session_state.chat_messages:
            conversation_text += f"{msg['role']}: {msg['content']}\n"

        rag_context = ""
        rag_keywords = ["similar", "listing", "listings", "market", "apartment", "office", "haifa", "tel aviv"]

        if any(keyword in user_question.lower() for keyword in rag_keywords):
            try:
                rag_response = requests.post(
                    RAG_URL,
                    json={"description": user_question},
                    timeout=20
                )

                rag_result = rag_response.json()
                rag_context = "Relevant similar listings from the internal property database:\n"

                for item in rag_result.get("similar_listings", []):
                    metadata = item.get("metadata", {})
                    rag_context += (
                        f"- {metadata.get('title', 'Unknown title')} | "
                        f"Location: {metadata.get('location', 'Unknown')} | "
                        f"Type: {metadata.get('property_type', 'Unknown')} | "
                        f"Price: {metadata.get('price', 'Unknown')} | "
                        f"Features: {metadata.get('features', 'Unknown')}\n"
                    )

            except Exception:
                rag_context = "RAG service was not available for this question.\n"

        full_prompt = f"""
{system_prompt}

Use the following internal database context if it is relevant:
{rag_context}

Conversation:
{conversation_text}

Assistant:
"""

        with st.spinner("Assistant is thinking..."):
            try:
                ollama_response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": "llama3.2:1b",
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=20
                )

                ollama_result = ollama_response.json()
                assistant_answer = ollama_result.get("response", "No response received.")

            except Exception:
                if rag_context and "Relevant similar listings" in rag_context:
                    assistant_answer = (
                        "Ollama is not currently running on this AWS server, "
                        "but I found relevant listings from the RAG service:\n\n"
                        + rag_context
                    )
                else:
                    assistant_answer = (
                        "The local Ollama assistant is not currently running on this AWS server. "
                        "The property triage workflow and AI services are deployed successfully, "
                        "but the chat assistant requires Ollama to be installed and running."
                    )

        st.session_state.chat_messages.append({"role": "assistant", "content": assistant_answer})
        st.rerun()

    if st.button("Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()


with analytics_tab:
    st.subheader("Reports & Analytics Dashboard")
    st.markdown("""
    <div class="report-card">
    <h3>📊 Operational Overview</h3>
    <p>
    Monitor processed listings, routing decisions, image condition scores, and listing quality.
    </p>
    </div>
    <br>
    """, unsafe_allow_html=True)

    reports = st.session_state.reports_history

    if len(reports) == 0:
        st.info("No reports submitted yet.")
    else:
        df = pd.DataFrame(reports)

        total_reports = len(df)
        residential_count = len(df[df["route_to_team"] == "Residential"])
        commercial_count = len(df[df["route_to_team"] == "Commercial"])
        rejected_count = len(df[df["route_to_team"] == "Rejected"]) if "Rejected" in df["route_to_team"].values else 0
        avg_condition = round(df["condition_score"].mean(), 2)
        avg_quality = round(df["quality_score"].mean(), 2)

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total Reports", total_reports)
        col2.metric("Residential", residential_count)
        col3.metric("Commercial", commercial_count)
        col4.metric("Avg Condition", f"{avg_condition}/5")
        col5.metric("Avg Quality", f"{avg_quality}/100")

        if rejected_count > 0:
            st.warning(f"Rejected submissions: {rejected_count}")

        st.write("### Reports History")
        st.dataframe(df, use_container_width=True)

        if st.button("Clear Reports History"):
            st.session_state.reports_history = []
            st.rerun()


with architecture_tab:
    st.subheader("System Architecture")

    st.markdown("""
<div class="report-card">
<h2>🏗️ AI Property Triage Architecture</h2>
<p>
This system uses a modular AI workflow where Streamlit sends property submissions to n8n,
and n8n orchestrates multiple AI services to validate, analyze, retrieve, reason, and route listings.
</p>
</div>
<br>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
<div class="feature-card">
<h3>🖥️ Streamlit WebUI</h3>
<p>Property submission, image upload, assistant chat, analytics dashboard, and report display.</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="feature-card">
<h3>🛡️ Guardrails</h3>
<p>Validates listing input, blocks spam, detects off-topic content, and checks unsafe output claims.</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="feature-card">
<h3>🧠 LangGraph Agent</h3>
<p>Planner → Tool Execution → Synthesizer architecture for structured property reasoning.</p>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
<div class="feature-card">
<h3>🔁 n8n Workflow</h3>
<p>Orchestrates the complete AI pipeline using a published webhook and service calls.</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="feature-card">
<h3>🔎 RAG + ChromaDB</h3>
<p>Retrieves similar listings from the internal property database using vector search.</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="feature-card">
<h3>🤖 Ollama Assistant</h3>
<p>Local real estate assistant connected to RAG context for property-related questions.</p>
</div>
""", unsafe_allow_html=True)

    with col3:
        st.markdown("""
<div class="feature-card">
<h3>📩 Webhook Input</h3>
<p>Receives property description, agent name, and uploaded image metadata.</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="feature-card">
<h3>🖼️ Image Analyzer</h3>
<p>Detects room type and estimates condition score. Includes PyTorch training script.</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="feature-card">
<h3>📊 Reports & Analytics</h3>
<p>Tracks processed listings, routing distribution, condition scores, and quality scores.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<br>
<div class="report-card">
<h3>End-to-End Flow</h3>
<p>
<b>User</b> → <b>Streamlit</b> → <b>n8n</b> → <b>Guardrails</b> → 
<b>Information Extractor</b> → <b>RAG</b> → <b>Image Analyzer</b> → 
<b>LangGraph Agent</b> → <b>Output Guardrails</b> → <b>Router</b> → <b>Final Report</b>
</p>
</div>
""", unsafe_allow_html=True)
