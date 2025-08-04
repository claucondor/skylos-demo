<template>
  <v-card class="voice-settings mb-4" elevation="1">
    <v-card-title class="text-h6 pb-2">
      <v-icon class="mr-2">mdi-account-voice</v-icon>
      Configuración de Voz
    </v-card-title>
    
    <v-card-text>
      <v-row v-if="selectedAgent">
        <v-col cols="12" md="6">
          <v-select
            v-model="selectedVoice"
            :items="availableVoices"
            item-title="label"
            item-value="value"
            label="Voz del Agente"
            outlined
            dense
            @update:modelValue="updateVoice"
          >
            <template v-slot:prepend-inner>
              <v-icon>mdi-microphone</v-icon>
            </template>
          </v-select>
        </v-col>
        
        <v-col cols="12" md="6">
          <v-select
            v-model="selectedLanguage"
            :items="availableLanguages"
            item-title="label"
            item-value="value"
            label="Idioma"
            outlined
            dense
            @update:modelValue="updateLanguage"
          >
            <template v-slot:prepend-inner>
              <v-icon>mdi-translate</v-icon>
            </template>
          </v-select>
        </v-col>
      </v-row>
      
      <v-row v-if="selectedAgent">
        <v-col cols="12">
          <v-chip
            :color="selectedAgent.color"
            variant="tonal"
            size="small"
            class="mr-2"
          >
            <v-icon start>mdi-account-voice</v-icon>
            {{ getVoiceDescription(selectedVoice) }}
          </v-chip>
          
          <v-chip
            color="primary"
            variant="tonal"
            size="small"
          >
            <v-icon start>mdi-translate</v-icon>
            {{ getLanguageDescription(selectedLanguage) }}
          </v-chip>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'VoiceSettings',
  props: {
    selectedAgent: {
      type: Object,
      default: null
    }
  },
  emits: ['voice-updated'],
  data() {
    return {
      selectedVoice: 'Aoede',
      selectedLanguage: 'es-ES',
      availableVoices: [
        { label: 'Zephyr - Iluminación', value: 'Zephyr' },
        { label: 'Puck - Animado', value: 'Puck' },
        { label: 'Charon - Informativo', value: 'Charon' },
        { label: 'Kore - Firme', value: 'Kore' },
        { label: 'Fenrir - Excitación', value: 'Fenrir' },
        { label: 'Leda - Joven', value: 'Leda' },
        { label: 'Orus - Firma', value: 'Orus' },
        { label: 'Aoede - Viento', value: 'Aoede' },
        { label: 'Callirrhoe - Desenfadado', value: 'Callirrhoe' },
        { label: 'Autonoe - Brillo', value: 'Autonoe' },
        { label: 'Enceladus - Breathy', value: 'Enceladus' },
        { label: 'Iapetus - Transparente', value: 'Iapetus' },
        { label: 'Umbriel - Agradable', value: 'Umbriel' },
        { label: 'Algieba - Smooth', value: 'Algieba' },
        { label: 'Despina - Smooth', value: 'Despina' },
        { label: 'Erinome - Transparente', value: 'Erinome' },
        { label: 'Algenib - Grasoso', value: 'Algenib' },
        { label: 'Rasalgethi - Informativa', value: 'Rasalgethi' },
        { label: 'Laomedeia - Animada', value: 'Laomedeia' },
        { label: 'Achernar - Suave', value: 'Achernar' },
        { label: 'Alnilam - Firma', value: 'Alnilam' },
        { label: 'Schedar - Par', value: 'Schedar' },
        { label: 'Gacrux - Mayores de edad', value: 'Gacrux' },
        { label: 'Pulcherrima - Reenviar', value: 'Pulcherrima' },
        { label: 'Achird - Amistoso', value: 'Achird' },
        { label: 'Zubenelgenubi - Informal', value: 'Zubenelgenubi' },
        { label: 'Vindemiatrix - Suave', value: 'Vindemiatrix' },
        { label: 'Sadachbia - Lively', value: 'Sadachbia' },
        { label: 'Sadaltager - Conocimiento', value: 'Sadaltager' },
        { label: 'Sulafat - Cálido', value: 'Sulafat' }
      ],
      availableLanguages: [
        { label: 'Español (España)', value: 'es-ES' },
        { label: 'Español (México)', value: 'es-MX' },
        { label: 'Español (Argentina)', value: 'es-AR' },
        { label: 'English (US)', value: 'en-US' },
        { label: 'English (UK)', value: 'en-GB' },
        { label: 'Français', value: 'fr-FR' },
        { label: 'Deutsch', value: 'de-DE' },
        { label: 'Italiano', value: 'it-IT' },
        { label: 'Português (Brasil)', value: 'pt-BR' }
      ]
    }
  },
  watch: {
    selectedAgent: {
      handler(newAgent) {
        if (newAgent) {
          this.selectedVoice = newAgent.voice_name || 'Aoede';
          this.selectedLanguage = newAgent.language_code || 'es-ES';
        }
      },
      immediate: true
    }
  },
  methods: {
    updateVoice() {
      this.emitUpdate();
    },
    updateLanguage() {
      this.emitUpdate();
    },
    emitUpdate() {
      this.$emit('voice-updated', {
        voice_name: this.selectedVoice,
        language_code: this.selectedLanguage
      });
    },
    getVoiceDescription(voiceName) {
      const voice = this.availableVoices.find(v => v.value === voiceName);
      return voice ? voice.label : voiceName;
    },
    getLanguageDescription(languageCode) {
      const language = this.availableLanguages.find(l => l.value === languageCode);
      return language ? language.label : languageCode;
    }
  }
}
</script>

<style scoped>
.voice-settings {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>