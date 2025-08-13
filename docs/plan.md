# Test Plan for Sections 3 and 4 (Workspace + Multimodule)

This plan follows strict TDD (Red → Green → Refactor) and Tidy First.
We will implement the smallest vertical slices, one test at a time.

Conventions:
- [ ] = not implemented yet
- [x] = implemented and passing
- Keep tests minimal; add code only to pass the current test

---

## Section 3: First Workspace Project (my-core)

1. [x] my_core.models.User.greeting returns "Hello, {name}!"
2. [x] my_core.models.User can be instantiated with id, name, email
3. [x] my_core.models.User.model_dump() contains id, name, email keys

## Section 4: Multimodule Design (my-api depends on my-core)

4. [x] my_api.main app root GET "/" returns {"message": "Welcome to My API"}
5. [x] POST "/users/" echoes a valid User (id, name, email)
6. [x] GET "/users/" returns list of created users
7. [x] GET "/users/{id}" returns the matching user or 404 if missing

Notes:
- Keep in-memory storage for users as a simple list per curriculum.
- Do not over-design; build only enough to satisfy each test.
- Structural steps (workspace layout, pyproject changes) precede behavioral tests when required.
