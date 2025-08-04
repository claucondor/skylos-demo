import os
from datetime import datetime
import aiofiles
from typing import Optional

from core.interviewer.context import DATA_PATH

# Global variable to track current agent
current_agent_id: Optional[str] = None

def set_current_agent(agent_id: str):
    """Set the current agent ID for note-taking."""
    global current_agent_id
    current_agent_id = agent_id

async def tool_take_notes(conversation_exchange: str) -> str:
    """
    Update the conversation notes file with a new exchange.

    Args:
        conversation_exchange (str): The conversation exchange between agent and lead formatted as a string.
    Returns:
        str: Confirmation message
    """
    global current_agent_id
    
    # Use default agent if none set
    if not current_agent_id:
        current_agent_id = "sdr"
    
    notes_file = f"{DATA_PATH}conversation_notes_{current_agent_id}.md"
    
    # Ensure notes are loaded or initialized
    if not os.path.exists(notes_file):
        notes = f"# Notas de Conversación - {current_agent_id.upper()}\n\n"
    else:
        async with aiofiles.open(notes_file, "r", encoding="utf-8") as f:
            notes = await f.read()

    # Append new exchange
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notes += f"\n## {timestamp}\n\n{conversation_exchange}\n\n"

    async with aiofiles.open(notes_file, "w", encoding="utf-8") as f:
        await f.write(notes)
    
    return f"Notas actualizadas correctamente en {notes_file}"

# Legacy function for backward compatibility
async def tool_take_interview_notes(question_and_answer: str) -> str:
    """Legacy function for interview notes."""
    notes_file = f"{DATA_PATH}interview_note.md"
    
    if not os.path.exists(notes_file):
        notes = "# Notas de Entrevista\n\n"
    else:
        async with aiofiles.open(notes_file, "r", encoding="utf-8") as f:
            notes = await f.read()

    # Append new Q&A
    notes += f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{question_and_answer}\n\n"

    async with aiofiles.open(notes_file, "w", encoding="utf-8") as f:
        await f.write(notes)
    
    return "Notas de entrevista actualizadas"
    
if __name__ == "__main__":
    # Example usage
    import asyncio
    set_current_agent("sdr")
    conversation_exchange = "Agente: Hola, soy Elena de Skylos AI. ¿Podrías contarme sobre tu empresa?\nLead: Hola Elena, somos TechCorp Solutions, una empresa de tecnología con 150 empleados."
    result = asyncio.run(tool_take_notes(conversation_exchange))
    print(result)