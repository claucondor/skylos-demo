<template>
  <div class="objectives-tracker">
    <v-card>
      <v-card-title class="font-weight-bold d-flex align-center">
        <v-icon class="mr-2" :color="selectedAgent?.color">mdi-target</v-icon>
        {{ selectedAgent ? `Objetivos - ${selectedAgent.name}` : 'Objetivos del Agente' }}
        <v-spacer></v-spacer>
        <v-chip 
          v-if="conversationStarted" 
          color="primary" 
          size="small"
        >
          Demo en progreso
        </v-chip>
      </v-card-title>
      
      <v-card-text>
        <div v-if="!selectedAgent" class="text-center text-medium-emphasis py-8">
          <v-icon size="64" color="grey-lighten-1">mdi-robot-outline</v-icon>
          <p class="mt-4">Selecciona un agente para ver sus objetivos</p>
        </div>
        
        <div v-else-if="!conversationStarted" class="text-center text-medium-emphasis py-4">
          <v-icon size="48" color="grey-lighten-1">mdi-play-circle-outline</v-icon>
          <p class="mt-3 mb-2">Inicia el demo para ver el progreso en tiempo real</p>
          <v-chip size="small" variant="outlined">
            {{ totalObjectives }} objetivos por cumplir
          </v-chip>
        </div>
        
        <v-list v-else density="compact">
          <v-list-item
            v-for="(objective, index) in selectedAgent.objectives"
            :key="objective.id"
            class="mb-2"
          >
            <template v-slot:prepend>
              <v-chip
                size="x-small"
                :color="selectedAgent.color"
                variant="flat"
                class="mr-2"
              >
                {{ index + 1 }}
              </v-chip>
            </template>
            
            <v-list-item-title class="text-body-2">
              {{ objective.label }}
            </v-list-item-title>
            
            <v-list-item-subtitle class="text-caption">
              {{ objective.description }}
            </v-list-item-subtitle>
            
            <template v-slot:append>
              <v-chip
                color="primary"
                size="x-small"
                variant="outlined"
              >
                En progreso
              </v-chip>
            </template>
          </v-list-item>
        </v-list>
        
        <!-- Progress Bar -->
        <v-progress-linear
          v-if="conversationStarted && selectedAgent"
          indeterminate
          color="primary"
          height="8"
          rounded
          class="mt-4"
        ></v-progress-linear>
        
        <v-alert
          v-if="conversationStarted"
          type="info"
          variant="tonal"
          density="compact"
          class="mt-3"
        >
          <template v-slot:prepend>
            <v-icon>mdi-information</v-icon>
          </template>
          El análisis de objetivos se realizará al finalizar el demo.
        </v-alert>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'ObjectivesTracker',
  props: {
    selectedAgent: {
      type: Object,
      default: null
    },
    conversationStarted: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      objectiveStatuses: {}, // { objectiveId: 'pending' | 'in_progress' | 'completed' }
      intervalId: null,
      lastAnalysisTime: 0, // Track when we last analyzed
    };
  },
  computed: {
    objectivesWithStatus() {
      if (!this.selectedAgent?.objectives) return [];
      
      return this.selectedAgent.objectives.map(objective => ({
        ...objective,
        status: this.objectiveStatuses[objective.id] || 'pending'
      }));
    },
    totalObjectives() {
      return this.selectedAgent?.objectives?.length || 0;
    },
    completedObjectives() {
      return Object.values(this.objectiveStatuses).filter(status => status === 'completed').length;
    },
    progressPercentage() {
      if (this.totalObjectives === 0) return 0;
      return (this.completedObjectives / this.totalObjectives) * 100;
    }
  },
  methods: {
    getObjectiveIcon(status) {
      switch (status) {
        case 'completed': return 'mdi-check-circle';
        case 'in_progress': return 'mdi-clock-outline';
        default: return 'mdi-circle-outline';
      }
    },
    getObjectiveColor(status) {
      switch (status) {
        case 'completed': return 'success';
        case 'in_progress': return 'warning';
        default: return 'grey-lighten-1';
      }
    },
    getStatusText(status) {
      switch (status) {
        case 'completed': return 'Completado';
        case 'in_progress': return 'En progreso';
        default: return 'Pendiente';
      }
    },
    getProgressColor() {
      const percentage = this.progressPercentage;
      if (percentage >= 80) return 'success';
      if (percentage >= 50) return 'warning';
      return 'primary';
    },
    async analyzeObjectiveProgress() {
      if (!this.selectedAgent || !this.conversationStarted) return;
      
      // Throttle analysis to avoid API limits
      const now = Date.now();
      if (now - this.lastAnalysisTime < 25000) { // Minimum 25 seconds between analyses
        return;
      }
      
      try {
        const response = await fetch(`/api/objectives_progress/${this.selectedAgent.id}`);
        if (response.ok) {
          const data = await response.json();
          this.objectiveStatuses = data.statuses || {};
          this.lastAnalysisTime = now;
        } else if (response.status === 429) {
          console.warn('API rate limit reached, skipping objective analysis');
          // Don't update statuses on rate limit
        } else {
          console.error('Error fetching objective progress:', response.status);
        }
      } catch (error) {
        console.error('Error fetching objective progress:', error);
      }
    },
    resetObjectives() {
      this.objectiveStatuses = {};
      this.lastAnalysisTime = 0;
    },
    
    // Public method to trigger analysis (called from parent)
    async triggerAnalysis() {
      await this.analyzeObjectiveProgress();
    }
  },
  watch: {
    selectedAgent() {
      this.resetObjectives();
    },
    conversationStarted(newValue) {
      if (newValue) {
        this.resetObjectives();
        // Don't start polling - analysis will be done only at the end
      } else {
        // Stop polling when conversation ends (if any)
        if (this.intervalId) {
          clearInterval(this.intervalId);
          this.intervalId = null;
        }
      }
    }
  },
  beforeUnmount() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  },
};
</script>

<style scoped>
.objectives-tracker {
  margin: 16px 0;
}

.v-list-item {
  border-radius: 8px;
  margin-bottom: 4px;
}

.v-list-item:hover {
  background-color: rgba(0,0,0,0.04);
}
</style>
