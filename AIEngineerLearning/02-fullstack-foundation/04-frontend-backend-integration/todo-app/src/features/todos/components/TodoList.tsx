import type {
  Todo,
  TodoFilterValue,
  TodoId,
  UpdateTodoInput,
} from "../types";

import  {TodoItem}  from "./TodoItem";

interface TodoListProps {
  todos: Todo[];
  totalTodoCount: number;
  filter: TodoFilterValue;
  onToggle: (
    todoId: TodoId,
    completed: boolean,
  ) => Promise<unknown>;
  onUpdate: (
    todoId: TodoId,
    input: UpdateTodoInput,
  ) => Promise<unknown>;
  onDeleteRequest: (todo: Todo) => void;
  isUpdating: (todoId: TodoId) => boolean;
  isDeleting: (todoId: TodoId) => boolean;
}

export function TodoList({
  todos,
  totalTodoCount,
  filter,
  onToggle,
  onUpdate,
  onDeleteRequest,
  isDeleting,
  isUpdating
}: TodoListProps) {
  if (totalTodoCount === 0) {
    return (
      <section
        className="panel empty-state"
        aria-live="polite"
      >
        <h2>No todos yet</h2>
        <p>
          Create your first todo using the
          form above.
        </p>
      </section>
    );
  }

  if (todos.length === 0) {
    return (
      <section
        className="panel empty-state"
        aria-live="polite"
      >
        <h2>No matching todos</h2>
        <p>
          There are no {filter} todos at the
          moment.
        </p>
      </section>
    );
  }

  return (
    <section
      className="panel"
      aria-labelledby="todo-list-heading"
    >
      <h2 id="todo-list-heading">
        Todo list
      </h2>

      <ul className="todo-list">
        {todos.map((todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onToggle={onToggle}
            onUpdate={onUpdate}
            isDeleting={isDeleting(todo.id)}
            isUpdating={isUpdating(todo.id)}
            onDeleteRequest={
              onDeleteRequest
            }
          />
        ))}
      </ul>
    </section>
  );
}