import {
  type RefObject,
  useEffect,
  useRef,
} from "react";

import type { Todo } from "../../types/todo";

interface DeleteTodoDialogProps {
  todo: Todo | null;
  onCancel: () => void;
  onConfirm: (todo: Todo) => void;
}

export function DeleteTodoDialog({
  todo,
  onCancel,
  onConfirm,
}: DeleteTodoDialogProps) {
  const dialogRef =
    useRef<HTMLDialogElement>(null);

  useDialogState(dialogRef, todo !== null);

  if (!todo) {
    return null;
  }

  return (
    <dialog
      ref={dialogRef}
      className="delete-dialog"
      aria-labelledby="delete-dialog-title"
      onCancel={(event) => {
        event.preventDefault();
        onCancel();
      }}
      onClose={onCancel}
    >
      <h2 id="delete-dialog-title">
        Delete todo?
      </h2>

      <p>
        You are about to delete{" "}
        <strong>{todo.title}</strong>. This
        action cannot be undone.
      </p>

      <div className="dialog-actions">
        <button
          type="button"
          onClick={onCancel}
        >
          Cancel
        </button>

        <button
          type="button"
          className="danger-button"
          onClick={() => {
            onConfirm(todo);
          }}
        >
          Delete
        </button>
      </div>
    </dialog>
  );
}

function useDialogState(
  dialogRef: RefObject<HTMLDialogElement | null>,
  isOpen: boolean,
): void {
  useEffect(() => {
    const dialog = dialogRef.current;

    if (!dialog) {
      return;
    }

    if (isOpen && !dialog.open) {
      dialog.showModal();
      return;
    }

    if (!isOpen && dialog.open) {
      dialog.close();
    }
  }, [dialogRef, isOpen]);
}