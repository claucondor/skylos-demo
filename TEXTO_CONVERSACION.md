# 📝 Sistema de Texto en la Conversación

El sistema maneja **texto de múltiples formas simultáneas** junto con la voz:

## 🔄 **Flujo de Datos en Tiempo Real**

```
🎤 Usuario habla
    ↓
🤖 Agente procesa (Gemini Live)
    ↓
📢 Respuesta simultánea:
    ├── 🔊 Audio (voz del agente)
    └── 📝 Texto (transcripción automática)
    ↓
💬 StatusWindow (chat en tiempo real)
    ↓
📋 tool_take_notes (notas estructuradas)
    ↓
💾 conversation_notes_{agent_id}.md
```

## 📱 **Componentes de Texto**

### 1. **StatusWindow** - Chat en Tiempo Real
- **Ubicación**: Parte inferior de la interfaz
- **Función**: Muestra mensajes como WhatsApp
- **Contenido**: 
  - Transcripción automática del agente
  - Mensajes del sistema
  - Estados de conexión
- **Estilo**: Burbujas de chat con scroll automático

### 2. **InterviewNotesWindow** - Notas Estructuradas
- **Ubicación**: Panel central
- **Función**: Notas formales de la conversación
- **Contenido**:
  - Intercambios importantes guardados por el agente
  - Formato markdown con timestamps
  - Actualización cada 3 segundos
- **Archivos**: `conversation_notes_sdr.md`, `conversation_notes_cs.md`

### 3. **Análisis de Conversación**
- **Función**: Análisis post-conversación
- **Contenido**: Evaluación de objetivos cumplidos
- **Formato**: Markdown estructurado
- **Archivo**: `conversation_analysis_{agent_id}.md`

## 📂 **Archivos de Texto Generados**

### Durante la Conversación:
```
default_context/
├── conversation_notes_sdr.md      # Notas del SDR Agent
├── conversation_notes_cs.md       # Notas del Customer Service Agent
└── lead_profile.md                # Perfil del lead
```

### Después del Análisis:
```
default_context/
├── conversation_analysis_sdr.md   # Análisis SDR
├── conversation_analysis_cs.md    # Análisis Customer Service
└── interview_analysis.md          # Análisis legacy
```

## 🎯 **Ejemplo de Contenido de Texto**

### StatusWindow (Tiempo Real):
```
Sistema: Conectado con Agente SDR. Puedes comenzar a hablar.
Agente: Hola, soy Elena de Skylos AI. ¿Podrías darme tu nombre y empresa?
Sistema: Conversación en progreso...
Agente: Perfecto María, cuéntame sobre los desafíos de TechCorp...
```

### Notas Estructuradas:
```markdown
# Notas de Conversación - SDR

## 2025-01-31 14:30:15

**Agente (Elena)**: Hola, soy Elena de Skylos AI...
**Lead (María)**: Hola Elena, soy María González...

## 2025-01-31 14:31:22

**Agente (Elena)**: ¿Cuál es el mayor desafío operacional?
**Lead (María)**: Nuestro tiempo de respuesta es de 4-6 horas...
```

### Análisis Final:
```markdown
# Análisis de Conversación - SDR Agent

## Objetivos Cumplidos

✅ **Información empresarial**: TechCorp Solutions, 150 empleados
✅ **Desafíos actuales**: Tiempo de respuesta 4-6 horas, 200 consultas/día
✅ **Presupuesto**: €50,000-€100,000 anuales
⚠️ **Timeline**: Parcialmente identificado...
```

## 🔧 **Configuración Técnica**

### WebSocket Messages:
```javascript
// Audio + Texto simultáneo
{
  "mime_type": "audio/pcm",
  "data": "base64_audio_data"
}
{
  "mime_type": "text/plain", 
  "data": "Hola, soy Elena de Skylos AI..."
}
```

### Tool de Notas:
```python
async def tool_take_notes(conversation_exchange: str) -> str:
    # Guarda intercambios importantes en markdown
    # Archivo: conversation_notes_{agent_id}.md
```

## ✅ **Ventajas del Sistema Híbrido**

1. **Accesibilidad**: Texto para usuarios con problemas auditivos
2. **Registro**: Historial completo de la conversación
3. **Análisis**: Datos estructurados para evaluación
4. **Debugging**: Logs detallados para troubleshooting
5. **Multimodal**: Experiencia rica con audio + texto
6. **Persistencia**: Las conversaciones se guardan automáticamente

## 🎮 **Cómo Verlo en Acción**

1. **Inicia una conversación** → Ve el texto aparecer en StatusWindow
2. **Habla con el agente** → Observa la transcripción en tiempo real
3. **Revisa las notas** → Panel de notas se actualiza automáticamente
4. **Analiza la conversación** → Genera reporte de texto estructurado

¡El sistema es completamente híbrido: **voz para la experiencia natural + texto para el registro y análisis**!