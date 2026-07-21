export type TodoId = string

export interface Todo {
    id: TodoId;
    title: string;
    description: string;
    completed: boolean;
    createdAt: string;
}

export interface CreateTodoInput {
  title: string;
  description: string;
}

export interface UpdateTodoInput {
  title?: string;
  description?: string;
  completed?: boolean;
}

export type TodoFilterValue = "all" | "active" | "completed";