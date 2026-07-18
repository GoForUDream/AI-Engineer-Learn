# 03. React, TypeScript, and Vite

Goal: Build a typed browser interface with clear component and state boundaries.

## Why This Matters

An AI feature is only useful when a person can provide input, understand progress, inspect output, recover from errors, and continue their workflow.

## Exercise

Build the Todo interface using local mock data first. Do not connect FastAPI yet.

The UI should support:

- Listing todos.
- Creating a todo through a form.
- Marking a todo complete.
- Editing a todo.
- Deleting a todo after confirmation.
- Filtering by all, active, and completed.

## Build Steps

1. Create a React TypeScript app with Vite.
2. Define a `Todo` type and typed component props.
3. Split the page into focused form, list, item, and filter components.
4. Keep state in the nearest common owner.
5. Validate required form values before submission.
6. Add routing for `/todos` and a placeholder `/settings` page.
7. Add component tests for the form and one important interaction.

## UI States

Build these states explicitly:

- Empty list.
- Populated list.
- Validation error.
- Delete confirmation.
- No results for the selected filter.

## Done When

- TypeScript runs without errors.
- The app works without a backend using local state.
- Components have clear responsibilities.
- Forms are keyboard accessible and labels identify their controls.
- Tests cover creation and one update/delete interaction.

## Reflection

- What is the difference between props and state?
- Why should server data and temporary form state be treated differently?
- When should a component be split into smaller components?
