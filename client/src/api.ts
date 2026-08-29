import type { Task, Priority } from './types'
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function listTasks(): Promise<Task[]> {
  const res = await fetch(`${API_URL}/tasks`)
  return await res.json()
}

export async function createTask(payload: {
  title: string
  description: string
  priority: Priority
}): Promise<Task> {
  const res = await fetch(`${API_URL}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return await res.json()
}

export async function updateTask(id: string, patch: Partial<Task>): Promise<Task> {
  const res = await fetch(`${API_URL}/tasks/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  })
  return await res.json()
}

export async function deleteTask(id: string): Promise<void> {
  await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' })
}

export async function reorderColumns(columns: {
  todo: string[]
  in_progress: string[]
  done: string[]
}): Promise<void> {
  await fetch(`${API_URL}/tasks/reorder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(columns),
  })
}
