export type TodoId = string;

export interface Todo {
  id: TodoId;
  title: string;
  description: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
  dueAt: string | null;
}

export interface CreateTodoInput {
  title: string;
  description: string;
  dueAt?: string | null;
}

export interface UpdateTodoInput {
  title?: string;
  description?: string;
  completed?: boolean;
  dueAt?: string | null;
}

export type TodoFilterValue =
  | "all"
  | "active"
  | "completed";