# Demo Skylos AI

Demo de agentes conversacionales con voz. Dos agentes: uno para ventas (SDR) y otro para soporte al cliente.

## Qué hace

Hablas por voz con un agente de IA que simula ser:
- **SDR**: Te vende algo, califica leads, hace preguntas de ventas
- **Customer Service**: Te ayuda con problemas técnicos, da soporte

Los agentes toman notas automáticamente y al final puedes ver si cumplieron sus objetivos.

## Cómo ejecutar

Necesitas Python, Node.js y una API key de Gemini.

```bash
# Backend
uv sync
cp .env.example .env
# Edita .env y pon tu GEMINI_API_KEY
uv run python api/main.py

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

Abre http://localhost:8000

## Cómo usar

1. Pon tu API key de Gemini en el sidebar
2. Elige agente (SDR o Customer Service)
3. Dale a "Iniciar Demo" y habla
4. Cuando termines, dale a "Analizar Demo" para ver qué tal lo hizo

## Qué evalúa

El agente SDR intenta conseguir info sobre:
- Tu empresa y qué hace
- Qué problemas tienes
- Presupuesto y timeline
- Quién toma decisiones

El agente de Customer Service intenta:
- Entender tu problema
- Darte una solución
- Asegurarse de que funciona

## Estructura del código

```
api/          # Backend FastAPI
frontend/     # Vue.js con Vuetify
core/         # Lógica de los agentes
default_context/  # Templates y contexto
```

Los agentes están en `core/agents/config.py`. El contexto (como el perfil de empresa falso) está en `default_context/`.

## Notas técnicas

- Usa Gemini Live para las conversaciones por voz
- Toma notas automáticamente durante la charla
- Al final analiza si cumplió los objetivos
- Todo en español
- 30 voces diferentes disponibles