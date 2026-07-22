import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { todoApi } from "../../../api/todos";
import type {
  CreateTodoInput,
  Todo,
  TodoFilterValue,
  TodoId,
  UpdateTodoInput,
} from "../types";

interface MutationState {
  creating: boolean;
  updatingIds: Set<TodoId>;
  deletingIds: Set<TodoId>;
}

interface UseTodosResult {
  todos: Todo[];
  visibleTodos: Todo[];
  filter: TodoFilterValue;
  setFilter: (filter: TodoFilterValue) => void;
  isInitialLoading: boolean;
  loadError: unknown;
  mutationError: unknown;
  isCreating: boolean;
  isUpdating: (todoId: TodoId) => boolean;
  isDeleting: (todoId: TodoId) => boolean;
  createTodo: (
    input: CreateTodoInput,
  ) => Promise<Todo>;
  updateTodo: (
    todoId: TodoId,
    input: UpdateTodoInput,
  ) => Promise<Todo>;
  deleteTodo: (todoId: TodoId) => Promise<void>;
  retryLoad: () => void;
  clearMutationError: () => void;
}

const INITIAL_MUTATION_STATE: MutationState = {
  creating: false,
  updatingIds: new Set(),
  deletingIds: new Set(),
};

export function useTodos(): UseTodosResult {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [filter, setFilter] =
    useState<TodoFilterValue>("all");

  const [isInitialLoading, setIsInitialLoading] =
    useState(true);

  const [loadError, setLoadError] =
    useState<unknown>(null);

  const [mutationError, setMutationError] =
    useState<unknown>(null);

  const [reloadKey, setReloadKey] = useState(0);

  const [mutationState, setMutationState] =
    useState<MutationState>(
      INITIAL_MUTATION_STATE,
    );

  const createInFlightRef = useRef(false);

  useEffect(() => {
    const abortController =
      new AbortController();

    async function loadTodos(): Promise<void> {
      setIsInitialLoading(true);
      setLoadError(null);

      try {
        const loadedTodos = await todoApi.list(
          abortController.signal,
        );

        setTodos(loadedTodos);
      } catch (error) {
        if (
          error instanceof DOMException &&
          error.name === "AbortError"
        ) {
          return;
        }

        setLoadError(error);
      } finally {
        if (!abortController.signal.aborted) {
          setIsInitialLoading(false);
        }
      }
    }

    void loadTodos();

    return () => {
      abortController.abort();
    };
  }, [reloadKey]);

  const visibleTodos = useMemo(() => {
    switch (filter) {
      case "active":
        return todos.filter(
          (todo) => !todo.completed,
        );

      case "completed":
        return todos.filter(
          (todo) => todo.completed,
        );

      case "all":
        return todos;

      default: {
        const exhaustiveCheck: never = filter;
        return exhaustiveCheck;
      }
    }
  }, [todos, filter]);

  const createTodo = useCallback(
    async (
      input: CreateTodoInput,
    ): Promise<Todo> => {
      if (createInFlightRef.current) {
        throw new Error(
          "A create request is already in progress.",
        );
      }

      createInFlightRef.current = true;
      setMutationError(null);

      setMutationState((current) => ({
        ...current,
        creating: true,
      }));

      try {
        const createdTodo =
          await todoApi.create(input);

        setTodos((current) => [
          createdTodo,
          ...current,
        ]);

        return createdTodo;
      } catch (error) {
        setMutationError(error);
        throw error;
      } finally {
        createInFlightRef.current = false;

        setMutationState((current) => ({
          ...current,
          creating: false,
        }));
      }
    },
    [],
  );

  const updateTodo = useCallback(
    async (
      todoId: TodoId,
      input: UpdateTodoInput,
    ): Promise<Todo> => {
      setMutationError(null);

      setMutationState((current) => ({
        ...current,
        updatingIds: new Set(
          current.updatingIds,
        ).add(todoId),
      }));

      try {
        const updatedTodo =
          await todoApi.update(todoId, input);

        setTodos((current) =>
          current.map((todo) =>
            todo.id === todoId
              ? updatedTodo
              : todo,
          ),
        );

        return updatedTodo;
      } catch (error) {
        setMutationError(error);
        throw error;
      } finally {
        setMutationState((current) => {
          const updatingIds = new Set(
            current.updatingIds,
          );

          updatingIds.delete(todoId);

          return {
            ...current,
            updatingIds,
          };
        });
      }
    },
    [],
  );

  const deleteTodo = useCallback(
    async (todoId: TodoId): Promise<void> => {
      setMutationError(null);

      setMutationState((current) => ({
        ...current,
        deletingIds: new Set(
          current.deletingIds,
        ).add(todoId),
      }));

      try {
        await todoApi.delete(todoId);

        setTodos((current) =>
          current.filter(
            (todo) => todo.id !== todoId,
          ),
        );
      } catch (error) {
        setMutationError(error);
        throw error;
      } finally {
        setMutationState((current) => {
          const deletingIds = new Set(
            current.deletingIds,
          );

          deletingIds.delete(todoId);

          return {
            ...current,
            deletingIds,
          };
        });
      }
    },
    [],
  );

  return {
    todos,
    visibleTodos,
    filter,
    setFilter,
    isInitialLoading,
    loadError,
    mutationError,
    isCreating: mutationState.creating,
    isUpdating: (todoId) =>
      mutationState.updatingIds.has(todoId),
    isDeleting: (todoId) =>
      mutationState.deletingIds.has(todoId),
    createTodo,
    updateTodo,
    deleteTodo,
    retryLoad: () => {
      setReloadKey((current) => current + 1);
    },
    clearMutationError: () => {
      setMutationError(null);
    },
  };
}