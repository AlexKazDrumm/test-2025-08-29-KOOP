<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import type { Task, Priority } from '@/types'
import Modal from './Modal.vue'

const props = defineProps<{ open: boolean; task?: Task | null }>()
const emit = defineEmits<{
  (e: 'close'): void
  (
    e: 'submit',
    payload: { title: string; description: string; priority: Priority; id?: string }
  ): void
}>()

const title = ref(''),
  description = ref(''),
  priority = ref<Priority>('normal')

watch(
  () => props.task,
  (t) => {
    title.value = t?.title ?? ''
    description.value = t?.description ?? ''
    priority.value = t?.priority ?? 'normal'
  },
  { immediate: true }
)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen && !props.task) {
      title.value = ''
      description.value = ''
      priority.value = 'normal'
    }
  }
)

function submit() {
  if (!title.value.trim()) return
  emit('submit', {
    id: props.task?.id,
    title: title.value.trim(),
    description: description.value.trim(),
    priority: priority.value,
  })
}
</script>

<template>
  <Modal v-if="open" @close="emit('close')">
    <template #title>
      <div>{{ props.task ? 'Edit task' : 'New task' }}</div>
    </template>
    <div class="grid">
      <label>
        <span>Title</span>
        <input v-model="title" type="text" required />
      </label>
      <label>
        <span>Description</span>
        <textarea v-model="description" rows="4" />
      </label>
      <label>
        <span>Priority</span>
        <select v-model="priority">
          <option value="low">Low</option>
          <option value="normal">Normal</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </label>
    </div>
    <template #actions>
      <button class="btn ghost" @click="emit('close')">Cancel</button>
      <button class="btn primary" @click="submit">
        {{ props.task ? 'Save' : 'Create' }}
      </button>
    </template>
  </Modal>
</template>

<style scoped>
.grid {
  display: grid;
  gap: 12px;
  overflow-wrap: anywhere;
}
label {
  display: grid;
  gap: 6px;
  min-width: 0;
}

input,
textarea,
select {
  display: block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  background: #0b1020;
  color: #e5e7eb;
  border: 1px solid #293142;
  border-radius: 10px;
  padding: 10px;
}
textarea {
  resize: vertical;
}

.btn {
  appearance: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid #374151;
}
.btn.ghost {
  background: transparent;
  color: #9ca3af;
}
.btn.ghost:hover {
  background: #111827;
  color: #e5e7eb;
}
.btn.primary {
  background: #10b981;
  color: #052014;
  border-color: #065f46;
}
.btn.primary:hover {
  filter: brightness(1.05);
}
</style>
