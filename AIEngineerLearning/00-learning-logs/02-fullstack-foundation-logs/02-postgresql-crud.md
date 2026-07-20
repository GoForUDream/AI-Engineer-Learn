# PostgreSQL CRUD — Architecture Learning Log

## 1. Verified Project State

The project uses:

- FastAPI for HTTP routing and dependency injection.
- Pydantic for request, response, error, and settings validation.
- SQLAlchemy 2.0 for database access and session management.
- PostgreSQL as durable storage.
- Alembic for versioned schema migrations.
- Docker Compose for development and test databases.
- Pytest with migrations and transaction-isolated tests.

Verified result:

```text
postgres      healthy on localhost:5432
postgres_test healthy on localhost:5433
18 tests passed
```

## 2. Current Architecture

```text
HTTP request
    ↓
FastAPI router
    ↓
Pydantic request validation
    ↓
get_db_session()
    ↓
request-scoped SQLAlchemy Session
    ↓
get_todo_service()
    ↓
TodoService
    ↓
TodoRepository
    ↓
SQLAlchemy ORM
    ↓
connection pool
    ↓
PostgreSQL
```

On the response path:

```text
PostgreSQL row
    ↓
SQLAlchemy Todo model
    ↓
TodoResponse.model_validate()
    ↓
FastAPI response-model validation
    ↓
JSON response
```

The main responsibility boundaries are:

| Layer | Responsibility |
| --- | --- |
| Router | HTTP paths, methods, status codes, and API schemas. |
| Dependency layer | Creates request-scoped sessions, repositories, and services. |
| Service | Application use cases and transaction decisions. |
| Repository | SQLAlchemy queries and persistence operations. |
| ORM model | Database table mapping. |
| Pydantic schema | External API and configuration validation. |
| Alembic | Database schema history and repeatable deployment changes. |

# Answers to Existing Questions

## 3. What Is the Difference Between `BaseModel` and `BaseSettings`?

### `BaseModel`

`BaseModel` represents and validates normal application data.

This project uses it for:

- `TodoCreate` request bodies.
- `TodoUpdate` PATCH bodies.
- `TodoResponse` API responses.
- `ErrorResponse` error contracts.

Example:

```python
class TodoCreate(BaseModel):
    title: str
    description: str = ""
```

The values normally come from Python data or an HTTP body:

```python
payload = TodoCreate(
    title="Learn PostgreSQL",
    description="Practice SQLAlchemy",
)
```

`BaseModel` validates the supplied data but does not automatically search environment variables for missing values.

### `BaseSettings`

`BaseSettings` comes from `pydantic-settings` and is designed for application configuration.

This project uses:

```python
class Settings(BaseSettings):
    database_url: str
    database_pool_size: int = 5
```

When `Settings()` is created, it can load values from:

- Process environment variables.
- The configured `.env` file.
- Explicit constructor arguments.
- Default field values.

It also converts strings from the environment into declared types. For example:

```text
DATABASE_ECHO=false
DATABASE_POOL_SIZE=5
```

becomes:

```python
settings.database_echo == False
settings.database_pool_size == 5
```

### Main Difference

| Feature | `BaseModel` | `BaseSettings` |
| --- | --- | --- |
| Main purpose | Validate application data | Load and validate configuration |
| Typical source | Request body or Python dictionary | Environment variables and `.env` |
| Used here for | Todos and API errors | App and database settings |
| Missing required field | Validation error | Configuration validation error |
| Environment lookup | No automatic lookup | Yes |

`BaseSettings` still uses Pydantic validation. It adds configuration-source behavior on top of model validation.

## 4. How Is Database Configuration Set in `config.py`?

The configuration class declares every setting the application expects:

```python
class Settings(BaseSettings):
    app_name: str = "Todo API"
    app_env: Literal["development", "test", "staging", "production"]
    app_debug: bool = False
    database_url: str
    test_database_url: str | None = None
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout_seconds: int = 30
    database_pool_recycle_seconds: int = 1800
```

The settings configuration says:

```python
model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="ignore",
)
```

### Meaning of Each Configuration Option

#### `env_file=".env"`

Loads local settings from `.env` when process environment values are not supplied.

Why it matters:

- Developers do not hardcode credentials.
- Each environment can supply different connection details.
- `.env.example` documents required variables without containing real secrets.

#### `env_file_encoding="utf-8"`

Reads the file predictably using UTF-8.

#### `case_sensitive=False`

Allows environment names to be matched without requiring exact letter case. The conventional uppercase variables still map to lowercase Python fields.

#### `extra="ignore"`

Ignores environment values that are not declared by this settings class. This is useful because one `.env` file may contain settings for several components.

### Why Each Database Setting Exists

#### `database_url`

```text
postgresql+psycopg://user:password@host:port/database
```

It tells SQLAlchemy:

- Database dialect: PostgreSQL.
- Driver: psycopg.
- Credentials.
- Network host and port.
- Database name.

It is required because the application cannot build its engine without a destination.

#### `test_database_url`

Separates test data from development data. Tests must never delete or roll back real development/production records.

The test fixture also refuses a URL that does not appear to identify a test database.

#### `database_echo`

Controls SQLAlchemy SQL logging. It is useful while learning or debugging but should usually remain off in production because logs can be noisy and may reveal data.

#### `database_pool_size`

Controls the number of persistent connections maintained by each SQLAlchemy engine process.

A connection pool avoids creating a new TCP/database connection for every request.

#### `database_max_overflow`

Allows temporary connections above the normal pool size during bursts.

With the current defaults, one process may use:

```text
5 persistent connections + 10 overflow connections = 15 maximum checked-out connections
```

#### `database_pool_timeout_seconds`

Specifies how long a request waits for an available pooled connection before failing.

Without a bound, requests could wait indefinitely when the pool is exhausted.

#### `database_pool_recycle_seconds`

Replaces older connections after a configured age. This helps when infrastructure closes idle or long-lived connections.

### Configuration Data Flow

```text
.env / process environment
        ↓
Settings()
        ↓ Pydantic conversion and validation
Settings object
        ↓
get_settings()
        ↓
database.py
        ↓
build_engine(...)
```

## 5. What Does `@lru_cache` Do for `get_settings()`?

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`lru_cache` stores the result of a function call. Because `get_settings()` has no arguments, there is only one possible cache key.

### First Call

```text
get_settings()
    ↓ cache miss
Settings() reads environment and .env
    ↓ validates values
Settings object cached and returned
```

### Later Calls

```text
get_settings()
    ↓ cache hit
same Settings object returned
```

### Why It Is Useful

- Avoids rereading `.env` repeatedly.
- Avoids rebuilding and revalidating configuration.
- Gives the process one consistent settings snapshot.
- Makes `get_settings` suitable as a FastAPI dependency if needed.

### Trade-Off

Environment changes made after the first call are not automatically visible. This is normally desirable in production because configuration should be stable for the lifetime of a process.

Tests intentionally call:

```python
get_settings.cache_clear()
```

after changing `DATABASE_URL`. Clearing the cache forces the next call to construct settings from the updated environment.

This cache is process-local. Every Uvicorn worker process gets its own cached `Settings` object.

## 6. How Are Database Settings Applied in `database.py`?

### Naming Convention

```python
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
```

This gives indexes and constraints deterministic names.

Why it matters:

- Alembic can refer to constraints reliably.
- Migration diffs are more predictable.
- Database errors and operations are easier to understand.
- Different environments produce consistent schema names.

### Declarative Base

```python
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

Every ORM table model inherits from `Base`. `Base.metadata` becomes the complete SQLAlchemy schema description used by Alembic autogeneration.

### Engine Construction

```python
engine = build_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout_seconds,
    pool_recycle=settings.database_pool_recycle_seconds,
)
```

The engine is SQLAlchemy's central database connectivity object. It owns the connection pool and knows which dialect and driver to use.

Important settings:

- `pool_pre_ping=True` checks a connection before giving it to a session.
- `pool_size` controls normal retained connections.
- `max_overflow` controls temporary burst capacity.
- `pool_timeout` bounds how long connection checkout waits.
- `pool_recycle` replaces aging connections.

### Session Factory

```python
SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)
```

`SessionFactory` is not a session. It is a configured callable that creates sessions.

#### `autoflush=False`

SQLAlchemy does not automatically flush pending changes before every query. The repository explicitly flushes where it needs database-generated values or persistence checks.

Trade-off: developers must understand when a flush is required.

#### `expire_on_commit=False`

Objects keep their loaded attribute values after commit.

This project can serialize `created_todo` after committing without SQLAlchemy automatically expiring every field.

Trade-off: the in-memory object may become stale if another transaction modifies the row.

### Session Dependency

```python
def get_db_session() -> Generator[Session, None, None]:
    session = SessionFactory()

    try:
        yield session
    finally:
        session.close()
```

FastAPI starts the generator, injects the yielded session, and executes the `finally` block after the request finishes.

## 7. What Does `@model_validator(mode="after")` Mean?

```python
@model_validator(mode="after")
def reject_null_for_required_fields(self) -> TodoUpdate:
```

A model validator can run before or after normal field validation.

`mode="after"` means:

1. Pydantic parses the raw input.
2. Field types and field constraints are validated.
3. A `TodoUpdate` instance is created.
4. The model validator receives that validated instance.
5. The validator checks relationships or rules involving the complete model.

That is why the method receives `self` and can inspect:

```python
self.model_fields_set
```

`model_fields_set` contains fields explicitly sent by the client.

### Why This Is Needed for PATCH

These requests mean different things:

```json
{}
```

`title` was omitted, so keep the existing title.

```json
{"title": null}
```

`title` was explicitly provided as null, so reject it.

```json
{"due_at": null}
```

`due_at` was explicitly cleared, which is allowed.

The validator intersects supplied fields with the non-nullable group:

```python
self.model_fields_set & {
    "title",
    "description",
    "completed",
}
```

Only explicitly supplied non-nullable fields are checked for `None`.

An after-validator is appropriate because it needs the fully parsed model and the complete field-set context.

## 8. What Is a Database Session?

A SQLAlchemy `Session` is a unit-of-work and transaction-management object.

It is not the same as a raw database connection. The session borrows connections from the engine's pool as needed.

A session:

- Tracks ORM objects loaded or changed during a unit of work.
- Maintains an identity map so one row normally maps to one Python object within the session.
- Collects pending inserts, updates, and deletes.
- Flushes SQL statements to the database.
- Commits or rolls back a transaction.
- Refreshes objects from persisted database state.

### Session Lifecycle in This Project

```text
Request starts
    ↓
get_db_session creates Session
    ↓
repository and service share that Session
    ↓
service performs use case
    ↓
service commits or rolls back writes
    ↓
response is produced
    ↓
get_db_session closes Session
```

### Why One Session Per Request?

- All database work for one request shares one unit of work.
- The service and repository see consistent ORM identity state.
- Sessions are not shared concurrently between requests.
- The session is always closed through dependency cleanup.
- Connection checkout is returned to the pool.

### Why Does the Service Control Commit and Rollback?

The service understands the complete use case. A future operation might modify several repositories and must commit all changes together.

If each repository committed independently, a multi-step use case could partially succeed.

```text
Service transaction
├── repository operation A
├── repository operation B
└── one final commit
```

If either operation fails, the service can roll back the whole unit.

### What Does `flush()` Do?

`flush()` sends pending SQL to PostgreSQL but does not finalize the transaction.

That allows:

- Database constraints to fail before commit.
- Server-generated values to become available.
- The service to continue the same transaction.

### What Does `commit()` Do?

It makes the transaction durable and visible according to PostgreSQL isolation rules.

### What Does `rollback()` Do?

It abandons uncommitted changes and returns the session to a usable transaction state after failure.

### What Does `close()` Do?

It releases session resources and returns checked-out connections to the pool. Closing is not a substitute for an intentional commit or rollback.

### Trade-Offs

#### Benefits

- Clear unit-of-work boundary.
- ORM identity tracking.
- Transaction control.
- Connection-pool integration.
- Dependency injection and test override support.

#### Costs and Risks

- Sessions are stateful and not thread-safe.
- Long sessions retain objects and connections.
- Unclear commit ownership can cause partial transactions.
- Lazy-loaded relationships can trigger unexpected queries.
- `expire_on_commit=False` can leave stale in-memory values.
- Synchronous sessions occupy a thread while waiting for database I/O.

# System Design and Architecture Interview Questions and Answers

## 9. Why Use Router, Service, and Repository Layers?

The router owns HTTP concerns: request schemas, path parameters, response models, and status codes. The service owns application use cases and transaction boundaries. The repository owns SQLAlchemy queries and persistence mechanics.

This separation lets each layer change for a different reason. Replacing PostgreSQL query details should not rewrite routes. Changing an HTTP response should not require changing SQL. The trade-off is additional files and indirection, so this structure is justified when the project is expected to grow.

## 10. Where Should a Transaction Begin and End?

A transaction should normally match one application use case.

In this project, the service begins conceptually when a create, update, or delete method starts and ends when the service commits or rolls back. Repository methods flush but do not commit.

That design allows one service operation to call multiple repositories and commit them atomically. If repositories committed individually, a later failure could leave partial data persisted.

## 11. Why Is the Session Request-Scoped Instead of Global?

SQLAlchemy sessions are mutable units of work and are not safe to share across concurrent requests.

A request-scoped session isolates transaction and identity-map state. It also creates a predictable cleanup boundary. A global engine and connection pool are appropriate, but a global session would mix unrelated requests, hold stale objects, and create concurrency bugs.

## 12. What Is the Repository Pattern Buying This Project?

The repository centralizes persistence operations such as `select`, `add`, `flush`, `refresh`, and `delete`. The service can describe use cases without constructing SQLAlchemy statements.

It also creates a future seam for repository unit tests or alternative implementations. The limitation is that this repository is a concrete class rather than a formal protocol, and the service still imports SQLAlchemy `Session`. The boundary could become stricter if database independence became an actual requirement.

## 13. How Does Connection Pool Size Affect Deployment Capacity?

Pool settings apply per engine process, not globally.

With:

```text
pool_size = 5
max_overflow = 10
```

one worker can check out up to 15 connections during a burst.

If there are four workers:

```text
4 × (5 + 10) = up to 60 connections
```

If the service runs on three instances with four workers each:

```text
3 × 4 × 15 = up to 180 connections
```

The database must support that connection count with room for migrations, administration, and other services. Pool tuning must consider worker count, replica count, request latency, concurrency, and PostgreSQL limits together.

## 14. Why Does PostgreSQL Allow Multiple Uvicorn Workers Here?

The earlier in-memory service stored different data in every process. This version stores todos in shared PostgreSQL.

Every worker has its own engine and pool, but all workers connect to the same durable database. Data created through one worker is therefore available to another.

The remaining concern is total pool capacity and transaction concurrency, not process-local data loss.

## 15. Why Use Alembic Instead of `Base.metadata.create_all()` at Startup?

`create_all()` can create missing tables, but it does not provide a reviewed, ordered history of schema evolution.

Alembic migrations:

- Record exactly how schema changes over time.
- Can be reviewed with application changes.
- Reproduce schemas across environments.
- Support controlled upgrade and downgrade operations.
- Avoid every app worker racing to mutate production schema at startup.

Migrations should normally run as a separate deployment step before or during a compatible rollout.

## 16. Was Adding `due_at` a Safe Schema Evolution?

Adding a nullable column is generally compatible with existing rows because old rows can store `NULL`.

The migration then adds an index. On a very large production table, creating a normal index may block writes depending on PostgreSQL behavior and deployment conditions. A production migration might use a concurrent index strategy and separate transaction handling.

Application rollout should also be ordered so old and new app versions can both tolerate the transitional schema.

## 17. Why Guarantee Ordering with `created_at` and `id`?

Ordering only by `created_at` can be nondeterministic when two rows share the same timestamp. Adding `id` creates a stable tie-breaker.

Stable ordering matters for:

- Repeatable API behavior.
- Deterministic tests.
- Cursor pagination.
- Avoiding duplicate or skipped records across pages.

At scale, the database should have a composite index matching the query order:

```text
(created_at, id)
```

The current separate `created_at` index may not be as effective as a matching composite index for cursor pagination.

## 18. How Would You Add Pagination?

I would use keyset pagination rather than large offsets.

The request could accept a bounded `limit` and an opaque cursor encoding the last `created_at` and `id`.

The next query would apply:

```text
WHERE (created_at, id) > (:last_created_at, :last_id)
ORDER BY created_at, id
LIMIT :limit_plus_one
```

Keyset pagination avoids scanning and discarding increasingly large offsets and remains more stable under concurrent inserts.

## 19. What Is the N+1 Query Problem?

The N+1 problem occurs when the application loads a collection with one query and then performs one additional query for each item, often through lazy-loaded relationships.

```text
1 query for 100 todos
+ 100 queries for each todo's owner
= 101 queries
```

This project has no relationships yet, so the current list query is one query. If owners, tags, or projects are added, loading strategy must be chosen deliberately using joins or eager-loading options.

## 20. How Would You Prevent Lost Updates?

Two clients can read the same todo and then PATCH it. The later commit may silently overwrite the earlier update.

I would add optimistic concurrency control:

- A version column or revision number.
- Return the version in the response.
- Require the client to send the version or `If-Match` value.
- Update with both ID and expected version.
- Increment version on success.
- Return a conflict or precondition response when no row matches.

PostgreSQL row locks are another option for short server-controlled workflows, but they should not be held while waiting for user interaction.

## 21. Why Return `503` for Database Failures?

A database outage is usually a temporary server dependency failure, not invalid client input.

`503 Service Unavailable` tells clients and infrastructure that the service currently cannot complete the operation. The response hides SQL details while logs retain the operation and exception chain.

Clients should retry only appropriate idempotent operations, using backoff and jitter. Retrying every failed write automatically could create duplicate effects.

## 22. Is the Current `/health` Endpoint Liveness or Readiness?

Because it runs `SELECT 1` against PostgreSQL, it behaves more like a readiness check. It reports whether the process can reach the database and execute a query.

A production service often separates:

- Liveness: the process is alive and should not be restarted.
- Readiness: the instance can serve traffic.
- Startup: initialization or migrations have completed.

If PostgreSQL is briefly unavailable, readiness should fail and remove the instance from traffic, while liveness may remain healthy to avoid restart loops.

## 23. How Would You Scale Reads?

I would first measure whether PostgreSQL is actually the bottleneck.

Possible steps:

1. Add pagination and appropriate indexes.
2. Optimize query shapes.
3. Increase database resources and tune the pool.
4. Add caching only for suitable read patterns.
5. Add read replicas when read volume justifies them.

Read replicas introduce replication lag. A client may create a todo and not immediately see it if the next read goes to a lagging replica. Read-after-write requirements must determine routing.

## 24. When Would You Add Caching?

I would add caching only after identifying repeated expensive reads with acceptable staleness.

A todo-by-ID cache would require invalidation on update and delete. List caches are harder because many mutations affect them.

For this CRUD project, PostgreSQL with indexes is simpler and likely sufficient. Premature caching creates invalidation complexity without proven benefit.

## 25. How Do Database Constraints and Pydantic Validation Differ?

Pydantic protects the API boundary and gives clients fast, readable errors. Database constraints protect persisted integrity regardless of which process writes the data.

Critical rules should exist in the database when possible because data may be written by migrations, scripts, workers, or another service.

For example:

- Pydantic limits title length.
- PostgreSQL `VARCHAR(200)` also limits title storage.
- Non-null columns prevent invalid writes outside FastAPI.
- Foreign keys and uniqueness rules belong in PostgreSQL.

## 26. How Does the Test Architecture Protect Real Data?

Tests require `TEST_DATABASE_URL` and reject a URL that does not appear to identify the test database.

At session scope, Alembic upgrades the test database from migrations and downgrades it afterward. Each test opens a connection and outer transaction. The SQLAlchemy session joins using a savepoint, so service commits do not commit the outer test transaction.

After each test, the outer transaction rolls back, restoring isolation without recreating the entire schema.

## 27. Why Test Migrations Instead of Creating Tables from ORM Metadata?

Using Alembic in tests proves the deployment path actually produces a working schema.

If tests used `Base.metadata.create_all()`, the ORM model could work while migration files were missing, out of order, or incorrect. Migration-backed tests verify that a new environment can be built from the same artifacts used in deployment.

## 28. What Is the Risk of a Global Engine Created at Import Time?

Importing `app.database` immediately loads settings and creates the engine. This is simple, but configuration must be correct before import.

Trade-offs include:

- Tests must control environment before importing database modules.
- Reconfiguring the engine in one process is difficult.
- Application startup ownership is less explicit.
- Engine disposal during shutdown is not currently managed by lifespan.

A larger application may create and dispose the engine in FastAPI lifespan state, then inject a session factory from that managed resource.

## 29. Sync or Async SQLAlchemy?

The project uses synchronous SQLAlchemy sessions and synchronous routes. FastAPI runs synchronous route/dependency work in a thread pool, so blocking database calls do not directly block the event loop.

Async SQLAlchemy can reduce thread usage for high-concurrency I/O workloads when the driver and entire call chain are async. It also increases complexity and does not make database queries themselves execute faster.

I would choose based on measured concurrency needs, team familiarity, library compatibility, and operational simplicity.

## 30. How Would You Observe This Database Layer in Production?

I would collect:

- Request rate, status, and latency by route.
- Database query latency and error rate.
- Pool checked-out connections and checkout wait time.
- Pool timeout and overflow usage.
- PostgreSQL connection count, CPU, locks, slow queries, and replication lag.
- Transaction rollback counts.
- Migration version.

Structured logs should include a request ID, operation name, route, and safe error category without credentials or raw sensitive SQL parameters.

## 31. How Would You Design Backup and Recovery?

I would define recovery objectives first:

- RPO: acceptable amount of data loss.
- RTO: acceptable restoration time.

Then use automated PostgreSQL backups, point-in-time recovery through WAL archiving where needed, retention policies, encryption, and access controls.

A backup is not trustworthy until restoration is tested. Recovery drills should verify that the application can connect, migrations align, and data integrity checks pass.

## 32. How Would You Deploy Migrations Safely?

I would avoid running migrations independently in every web worker.

A safe deployment flow is:

1. Back up or ensure recovery capability.
2. Run one controlled migration job.
3. Use backward-compatible expand changes first.
4. Deploy application code that supports the expanded schema.
5. Backfill data separately when large.
6. Switch reads/writes to the new shape.
7. Remove old columns only in a later release.
8. Monitor and preserve rollback options.

Large schema changes should be evaluated for table locks, rewrite cost, index build time, and mixed-version application compatibility.

## 33. What Architectural Improvements Would You Prioritize Next?

For the next production-oriented iteration, I would prioritize:

1. Composite pagination index and bounded pagination.
2. Explicit application lifespan for engine disposal.
3. Repository protocol if multiple implementations or stronger unit isolation are needed.
4. Optimistic concurrency using a version column.
5. Authentication and owner-scoped queries.
6. Separate liveness and readiness endpoints.
7. Structured logging and pool/database metrics.
8. CI that starts PostgreSQL and runs Alembic-backed tests.
9. Controlled migration deployment documentation.
10. Backup and restoration procedures.

These changes address correctness and operability before adding caching or distributed complexity.
