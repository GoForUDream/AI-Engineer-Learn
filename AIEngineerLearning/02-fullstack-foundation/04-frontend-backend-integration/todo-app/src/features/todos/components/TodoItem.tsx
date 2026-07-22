import {
  type FormEvent,
  useId,
  useState,
} from "react";

import type {
  Todo,
  TodoId,
  UpdateTodoInput,
} from "../types";

import { isApiError } from "../../../api/errors";

interface TodoItemProps {
  todo: Todo;
  isUpdating: boolean;
  isDeleting: boolean;
  onToggle: (
    todoId: TodoId,
    completed: boolean,
  ) => Promise<unknown>;
  onUpdate: (
    todoId: TodoId,
    input: UpdateTodoInput,
  ) => Promise<unknown>;
  onDeleteRequest: (todo: Todo) => void;
}

interface EditForm {
  title: string;
  description: string;
}

export function TodoItem({
  todo,
  onToggle,
  onUpdate,
  onDeleteRequest,
  isUpdating,
  isDeleting
}: TodoItemProps) {
  const titleId = useId();
  const descriptionId = useId();
  const editErrorId = useId();

  const [isEditing, setIsEditing] =
    useState(false);

  const [editForm, setEditForm] =
    useState<EditForm>({
      title: todo.title,
      description: todo.description,
    });

  const [titleError, setTitleError] =
    useState<string | null>(null);

  function beginEditing(): void {
    setEditForm({
      title: todo.title,
      description: todo.description,
    });

    setTitleError(null);
    setIsEditing(true);
  }

  function cancelEditing(): void {
    setEditForm({
      title: todo.title,
      description: todo.description,
    });

    setTitleError(null);
    setIsEditing(false);
  }

  async function submitEdit(
  event: FormEvent<HTMLFormElement>,
): Promise<void> {
  event.preventDefault();

  const title = editForm.title.trim();

  if (!title) {
    setTitleError("Title is required.");
    return;
  }

  try {
    await onUpdate(todo.id, {
      title,
      description:
        editForm.description.trim(),
    });

    setTitleError(null);
    setIsEditing(false);
  } catch (error) {
    if (isApiError(error)) {
      setTitleError(
        error.getFieldMessage("title") ??
          error.message,
      );
      return;
    }

    setTitleError(
      "The todo could not be updated.",
    );
  }
}

  if (isEditing) {
    return (
      <li className="todo-item">
        <form
          className="todo-edit-form"
          onSubmit={submitEdit}
          noValidate
        >
          <div className="form-field">
            <label htmlFor={titleId}>
              Edit title
            </label>

            <input
              id={titleId}
              value={editForm.title}
              aria-invalid={Boolean(titleError)}
              aria-describedby={
                titleError
                  ? editErrorId
                  : undefined
              }
              onChange={(event) => {
                setEditForm((current) => ({
                  ...current,
                  title: event.target.value,
                }));

                if (titleError) {
                  setTitleError(null);
                }
              }}
            />

            {titleError ? (
              <p
                id={editErrorId}
                role="alert"
                className="form-error"
              >
                {titleError}
              </p>
            ) : null}
          </div>

          <div className="form-field">
            <label htmlFor={descriptionId}>
              Edit description
            </label>

            <textarea
              id={descriptionId}
              rows={3}
              value={editForm.description}
              onChange={(event) => {
                setEditForm((current) => ({
                  ...current,
                  description:
                    event.target.value,
                }));
              }}
            />
          </div>

          <div className="todo-actions">
            <button
              type="submit"
              disabled={isUpdating}
            >
              {isUpdating ? "Saving…" : "Save"}
            </button>

            <button
              type="button"
              disabled={isUpdating}
              onClick={cancelEditing}
            >
              Cancel
            </button>
          </div>
        </form>
      </li>
    );
  }

  return (
    <li className="todo-item">
      <div className="todo-content">
        <label className="todo-completion">
        <input
          type="checkbox"
          checked={todo.completed}
          disabled={isUpdating || isDeleting}
          onChange={() => {
            void onToggle(
              todo.id,
              !todo.completed,
            );
          }}
        />

          <span className="sr-only">
            Mark {todo.title} as{" "}
            {todo.completed
              ? "active"
              : "completed"}
          </span>
        </label>

        <div>
          <h3
            className={
              todo.completed
                ? "todo-title completed"
                : "todo-title"
            }
          >
            {todo.title}
          </h3>

          {todo.description ? (
            <p>{todo.description}</p>
          ) : (
            <p className="muted">
              No description
            </p>
          )}
        </div>
      </div>

      <div className="todo-actions">
        <button
          type="button"
          onClick={beginEditing}
        >
          Edit
        </button>

        <button
          type="button"
          disabled={isDeleting}
          onClick={() => {
            onDeleteRequest(todo);
          }}
        >
          {isDeleting ? "Deleting…" : "Delete"}
        </button>
      </div>
    </li>
  );
}