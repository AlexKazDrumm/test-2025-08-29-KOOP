<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{ (e: 'close'): void }>()

const startedOnOverlay = ref(false)

function onOverlayMousedown(e: MouseEvent) {
  startedOnOverlay.value = e.target === e.currentTarget
}

function onOverlayClick(e: MouseEvent) {
  const isOverlay = e.target === e.currentTarget
  if (isOverlay && startedOnOverlay.value) {
    const el = e.currentTarget as HTMLElement | null
    el?.blur()
    emit('close')
  }
  startedOnOverlay.value = false
}
</script>

<template>
  <div
    class="overlay"
    tabindex="0"
    @mousedown.self="onOverlayMousedown"
    @click.self="onOverlayClick"
    @keydown.esc="emit('close')"
  >
    <div class="modal">
      <header class="head">
        <slot name="title" />
        <button class="x" @click="emit('close')">✕</button>
      </header>
      <section class="body">
        <slot />
      </section>
      <footer class="foot">
        <slot name="actions" />
      </footer>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.6);
  display: grid;
  place-items: center;
  z-index: 50;
  backdrop-filter: blur(2px);
  padding: 12px;
}
.modal {
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  background: #0f1428;
  border: 1px solid #1f2937;
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #192132;
  font-weight: 800;
}
.body {
  padding: 14px 16px;
  overflow-y: auto;
  overflow-x: hidden;
}
.foot {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 14px 16px;
  border-top: 1px solid #192132;
}
.x {
  appearance: none;
  background: transparent;
  border: 1px solid #374151;
  color: #9ca3af;
  border-radius: 8px;
  padding: 4px 8px;
  cursor: pointer;
}
.x:hover {
  background: #111827;
  color: #e5e7eb;
}
</style>
