<template>
  <v-app>
    <settings-sidebar
      v-model="showSettings"
      :is-dark-theme="isDarkTheme"
      @toggle-theme="toggleTheme"
      @api-key-updated="updateApiKeyStatus"
    />

    <v-app-bar app>
      <v-app-bar-nav-icon @click.stop="showSettings = !showSettings"></v-app-bar-nav-icon>
      <v-toolbar-title>🤖 Demo de Agentes IA - Skylos AI</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container fluid class="fill-height pa-4">
        <v-row class="fill-height">
          <v-col :cols="analysisCompleted ? 6 : 12" class="d-flex flex-column">
            <!-- Agent Selection -->
            <agent-selector
              :selected-agent="selectedAgent"
              @agent-selected="onAgentSelected"
              class="mb-4"
            />
            
            <!-- Voice Settings -->
            <voice-settings
              :selected-agent="selectedAgent"
              @voice-updated="onVoiceUpdated"
            />
            
            <v-card class="flex-grow-1 d-flex flex-column">
              <v-card-text class="flex-grow-1 d-flex flex-column">
                <agent-profile
                  :analyser-node="analyserNode"
                  :conversation-started="conversationStarted"
                  :selected-agent="selectedAgent"
                />
                <objectives-tracker 
                  ref="objectivesTracker" 
                  :selected-agent="selectedAgent"
                  :conversation-started="conversationStarted"
                />
              </v-card-text>
              <v-card-actions class="d-flex flex-column align-center justify-center">
                <control-buttons
                  :conversation-started="conversationStarted"
                  :conversation-finished="conversationFinished"
                  :is-connecting="isConnecting"
                  :is-analysing="isAnalysing"
                  :is-api-key-set="isApiKeySet"
                  :selected-agent="selectedAgent"
                  @toggle-conversation="toggleConversation"
                  @analyse="analyseConversation"
                />
                <status-window :messages="messages" class="flex-grow-1" />
              </v-card-actions>
            </v-card>
          </v-col>
          <v-col v-if="analysisCompleted" cols="6" class="d-flex flex-column">
            <conversation-analysis-viewer :content="analysisContent" />
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { useTheme } from 'vuetify';
import AgentProfile from './components/AgentProfile.vue';
import StatusWindow from './components/StatusWindow.vue';
import ControlButtons from './components/ControlButtons.vue';
import SettingsSidebar from './components/SettingsSidebar.vue';
import ObjectivesTracker from './components/ObjectivesTracker.vue';
import ConversationAnalysisViewer from "./components/ConversationAnalysisViewer.vue";
import AgentSelector from './components/AgentSelector.vue';
import VoiceSettings from './components/VoiceSettings.vue';
import { useAudio } from './composables/useAudio';
import { useAgentWebSocket } from './composables/useAgentWebSocket';

// --- Reactive State ---

// Theme
const theme = useTheme();
const isDarkTheme = ref(theme.global.current.value.dark);

// Component State
const showSettings = ref(true);
const isApiKeySet = ref(false);
const isAnalysing = ref(false);
const analysisCompleted = ref(false);
const analysisContent = ref('');
const objectivesTracker = ref(null); // for the ref in the template
const selectedAgent = ref(null);
const voiceConfig = ref({ voice_name: 'Aoede', language_code: 'es-ES' });

// Composables
const audioWebsocket = ref(null);
const {
  analyserNode,
  startAudio,
  stopAudio,
  playAudio,
  stopPlayback,
} = useAudio(audioWebsocket);

const {
  websocket,
  messages,
  isConnecting,
  conversationStarted,
  conversationFinished,
  connect,
  disconnect,
} = useAgentWebSocket(playAudio, stopPlayback, selectedAgent, voiceConfig);

// --- Watchers ---

watch(websocket, (newWebsocketInstance) => {
  audioWebsocket.value = newWebsocketInstance;
});

// --- Functions ---

const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark';
  isDarkTheme.value = theme.global.current.value.dark;
};

function onAnalysisComplete(analysis) {
  analysisContent.value = analysis;
  analysisCompleted.value = true;
}

function onAgentSelected(agent) {
  selectedAgent.value = agent;
  // Update voice config with agent defaults
  if (agent) {
    voiceConfig.value = {
      voice_name: agent.voice_name || 'Aoede',
      language_code: agent.language_code || 'es-ES'
    };
  }
  // Reset analysis when agent changes
  analysisCompleted.value = false;
  analysisContent.value = '';
}

function onVoiceUpdated(newVoiceConfig) {
  voiceConfig.value = newVoiceConfig;
}

async function analyseConversation() {
  if (!selectedAgent.value) {
    console.error('No agent selected');
    return;
  }
  
  isAnalysing.value = true;
  try {
    // First, trigger the objectives analysis to update the tracker
    if (objectivesTracker.value && objectivesTracker.value.triggerAnalysis) {
      await objectivesTracker.value.triggerAnalysis();
    }
    
    // Then do the full conversation analysis
    const response = await fetch(`/api/analyse/${selectedAgent.value.id}`, { method: 'POST' });
    if (response.ok) {
      const data = await response.json();
      onAnalysisComplete(data.analysis);
    } else {
      console.error('Error analysing conversation:', response.statusText);
    }
  } catch (error) {
    console.error('Error analysing conversation:', error);
  } finally {
    isAnalysing.value = false;
    conversationFinished.value = false; // Ready for a new conversation
  }
}

function updateApiKeyStatus() {
  setApiKey();
}

async function toggleConversation() {
  if (conversationStarted.value) {
    stopConversation();
  } else {
    await startConversation();
  }
}

async function startConversation() {
  analysisCompleted.value = false;
  analysisContent.value = '';
  try {
    await startAudio();
    connect();
  } catch (error) {
    console.error('Error starting conversation:', error);
    messages.value.push({ id: Date.now(), sender: 'system', text: 'Error accessing microphone. Please grant permission and try again.' });
    stopAudio();
  }
}

function stopConversation() {
  stopAudio();
  disconnect();
}

async function setApiKey() {
  try {
    // Check if API key is configured on server
    const response = await fetch('/api/api_key_status');
    const data = await response.json();
    isApiKeySet.value = data.configured;
    
    if (data.configured) {
      console.log('API key configured from environment');
    } else {
      console.warn('API key not configured in environment');
    }
  } catch (error) {
    isApiKeySet.value = false;
    console.error('Error checking API key status:', error);
  }
}

// --- Lifecycle Hooks ---

onMounted(() => {
  setApiKey();
});

onBeforeUnmount(() => {
  stopConversation();
});
</script>

<style>
body {
  font-family: 'Inter', sans-serif;
}

.v-app-bar-title {
  font-weight: 600;
}

pre {
  white-space: pre-wrap;
  font-family: inherit;
}
</style>
