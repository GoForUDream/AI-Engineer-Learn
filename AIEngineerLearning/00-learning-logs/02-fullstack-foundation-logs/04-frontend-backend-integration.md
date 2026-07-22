# Frontend-Backend Integration — React and TypeScript Learning Log

This log first answers the questions raised while building the Todo application. It then adds 15 interview questions aimed at middle/senior React and frontend roles. The answers focus on reasoning, trade-offs, and production behavior rather than syntax alone.

## Answers to Existing Questions

### 1. What Is the Difference Between `type` and `interface` When Defining Types?

Both describe TypeScript types, and both use structural typing: a value is compatible when its shape matches, regardless of the type's name.

```ts
interface Todo {
  id: string;
  title: string;
}

type TodoAlias = {
  id: string;
  title: string;
};
```

For ordinary object shapes, these declarations are almost interchangeable. The important differences are what each construct can express and how it can be extended.

#### Use an `interface` for an object contract that may be extended

Interfaces have first-class `extends` syntax:

```ts
interface Entity {
  id: string;
}

interface Todo extends Entity {
  title: string;
  completed: boolean;
}
```

An interface is also **open**. Declarations with the same name in the same scope merge:

```ts
interface RequestContext {
  requestId: string;
}

interface RequestContext {
  userId: string;
}

// Has both requestId and userId.
```

Declaration merging is useful for library or global type augmentation, but accidental merging can be surprising in application code.

#### Use a `type` for unions, tuples, primitives, and type composition

A type alias can name types that are not object declarations:

```ts
type TodoId = string;
type TodoFilter = all | active | completed;
type Point = readonly [x: number, y: number];
type AsyncState<T> =
  | { status: idle }
  | { status: loading }
  | { status: success; data: T }
  | { status: error; error: unknown };
```

Type aliases support intersections and work naturally with conditional, mapped, and utility types:

```ts
type TodoSummary = Pick<Todo, id | title>;
type TodoWithAudit = Todo & {
  updatedBy: string;
};
```

#### Extension and composition

An interface can extend another interface or an object-like type alias. A type alias can combine object types with an intersection. These are similar, but an invalid interface extension usually produces a clearer error at the declaration, while a complex intersection can produce a type that is difficult or impossible to satisfy.

```ts
interface Named {
  name: string;
}

interface User extends Named {
  email: string;
}

type AuditedUser = User & {
  createdAt: string;
};
```

#### Practical convention

- Use `interface` for public object contracts such as component props, service contracts, and class implementations.
- Use `type` for unions, aliases, tuples, mapped types, and domain-state variants.
- Do not rewrite a clear type merely to follow a rigid rule. Consistency inside the codebase matters more than claiming that one is always better.
- Neither exists at runtime. TypeScript erases both during compilation, so runtime API data still needs validation.

This application follows a reasonable convention: component prop shapes such as `TodoListProps` are interfaces, while `TodoId` and `TodoFilterValue` are aliases because they represent an alias and a union.

### 2. How Is Frontend Error Handling Set Up in This Application, and Why?

The application handles errors in layers. Each layer has one responsibility:

```text
fetch / HTTP response
        ↓
request<TResponse>() normalizes failures into ApiError
        ↓
todoApi maps transport DTOs to frontend domain objects
        ↓
useTodos stores load and mutation error state
        ↓
page/form/item renders the error in the correct UI context
```

#### Layer 1: `request()` normalizes transport failures

`src/api/clients.ts` is the shared HTTP boundary. It:

- configures the API base URL and JSON headers;
- converts the request body to JSON;
- distinguishes an intentional `AbortError` from a network failure;
- checks `response.ok`, because `fetch` does not reject a Promise for HTTP `4xx` or `5xx` responses;
- safely parses JSON only when the content type is JSON;
- supports `204 No Content`;
- converts known and unknown HTTP failures into one `ApiError` model.

This prevents every component from having to understand `fetch`, status codes, content types, and backend error envelopes.

#### Layer 2: `ApiError` provides a stable application error

`src/api/errors.ts` preserves:

- `status` for the HTTP status;
- `code` for programmatic decisions;
- `message` for a user-safe explanation;
- `fields` for validation errors;
- `cause` for the original low-level failure when available.

The `isApiError(error)` type guard safely narrows a caught `unknown`, and `getFieldMessage(title)` lets a form attach a backend validation message to the correct input.

#### Layer 3: `useTodos` owns asynchronous operation state

The custom hook separates initial-load failures from mutation failures:

- `loadError` represents failure to fetch the list;
- `mutationError` represents create, update, or delete failure;
- `isInitialLoading` controls the loading state;
- per-operation flags prevent conflicting UI actions;
- `retryLoad()` triggers a new list request;
- `AbortController` cancels an obsolete list request during cleanup.

The mutation methods store the error and rethrow it. This is deliberate: the page can show a general operation error while a form or item can also handle a contextual field error.

#### Layer 4: components present errors near the affected action

- `ApiFailure` renders a page-level message and optional recovery action.
- `TodoForm` performs immediate client validation and maps backend field errors to inputs.
- `TodoItem` keeps edit validation near the edited todo.
- `TodosPage` keeps the delete dialog open after deletion fails so the user can retry or cancel.
- `role=alert`, `aria-invalid`, and `aria-describedby` expose errors to assistive technology.

#### Benefits

1. **Consistency:** network, HTTP, malformed-error-body, and validation failures have one application shape.
2. **Separation of concerns:** UI components do not parse HTTP responses, and the API client does not decide page layout.
3. **Better typing:** caught values remain `unknown` until narrowed.
4. **Contextual UX:** field errors appear beside fields, while load failures replace or supplement the list.
5. **Testability:** the API boundary, hook state transitions, and UI behavior can be tested independently.
6. **Recovery:** cancellation and retry are explicit rather than accidental.

#### Trade-offs and current limitations

1. **More code and conventions:** every developer must understand the error envelope, `ApiError`, hook state, and presentation rules.
2. **Possible duplicate messages:** a mutation can be stored globally by `useTodos` and also rendered locally by a form.
3. **Successful responses are not runtime-validated:** `request<TResponse>` uses a TypeScript assertion after parsing. If the backend returns JSON with the wrong successful shape, TypeScript cannot detect it at runtime. A schema validator such as Zod or generated OpenAPI validation would close this gap.
4. **Cancellation is incomplete:** list loading is aborted, but create/update/delete requests do not currently accept abort signals.
5. **No render error boundary is shown:** `ApiError` handles expected operational failures, not exceptions thrown while React renders a component.
6. **No observability policy is visible:** production systems should report unexpected failures with context and correlation IDs while avoiding secrets and personal data.
7. **Retry semantics vary:** retrying a GET is usually safe; retrying a POST may duplicate work unless the API supports idempotency.
8. **The mutation recovery label is misleading:** `TodosPage` passes `clearMutationError` to an `ApiFailure` button labeled “Try again.” That handler dismisses the error but does not replay the failed mutation. It should be labeled “Dismiss,” or the UI should retain enough operation context to perform a safe, explicit retry.

The design is good for a small application because it creates a clean error boundary around HTTP. At larger scale, a server-state library, runtime schema validation, centralized telemetry, route-level error boundaries, and an explicit retry policy would reduce repeated state machinery.

## Middle/Senior React and Frontend Interview Questions

### 3. What Causes a React Component to Render, and What Are the Render and Commit Phases?

A component renders initially and can render again when its state changes, its parent renders, a consumed context value changes, or an external store subscription reports a change. A render does not automatically mean the browser DOM changes.

During the **render phase**, React calls components and calculates the next UI tree. Rendering must be pure: the same props, state, and context should produce the same result, without network calls, DOM mutation, or subscription setup.

During the **commit phase**, React applies the necessary DOM changes. Layout effects run around this phase, and normal effects run after the updated screen is committed.

React may start, pause, repeat, or discard render work. Therefore side effects inside the component body are unsafe. Event handlers are for user-triggered work; effects are for synchronization caused by rendering.

A senior answer also distinguishes “rendered” from “committed” and avoids treating every parent render as a performance bug. Measure whether the render is expensive and whether it results in meaningful latency.

### 4. How Should You Decide Where State Belongs?

Keep state as close as possible to the components that need it, but high enough to provide one source of truth for all consumers.

First classify the state:

- **Local UI state:** dialog visibility or edit mode; keep it in the nearest component.
- **Shared client state:** a filter used by siblings; lift it to their closest common owner or use focused context.
- **Server state:** todos fetched from the API; it needs caching, freshness, retry, and invalidation semantics.
- **URL state:** filters, pagination, and selected IDs that should survive refresh or be shareable.
- **Form state:** draft input and validation, usually local until submission.
- **Derived state:** values such as `visibleTodos`; calculate them from source state instead of storing another synchronized copy.

In this app, `todos` and `filter` are sources, while `visibleTodos` is derived with `useMemo`. Storing all three independently would allow them to contradict each other.

Context is dependency injection through the component tree, not a universal state manager. Large frequently changing context values can rerender many consumers and hide dependencies. Split contexts by responsibility and select a dedicated state solution only when the application’s update patterns justify it.

### 5. When Should You Use `useEffect`, and When Should You Avoid It?

Use an effect to synchronize React with an external system after a commit: HTTP requests tied to mounted UI, subscriptions, timers, browser APIs, or imperative third-party widgets. The effect should declare all reactive dependencies and return cleanup when the external work must be stopped or undone.

Do not use an effect for:

- values that can be calculated during render;
- user actions that belong in an event handler;
- resetting state merely because a prop changed when component identity or a key models the requirement better;
- chains of effects that repeatedly copy state into other state.

The list request in `useTodos` is a valid effect because the UI synchronizes with an external API. Its cleanup aborts the request so an obsolete operation does not update the current screen.

Development Strict Mode may run effect setup and cleanup an extra time to expose unsafe logic. The fix is not a “run once” ref that hides the behavior; the effect should be idempotent and have correct cleanup.

### 6. What Are Stale Closures, and How Do Hook Dependency Arrays Prevent Them?

Each render creates a snapshot of props, state, and functions. A callback closes over the snapshot from the render in which it was created. If an effect or memoized callback uses a reactive value but omits it from its dependencies, it can continue reading an old value—a stale closure.

```ts
setTodos((current) => [createdTodo, ...current]);
```

This app correctly uses a functional state update, so the callback does not need to capture an older `todos` array. Functional updates are especially important when multiple updates may be queued.

`useCallback` caches a function identity; `useMemo` caches a calculation result. Neither makes code correct and neither should be added automatically. Include every reactive dependency, restructure the code if dependencies cause unwanted reruns, and treat the hooks as performance tools—not as ways to silence the hooks linter.

### 7. Why Are React Keys Important, and Why Is an Array Index Often a Bad Key?

A key tells React which logical child corresponds to which previous child. React uses the key together with the element’s position/type to preserve component identity and local state across renders.

An array index is unsafe when items can be inserted, removed, filtered, or reordered. After a deletion, the same index may refer to a different todo, so edit state or input state can appear to move to the wrong row.

This application correctly uses `key={todo.id}` because the backend ID is stable and unique among sibling todos. Generate IDs when data is created, not during rendering. Changing a key intentionally resets that component’s state, which can be useful for resetting a form when switching between different records.

Keys only need to be unique among siblings, and a key is not passed to the child as a normal prop.

### 8. How Do You Prevent Race Conditions and State Updates from Obsolete Requests?

A race occurs when multiple requests overlap and an older response finishes after a newer response, incorrectly replacing newer state. Common examples are search-as-you-type, route changes, and quickly changing filters.

Use one or more of these strategies:

- abort the old request with `AbortController`;
- ignore responses whose request ID/version is no longer current;
- let a server-state library deduplicate and cancel requests;
- design mutations with version checks or idempotency keys when correctness crosses the network boundary.

Cleanup must treat abort as an expected control path, not show it as a user-facing failure. The app does this for initial list loading.

Cancellation alone does not guarantee server-side cancellation: the server may already be processing the request. For writes, frontend controls must be combined with backend concurrency and idempotency rules.

### 9. What Is the Difference Between Client State and Server State, and When Would You Use a Server-State Library?

Client state is owned by the browser UI, such as whether a dialog is open. Server state is a cached snapshot of remote data owned by the backend. Server state can become stale and needs fetching, deduplication, retry, invalidation, background refresh, and mutation coordination.

`useTodos` manually implements a small server-state layer. That is appropriate for learning and for a small feature, but complexity grows when several screens need the same data or require pagination, dependent queries, cache invalidation, offline behavior, or optimistic updates.

A library such as TanStack Query can standardize those mechanics. It does not remove the need for a typed API client, DTO mapping, validation, or domain-specific error UX. The decision should be based on repeated server-state complexity, not merely application size.

### 10. What Are Optimistic and Pessimistic Updates, and How Do You Choose Between Them?

A **pessimistic update** waits for the server to succeed before changing local data. This app uses that approach for create, update, and delete. It is easier to reason about and avoids rollback logic, but the interface can feel slower.

An **optimistic update** changes the UI immediately, then confirms with the server. On failure it must restore the previous state, show the error, and handle conflicts with other updates.

Choose optimistic behavior when success is likely, the operation is reversible, and immediate feedback matters—for example, toggling a todo. Prefer pessimistic behavior for destructive, expensive, security-sensitive, or conflict-prone operations.

A production optimistic implementation should snapshot affected cache data, cancel/refetch related queries, reconcile the authoritative server response, and prevent an older response from overwriting a newer action.

### 11. Why Should the Frontend Separate API DTOs from Domain Models?

Transport contracts are optimized for the API; UI domain models are optimized for frontend use. In this app, `TodoDto` uses `created_at`, while `Todo` uses `createdAt`. `mapTodoDto()` creates an explicit boundary between them.

Benefits include:

- backend naming or serialization changes stay inside the API layer;
- components do not depend on HTTP-specific shapes;
- dates, nullable fields, enums, and nested values can be normalized once;
- tests can target mapping independently.

TypeScript generics do not validate network data. `request<TodoDto>()` tells the compiler what the developer expects; it does not prove that the JSON matches. At a trust boundary, validate `unknown` with a runtime schema or generated validator before mapping it. Fail with a controlled `invalid_api_response` error if the contract is broken.

### 12. What Is an Error Boundary, and What Errors Does It Not Catch?

An error boundary catches errors thrown while rendering descendant components and in descendant lifecycle logic. It can render fallback UI and report the failure. Route or feature boundaries are often more useful than one boundary around the entire application because unaffected areas can remain usable.

An error boundary generally does not replace `try/catch` for:

- event handlers;
- rejected Promises and ordinary asynchronous callbacks;
- HTTP errors already represented as application state;
- errors thrown inside the boundary itself.

This app’s `ApiError` flow handles expected operational failures. A render error boundary would handle a different category: a programming defect or unexpected data that causes React rendering to throw. Production reporting should attach route, release, and correlation context while filtering sensitive data.

### 13. How Would You Diagnose and Improve React Performance?

Measure first with the React Profiler and browser performance tools. Identify whether the cost is JavaScript execution, excessive commits, layout/paint, network waterfalls, large bundles, or too many DOM nodes.

Then apply a targeted solution:

- move state closer to where it changes;
- avoid unnecessary effect-driven state chains;
- memoize an expensive derived calculation with `useMemo`;
- use `memo` for an expensive child that often receives unchanged props;
- stabilize props with `useCallback`/`useMemo` only when identity prevents a measured optimization;
- virtualize very large lists;
- debounce high-frequency network input where appropriate;
- split code by route or expensive feature;
- use transitions/deferred values for non-urgent rendering work.

Memoization has comparison, memory, and maintenance cost. It is an optimization, not a correctness guarantee. In this Todo app, filtering a short list is cheap; `useMemo` demonstrates derived-state caching, but a profiler should decide whether it is necessary in production.

### 14. What Does Accessible React UI Require Beyond Adding ARIA Attributes?

Start with semantic HTML: real buttons, labels, headings, lists, forms, and dialogs. Native elements provide keyboard and assistive-technology behavior that custom clickable elements must reimplement.

Then ensure:

- all interactions work with a keyboard;
- focus moves intentionally when dialogs open/close and after destructive actions;
- visible focus is not removed;
- inputs have labels and errors are associated with `aria-describedby`;
- loading and dynamic feedback are announced without excessive interruption;
- color contrast and zoom/reflow work;
- disabled and busy states remain understandable.

This app has good foundations such as labels, `role=alert`, `aria-invalid`, and `aria-busy`. Accessibility still requires manual keyboard and screen-reader checks. ARIA can improve semantics, but incorrect ARIA can make native behavior worse.

### 15. What Testing Strategy Would You Use for a React Feature?

Use a layered, risk-based strategy:

1. Unit-test pure mapping, validation, reducer, and formatting logic.
2. Component/integration-test behavior through accessible roles and user actions with Testing Library.
3. Mock the network at the HTTP boundary, preferably with a tool such as MSW, so API client, hook, and component behavior run together.
4. Add a small number of end-to-end tests for critical browser workflows against a realistic backend.

Test loading, empty, success, validation, retry, cancellation, concurrent actions, and failure states—not only the happy path. Assert what the user observes rather than component internals.

Avoid snapshots as the primary behavioral strategy; large snapshots often approve accidental changes without explaining the broken requirement. Tests should be deterministic, isolated, and capable of catching contract drift.

### 16. How Would You Structure a React Application as It Grows?

Prefer feature-oriented boundaries over one global folder per technical type. This app already groups the Todo page, hook, types, and components under `features/todos`, while shared HTTP and configuration live outside the feature.

A scalable dependency direction is:

```text
route/page composition
        ↓
feature components and hooks
        ↓
domain types and feature services
        ↓
shared API/configuration infrastructure
```

Keep domain rules outside presentational components, define narrow component props, and expose a small public API from each feature. Avoid a generic `utils` or `components` directory becoming an unowned dumping ground.

Architecture should respond to actual change patterns. Do not create repositories, contexts, or abstraction layers solely to look “enterprise.” A good boundary makes related changes local, supports independent tests, and prevents infrastructure details from leaking into every component.

### 17. What Frontend Security Risks Should a Senior React Developer Understand?

React escapes interpolated text by default, which reduces XSS risk, but security is not automatic. Dangerous HTML insertion, unsafe URL construction, untrusted third-party scripts, and DOM APIs can reintroduce XSS. Sanitize trusted use cases with a well-maintained policy and enforce a Content Security Policy where possible.

Authentication and authorization are different. Hiding a button is UX, not authorization; the backend must enforce every permission. Avoid placing long-lived sensitive tokens in storage accessible to injected JavaScript. Cookie-based sessions require appropriate `HttpOnly`, `Secure`, and `SameSite` settings and may require CSRF defenses depending on the architecture.

Also consider dependency supply-chain risk, source-map exposure, secrets accidentally bundled through frontend environment variables, clickjacking, open redirects, and sensitive data in logs or monitoring events.

A frontend cannot keep a shipped secret: anything included in browser code or network requests is observable by the user. Security decisions must be designed across browser, CDN, API, identity provider, and backend boundaries.

## Further Reading

- [TypeScript: Declaration Merging](https://www.typescriptlang.org/docs/handbook/declaration-merging.html)
- [React: Render and Commit](https://react.dev/learn/render-and-commit)
- [React: Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)
- [React: Preserving and Resetting State](https://react.dev/learn/preserving-and-resetting-state)
- [React: `useMemo`](https://react.dev/reference/react/useMemo)
- [React: `useCallback`](https://react.dev/reference/react/useCallback)
- [React: `memo`](https://react.dev/reference/react/memo)
