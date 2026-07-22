import type {
  Todo,
  TodoFilterValue,
  TodoId,
} from "../types/todo";

export function createTodoId(): TodoId {
  return crypto.randomUUID();
}

export function filterTodos(
  todos: Todo[],
  filter: TodoFilterValue,
): Todo[] {
  switch (filter) {
    case "active":
      return todos.filter((todo) => !todo.completed);

    case "completed":
      return todos.filter((todo) => todo.completed);

    case "all":
      return todos;

    default: {
      const exhaustiveCheck: never = filter;
      return exhaustiveCheck;
    }
  }
}

export function countActiveTodos(todos: Todo[]): number {
  return todos.reduce(
    (count, todo) => count + (todo.completed ? 0 : 1),
    0,
  );
}