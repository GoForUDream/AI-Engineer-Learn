import {
  render,
  screen,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { TodoForm } from "../components/todos/TodoForm";

describe("TodoForm", () => {
  it("shows a validation error when title is empty", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(
      <TodoForm onSubmit={onSubmit} />,
    );

    await user.click(
      screen.getByRole("button", {
        name: /add todo/i,
      }),
    );

    expect(
      screen.getByRole("alert"),
    ).toHaveTextContent(
      "Title is required.",
    );

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits normalized form values", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(
      <TodoForm onSubmit={onSubmit} />,
    );

    await user.type(
      screen.getByLabelText("Title"),
      "  Write tests  ",
    );

    await user.type(
      screen.getByLabelText("Description"),
      "  Add component coverage.  ",
    );

    await user.click(
      screen.getByRole("button", {
        name: /add todo/i,
      }),
    );

    expect(onSubmit).toHaveBeenCalledWith({
      title: "Write tests",
      description:
        "Add component coverage.",
    });

    expect(
      screen.getByLabelText("Title"),
    ).toHaveValue("");

    expect(
      screen.getByLabelText("Description"),
    ).toHaveValue("");
  });
});