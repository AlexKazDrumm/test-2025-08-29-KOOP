<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue'
import type { Task } from '@/types'
const props = defineProps<{ task: Task }>()
const emit = defineEmits<{ (e: 'delete', id: string): void; (e: 'edit', task: Task): void }>()
const dragging = ref(false)
function onDragStart(e: DragEvent) {
  dragging.value = true
  e.dataTransfer?.setData('text/plain', props.task.id)
}
function onDragEnd() {
  dragging.value = false
}
</script>

<template>
  <article
    class="card"
    :data-dragging="dragging"
    draggable="true"
    @dragstart="onDragStart"
    @dragend="onDragEnd"
    @dblclick="emit('edit', props.task)"
  >
    <div class="top">
      <span class="badge" :data-p="props.task.priority">{{ props.task.priority }}</span>
      <button class="btn" title="View" @click.stop="emit('edit', props.task)">👁</button>
      <button class="btn" title="Delete" @click.stop="emit('delete', props.task.id)">✕</button>
    </div>
    <h3 class="title">
      {{ props.task.title }}
    </h3>
    <p class="desc">
      {{ props.task.description }}
    </p>
  </article>
</template>

<style scoped>
:root {
}
.card {
  --card-h: 128px;
  background: #0b1020;
  border: 1px solid #293142;
  border-radius: 12px;
  padding: 10px;
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 6px;
  height: var(--card-h);
  box-sizing: border-box;
  overflow: hidden;
  transition: opacity 0.12s;
  cursor: grab;
}
.card[data-dragging='true'] {
  opacity: 0.6;
  cursor: grabbing;
}

.top {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: flex-end;
  min-height: 24px;
  margin-top: -2px;
}

.title {
  margin: 0;
  font-weight: 800;
  font-size: 15px;
  line-height: 1.3;
  color: #e5e7eb;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.desc {
  margin: 0;
  color: #c4c7ce;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  word-break: break-word;
  overflow-wrap: anywhere;
  white-space: normal;
}

.btn {
  appearance: none;
  background: transparent;
  color: #9ca3af;
  border: 1px solid #374151;
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
}
.btn:hover {
  background: #111827;
  color: #e5e7eb;
}

.badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid #374151;
  text-transform: capitalize;
  margin-right: auto;
}
.badge[data-p='low'] {
  background: #0b1f14;
  border-color: #1b4d2e;
}
.badge[data-p='normal'] {
  background: #0b1620;
  border-color: #2a3d58;
}
.badge[data-p='high'] {
  background: #21140b;
  border-color: #6a3b12;
}
.badge[data-p='urgent'] {
  background: #2a0b0b;
  border-color: #7a1f1f;
}
</style>
