from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user
from app.services.firebase import get_db
from app.services.anthropic import run_agent
from app.models.models import AgentChatRequest, AgentChatResponse

router = APIRouter()


@router.post("/{workflow_id}/chat", response_model=AgentChatResponse)
def agent_chat(
    workflow_id: str,
    body: AgentChatRequest,
    user: dict = Depends(get_current_user),
):
    """
    Run the AI agent for a specific workflow.
    Accepts message + full conversation history from the UI.
    """
    db = get_db()
    doc = db.collection("workflows").document(workflow_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = doc.to_dict()

    # Increment usage count
    db.collection("workflows").document(workflow_id).update(
        {"usageCount": workflow.get("usageCount", 0) + 1}
    )

    result = run_agent(
        workflow_title=workflow.get("title", ""),
        workflow_department=workflow.get("department", ""),
        workflow_problem=workflow.get("problem", ""),
        workflow_instructions=workflow.get("instructions", []),
        master_prompt=workflow.get("masterPrompt", ""),
        agent_prompt=workflow.get("agentPrompt", ""),
        history=[msg.model_dump() for msg in body.history],
        user_message=body.message,
        user_image=body.image,
    )

    return AgentChatResponse(
        response=result["response"],
        usage=result["usage"],
    )
