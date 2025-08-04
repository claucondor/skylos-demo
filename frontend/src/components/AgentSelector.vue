<template>
  <v-card class="agent-selector" elevation="2">
    <v-card-title class="text-h6 pb-2">
      <v-icon class="mr-2">mdi-robot</v-icon>
      Seleccionar Agente
    </v-card-title>
    
    <v-card-text>
      <v-row>
        <v-col 
          v-for="agent in agents" 
          :key="agent.id" 
          cols="12" 
          md="6"
        >
          <v-card
            :class="['agent-card', { 'selected': selectedAgent?.id === agent.id }]"
            :style="{ borderColor: agent.color }"
            @click="selectAgent(agent)"
            elevation="1"
            hover
          >
            <v-card-text class="text-center pa-4">
              <div class="agent-icon mb-2" :style="{ color: agent.color }">
                {{ agent.icon }}
              </div>
              <h3 class="agent-name mb-1">{{ agent.name }}</h3>
              <p class="agent-description text-body-2 text-medium-emphasis">
                {{ agent.description }}
              </p>
              
              <!-- Voice info -->
              <div class="mt-2">
                <v-chip
                  size="x-small"
                  variant="outlined"
                  class="mr-1 mb-1"
                >
                  <v-icon start size="x-small">mdi-account-voice</v-icon>
                  {{ agent.voice_name }}
                </v-chip>
                <v-chip
                  size="x-small"
                  variant="outlined"
                  class="mb-1"
                >
                  <v-icon start size="x-small">mdi-translate</v-icon>
                  {{ agent.language_code }}
                </v-chip>
              </div>
              
              <v-chip
                v-if="selectedAgent?.id === agent.id"
                color="success"
                size="small"
                class="mt-2"
              >
                <v-icon start>mdi-check</v-icon>
                Seleccionado
              </v-chip>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <v-divider class="my-4"></v-divider>
      
      <div v-if="selectedAgent" class="selected-agent-info">
        <v-alert
          type="info"
          variant="tonal"
          class="mt-3"
          density="compact"
        >
          <template v-slot:prepend>
            <v-icon>mdi-phone</v-icon>
          </template>
          El agente se presentará y comenzará la conversación de forma natural, como en una llamada real.
        </v-alert>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'AgentSelector',
  props: {
    selectedAgent: {
      type: Object,
      default: null
    }
  },
  emits: ['agent-selected'],
  data() {
    return {
      agents: []
    }
  },
  async mounted() {
    await this.loadAgents()
  },
  methods: {
    async loadAgents() {
      try {
        const response = await fetch('/api/agents')
        const data = await response.json()
        this.agents = data.agents
        
        // Auto-select first agent if none selected
        if (!this.selectedAgent && this.agents.length > 0) {
          this.selectAgent(this.agents[0])
        }
      } catch (error) {
        console.error('Error loading agents:', error)
      }
    },
    selectAgent(agent) {
      this.$emit('agent-selected', agent)
    }
  }
}
</script>

<style scoped>
.agent-selector {
  margin-bottom: 20px;
}

.agent-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

.agent-card.selected {
  border-width: 2px;
  border-style: solid;
}

.agent-icon {
  font-size: 2.5rem;
  line-height: 1;
}

.agent-name {
  color: rgba(0,0,0,0.87);
  font-weight: 500;
}

.agent-description {
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.selected-agent-info {
  background-color: rgba(0,0,0,0.02);
  border-radius: 8px;
  padding: 16px;
}
</style>