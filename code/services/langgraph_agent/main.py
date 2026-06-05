from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="LangGraph Agent Service")


class AgentInput(BaseModel):
    query: str


def planner_node(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    tools_to_use = []

    if any(word in query_lower for word in ["similar", "market", "price", "listing", "listings"]):
        tools_to_use.append("RAG Service")

    if any(word in query_lower for word in ["image", "condition", "room", "renovation", "kitchen", "bathroom"]):
        tools_to_use.append("Image Analyzer")

    if not tools_to_use:
        tools_to_use = ["General Reasoning"]

    return {
        "step": "planner",
        "decision": "Selected tools based on query intent.",
        "tools_to_use": tools_to_use
    }


def tool_execution_node(tools_to_use: List[str]) -> Dict[str, Any]:
    tool_outputs = {}

    if "RAG Service" in tools_to_use:
        tool_outputs["rag"] = {
            "status": "selected",
            "purpose": "Retrieve similar property listings and market context."
        }

    if "Image Analyzer" in tools_to_use:
        tool_outputs["image_analyzer"] = {
            "status": "selected",
            "purpose": "Analyze room type, image condition, and renovation needs."
        }

    if "General Reasoning" in tools_to_use:
        tool_outputs["general"] = {
            "status": "selected",
            "purpose": "Provide general property analysis."
        }

    return {
        "step": "tool_execution",
        "tool_outputs": tool_outputs
    }


def synthesizer_node(query: str, tools_to_use: List[str], tool_outputs: Dict[str, Any]) -> Dict[str, Any]:
    answer = (
        "Based on the submitted property information, the listing should be reviewed "
        "for condition, comparable listings, and routing before publication."
    )

    if "RAG Service" in tools_to_use and "Image Analyzer" in tools_to_use:
        answer = (
            "The property should be compared against similar listings and reviewed for visible "
            "condition issues. Image analysis can help identify rooms that may need renovation, "
            "while RAG retrieval supports market comparison."
        )
    elif "RAG Service" in tools_to_use:
        answer = (
            "The property should be compared with similar listings to understand market positioning "
            "and pricing context."
        )
    elif "Image Analyzer" in tools_to_use:
        answer = (
            "The uploaded images should be reviewed for room type and condition score to identify "
            "possible renovation needs before publication."
        )

    return {
        "step": "synthesizer",
        "answer": answer,
        "tool_outputs_used": tool_outputs
    }


@app.get("/")
def root():
    return {
        "message": "LangGraph Agent Service is running",
        "architecture": "planner -> tool_execution -> synthesizer"
    }


@app.post("/agent/run")
def run_agent(data: AgentInput):
    planner_result = planner_node(data.query)

    tool_execution_result = tool_execution_node(
        planner_result["tools_to_use"]
    )

    synthesizer_result = synthesizer_node(
        data.query,
        planner_result["tools_to_use"],
        tool_execution_result["tool_outputs"]
    )

    reasoning_steps = [
        planner_result,
        tool_execution_result,
        {
            "step": "synthesizer",
            "decision": "Combined planner decision and tool outputs into final answer."
        }
    ]

    return {
        "answer": synthesizer_result["answer"],
        "tools_used": planner_result["tools_to_use"],
        "reasoning_steps": reasoning_steps,
        "agent_architecture": {
            "node_1": "planner_node",
            "node_2": "tool_execution_node",
            "node_3": "synthesizer_node"
        }
    }