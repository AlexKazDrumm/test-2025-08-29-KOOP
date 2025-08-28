<script setup lang="ts">
import { ref, defineProps, defineEmits, computed, watch } from 'vue'
import type { Task, Status } from '@/types'
import TaskCard from './TaskCard.vue'

const props = defineProps<{ title: string; status: Status; tasks: Task[] }>()
const emit = defineEmits<{
  (e: 'drop-task', payload: { id: string; to: Status; index: number }): void
  (e: 'delete-task', id: string): void
  (e: 'edit-task', task: Task): void
}>()

const over = ref(false)
const listRef = ref<HTMLElement | null>(null)

const CHUNK = 30
const visibleCount = ref(CHUNK)
watch(
  () => props.tasks.length,
  (len) => {
    if (visibleCount.value > len) visibleCount.value = Math.max(CHUNK, len)
  }
)
const visibleTasks = computed(() => props.tasks.slice(0, visibleCount.value))

function onScroll() {
  const el = listRef.value
  if (!el) return
  const nearBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 48
  if (nearBottom && visibleCount.value < props.tasks.length) {
    visibleCount.value = Math.min(visibleCount.value + CHUNK, props.tasks.length)
  }
}

const dragOverIndex = ref<number | null>(null)
const markerTop = ref<number | null>(null)

function computeMarkerTop(idx: number) {
  const root = listRef.value
  if (!root) {
    markerTop.value = null
    return
  }
  const cards = Array.from(root.querySelectorAll<HTMLElement>('[data-card]'))
  if (!cards.length) {
    markerTop.value = 0
    return
  }
  if (idx <= 0) {
    markerTop.value = 0
    return
  }
  const lastIdx = Math.min(idx - 1, cards.length - 1)
  const el = cards[lastIdx]
  markerTop.value = el.offsetTop + el.offsetHeight
}

function findIndexByY(y: number): number {
  const root = listRef.value
  if (!root) return visibleTasks.value.length
  const cards = Array.from(root.querySelectorAll<HTMLElement>('[data-card]'))
  for (let i = 0; i < cards.length; i++) {
    const r = cards[i].getBoundingClientRect()
    const mid = r.top + r.height / 2
    if (y < mid) return i
  }
  return cards.length
}

function onDragOver(e: DragEvent) {
  e.preventDefault()
  over.value = true
  const idx = findIndexByY(e.clientY)
  dragOverIndex.value = idx
  computeMarkerTop(idx)
}
function onDragLeave() {
  over.value = false
  dragOverIndex.value = null
  markerTop.value = null
}
function onDrop(e: DragEvent) {
  over.value = false
  const id = e.dataTransfer?.getData('text/plain')
  if (!id) return
  const idx = dragOverIndex.value ?? visibleTasks.value.length
  dragOverIndex.value = null
  markerTop.value = null
  emit('drop-task', { id, to: props.status, index: idx })
}
</script>

<template>
  <section
    class="col"
    :data-col="status"
    :data-over="over"
    @dragover.prevent="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
  >
    <header class="col__header">
      {{ title }}
    </header>

    <div ref="listRef" class="col__list" :data-empty="!visibleTasks.length" @scroll="onScroll">
      <div v-if="markerTop !== null" class="drop-marker-abs" :style="{ top: markerTop + 'px' }" />

      <TaskCard
        v-for="t in visibleTasks"
        :key="t.id"
        :task="t"
        data-card
        @delete="(id) => emit('delete-task', id)"
        @edit="(task) => emit('edit-task', task)"
      />

      <div v-if="visibleTasks.length < props.tasks.length" class="tail-hint">
        {{ props.tasks.length - visibleTasks.length }} more…
      </div>
    </div>
  </section>
</template>

<style scoped>
.col {
  background: #0f1428;
  border: 1px solid #1f2937;
  border-radius: 12px;
  padding: 12px;
  transition:
    border-color 0.15s,
    box-shadow 0.15s;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.col[data-over='true'] {
  border-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.15) inset;
}
.col__header {
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 0.02em;
}

.col__list {
  position: relative;
  display: grid;
  gap: 10px;

  flex: 1 1 auto;
  min-height: 0;
  overflow: auto;

  align-content: start;
  align-items: start;
  grid-auto-rows: max-content;

  padding-right: 8px;
  scrollbar-width: thin;
  scrollbar-color: #334155 #0f172a;
}
.col__list::-webkit-scrollbar {
  width: 10px;
}
.col__list::-webkit-scrollbar-track {
  background: #0f172a;
  border-radius: 8px;
}
.col__list::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 8px;
  border: 2px solid #0f172a;
}
.col__list[data-empty='true']::before {
  content: 'Drop tasks here';
  color: #64748b;
  font-size: 12px;
}

.drop-marker-abs {
  position: absolute;
  left: 4px;
  right: 4px;
  height: 0;
  pointer-events: none;
  border-top: 2px dashed #60a5fa;
  filter: drop-shadow(0 0 2px rgba(96, 165, 250, 0.35));
}

.tail-hint {
  text-align: center;
  color: #94a3b8;
  font-size: 12px;
  padding: 6px 0 2px;
}
</style>
