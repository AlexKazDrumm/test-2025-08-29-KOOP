<script setup lang="ts">
import { ref } from 'vue'
const title = ref('')
const description = ref('')
const emit = defineEmits<{ (e: 'create', title: string, description: string): void }>()
function submit() {
  const t = title.value.trim()
  if (!t) return
  emit('create', t, description.value.trim())
  title.value = ''
  description.value = ''
}
</script>
<template>
  <form class="new" @submit.prevent="submit">
    <input v-model="title" type="text" placeholder="Task title" required />
    <textarea v-model="description" rows="2" placeholder="Description (optional)" />
    <button type="submit">Add task</button>
  </form>
</template>
<style scoped>
.new {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: start;
}
.new input,
.new textarea {
  width: 100%;
  background: #0b1020;
  color: #e5e7eb;
  border: 1px solid #293142;
  border-radius: 10px;
  padding: 10px;
}
.new button {
  background: #10b981;
  color: #052014;
  border: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}
.new button:hover {
  filter: brightness(1.05);
}
</style>
