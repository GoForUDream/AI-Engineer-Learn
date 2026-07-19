# FastAPI Todo API — Backend Interview Question Bank

## 1. Current Project Assessment

This project currently demonstrates:

- Resource-oriented CRUD endpoints.
- Separate create, update, response, and error schemas.
- Pydantic request and response validation.
- FastAPI dependency injection.
- An application factory.
- Centralized exception handlers.
- A separate service and domain entity.
- Thread-safe in-memory mutation with `RLock`.
- Isolated tests using a fresh app per test.
- Success and important failure-path coverage.

Verified test result:

```text
18 passed
```

There are dependency deprecation warnings, but no failing tests.

As an interviewer, I would evaluate this as a strong junior or early mid-level learning project. Junior questions verify that the candidate understands what they built. Mid-level questions test design tradeoffs and failure behavior. Senior questions test how the candidate would evolve the application into a secure, observable, distributed production service.

## 2. How Interview Levels Differ

| Level | What the Interviewer Looks For |
| --- | --- |
| Junior | Correct explanation of HTTP, FastAPI, validation, code flow, and tests. |
| Mid-level | Tradeoffs, boundaries, concurrency, persistence, maintainability, and testing strategy. |
| Senior | Production architecture, scaling, reliability, security, observability, and migration strategy. |

A candidate should not only describe what the code does. Stronger answers explain why the design exists, its limitations, and what should change when requirements grow.

## 3. Interview Questions and Model Answers

These are reference answers, not scripts to memorize word for word. Practice explaining the idea in your own language, then use the project code as evidence.

### Junior-Level Questions and Answers

#### Question 1: Why are these routes resource-oriented?

The main resource is a todo. `/api/todos` represents the todo collection, while `/api/todos/{todo_id}` represents one todo. The HTTP method describes what happens to that resource: POST creates, GET reads, PATCH partially updates, and DELETE removes.

I prefer this design over action-based paths such as `/createTodo` because the URL identifies the resource and standard HTTP semantics identify the operation. It also makes the API easier for clients, documentation tools, and monitoring systems to understand.

#### Question 2: Why does create return `201 Created`?

`201 Created` communicates that the request successfully created a new resource. A normal `200 OK` would say the request succeeded, but it would not express the more specific creation result.

This endpoint also returns the created todo, including server-generated fields such as `id` and `created_at`. In a production API, I would consider adding a `Location` header containing something like `/api/todos/{new_id}`.

#### Question 3: Why does delete return `204 No Content`?

`204 No Content` means the delete operation succeeded and the server has no response representation to send. The response must not contain a body, which is why the route returns an empty FastAPI `Response`.

If the product needed to return deletion metadata or the deleted object, I would choose a status such as `200 OK` instead. For this contract, `204` is clear and minimal.

#### Question 4: What is the difference between `400`, `404`, and `422`?

`400 Bad Request` is a general client-error response when the request cannot be processed because it is malformed or semantically invalid. `404 Not Found` means the requested resource does not exist. `422 Unprocessable Content` means the request can be parsed, but one or more values fail the endpoint's validation contract.

In this project, a missing todo returns `404`. A malformed UUID, empty title, unknown request field, or rejected null value returns `422` through the centralized validation handler.

#### Question 5: Why is `todo_id` typed as `UUID`?

Typing the path parameter as `UUID` makes FastAPI validate and convert the incoming string before the route logic runs. The service therefore receives a real UUID instead of repeatedly parsing strings.

Invalid UUID text produces a consistent `422` response. UUIDs also avoid exposing a simple sequential identifier, although UUIDs alone do not provide authorization or security.

#### Question 6: How does `TodoServiceDependency` reach a route?

`TodoServiceDependency` is an `Annotated` type that combines `TodoService` with `Depends(get_todo_service)`. When FastAPI prepares a route call, it sees the dependency marker and calls `get_todo_service(request)`.

That function reads `request.app.state.todo_service` and returns it. FastAPI then passes the returned service into the route parameter. This keeps routes from constructing their own service and gives the application control over service lifetime.

#### Question 7: Why is the service stored in `application.state`?

The todo service is application-scoped state. Each FastAPI app created by `create_app()` owns one service and therefore one in-memory todo collection.

`application.state` is the framework-supported location for arbitrary app-level objects. Reading it through `request.app.state` ensures a route uses the service belonging to the current application. This also supports test isolation because every test fixture creates a fresh app and a fresh service.

#### Question 8: What problem does `create_app()` solve?

`create_app()` centralizes application construction. It creates FastAPI, creates the service, registers routes, registers exception handlers, and returns a complete app.

The factory is valuable for testing because each test can receive a new app instead of sharing the module-level instance. It also gives a clean place to introduce environment configuration, lifespan resources, or alternative dependencies later.

#### Question 9: What does `response_model` do?

`response_model` declares the public response contract. FastAPI validates the returned value against that model, serializes types such as UUID and datetime, filters the output to declared fields, and documents the response in OpenAPI.

It can detect server-side bugs. If a route promises `TodoResponse` but returns a different shape, FastAPI raises `ResponseValidationError` instead of silently publishing an invalid API response.

#### Question 10: Why did `response_model=TodoResponse` fail for the list endpoint?

The service returned `list[TodoResponse]`, but the decorator declared one `TodoResponse`. FastAPI therefore tried to treat the outer list as one object with fields such as `id` and `title`.

Both a populated list and an empty list have the wrong outer shape. Changing the declaration to `response_model=list[TodoResponse]` aligned the runtime value, Python return annotation, OpenAPI schema, and validation contract.

#### Question 11: Why are create, update, and response schemas separate?

They represent different contracts. `TodoCreate` accepts only values the client may provide during creation. It excludes server-owned fields such as `id`, `created_at`, and the initial completion state.

`TodoUpdate` makes fields optional to support partial updates. `TodoResponse` includes the complete public representation. Separate models reduce accidental mass assignment, clarify ownership, and let each operation evolve independently.

#### Question 12: What does `extra="forbid"` protect against?

It rejects fields that are not declared by the Pydantic model. If a client sends `titel` instead of `title`, the request fails instead of silently discarding the mistake.

It also prevents clients from assuming unsupported fields are being stored. This makes the API contract strict and helps detect client/server schema drift early.

#### Question 13: What does `str_strip_whitespace=True` do?

It removes leading and trailing whitespace from strings during Pydantic validation. For example, `"  Learn FastAPI  "` becomes `"Learn FastAPI"`.

This works well with `min_length=1`. A title containing only spaces is normalized to an empty string and then rejected, preventing visually empty titles from entering the system.

#### Question 14: Why does update use `model_dump(exclude_unset=True)`?

PATCH should change only fields explicitly provided by the client. `exclude_unset=True` returns only fields present in the request body.

This distinction matters because false and empty values can be valid updates. If the client sends `{"completed": false}`, that field must be included. If the client omits `completed`, the existing value must remain unchanged.

#### Question 15: What is the difference between omitted, null, false, and empty string?

An omitted field means “do not change this value.” A supplied `null` means the client explicitly sent no value; this API rejects null for title and description. `false` is a valid boolean value and must update `completed`. An empty description is allowed and means clear the description.

An empty title is supplied but invalid because title requires at least one character after whitespace normalization. These differences are why truthiness checks are not enough for PATCH logic.

#### Question 16: Why does `TodoResponse` use `from_attributes=True`?

The internal `Todo` is a dataclass instance, not a dictionary. `from_attributes=True` tells Pydantic that it may read model fields from object attributes.

That allows `TodoResponse.model_validate(todo)` to read `todo.id`, `todo.title`, and the other attributes. Without this setting, Pydantic would normally expect dictionary-like input for this validation path.

#### Question 17: Why is `Todo` separate from `TodoResponse`?

`Todo` is an internal domain entity, while `TodoResponse` is an external HTTP contract. Keeping them separate prevents API concerns from becoming the application's core data model.

The internal model could later become a SQLAlchemy entity or contain private fields without automatically exposing them. The response model can also change serialization rules without changing domain behavior.

#### Question 18: Why is `Todo` a frozen, slotted dataclass?

A dataclass removes boilerplate by generating initialization, representation, and comparison behavior. `frozen=True` prevents normal field reassignment, so a todo behaves like an immutable value after creation.

`slots=True` restricts instances to declared attributes and usually reduces memory. Because the entity is frozen, updates use `dataclasses.replace()` to create a new entity instead of mutating the existing one.

#### Question 19: What does `dataclasses.replace()` do during update?

`replace(existing_todo, **changes)` creates a new `Todo` using all values from the existing entity, then replaces only the fields contained in `changes`.

This preserves fields such as `id` and `created_at` while applying the PATCH data. The new object is then stored under the same dictionary key. This supports an immutable domain style.

#### Question 20: Why use timezone-aware UTC timestamps?

Naive datetimes do not identify a timezone, so their meaning can be ambiguous across servers and users. UTC provides one consistent storage and comparison standard.

The API can serialize UTC, while a frontend converts it to the user's local timezone. Timezone-aware values also prevent many comparison and daylight-saving errors.

#### Question 21: Why use `TodoNotFoundError` instead of `HTTPException` in the service?

`TodoNotFoundError` describes an application condition without coupling the service to HTTP. The service could later be called by a CLI, background worker, or message consumer.

The FastAPI exception handler maps that domain error to a `404` response. This keeps transport decisions at the API boundary and keeps service logic reusable.

#### Question 22: Why centralize exception handlers?

Central handlers produce one stable error shape across routes and remove repeated error-building code from each endpoint.

The not-found handler maps a known domain condition to `404`. The validation handler normalizes FastAPI/Pydantic details into the application's error contract. The catch-all handler logs unexpected exceptions and returns a safe `500` message without exposing a traceback.

#### Question 23: Why does every test create a new application?

Each created app owns a new `TodoService` and a new dictionary. This prevents a todo created in one test from leaking into another.

As a result, tests are independent of execution order and easier to reason about. Using `TestClient` as a context manager also ensures application lifecycle behavior is entered and exited correctly.

#### Question 24: What behavior is verified by the PATCH tests?

The tests verify normal partial updates, preserving omitted fields, explicitly setting `completed` to both true and false, clearing the description with an empty string, accepting an empty PATCH without changing data, returning `404` for a missing todo, and rejecting a null title.

Together, these tests define the important difference between “not supplied” and “supplied with a false, empty, or invalid value.”

### Mid-Level Questions and Answers

#### Question 25: What are the benefits and limitations of the service layer?

The service keeps route functions thin and centralizes use cases such as create, update, and delete. It also owns synchronization and makes behavior easier to test outside HTTP.

A limitation is that the service currently accepts and returns API Pydantic schemas, so it still depends on the transport layer. I would eventually make it accept application command objects or primitives and return domain entities. I would also move dictionary access behind a repository interface so persistence can change without rewriting business logic.

#### Question 26: How would you replace the dictionary with PostgreSQL?

I would first define a repository contract around the operations the service needs: create, list, get, update, and delete. Then I would implement that contract with SQLAlchemy or another database client.

I would create a migration-managed table with database constraints, use transactions for writes, and map database rows to domain entities. The HTTP routes and response schemas should remain stable. Tests would include service tests with a fake repository and integration tests against an isolated PostgreSQL database.

#### Question 27: Why would multiple Uvicorn workers break the app?

Each worker is a separate operating-system process. Importing `app.main:app` in each worker creates a different FastAPI instance, `TodoService`, and dictionary.

A todo written through worker A is invisible to worker B. A later request may land on another worker and appear to lose data. `RLock` only coordinates threads inside one process. The app needs shared durable storage before it can safely use multiple workers or multiple servers.

#### Question 28: What does `RLock` protect, and what does it not protect?

The lock protects the in-memory dictionary from concurrent access by threads in the same process. It serializes create, update, delete, and snapshot-copy operations.

An `RLock` is reentrant, so the same thread can acquire it again without deadlocking. It does not coordinate multiple processes, containers, or machines. It also does not provide database durability, rollback, isolation levels, or distributed consistency.

#### Question 29: Is `list_all()` consistent during concurrent updates?

It takes a snapshot by copying dictionary values while holding the lock. After releasing the lock, it sorts and converts those frozen entities.

The returned list is internally consistent with that captured moment. A todo created immediately after the copy will not appear until the next call, which is reasonable snapshot behavior. If stronger transactional consistency were required, the requirement and lock/transaction boundary would need to be defined explicitly.

#### Question 30: How would you add pagination?

I would define validated query parameters, preferably a bounded `limit` and an opaque cursor. Results need deterministic ordering such as `created_at, id` so pagination remains stable when timestamps tie.

The response should probably become an envelope containing `items` and `next_cursor`. With PostgreSQL, filtering and limiting must happen in the database rather than after loading every row. I would test empty pages, invalid limits, maximum limits, and continuation without duplicates or skipped records.

#### Question 31: Bare array or response envelope?

A bare array is simple and works for this small API. An envelope is easier to extend with pagination cursors, total counts, links, or metadata.

Changing from a bare array to an envelope later is a breaking response-shape change. If pagination is expected, I would choose the envelope early. If simplicity is the main requirement and the collection is guaranteed small, the array is acceptable.

#### Question 32: How would you prevent lost updates?

The current in-process lock serializes writes only inside one service instance. With a database and multiple servers, I would use transactions and optimistic concurrency.

For example, each row could have a version number. The client submits the version it read, and UPDATE includes `WHERE id = ? AND version = ?`. If no row changes, the write was stale and the API returns a conflict or precondition response. HTTP `ETag` and `If-Match` can expose the same idea at the protocol layer.

#### Question 33: Is POST create idempotent?

No. Every successful call generates a new UUID, so retrying the same POST creates another todo.

For retry-safe creation, I would accept an idempotency key, store it with the result under a uniqueness constraint, and return the original result when the same request is retried. The design must define key scope, expiration, payload conflicts, and whether failed attempts are retained.

#### Question 34: Why are the routes synchronous?

The current operations are synchronous and in-memory. Declaring them with normal `def` is appropriate, and FastAPI can run synchronous route/dependency work in its thread pool.

I would use `async def` when the implementation awaits an asynchronous database or HTTP client. Simply changing a function to async does not make synchronous work faster. CPU-heavy work should be moved away from the event loop, often to workers or processes.

#### Question 35: How should application resources be initialized?

I would use FastAPI's lifespan mechanism. Startup creates long-lived resources such as a database pool or HTTP client, makes them available to dependencies, and shutdown closes them cleanly.

This avoids creating expensive pools per request and prevents leaked connections. Startup should fail clearly if a required resource cannot initialize, and shutdown should be bounded so deployment termination does not hang forever.

#### Question 36: How would you override dependencies in tests?

FastAPI exposes `application.dependency_overrides`. I can map `get_todo_service` to a test function returning a fake or controlled service.

That allows route tests to trigger specific conditions without depending on the real storage implementation. I would remove the override after each test, usually through a fixture, to prevent cross-test contamination.

#### Question 37: What tests are still missing?

I would add boundary tests for maximum title and description sizes, unknown PATCH fields, invalid description values, and ordering when timestamps are equal.

I would also add direct service unit tests, dependency override tests, concurrent mutation tests, and a test for the generic `500` handler. As the project grows, I would add OpenAPI contract checks and database integration tests.

#### Question 38: Are these unit or integration tests?

They are lightweight in-process API integration tests. Each request exercises routing, request validation, dependency injection, the service, response validation, exception handling, and serialization together.

A unit test would call `TodoService` directly and isolate it from FastAPI. A real database test would be a broader integration test. An end-to-end test would usually run the deployed process and call it over a real network boundary.

#### Question 39: Why assert a stable error code?

A code such as `todo_not_found` is a machine-readable contract. A frontend can reliably branch on it, while the human-readable message can be edited or localized.

Stable codes also improve analytics and support diagnostics. They should be documented, tested, and changed carefully because clients may depend on them.

#### Question 40: How would you test the generic `500` handler?

I would override the service dependency with a fake whose method raises an unexpected exception. I would configure the test client so server exceptions are returned as responses rather than immediately re-raised when necessary.

Then I would assert status `500`, the safe `internal_server_error` body, and absence of traceback details. I would capture logs and verify the exception plus request method/path were recorded.

### Senior-Level Questions and Answers

#### Question 41: How would you migrate this app to production without breaking clients?

I would begin by treating the current HTTP behavior as a contract and strengthening tests around it. Then I would introduce a repository interface without changing routes or response models.

Next, I would create the PostgreSQL schema and migrations, implement the repository with transactions, and run integration tests. I would add configuration, secret management, readiness checks, logging, metrics, tracing, and deployment manifests. Rollout should be gradual, observable, and reversible. The public response and error shapes should stay compatible throughout the migration.

#### Question 42: What database schema and indexes would you choose?

I would use a UUID primary key, non-null owner or tenant ID when authentication exists, title, description, completed, created-at, updated-at, and possibly a version column for optimistic locking.

For the current list order, I would index `created_at, id` to support deterministic cursor pagination. Multi-user queries would likely need `owner_id, created_at, id`. Critical limits and nullability should be database constraints as well as application validation.

#### Question 43: How would you make this multi-user?

I would authenticate each request and derive the user identity from verified credentials, never from a client-supplied owner field.

Every todo would store an owner or tenant ID. Every read, update, and delete query would include both todo ID and owner ID. I would test attempts to access another user's resources. Depending on security policy, the API may return `404` to avoid confirming that another user's resource exists.

#### Question 44: How would you secure and abuse-protect the API?

I would add authentication, resource-level authorization, HTTPS, strict CORS, request-size limits, rate limits, and dependency vulnerability management.

I would avoid logging secrets or full sensitive payloads, keep errors generic for unexpected failures, and produce audit events for security-relevant actions. At the platform edge, I would consider a gateway or WAF. Security controls should be threat-driven rather than added as an unprioritized checklist.

#### Question 45: What should `/health` mean in production?

I would separate liveness and readiness. Liveness answers whether the process is functioning enough to remain running. Readiness answers whether the instance can serve traffic, including whether required dependencies such as the database are available.

Checks should be fast, use short timeouts, and avoid revealing infrastructure details. A failing readiness check should remove the instance from traffic without necessarily restarting it immediately.

#### Question 46: What observability would you add?

I would add structured logs with request and correlation IDs, deployment version, route, latency, status, and error category. I would collect request-rate, error-rate, latency-percentile, and resource-saturation metrics.

Distributed traces would show time spent in the API, database, and external calls. Dashboards and alerts should correspond to user-impacting objectives. Sensitive content should be redacted, and high-cardinality values should be controlled.

#### Question 47: What SLOs would you define?

I would define measurable targets based on user expectations, such as monthly availability, p95/p99 latency for reads and writes, and an acceptable server-error rate.

For a durable version, I would also define recovery and data-loss expectations. Alerts should be tied to error-budget burn rather than every single failure. I would validate the targets with load tests and revise architecture when measurements show the service cannot meet them.

#### Question 48: How would you handle API versioning?

I would prefer additive backward-compatible changes: add optional fields, preserve existing meanings, and avoid removing or renaming fields.

For unavoidable breaking changes, I would choose an explicit strategy such as a path or media-type version, publish a migration guide and deprecation deadline, and operate versions long enough for clients to migrate. OpenAPI diffing and contract tests can detect accidental breaking changes in CI.

#### Question 49: How would you implement graceful shutdown?

The deployment should first stop routing new traffic to the instance. The server should allow in-flight requests to finish within a deadline, then close database pools, HTTP clients, and other resources through lifespan shutdown handling.

Telemetry should be flushed where practical. The application's shutdown timeout must align with the platform's termination grace period so deployments do not cut active requests abruptly.

#### Question 50: What risks exist in the catch-all exception handler?

The handler is useful because it logs failures and prevents stack traces from reaching clients. The risk is that broad handling can make serious programming defects look like ordinary responses if monitoring is weak.

I would ensure every unexpected exception is correlated, counted, traced, and alertable. I would avoid swallowing cancellation or system-level signals incorrectly. Tests should verify safe responses while operations tooling makes repeated failures visible.

#### Question 51: How would you design distributed rate limiting?

I would first define the identity and policy: per user, API key, tenant, IP, or a combination. Then I would choose an algorithm such as token bucket or sliding window and decide burst and sustained limits.

Across instances, enforcement needs a shared store such as Redis or an API gateway. The API should return `429 Too Many Requests` and useful retry information. The design must also define what happens when the limiter store is unavailable and avoid allowing one noisy tenant to affect others.

#### Question 52: How would you diagnose increased latency after deployment?

I would first confirm user impact and compare latency percentiles, error rates, traffic, and saturation before and after the deployment. Then I would break the issue down by route and dependency using traces and structured logs.

I would compare code, configuration, dependency versions, database behavior, and infrastructure changes. If impact is significant, I would mitigate quickly through rollback, traffic shifting, or disabling the changed feature. After stabilization, I would preserve evidence, find the root cause, and add preventative tests, alerts, or capacity changes.
