import { ref } from 'vue';

export function useAgentWebSocket(playAudio, stopPlayback, selectedAgent, voiceConfig) {
  const websocket = ref(null);
  const messages = ref([]);
  const isConnecting = ref(false);
  const conversationStarted = ref(false);
  const conversationFinished = ref(false);
  const currentMessageId = ref(null);

  const connect = () => {
    if (!selectedAgent.value) {
      console.error('No agent selected');
      messages.value.push({ id: Date.now(), sender: 'system', text: 'Error: No agent selected. Please select an agent first.' });
      return;
    }

    isConnecting.value = true;
    conversationFinished.value = false;
    currentMessageId.value = null;

    const userId = Math.floor(Math.random() * 1000);
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const voiceParams = voiceConfig.value ? 
      `&voice_name=${voiceConfig.value.voice_name}&language_code=${voiceConfig.value.language_code}` : '';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/${userId}?is_audio=true&agent_id=${selectedAgent.value.id}${voiceParams}`;
    
    websocket.value = new WebSocket(wsUrl);

    websocket.value.onopen = () => {
      console.log('WebSocket connection established');
      messages.value.push({ id: Date.now(), sender: 'system', text: `Conectado con ${selectedAgent.value.name}. Puedes comenzar a hablar.` });
      conversationStarted.value = true;
      isConnecting.value = false;
    };

    websocket.value.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("[AGENT TO CLIENT] ", message);

      if (message.turn_complete) {
        currentMessageId.value = null;
        return;
      }

      if (message.interrupted) {
        if (stopPlayback) stopPlayback();
        return;
      }

      if (message.mime_type === 'audio/pcm' && message.data) {
        if (playAudio) playAudio(message.data);
      }

      if (message.mime_type === 'text/plain') {
        if (currentMessageId.value === null) {
          currentMessageId.value = `msg-${Date.now()}`;
          messages.value.push({ id: currentMessageId.value, sender: 'agent', text: message.data });
        } else {
          const msg = messages.value.find(m => m.id === currentMessageId.value);
          if (msg) {
            msg.text += message.data;
          }
        }
      }
    };

    websocket.value.onclose = () => {
      console.log('WebSocket connection closed');
      messages.value.push({ id: Date.now(), sender: 'system', text: 'Connection closed.' });
      conversationStarted.value = false;
      isConnecting.value = false;
    };

    websocket.value.onerror = (error) => {
      console.error('WebSocket error:', error);
      messages.value.push({ id: Date.now(), sender: 'system', text: 'Connection error.' });
      conversationStarted.value = false;
      isConnecting.value = false;
    };
  };

  const disconnect = () => {
    if (websocket.value && websocket.value.readyState < 2) { // OPEN or CONNECTING
      websocket.value.close();
    }
    conversationStarted.value = false;
    isConnecting.value = false;
    conversationFinished.value = true;
  };

  return {
    websocket,
    messages,
    isConnecting,
    conversationStarted,
    conversationFinished,
    connect,
    disconnect,
  };
}
