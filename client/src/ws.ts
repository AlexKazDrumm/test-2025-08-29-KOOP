import type { BoardState, Task } from './types'
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/^http/, 'ws')
export type ServerEvent =
  | { type: 'snapshot'; state: BoardState }
  | { type: 'created'; task: Task }
  | { type: 'updated'; task: Task }
  | { type: 'deleted'; task_id: string }
export function connect(onMessage: (ev: ServerEvent) => void) {
  const ws = new WebSocket(`${API_URL}/ws`)
  ws.onmessage = (e) => {
    try {
      onMessage(JSON.parse(e.data))
    } catch {}
  }
  ws.onopen = () => ws.send('ping')
  const t = setInterval(() => {
    if (ws.readyState === ws.OPEN) ws.send('ping')
  }, 15000)
  ws.onclose = () => clearInterval(t)
  return ws
}
