import type {
  CreateTodoInput,
  Todo,
  TodoId,
  UpdateTodoInput,
} from "../features/todos/types";
import { request } from "./clients";

interface TodoDto {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  due_at: string | null;
}

interface CreateTodoRequestDto {
  title: string;
  description: string;
  due_at?: string | null;
}

interface UpdateTodoRequestDto {
  title?: string;
  description?: string;
  completed?: boolean;
  due_at?: string | null;
}

function mapTodoDto(dto: TodoDto): Todo {
  return {
    id: dto.id,
    title: dto.title,
    description: dto.description,
    completed: dto.completed,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
    dueAt: dto.due_at,
  };
}

function toCreateDto(
  input: CreateTodoInput,
): CreateTodoRequestDto {
  return {
    title: input.title,
    description: input.description,
    ...(input.dueAt !== undefined
      ? { due_at: input.dueAt }
      : {}),
  };
}

function toUpdateDto(
  input: UpdateTodoInput,
): UpdateTodoRequestDto {
  return {
    ...(input.title !== undefined
      ? { title: input.title }
      : {}),
    ...(input.description !== undefined
      ? { description: input.description }
      : {}),
    ...(input.completed !== undefined
      ? { completed: input.completed }
      : {}),
    ...(input.dueAt !== undefined
      ? { due_at: input.dueAt }
      : {}),
  };
}

export const todoApi = {
  async list(
    signal?: AbortSignal,
  ): Promise<Todo[]> {
    const response = await request<TodoDto[]>(
      "/api/todos",
      { signal },
    );

    return response.map(mapTodoDto);
  },

  async create(
    input: CreateTodoInput,
  ): Promise<Todo> {
    const response = await request<
      TodoDto,
      CreateTodoRequestDto
    >("/api/todos", {
      method: "POST",
      body: toCreateDto(input),
    });

    return mapTodoDto(response);
  },

  async update(
    todoId: TodoId,
    input: UpdateTodoInput,
  ): Promise<Todo> {
    const response = await request<
      TodoDto,
      UpdateTodoRequestDto
    >(`/api/todos/${encodeURIComponent(todoId)}`, {
      method: "PATCH",
      body: toUpdateDto(input),
    });

    return mapTodoDto(response);
  },

  async delete(todoId: TodoId): Promise<void> {
    await request<void>(
      `/api/todos/${encodeURIComponent(todoId)}`,
      {
        method: "DELETE",
      },
    );
  },
};