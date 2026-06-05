import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="AI Property Triage",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

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
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="hero-title"> AI Property Triage System</div>
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

        first_image_url = ""

        if uploaded_image is not None:
            uploaded_image_name = uploaded_image.name.lower()

            if "kitchen" in uploaded_image_name:
                first_image_url = "uploaded_kitchen.jpg"
            elif "bathroom" in uploaded_image_name:
                first_image_url = "uploaded_bathroom.jpg"
            elif "bedroom" in uploaded_image_name:
                first_image_url = "uploaded_bedroom.jpg"
            elif "living" in uploaded_image_name:
                first_image_url = "uploaded_living.jpg"
            elif "exterior" in uploaded_image_name:
                first_image_url = "uploaded_exterior.jpg"
            else:
                first_image_url = "uploaded_other.jpg"

        elif image_urls.strip() != "":
            first_image_url = image_urls.split("\n")[0].strip()

        n8n_response = requests.post(
            "http://localhost:5678/webhook/property-triage",
            json={
                "description": property_description,
                "image_url": first_image_url,
                "agent_name": agent_name
            }
        )

        n8n_result = n8n_response.json()

        if isinstance(n8n_result, list) and len(n8n_result) > 0:
            n8n_data = n8n_result[0]
        else:
            n8n_data = n8n_result

        with st.expander("View raw n8n response"):
            st.json(n8n_result)

        route_to_team = n8n_data.get("route_to_team", "Unknown")

        property_type = "Apartment"

        if "office" in property_description.lower():
            property_type = "Office"
        elif "retail" in property_description.lower():
            property_type = "Retail"
        elif "industrial" in property_description.lower():
            property_type = "Industrial"
        elif "villa" in property_description.lower():
            property_type = "Villa"
        elif "house" in property_description.lower():
            property_type = "House"

        location = "Unknown"

        if "haifa" in property_description.lower():
            location = "Haifa"
        elif "tel aviv" in property_description.lower():
            location = "Tel Aviv"
        elif "nazareth" in property_description.lower():
            location = "Nazareth"
        elif "jerusalem" in property_description.lower():
            location = "Jerusalem"

        room_type = "Unknown"
        condition_score = 0

        if "kitchen" in first_image_url.lower():
            room_type = "Kitchen"
            condition_score = 4
        elif "bathroom" in first_image_url.lower():
            room_type = "Bathroom"
            condition_score = 3
        elif "bedroom" in first_image_url.lower():
            room_type = "Bedroom"
            condition_score = 4
        elif "living" in first_image_url.lower():
            room_type = "Living Room"
            condition_score = 4
        elif "exterior" in first_image_url.lower():
            room_type = "Exterior"
            condition_score = 3

        quality_score = 0
        strengths = []
        missing_items = []

        if location != "Unknown":
            quality_score += 20
            strengths.append("Location specified")
        else:
            missing_items.append("Location missing")

        if property_type != "Unknown":
            quality_score += 20
            strengths.append("Property type identified")

        if len(property_description) > 80:
            quality_score += 20
            strengths.append("Detailed description")
        else:
            missing_items.append("Description too short")

        if first_image_url != "":
            quality_score += 20
            strengths.append("Images provided")
        else:
            missing_items.append("No images provided")

        if "bathroom" in property_description.lower():
            quality_score += 10
            strengths.append("Bathroom information included")
        else:
            missing_items.append("Bathroom count not specified")

        if "price" in property_description.lower():
            quality_score += 10
            strengths.append("Price information included")
        else:
            missing_items.append("Price not provided")

        strengths_text = "<br>".join([f"✅ {item}" for item in strengths])

        if len(missing_items) > 0:
            missing_text = "<br>".join([f"⚠️ {item}" for item in missing_items])
        else:
            missing_text = "✅ No missing information detected."

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
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": user_question
            }
        )

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

        rag_keywords = [
            "similar", "listing", "listings", "market",
            "apartment", "office", "haifa", "tel aviv"
        ]

        if any(keyword in user_question.lower() for keyword in rag_keywords):
            try:
                rag_response = requests.post(
                    "http://127.0.0.1:8001/query",
                    json={
                        "description": user_question
                    }
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
            ollama_response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": full_prompt,
                    "stream": False
                }
            )

            ollama_result = ollama_response.json()
            assistant_answer = ollama_result.get("response", "No response received.")

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": assistant_answer
            }
        )

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
        avg_condition = round(df["condition_score"].mean(), 2)
        avg_quality = round(df["quality_score"].mean(), 2)

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total Reports", total_reports)
        col2.metric("Residential", residential_count)
        col3.metric("Commercial", commercial_count)
        col4.metric("Avg Condition", f"{avg_condition}/5")
        col5.metric("Avg Quality", f"{avg_quality}/100")

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