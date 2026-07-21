import type {
  Todo,
  TodoFilterValue,
  TodoId,
  UpdateTodoInput,
} from "../../types/todo";

import  {TodoItem}  from "./TodoItem";

interface TodoListProps {
  todos: Todo[];
  totalTodoCount: number;
  filter: TodoFilterValue;
  onToggle: (todoId: TodoId) => void;
  onUpdate: (
    todoId: TodoId,
    input: UpdateTodoInput,
  ) => void;
  onDeleteRequest: (todo: Todo) => void;
}

export function TodoList({
  todos,
  totalTodoCount,
  filter,
  onToggle,
  onUpdate,
  onDeleteRequest,
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
            onDeleteRequest={
              onDeleteRequest
            }
          />
        ))}
      </ul>
    </section>
  );
}