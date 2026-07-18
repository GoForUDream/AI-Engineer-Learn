# 06. Authentication Basics

Goal: Identify users and protect user-owned data.

## Why This Matters

AI applications often contain private conversations, documents, and provider settings. Authentication identifies the caller; authorization decides which data that caller may access.

## Exercise

Add registration, login, logout, and a current-user endpoint. Make todos and uploaded files user-owned.

Support these endpoints:

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

## Build Steps

1. Add a `users` table with a unique normalized email.
2. Hash passwords with a maintained password-hashing library.
3. Create a short-lived signed session or token delivered in an HttpOnly cookie.
4. Add a FastAPI dependency that resolves the current user.
5. Protect todo and upload endpoints.
6. Filter every user-owned query by the authenticated user ID.
7. Build login, registration, logout, and protected-route UI states.
8. Test wrong passwords, missing sessions, expired sessions, and cross-user access.

## Security Boundaries

- Never store or log a plain-text password.
- Never put a long-lived authentication token in browser local storage.
- A hidden frontend button is not authorization.
- Return a generic login failure instead of revealing whether an email exists.
- Store only model/provider names for now, not provider API keys.

## Done When

- A user can register, sign in, refresh the page, and sign out.
- Unauthenticated requests cannot access protected endpoints.
- User A cannot read or modify User B's records.
- Password hashes cannot be used as API response fields.
- You can explain authentication, authorization, sessions, and tokens.

## Reflection

- Why must authorization be enforced in the database query or service layer?
- What are the benefits of an HttpOnly cookie?
- What additional protection is needed when cookies are used across sites?
