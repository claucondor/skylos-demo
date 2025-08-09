# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import asyncio
import base64
import warnings

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.interviewer.agent import create_agent
from core.interviewer.tools import set_current_agent
from core.analyser.analyse_interview import analyse_interview, save_analysis, analyse_with_prompt

def get_agent_voice(agent_id: str) -> str:
    """Get the appropriate voice for each agent."""
    agent_config = next((config for config in AGENT_CONFIGS if config.id == agent_id), None)
    if agent_config:
        return agent_config.voice_name
    return "Aoede"  # Default voice if agent not found

def get_agent_language(agent_id: str) -> str:
    """Get the appropriate language for each agent."""
    agent_config = next((config for config in AGENT_CONFIGS if config.id == agent_id), None)
    if agent_config:
        return agent_config.language_code
    return "es-ES"  # Default language if agent not found
from core.interviewer.context import load_interviewer_context, load_agent_context, DATA_PATH
from core.agents.config import AGENT_CONFIGS
from api import documents
from api import api_key


load_dotenv()

APP_NAME = "Interviewer"


async def start_agent_session(user_id, is_audio=False, agent_id="sdr", voice_name=None, language_code=None):
    """Starts an agent session"""

    # Set current agent for note-taking
    set_current_agent(agent_id)

    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=create_agent(agent_id),
    )

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # Replace with actual user ID
    )

    # Set response modality with voice configuration
    modality = "AUDIO" if is_audio else "TEXT"
    
    # Configure voice for audio responses
    if is_audio:
        # Use provided voice or get agent-specific voice
        selected_voice = voice_name or get_agent_voice(agent_id)
        selected_language = language_code or get_agent_language(agent_id)
        
        run_config = RunConfig(
            response_modalities=[modality],
            speech_config={
                "voice_config": {"prebuilt_voice_config": {"voice_name": selected_voice}},
                "language_code": selected_language
            }
        )
        print(f"Audio config: voice={selected_voice}, language={selected_language}")
    else:
        run_config = RunConfig(response_modalities=[modality])

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        user_id=user_id,
        session_id=session.id,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    
    # Don't send initial message - let the agent start naturally when user speaks
    
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    while True:
        async for event in live_events:

            # If the turn complete or interrupted, send it
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: {message}")
                continue

            # Read the Content and its first Part
            part: Part = (
                event.content and event.content.parts and event.content.parts[0]
            )
            if not part:
                continue

            # If it's audio, send Base64 encoded audio data
            is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
            if is_audio:
                audio_data = part.inline_data and part.inline_data.data
                if audio_data:
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_data).decode("ascii")
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                    continue

            # If it's text and a parial text, send it
            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: text/plain: {message}")


async def client_to_agent_messaging(websocket, live_request_queue):
    """Client to agent communication"""
    while True:
        # Decode JSON message
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]

        # Send the message to the agent
        if mime_type == "text/plain":
            # Send a text message
            content = Content(role="user", parts=[Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # Send an audio data
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
            print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes.")
        else:
            raise ValueError(f"Mime type not supported: {mime_type}")

app = FastAPI()


@app.get("/api/agents")
async def get_agents():
    """Get available agent configurations."""
    return {"agents": [agent.dict() for agent in AGENT_CONFIGS]}

@app.get("/api/api_key_status")
async def get_api_key_status():
    """Check if API key is configured."""
    api_key = os.getenv("GEMINI_API_KEY")
    return {"configured": bool(api_key and api_key.strip())}

@app.get("/api/objectives_progress/{agent_id}")
async def get_objectives_progress(agent_id: str):
    """Analyze conversation progress and return objective completion status."""
    try:
        context = load_agent_context(agent_id)
        agent_config = next((config for config in AGENT_CONFIGS if config.id == agent_id), None)
        
        if not agent_config:
            return {"statuses": {}}
            
        # If no conversation notes yet, return all pending
        if not context.conversation_notes or not context.conversation_notes.strip():
            return {"statuses": {obj.id: "pending" for obj in agent_config.objectives}}
        
        # Analyze conversation notes to determine objective progress
        from core.analyser.analyse_interview import analyse_with_prompt
        
        analysis_prompt = f"""
        Analiza CUIDADOSAMENTE las siguientes notas de conversación y determina el estado REAL de cada objetivo.
        
        IMPORTANTE: Solo marca como "completed" si hay evidencia CLARA de que el objetivo se cumplió completamente.
        
        Objetivos del agente:
        {chr(10).join([f"- {obj.id}: {obj.label} - {obj.description}" for obj in agent_config.objectives])}
        
        Notas de la conversación:
        {context.conversation_notes}
        
        REGLAS ESTRICTAS:
        - pending: No se ha mencionado o trabajado en absoluto
        - in_progress: Se está trabajando pero NO completado totalmente
        - completed: SOLO si hay evidencia CLARA y COMPLETA del objetivo cumplido
        
        Si las notas están vacías o no hay conversación real, TODO debe ser "pending".
        
        Responde SOLO con el formato:
        objetivo_id:estado
        
        Ejemplo:
        1:pending
        2:pending
        3:pending
        """
        
        analysis_result = analyse_with_prompt(analysis_prompt)
        
        # Parse the analysis result
        statuses = {}
        for line in analysis_result.split('\n'):
            if ':' in line:
                try:
                    obj_id, status = line.strip().split(':', 1)
                    if status in ['pending', 'in_progress', 'completed']:
                        statuses[obj_id] = status
                except:
                    continue
        
        return {"statuses": statuses}
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error analyzing objectives progress: {error_msg}")
        
        # If it's a rate limit error, return 429 status
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            from fastapi import HTTPException
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Return all pending on other errors
        agent_config = next((config for config in AGENT_CONFIGS if config.id == agent_id), None)
        if agent_config:
            return {"statuses": {obj.id: "pending" for obj in agent_config.objectives}}
        return {"statuses": {}}

@app.post("/api/analyse/{agent_id}")
async def analyse_conversation(agent_id: str):
    """Triggers the conversation analysis for a specific agent."""
    context = load_agent_context(agent_id)
    
    # Get agent config
    agent_config = next((config for config in AGENT_CONFIGS if config.id == agent_id), None)
    if not agent_config:
        return {"error": "Agent not found"}
    
    # Create analysis prompt
    analysis_prompt = f"""
    Analiza la siguiente conversación del agente {agent_config.name} y evalúa qué objetivos se cumplieron:

    ## Objetivos del Agente:
    {chr(10).join([f"- {obj.label}: {obj.description}" for obj in agent_config.objectives])}

    ## Perfil del Lead:
    {context.lead_profile}

    ## Notas de la Conversación:
    {context.conversation_notes}

    ## Instrucciones:
    1. Evalúa cada objetivo y determina si se cumplió (Sí/No/Parcialmente)
    2. Proporciona evidencia específica de la conversación
    3. Sugiere mejoras para futuros intercambios
    4. Califica el desempeño general del agente (1-10)

    Formato tu respuesta en Markdown con secciones claras.
    """
    
    from core.analyser.analyse_interview import analyse_with_prompt
    analysis_result = analyse_with_prompt(analysis_prompt)
    
    # Save analysis
    analysis_file = f"{DATA_PATH}conversation_analysis_{agent_id}.md"
    with open(analysis_file, "w", encoding="utf-8") as f:
        f.write(analysis_result)
    
    return {"message": "Analysis complete", "analysis": analysis_result}

@app.post("/api/analyse")
async def analyse():
    """Legacy endpoint - triggers the interview analysis."""
    context = load_interviewer_context()
    analysis_result = analyse_interview(context)
    save_analysis(analysis_result)
    return {"message": "Analysis complete", "analysis": analysis_result}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: int, 
    is_audio: str, 
    agent_id: str = "sdr",
    voice_name: str = None,
    language_code: str = None
):
    """Client websocket endpoint"""
    # Wait for client connection
    await websocket.accept()
    print(f"Client #{user_id} connected, audio mode: {is_audio}, agent: {agent_id}, voice: {voice_name}, language: {language_code}")

    # Start agent session
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(
        user_id_str, is_audio == "true", agent_id, voice_name, language_code
    )

    # Start tasks
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # Wait until the websocket is disconnected or an error occurs
    tasks = [agent_to_client_task, client_to_agent_task]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    for task in pending:
        task.cancel()

    for task in done:
        try:
            task.result()
        except WebSocketDisconnect:
            break
        except Exception as e:
            print(f"Task finished with unexpected exception: {e}")


    # Close LiveRequestQueue
    live_request_queue.close()

    # Disconnected
    print(f"Client #{user_id} disconnected")


app.include_router(documents.router)
app.include_router(api_key.router)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()