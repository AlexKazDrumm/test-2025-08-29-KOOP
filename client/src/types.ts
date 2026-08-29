export type Status = 'todo' | 'in_progress' | 'done'
export type Priority = 'low' | 'normal' | 'high' | 'urgent'

export interface Task {
  id: string
  title: string
  description: string
  status: Status
  priority: Priority
  sort_order: number
  created_at: string
  updated_at: string
}

export interface BoardState {
  tasks: Task[]
}
