import {
  type FormEvent,
  useId,
  useState,
} from "react";

import type { CreateTodoInput } from "../../types/todo";

interface TodoFormProps {
  onSubmit: (input: CreateTodoInput) => void;
}

interface FormErrors {
  title?: string;
}

const INITIAL_FORM: CreateTodoInput = {
  title: "",
  description: "",
};

export function TodoForm({
  onSubmit,
}: TodoFormProps) {
  const titleId = useId();
  const descriptionId = useId();
  const titleErrorId = useId();

  const [form, setForm] =
    useState<CreateTodoInput>(INITIAL_FORM);

  const [errors, setErrors] =
    useState<FormErrors>({});

  function validate(
    input: CreateTodoInput,
  ): FormErrors {
    const nextErrors: FormErrors = {};

    if (!input.title.trim()) {
      nextErrors.title = "Title is required.";
    }

    return nextErrors;
  }

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): void {
    event.preventDefault();

    const normalizedInput: CreateTodoInput = {
      title: form.title.trim(),
      description: form.description.trim(),
    };

    const validationErrors =
      validate(normalizedInput);

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    onSubmit(normalizedInput);

    setForm(INITIAL_FORM);
    setErrors({});
  }

  return (
    <section
      className="panel"
      aria-labelledby="create-todo-heading"
    >
      <h2 id="create-todo-heading">
        Create todo
      </h2>

      <form
        className="todo-form"
        onSubmit={handleSubmit}
        noValidate
      >
        <div className="form-field">
          <label htmlFor={titleId}>
            Title
          </label>

          <input
            id={titleId}
            name="title"
            type="text"
            value={form.title}
            maxLength={200}
            aria-invalid={Boolean(errors.title)}
            aria-describedby={
              errors.title ? titleErrorId : undefined
            }
            onChange={(event) => {
              setForm((current) => ({
                ...current,
                title: event.target.value,
              }));

              if (errors.title) {
                setErrors({});
              }
            }}
          />

          {errors.title ? (
            <p
              id={titleErrorId}
              className="form-error"
              role="alert"
            >
              {errors.title}
            </p>
          ) : null}
        </div>

        <div className="form-field">
          <label htmlFor={descriptionId}>
            Description
          </label>

          <textarea
            id={descriptionId}
            name="description"
            value={form.description}
            maxLength={2_000}
            rows={4}
            onChange={(event) => {
              setForm((current) => ({
                ...current,
                description:
                  event.target.value,
              }));
            }}
          />
        </div>

        <button type="submit">
          Add todo
        </button>
      </form>
    </section>
  );
}