<template>
  <div class="conversation-notes-window">
    <v-card>
      <v-card-title class="font-weight-bold">
        {{ selectedAgent ? `Notas - ${selectedAgent.name}` : 'Notas de Conversación' }}
      </v-card-title>
      <v-card-text>
        <div v-html="renderedMarkdown"></div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn icon @click="resetNotes">
          <v-icon>mdi-restore</v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it';

export default {
  name: 'InterviewNotesWindow',
  data() {
    return {
      notes: '',
      intervalId: null,
      md: new MarkdownIt(),
    };
  },
  computed: {
    renderedMarkdown() {
      return this.md.render(this.notes);
    }
  },
  props: {
    selectedAgent: {
      type: Object,
      default: null
    }
  },
  methods: {
    async fetchNotes() {
      if (!this.selectedAgent) {
        this.notes = '# Selecciona un agente para ver las notas.';
        return;
      }
      
      try {
        const notesFile = `conversation_notes_${this.selectedAgent.id}`;
        const response = await fetch(`/api/documents/${notesFile}`);
        if (response.ok) {
          const data = await response.json();
          this.notes = data.content;
        } else {
          this.notes = `# Notas de Conversación - ${this.selectedAgent.name}\n\n*No hay notas disponibles aún. Las notas aparecerán aquí durante la conversación.*`;
        }
      } catch (error) {
        console.error('Error fetching conversation notes:', error);
        this.notes = '# Error cargando notas.';
      }
    },
    async saveNotes() {
      try {
        await fetch('/api/documents/interview_note', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: this.notes }),
        });
      } catch (error) {
        console.error('Error saving interview notes:', error);
      }
    },
    async resetNotes() {
      this.notes = '';
      await this.saveNotes();
    },
  },
  watch: {
    selectedAgent: {
      handler() {
        this.fetchNotes();
      },
      immediate: true
    }
  },
  created() {
    this.fetchNotes();
    this.intervalId = setInterval(this.fetchNotes, 3000);
  },
  beforeUnmount() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  },
};
</script>

<style scoped>
.interview-notes-window {
  margin: 16px 0;
}
</style>
