import {
  type FormEvent,
  useId,
  useState,
} from "react";

import {
  isApiError,
} from "../../../api/errors";
import type {
  CreateTodoInput,
} from "../types";

interface TodoFormProps {
  onSubmit: (
    input: CreateTodoInput,
  ) => Promise<unknown>;
  isSubmitting: boolean;
}

interface FormErrors {
  title?: string;
  description?: string;
  form?: string;
}

const INITIAL_FORM: CreateTodoInput = {
  title: "",
  description: "",
};

export function TodoForm({
  onSubmit,
  isSubmitting,
}: TodoFormProps) {
  const titleId = useId();
  const descriptionId = useId();
  const titleErrorId = useId();
  const descriptionErrorId = useId();
  const formErrorId = useId();

  const [form, setForm] =
    useState<CreateTodoInput>(INITIAL_FORM);

  const [errors, setErrors] =
    useState<FormErrors>({});

  function validate(
    input: CreateTodoInput,
  ): FormErrors {
    const nextErrors: FormErrors = {};

    if (!input.title.trim()) {
      nextErrors.title =
        "Title is required.";
    }

    return nextErrors;
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    if (isSubmitting) {
      return;
    }

    const normalizedInput = {
      title: form.title.trim(),
      description:
        form.description.trim(),
    };

    const validationErrors =
      validate(normalizedInput);

    if (
      Object.keys(validationErrors).length > 0
    ) {
      setErrors(validationErrors);
      return;
    }

    setErrors({});

    try {
      await onSubmit(normalizedInput);

      setForm(INITIAL_FORM);
    } catch (error) {
      if (isApiError(error)) {
        setErrors({
          title:
            error.getFieldMessage("title"),
          description:
            error.getFieldMessage(
              "description",
            ),
          form:
            error.fields.length === 0
              ? error.message
              : undefined,
        });

        return;
      }

      setErrors({
        form:
          "The todo could not be created.",
      });
    }
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
        onSubmit={(event) => {
          void handleSubmit(event);
        }}
        noValidate
        aria-describedby={
          errors.form
            ? formErrorId
            : undefined
        }
      >
        <div className="form-field">
          <label htmlFor={titleId}>
            Title
          </label>

          <input
            id={titleId}
            name="title"
            value={form.title}
            disabled={isSubmitting}
            aria-invalid={Boolean(errors.title)}
            aria-describedby={
              errors.title
                ? titleErrorId
                : undefined
            }
            onChange={(event) => {
              setForm((current) => ({
                ...current,
                title: event.target.value,
              }));

              setErrors((current) => ({
                ...current,
                title: undefined,
                form: undefined,
              }));
            }}
          />

          {errors.title ? (
            <p
              id={titleErrorId}
              role="alert"
              className="form-error"
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
            rows={4}
            value={form.description}
            disabled={isSubmitting}
            aria-invalid={Boolean(
              errors.description,
            )}
            aria-describedby={
              errors.description
                ? descriptionErrorId
                : undefined
            }
            onChange={(event) => {
              setForm((current) => ({
                ...current,
                description:
                  event.target.value,
              }));

              setErrors((current) => ({
                ...current,
                description: undefined,
                form: undefined,
              }));
            }}
          />

          {errors.description ? (
            <p
              id={descriptionErrorId}
              role="alert"
              className="form-error"
            >
              {errors.description}
            </p>
          ) : null}
        </div>

        {errors.form ? (
          <p
            id={formErrorId}
            role="alert"
            className="form-error"
          >
            {errors.form}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting
            ? "Adding todo…"
            : "Add todo"}
        </button>
      </form>
    </section>
  );
}