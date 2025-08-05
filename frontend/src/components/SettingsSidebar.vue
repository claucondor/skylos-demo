<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    app
    :width="drawerWidth"
    class="resizable-drawer"
  >
    <div class="drag-handle" @mousedown="startResize"></div>
    <v-list-item title="Configuración del Demo" subtitle="Skylos AI" class="font-weight-bold">
      <template v-slot:append>
        <v-switch
          :model-value="isDarkTheme"
          hide-details
          inset
          label="Modo Oscuro"
          @update:modelValue="$emit('toggle-theme')"
        ></v-switch>
      </template>
    </v-list-item>
    <v-divider></v-divider>
    
    <!-- API Status -->
    <v-container>
      <v-alert
        :type="apiKeyStatus.type"
        :text="apiKeyStatus.message"
        variant="tonal"
        class="mb-4"
      >
        <template v-slot:prepend>
          <v-icon>{{ apiKeyStatus.icon }}</v-icon>
        </template>
      </v-alert>
    </v-container>
    
    <v-divider></v-divider>
    
    <!-- Demo Info section removed -->
    
    <v-container>
      <v-card variant="outlined">
        <v-card-title class="text-h6">
          <v-icon class="mr-2">mdi-help-circle</v-icon>
          Instrucciones
        </v-card-title>
        <v-card-text>
          <ol class="text-body-2">
            <li class="mb-2">Selecciona un agente (SDR o Customer Service)</li>
            <li class="mb-2">Configura la voz si lo deseas</li>
            <li class="mb-2">Haz clic en "Iniciar Demo"</li>
            <li class="mb-2">Habla con el agente como si fueras el lead</li>
            <li>Analiza los resultados al finalizar</li>
          </ol>
        </v-card-text>
      </v-card>
    </v-container>
  </v-navigation-drawer>
</template>

<script>
export default {
  name: "SettingsSidebar",
  props: {
    modelValue: Boolean,
    isDarkTheme: Boolean,
  },
  emits: ["update:modelValue", "toggle-theme", "api-key-updated"],
  data() {
    return {
      drawerWidth: 400, // Reduced width for cleaner demo
      apiKeyStatus: {
        type: 'info',
        message: 'Verificando configuración de API...',
        icon: 'mdi-loading'
      }
    };
  },
  methods: {
    startResize(event) {
      event.preventDefault();
      document.addEventListener("mousemove", this.doResize);
      document.addEventListener("mouseup", this.stopResize);
    },
    doResize(event) {
      this.drawerWidth = Math.max(300, Math.min(600, event.clientX));
    },
    stopResize() {
      document.removeEventListener("mousemove", this.doResize);
      document.removeEventListener("mouseup", this.stopResize);
    },
    async checkApiKeyStatus() {
      try {
        // Check if API key is configured on the server
        const response = await fetch('/api/api_key_status');
        const result = await response.json();
        
        if (result.configured) {
          this.apiKeyStatus = {
            type: 'success',
            message: 'API Key configurada correctamente',
            icon: 'mdi-check-circle'
          };
          this.$emit('api-key-updated', true);
        } else {
          this.apiKeyStatus = {
            type: 'warning',
            message: 'API Key no configurada. Verifica el archivo .env',
            icon: 'mdi-alert-circle'
          };
          this.$emit('api-key-updated', false);
        }
      } catch (error) {
        this.apiKeyStatus = {
          type: 'error',
          message: 'Error verificando configuración de API',
          icon: 'mdi-close-circle'
        };
        this.$emit('api-key-updated', false);
      }
    },
    async fetchDocument(docName) {
      try {
        const response = await fetch(`/api/documents/${docName}`);
        const data = await response.json();
        if (response.ok) {
          return data.content;
        } else {
          return `Error: ${data.error}`;
        }
      } catch (error) {
        console.error(error);
        return 'Error fetching document.';
      }
    },

  },
  mounted() {
    this.checkApiKeyStatus();
  },
};
</script>

<style scoped>
.resizable-drawer {
  position: relative;
}

.drag-handle {
  position: absolute;
  top: 0;
  right: -5px;
  width: 10px;
  height: 100%;
  cursor: col-resize;
  z-index: 10;
}

.fancy-btn {
  background: linear-gradient(45deg, #972408 30%, #fa9256 90%);
  color: white !important;
  box-shadow: 0 3px 5px 2px rgba(255, 105, 135, .3);
}
</style>