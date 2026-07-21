import {
  render,
  screen,
  within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { TodosPage } from "../pages/TodosPage";

describe("TodosPage", () => {
  it("creates, completes, filters and deletes a todo", async () => {
    const user = userEvent.setup();

    render(<TodosPage />);

    await user.type(
      screen.getByLabelText("Title"),
      "Review FastAPI integration",
    );

    await user.type(
      screen.getByLabelText("Description"),
      "Connect the UI in the next lesson.",
    );

    await user.click(
      screen.getByRole("button", {
        name: /add todo/i,
      }),
    );

    const todoHeading = screen.getByRole(
      "heading",
      {
        name: "Review FastAPI integration",
      },
    );

    expect(todoHeading).toBeInTheDocument();

    const todoItem =
      todoHeading.closest("li");

    expect(todoItem).not.toBeNull();

    const item = within(
      todoItem as HTMLLIElement,
    );

    await user.click(
      item.getByRole("checkbox"),
    );

    await user.click(
      screen.getByRole("radio", {
        name: "Completed",
      }),
    );

    expect(
      screen.getByRole("heading", {
        name: "Review FastAPI integration",
      }),
    ).toBeInTheDocument();

    await user.click(
      item.getByRole("button", {
        name: "Delete",
      }),
    );

    const dialog =
      screen.getByRole("dialog");

    expect(
      within(dialog).getByText(
        /this action cannot be undone/i,
      ),
    ).toBeInTheDocument();

    await user.click(
      within(dialog).getByRole("button", {
        name: "Delete",
      }),
    );

    expect(
      screen.queryByRole("heading", {
        name: "Review FastAPI integration",
      }),
    ).not.toBeInTheDocument();
  });

  it("shows no-results state for the selected filter", async () => {
  const user = userEvent.setup();

  render(
    <TodosPage
      initialData={[
        {
          id: "todo_active",
          title: "Active todo",
          description: "",
          completed: false,
          createdAt:
            "2026-07-21T08:00:00.000Z",
        },
      ]}
    />,
  );

  await user.click(
    screen.getByRole("radio", {
      name: "Completed",
    }),
  );

  expect(
    screen.getByRole("heading", {
      name: "No matching todos",
    }),
  ).toBeInTheDocument();

  expect(
    screen.getByText(
      "There are no completed todos at the moment.",
    ),
  ).toBeInTheDocument();

  
  });
});