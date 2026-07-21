import {
  useMemo,
  useState,
} from "react";

import { DeleteTodoDialog } from "../components/todos/DeleteTodoDialog";
import { TodoFilter } from "../components/todos/TodoFilter";
import { TodoForm } from "../components/todos/TodoForm";
import { TodoList } from "../components/todos/TodoList";
import { initialTodos } from "../data/mockTodos";
import type {
  CreateTodoInput,
  Todo,
  TodoFilterValue,
  TodoId,
  UpdateTodoInput,
} from "../types/todo";
import {
  countActiveTodos,
  createTodoId,
  filterTodos,
} from "../utils/todo";

interface TodosPageProps {
  initialData?: Todo[];
}

export function TodosPage({initialData = initialTodos}: TodosPageProps) {
  const [todos, setTodos] =
    useState<Todo[]>(initialData);

  const [filter, setFilter] =
    useState<TodoFilterValue>("all");

  const [
    todoPendingDeletion,
    setTodoPendingDeletion,
  ] = useState<Todo | null>(null);

  const visibleTodos = useMemo(
    () => filterTodos(todos, filter),
    [todos, filter],
  );

  const activeCount = useMemo(
    () => countActiveTodos(todos),
    [todos],
  );

  function createTodo(
    input: CreateTodoInput,
  ): void {
    const todo: Todo = {
      id: createTodoId(),
      title: input.title,
      description: input.description,
      completed: false,
      createdAt: new Date().toISOString(),
    };

    setTodos((current) => [
      todo,
      ...current,
    ]);
  }

  function toggleTodo(todoId: TodoId): void {
    setTodos((current) =>
      current.map((todo) =>
        todo.id === todoId
          ? {
              ...todo,
              completed: !todo.completed,
            }
          : todo,
      ),
    );
  }

  function updateTodo(
    todoId: TodoId,
    input: UpdateTodoInput,
  ): void {
    setTodos((current) =>
      current.map((todo) =>
        todo.id === todoId
          ? {
              ...todo,
              ...input,
            }
          : todo,
      ),
    );
  }

  function confirmDelete(todo: Todo): void {
    setTodos((current) =>
      current.filter(
        (currentTodo) =>
          currentTodo.id !== todo.id,
      ),
    );

    setTodoPendingDeletion(null);
  }

  return (
    <main className="page-container">
      <header className="page-header">
        <div>
          <p className="eyebrow">
            Local mock application
          </p>

          <h1>Todos</h1>

          <p>
            {activeCount} active{" "}
            {activeCount === 1
              ? "todo"
              : "todos"}
          </p>
        </div>
      </header>

      <TodoForm onSubmit={createTodo} />

      <TodoFilter
        value={filter}
        onChange={setFilter}
      />

      <TodoList
        todos={visibleTodos}
        totalTodoCount={todos.length}
        filter={filter}
        onToggle={toggleTodo}
        onUpdate={updateTodo}
        onDeleteRequest={
          setTodoPendingDeletion
        }
      />

      <DeleteTodoDialog
        todo={todoPendingDeletion}
        onCancel={() => {
          setTodoPendingDeletion(null);
        }}
        onConfirm={confirmDelete}
      />
    </main>
  );
}