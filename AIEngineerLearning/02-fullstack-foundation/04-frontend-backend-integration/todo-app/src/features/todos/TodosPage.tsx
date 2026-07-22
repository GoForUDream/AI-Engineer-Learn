import { useState } from "react";

import { ApiFailure } from "./components/ApiFailure";
import { DeleteTodoDialog } from "./components/DeleteTodoDialog";
import { TodoFilter } from "./components/TodoFilter";
import { TodoForm } from "./components/TodoForm";
import { TodoList } from "./components/TodoList";
import { useTodos } from "./hooks/useTodos";
import type { Todo } from "./types";

export function TodosPage() {
  const {
    todos,
    visibleTodos,
    filter,
    setFilter,
    isInitialLoading,
    loadError,
    mutationError,
    isCreating,
    isUpdating,
    isDeleting,
    createTodo,
    updateTodo,
    deleteTodo,
    retryLoad,
    clearMutationError,
  } = useTodos();

  const [
    todoPendingDeletion,
    setTodoPendingDeletion,
  ] = useState<Todo | null>(null);

  async function confirmDelete(
    todo: Todo,
  ): Promise<void> {
    try {
      await deleteTodo(todo.id);
      setTodoPendingDeletion(null);
    } catch {
      // The hook stores the controlled error.
      // Keep the dialog open so the user can retry or cancel.
    }
  }

  return (
    <main className="page-container">
      <header className="page-header">
        <h1>Todos</h1>
        <p>
          {todos.filter(
            (todo) => !todo.completed,
          ).length}{" "}
          active
        </p>
      </header>

      <TodoForm
        onSubmit={createTodo}
        isSubmitting={isCreating}
      />

      {mutationError ? (
        <ApiFailure
          error={mutationError}
          onRetry={clearMutationError}
        />
      ) : null}

      {isInitialLoading ? (
        <section
          className="panel"
          aria-live="polite"
          aria-busy="true"
        >
          <p>Loading todos…</p>
        </section>
      ) : null}

      {!isInitialLoading &&
      loadError &&
      todos.length === 0 ? (
        <ApiFailure
          error={loadError}
          onRetry={retryLoad}
        />
      ) : null}

      {!isInitialLoading &&
      (!loadError || todos.length > 0) ? (
        <>
          <TodoFilter
            value={filter}
            onChange={setFilter}
          />

          <TodoList
            todos={visibleTodos}
            totalTodoCount={todos.length}
            filter={filter}
            isUpdating={isUpdating}
            isDeleting={isDeleting}
            onToggle={(
              todoId,
              completed,
            ) =>
              updateTodo(todoId, {
                completed,
              })
            }
            onUpdate={updateTodo}
            onDeleteRequest={
              setTodoPendingDeletion
            }
          />
        </>
      ) : null}

      <DeleteTodoDialog
        todo={todoPendingDeletion}
        isDeleting={
          todoPendingDeletion
            ? isDeleting(
                todoPendingDeletion.id,
              )
            : false
        }
        onCancel={() => {
          if (
            !todoPendingDeletion ||
            !isDeleting(
              todoPendingDeletion.id,
            )
          ) {
            setTodoPendingDeletion(null);
          }
        }}
        onConfirm={(todo) => {
          void confirmDelete(todo);
        }}
      />
    </main>
  );
}