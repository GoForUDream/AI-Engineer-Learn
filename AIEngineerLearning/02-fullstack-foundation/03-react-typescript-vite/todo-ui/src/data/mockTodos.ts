import type { Todo } from "../types/todo";

export const initialTodos: Todo[] = [
  {
    id: "todo_001",
    title: "Build the Todo form",
    description: "Create an accessible form with title and description fields.",
    completed: true,
    createdAt: "2026-07-21T08:00:00.000Z",
  },
  {
    id: "todo_002",
    title: "Add filtering",
    description: "Support all, active, and completed filters.",
    completed: false,
    createdAt: "2026-07-21T08:15:00.000Z",
  },
  {
    id: "todo_003",
    title: "Write component tests",
    description: "Test validation and an important user interaction.",
    completed: false,
    createdAt: "2026-07-21T08:30:00.000Z",
  },
];