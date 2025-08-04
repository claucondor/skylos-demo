# 🤖 Demo de Agentes IA - Skylos AI

Una aplicación de demostración profesional para mostrar las capacidades de dos agentes de IA especializados: **SDR Agent** y **Customer Service Agent**.

## 🎯 Agentes Disponibles

### 1. SDR Agent (Sales Development Representative)
- **Especialidad**: Prospección y desarrollo de leads
- **Objetivos**: Calificar leads, identificar oportunidades de negocio, programar demos
- **Metodología**: BANT (Budget, Authority, Need, Timeline)
- **Icono**: 🎯

### 2. Customer Service Agent
- **Especialidad**: Atención al cliente y soporte técnico
- **Objetivos**: Resolver consultas, proporcionar asistencia técnica, asegurar satisfacción
- **Metodología**: Diagnóstico de problemas y resolución paso a paso
- **Icono**: 🎧

## 🚀 Características

- **Conversación por voz en tiempo real** usando Gemini Live
- **Selección de agente** antes de iniciar la conversación
- **Configuración de voz personalizable** (30 voces disponibles)
- **Soporte multiidioma** (español, inglés, francés, alemán, etc.)
- **Perfil de lead predefinido** (TechCorp Solutions)
- **Análisis automático** de objetivos cumplidos
- **Notas de conversación** automáticas
- **Interfaz completamente en español**

## 📋 Estructura del Proyecto

```
├── api/                  # Backend FastAPI
├── frontend/             # Frontend Vue.js
├── core/
│   ├── agents/          # Configuración de agentes
│   ├── interviewer/     # Lógica principal
│   └── analyser/        # Análisis de conversaciones
├── default_context/     # Archivos de contexto
└── tests/              # Tests
```

## 🛠️ Instalación y Uso

### Prerrequisitos
- Python 3.8+
- Node.js 16+
- API Key de Gemini

### Backend
```bash
# Instalar dependencias
uv install

# Configurar API key
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY

# Ejecutar servidor
uv run python api/main.py
```

### Frontend
```bash
cd frontend
npm install
npm run build
```

### Acceso
Abrir http://localhost:8000

## 🎮 Cómo Usar el Demo

1. **Configurar API Key**: En el sidebar, ingresa tu API key de Gemini
2. **Seleccionar Agente**: Elige entre SDR Agent o Customer Service Agent
3. **Configurar Voz**: Selecciona voz e idioma preferidos
4. **Iniciar Demo**: Haz clic en "Iniciar Demo"
5. **Interactuar**: Habla con el agente y experimenta sus capacidades especializadas
6. **Analizar**: Al terminar, haz clic en "Analizar Demo" para ver los resultados

## 📊 Análisis de Objetivos

El sistema evalúa automáticamente si el agente cumplió sus objetivos:

### SDR Agent - Objetivos:
- ✅ Información empresarial
- ✅ Desafíos actuales  
- ✅ Objetivos estratégicos
- ✅ Stakeholders clave
- ✅ Procesos actuales
- ✅ Criterios de éxito
- ✅ Timeline estratégico
- ✅ Oportunidades de valor

### Customer Service Agent - Objetivos:
- ✅ Situación actual
- ✅ Necesidad específica
- ✅ Impacto del problema
- ✅ Soluciones intentadas
- ✅ Urgencia y prioridad
- ✅ Recursos disponibles
- ✅ Expectativas de resolución
- ✅ Feedback y mejoras

## 🔧 Configuración de Agentes

Los agentes se configuran en `core/agents/config.py`:

```python
AgentConfig(
    id="sdr",
    name="Agente SDR",
    description="Especialista en prospección y desarrollo de leads",
    icon="🎯",
    color="#1e40af",
    prompt="...",  # Prompt completo en español
    objectives=[...]  # Lista de objetivos
)
```

## 📁 Archivos de Contexto

- `lead_profile.md`: Perfil del lead (TechCorp Solutions)
- `conversation_notes_sdr.md`: Notas del SDR Agent
- `conversation_notes_cs.md`: Notas del Customer Service Agent
- `conversation_analysis_[agent].md`: Análisis de cada conversación

## 🤖 Modelos de IA

- **Conversaciones**: `gemini-live-2.5-flash-preview`
- **Análisis**: `gemini-2.5-flash`
- **Verificación API**: `gemini-2.5-flash`

## 🎙️ Configuración de Voz

### Voces Disponibles (30 opciones)
- **Kore** (Firme) - Recomendada para SDR Agent
- **Leda** (Joven) - Recomendada para Customer Service Agent
- **Zephyr** (Iluminación), **Puck** (Animado), **Charon** (Informativo)
- **Aoede** (Viento), **Fenrir** (Excitación), **Orus** (Firma)
- Y 24 voces adicionales con diferentes características

### Idiomas Soportados
- **es-ES** (Español España) - Por defecto
- **es-MX** (Español México)
- **es-AR** (Español Argentina)
- **en-US** (Inglés Estados Unidos)
- **en-GB** (Inglés Reino Unido)
- **fr-FR** (Francés), **de-DE** (Alemán), **it-IT** (Italiano)
- **pt-BR** (Portugués Brasil)

## 📝 Notas Técnicas

- El sistema toma notas automáticamente usando `tool_take_notes`
- Cada agente tiene su archivo de notas separado
- El análisis evalúa el cumplimiento de objetivos específicos por agente
- La interfaz está completamente en español
- Soporte para audio en tiempo real con visualización

## 🎯 Casos de Uso

### Demo SDR Agent
Demuestra capacidades de prospección y desarrollo de leads:
- Califica leads usando metodología BANT
- Identifica necesidades y desafíos empresariales
- Presenta propuestas de valor personalizadas
- Programa demos para leads calificados

### Demo Customer Service Agent  
Demuestra capacidades de atención al cliente y soporte:
- Diagnostica problemas técnicos del cliente
- Proporciona soluciones paso a paso
- Maneja objeciones y preocupaciones
- Asegura resolución completa y satisfacción

## 🔄 Flujo de Trabajo

1. **Selección** → Elegir agente apropiado
2. **Conexión** → Establecer WebSocket con agente
3. **Conversación** → Interacción por voz en tiempo real
4. **Notas** → Registro automático de intercambios
5. **Análisis** → Evaluación de objetivos cumplidos
6. **Reporte** → Visualización de resultados

¡Perfecto para demostrar capacidades de IA conversacional en ventas y soporte!