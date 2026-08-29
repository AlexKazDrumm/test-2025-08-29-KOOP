<script setup lang="ts"></script>

<template>
  <main class="shell">
    <header class="app-header">
      <h1>Kanban board</h1>
    </header>

    <section class="app-main">
      <KanbanBoard />
    </section>

    <footer class="app-footer">
      <p class="stack">FastAPI + PostgreSQL + WebSocket · Vue 3 + TS · drag-and-drop</p>
    </footer>
  </main>
</template>

<script lang="ts">
import KanbanBoard from './components/KanbanBoard.vue'
export default { components: { KanbanBoard } }
</script>

<style scoped>
.shell {
  height: 100vh;
  min-height: 100vh;
  box-sizing: border-box;

  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 12px;

  max-width: 1100px;
  margin: 0 auto;
  padding: 12px 16px;
}

.app-main {
  min-height: 0;
  overflow: hidden;
}

h1 {
  margin: 8px 0 0 0;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 0.02em;
}
.stack {
  margin: 0;
  color: #9ca3af;
  font-size: 12px;
}
</style>
