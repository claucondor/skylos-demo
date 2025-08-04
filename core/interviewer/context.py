from pydantic import BaseModel
from typing import Optional

DATA_PATH = "default_context/"  # Default path for data storage

class AgentContext(BaseModel):
    """Configuration for the agent demo."""
    agent_id: str
    agent_name: str
    lead_profile: str
    conversation_notes: str
    objectives_completed: dict = {}

class InterviewerContext(BaseModel):
    """Configuration for the interviewer agent (legacy)."""
    role_description: str
    job_description: str
    resume: str
    interview_notes: str

def load_agent_context(agent_id: str) -> AgentContext:
    """Load context for a specific agent demo."""
    try:
        with open(f"{DATA_PATH}lead_profile.md", "r", encoding="utf-8") as f:
            lead_profile = f.read()
    except FileNotFoundError:
        lead_profile = "# Perfil del Lead\n\nEl agente debe descubrir la información del lead durante la conversación. No hay información predefinida."
    
    try:
        with open(f"{DATA_PATH}conversation_notes_{agent_id}.md", "r", encoding="utf-8") as f:
            conversation_notes = f.read()
    except FileNotFoundError:
        conversation_notes = ""
    
    # Get agent name from config
    from core.agents.config import AGENT_CONFIGS
    agent_name = next((config.name for config in AGENT_CONFIGS if config.id == agent_id), "Agente Desconocido")
    
    return AgentContext(
        agent_id=agent_id,
        agent_name=agent_name,
        lead_profile=lead_profile,
        conversation_notes=conversation_notes
    )

def load_interviewer_context():
    """Legacy function for backward compatibility."""
    try:
        resume_content = open(f"{DATA_PATH}cv.md", "r", encoding="utf-8").read()
    except FileNotFoundError:
        resume_content = "# CV del Candidato\n\nInformación no disponible"
    
    try:
        job_description = open(f"{DATA_PATH}job_description.md", "r", encoding="utf-8").read()
    except FileNotFoundError:
        job_description = "# Descripción del Trabajo\n\nInformación no disponible"
    
    try:
        role_description = open(f"{DATA_PATH}role_description.md", "r", encoding="utf-8").read()
    except FileNotFoundError:
        role_description = "# Descripción del Rol\n\nInformación no disponible"
    
    try:
        with open(f"{DATA_PATH}interview_note.md", "r", encoding="utf-8") as f:
            interview_notes = f.read()
    except FileNotFoundError:
        interview_notes = ""

    return InterviewerContext(
        role_description=role_description,
        job_description=job_description,
        resume=resume_content,
        interview_notes=interview_notes
    )
