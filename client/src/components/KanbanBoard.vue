<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Task, Status, Priority } from '@/types'
import { createTask, deleteTask, updateTask, listTasks, reorderColumns } from '@/api'
import { connect, type ServerEvent } from '@/ws'
import Column from './Column.vue'
import TaskModal from './TaskModal.vue'

const tasks = ref<Task[]>([])
const ws = ref<WebSocket | null>(null)

function sortTasks(a: Task, b: Task) {
  if (a.status !== b.status) return a.status.localeCompare(b.status)
  return a.sort_order - b.sort_order
}
const byStatus = (s: Status) =>
  computed(() =>
    tasks.value.filter((t) => t.status === s).sort((a, b) => a.sort_order - b.sort_order)
  )

function snapshotApply(arr: Task[]) {
  tasks.value = arr.slice().sort(sortTasks)
}

function upsert(task: Task) {
  const i = tasks.value.findIndex((t) => t.id === task.id)
  if (i === -1) tasks.value.push(task)
  else tasks.value[i] = task
  tasks.value = tasks.value.sort(sortTasks)
}

async function bootstrap() {
  tasks.value = (await listTasks()).sort(sortTasks)
  ws.value = connect((ev: ServerEvent) => {
    if (ev.type === 'snapshot') snapshotApply(ev.state.tasks)
    if (ev.type === 'created') upsert(ev.task)
    if (ev.type === 'updated') upsert(ev.task)
    if (ev.type === 'deleted') tasks.value = tasks.value.filter((t) => t.id !== ev.task_id)
  })
}
onMounted(bootstrap)

const modalOpen = ref(false)
const editing = ref<Task | null>(null)
function openCreate() {
  editing.value = null
  modalOpen.value = true
}
function openEdit(task: Task) {
  editing.value = task
  modalOpen.value = true
}
function closeModal() {
  modalOpen.value = false
}

async function submitModal(payload: {
  id?: string
  title: string
  description: string
  priority: Priority
}) {
  if (payload.id) {
    const t = await updateTask(payload.id, {
      title: payload.title,
      description: payload.description,
      priority: payload.priority,
    })
    upsert(t)
  } else {
    const t = await createTask({
      title: payload.title,
      description: payload.description,
      priority: payload.priority,
    })
    upsert(t)
  }
  closeModal()
}

async function handleDelete(id: string) {
  await deleteTask(id)
  tasks.value = tasks.value.filter((t) => t.id !== id)
}

function columnsToPayload() {
  return {
    todo: byStatus('todo').value.map((t) => t.id),
    in_progress: byStatus('in_progress').value.map((t) => t.id),
    done: byStatus('done').value.map((t) => t.id),
  }
}

function applyOrderFor(status: Status, ids: string[]) {
  const col = tasks.value.filter((t) => t.status === status)
  ids.forEach((id, i) => {
    const t = col.find((x) => x.id === id)
    if (t) t.sort_order = i
  })
  tasks.value = tasks.value.sort(sortTasks)
}

async function moveTask(payload: { id: string; to: Status; index: number }) {
  const t = tasks.value.find((x) => x.id === payload.id)
  if (!t) return
  const from = t.status

  if (from === payload.to) {
    const ids = byStatus(from).value.map((x) => x.id)
    const fromIdx = ids.indexOf(t.id)

    let toIdx = payload.index
    if (toIdx > fromIdx) toIdx -= 1
    if (toIdx === fromIdx) return

    ids.splice(fromIdx, 1)
    toIdx = Math.max(0, Math.min(toIdx, ids.length))
    ids.splice(toIdx, 0, t.id)

    applyOrderFor(from, ids)
  } else {
    const fromIds = byStatus(from)
      .value.map((x) => x.id)
      .filter((id) => id !== t.id)
    const toIds = byStatus(payload.to).value.map((x) => x.id)
    const idx = Math.max(0, Math.min(payload.index, toIds.length))
    toIds.splice(idx, 0, t.id)

    t.status = payload.to
    applyOrderFor(from, fromIds)
    applyOrderFor(payload.to, toIds)
  }

  try {
    await reorderColumns(columnsToPayload())
  } catch {}
}
</script>

<template>
  <div class="board">
    <div class="toolbar">
      <button class="primary" @click="openCreate">New task</button>
    </div>

    <div class="columns">
      <Column
        title="To do"
        status="todo"
        :tasks="byStatus('todo').value"
        @drop-task="moveTask"
        @delete-task="handleDelete"
        @edit-task="openEdit"
      />
      <Column
        title="In progress"
        status="in_progress"
        :tasks="byStatus('in_progress').value"
        @drop-task="moveTask"
        @delete-task="handleDelete"
        @edit-task="openEdit"
      />
      <Column
        title="Done"
        status="done"
        :tasks="byStatus('done').value"
        @drop-task="moveTask"
        @delete-task="handleDelete"
        @edit-task="openEdit"
      />
    </div>

    <TaskModal :open="modalOpen" :task="editing" @close="closeModal" @submit="submitModal" />
  </div>
</template>

<style scoped>
.board {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 16px;

  height: 100%;
  min-height: 0;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: flex-end;
}
.primary {
  background: #10b981;
  color: #052014;
  border: 1px solid #065f46;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}
.primary:hover {
  filter: brightness(1.05);
}

.columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;

  height: 100%;
  min-height: 0;
  overflow: hidden;
}

@media (max-width: 900px) {
  .columns {
    grid-template-columns: 1fr;
  }
}
</style>
