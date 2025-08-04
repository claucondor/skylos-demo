import asyncio
from google.adk.agents import Agent

from core.interviewer.tools import tool_take_notes
from core.agents.config import AGENT_CONFIGS
from core.interviewer.context import load_agent_context

def create_agent(agent_id: str = "sdr") -> Agent:
    """Creates and returns an agent based on the specified agent ID."""
    
    # Get agent configuration
    agent_config = next((config for config in AGENT_CONFIGS if config.id == agent_id), None)
    if not agent_config:
        raise ValueError(f"Agent configuration not found for ID: {agent_id}")
    
    # Load agent context
    agent_context = load_agent_context(agent_id)
    
    # Create final instruction with lead profile
    final_instruction = f"{agent_config.prompt}\n\n## Perfil del Lead\n{agent_context.lead_profile}\n\nRecuerda tomar notas de la conversación usando la herramienta tool_take_notes después de cada intercambio importante."

    root_agent = Agent(
        name=f"{agent_id}_agent",
        model="gemini-live-2.5-flash-preview",
        description=agent_config.description,
        instruction=final_instruction,
        tools=[tool_take_notes],
    )
    return root_agent

def create_interviewer_agent() -> Agent:
    """Legacy function for backward compatibility."""
    return create_agent("sdr")
