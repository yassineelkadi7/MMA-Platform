# Implementation Plan: MMA Fighting Platform

## Overview

Incremental implementation of the MMA Fighting Platform using Django 5.x, PostgreSQL 16, Bootstrap 5, and Vanilla JS. Each task builds on the previous one, starting with project scaffolding and ending with a fully wired, tested application. The Groq API (llama-3.3-70b-versatile) powers the AI assistant; pdflatex/WeasyPrint handles PDF generation; APScheduler (dev) / Celery+Redis (prod) drives scheduled tasks.

## Tasks

- [x] 1. Project scaffolding and configuration
  - Create the Django project with `django-admin startproject mma_platform .`
  - Create the split settings package: `mma_platform/settings/base.py`, `development.py`, `production.py`
  - Add `INSTALLED_APPS` entries for all six apps (`accounts`, `news`, `events`, `training`, `ai_assistant`, `core`) plus `django.contrib.admin`
  - Configure PostgreSQL 16 database connection via `dj-database-url` and `.env`
  - Add `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_TIMEOUT`, `NEWS_API_KEY`, `SPORTS_API_KEY` to settings loaded from environment
  - Configure `STATIC_ROOT`, `MEDIA_ROOT`, `MEDIA_URL`, `SECURE_SSL_REDIRECT` (production), `ADMINS`
  - Create `requirements.txt` pinning: `Django==5.x`, `psycopg2-binary`, `groq>=0.9`, `requests`, `apscheduler`, `celery`, `redis`, `hypothesis`, `pytest-django`, `WeasyPrint`, `django-environ`
  - Create `pytest.ini` / `pyproject.toml` with `DJANGO_SETTINGS_MODULE=mma_platform.settings.development`
  - Create `apps/` directory and stub `apps.py` for each app
  - _Requirements: 13.1, 13.3, 13.4_

- [x] 2. `core` app — shared utilities
  - [x] 2.1 Create `APICallLog` model in `apps/core/models.py`
    - Fields: `endpoint`, `status_code`, `latency_ms`, `error_message`, `called_at` (auto, db_index)
    - Add composite index on `(called_at, status_code)`
    - _Requirements: 11.2_

  - [x] 2.2 Implement `log_api_call` utility in `apps/core/logging.py`
    - Signature: `log_api_call(endpoint, status_code, latency_ms, error=None) -> APICallLog`
    - Writes one `APICallLog` row atomically
    - _Requirements: 11.2, 11.3_

  - [ ]* 2.3 Write property test for API call log completeness (Property 10)
    - **Property 10: API call log completeness**
    - Generate random endpoint strings and HTTP status codes; call `log_api_call`; assert an `APICallLog` record exists with matching fields
    - **Validates: Requirements 11.2**

  - [x] 2.4 Implement `CacheHelper` in `apps/core/cache.py`
    - `get_or_fetch(key, fetch_fn, ttl_seconds) -> Any` using Django's cache framework
    - _Requirements: 13.3_

  - [x] 2.5 Create initial Django migration for `core` and run `makemigrations`
    - _Requirements: 11.2_

- [x] 3. `accounts` app — authentication and profiles
  - [x] 3.1 Create `User` and `UserSession` models in `apps/accounts/models.py`
    - `User` extends `AbstractUser` with `role`, `preferences` (JSONField), `is_suspended`
    - `UserSession` tracks active session keys per user for forced invalidation
    - _Requirements: 1.1, 2.1, 9.5_

  - [x] 3.2 Implement `RegistrationForm` and `ProfileUpdateForm` in `apps/accounts/forms.py`
    - `RegistrationForm`: unique email validation, password length ≥ 8, role choice field
    - `ProfileUpdateForm`: email format validation, role choice field
    - _Requirements: 1.1, 1.3, 1.4, 2.4_

  - [ ]* 3.3 Write property test for duplicate-email rejection (Property 1)
    - **Property 1: Registration rejects duplicate emails**
    - Generate random valid user data; register once; attempt again with same email; assert validation error and User count unchanged
    - **Validates: Requirements 1.3**

  - [ ]* 3.4 Write property test for short-password rejection (Property 2)
    - **Property 2: Registration rejects short passwords**
    - Generate random strings of length 0–7; assert `RegistrationForm` is invalid and no User is created
    - **Validates: Requirements 1.4**

  - [x] 3.5 Implement account service functions in `apps/accounts/services.py`
    - `register_user(username, email, password, role) -> User`
    - `authenticate_user(email, password) -> Optional[User]`
    - `update_profile(user, data) -> User`
    - `suspend_user(user) -> None` — sets `is_suspended=True`, calls `invalidate_sessions`
    - `invalidate_sessions(user) -> None` — deletes `UserSession` rows and Django session store entries
    - _Requirements: 1.2, 1.5, 1.7, 2.3, 9.4, 9.5_

  - [ ]* 3.6 Write property test for suspended-user session invalidation (Property 12)
    - **Property 12: Suspended user sessions are invalidated**
    - Generate 1–10 active sessions for a user; call `suspend_user`; assert all `UserSession` records deleted and Django session store contains no matching keys
    - **Validates: Requirements 9.5**

  - [x] 3.7 Implement `RegisterView`, `LoginView`, `LogoutView`, `ProfileView` in `apps/accounts/views.py`
    - `RegisterView`: POST → `register_user`, redirect to profile; error on duplicate email / short password
    - `LoginView`: POST → `authenticate_user`, create `UserSession`, redirect to home; generic error on failure (Requirement 1.6)
    - `LogoutView`: invalidate session, redirect to home
    - `ProfileView`: GET displays profile; POST calls `update_profile`, shows confirmation
    - _Requirements: 1.2, 1.5, 1.6, 1.7, 2.2, 2.3, 2.5_

  - [x] 3.8 Wire `accounts` URLs in `apps/accounts/urls.py` and include in `mma_platform/urls.py`
    - Paths: `/accounts/register/`, `/accounts/login/`, `/accounts/logout/`, `/accounts/profile/`
    - _Requirements: 1.1, 2.2_

  - [x] 3.9 Create registration, login, and profile templates using Bootstrap 5
    - `templates/accounts/register.html`, `login.html`, `profile.html`
    - Field-level error display; role selector; confirmation message on profile save
    - _Requirements: 1.1, 2.2, 2.4, 12.1, 12.2_

  - [x] 3.10 Create Django migrations for `accounts`
    - _Requirements: 1.1, 2.1_

- [x] 4. Checkpoint — core and accounts
  - Ensure all migrations apply cleanly (`python manage.py migrate`)
  - Run `pytest apps/core/ apps/accounts/` — all tests pass
  - Ask the user if questions arise.

- [x] 5. `news` app — article fetching and display
  - [x] 5.1 Create `Article` model in `apps/news/models.py`
    - Fields: `external_id` (unique), `title`, `summary`, `source_name`, `source_url`, `category`, `published_at` (db_index), `fetched_at` (auto_now), `is_hidden` (db_index)
    - Composite index on `(category, -published_at)`
    - _Requirements: 3.1, 3.4_

  - [x] 5.2 Implement `NewsAPIClient` in `apps/news/api_client.py`
    - Wraps HTTP GET to the configured news API endpoint
    - Records start time, calls `log_api_call` with status and latency after each request
    - Raises `NewsAPIError` on 4xx/5xx; returns raw JSON on success
    - _Requirements: 3.1, 11.2_

  - [x] 5.3 Implement `NewsFetchService` in `apps/news/services.py`
    - `fetch_and_store_articles() -> FetchResult` — calls `NewsAPIClient`, deduplicates by `external_id`, bulk-inserts new articles, returns `{new_count, errors}`
    - `get_articles(category=None, page=1) -> Page[Article]` — filters `is_hidden=False`, orders by `-published_at`
    - `hide_article(article_id) -> None` — sets `is_hidden=True`
    - _Requirements: 3.2, 3.3, 3.5, 3.7, 10.2_

  - [ ]* 5.4 Write property test for news listing sort order (Property 4)
    - **Property 4: News listing is sorted by publication date descending**
    - Generate random Article objects with random `published_at` values; insert; call `get_articles()`; assert returned list is sorted descending by `published_at`
    - **Validates: Requirements 3.3**

  - [ ]* 5.5 Write property test for hidden article exclusion (Property 5)
    - **Property 5: Hidden articles are excluded from all user-facing listings**
    - Generate random articles, mark a random subset hidden; call `get_articles()`; assert no hidden article appears
    - **Validates: Requirements 3.5, 10.2**

  - [ ]* 5.6 Write property test for category filter correctness (Property 6)
    - **Property 6: Category filter returns only matching articles**
    - Generate articles across all categories; call `get_articles(category=X)` for a random category; assert every returned article has `category == X`
    - **Validates: Requirements 3.5**

  - [x] 5.7 Implement scheduled fetch task in `apps/news/tasks.py`
    - APScheduler job (dev): `IntervalTrigger(minutes=60)` calling `fetch_and_store_articles()`
    - Celery task (prod): `@shared_task` with `beat_schedule` entry at 60-minute interval
    - _Requirements: 3.2_

  - [x] 5.8 Implement `NewsListView` and `NewsDetailView` in `apps/news/views.py`
    - `NewsListView`: paginated, category filter via GET param, renders within 3 s (uses `get_articles`)
    - `NewsDetailView`: title, date, source attribution, summary, external link
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.8_

  - [x] 5.9 Create news templates with Bootstrap 5
    - `templates/news/list.html`: article cards, category tabs, "last updated" indicator
    - `templates/news/detail.html`: full article view with source link
    - _Requirements: 3.3, 3.6, 3.7, 12.1, 12.2_

  - [x] 5.10 Wire `news` URLs and create Django migration
    - Paths: `/news/`, `/news/<int:pk>/`, `/news/?category=<cat>`
    - _Requirements: 3.3, 3.5_

- [x] 6. `events` app — fighters, events, calendar, countdown
  - [x] 6.1 Create `WeightClass`, `Fighter`, `Event`, `Fight` models in `apps/events/models.py`
    - `Fighter`: `external_id` (unique), `full_name` (db_index), `nationality`, `weight_class` FK, `fighting_style`, `wins`, `losses`, `draws`
    - `Event`: `external_id` (unique), `name`, `date` (db_index), `location`, `venue`, `broadcast_info`, `status` choices
    - `Fight`: FK to `Event` and two FKs to `Fighter`, `winner` nullable FK, `method`, `is_main_event`, `bout_order`
    - _Requirements: 4.1, 5.1_

  - [x] 6.2 Implement `EventsAPIClient` in `apps/events/api_client.py`
    - Wraps HTTP GET to the sports API; calls `log_api_call` with latency; raises `EventsAPIError` on failure
    - _Requirements: 5.5, 11.2_

  - [x] 6.3 Implement service functions in `apps/events/services.py`
    - `search_fighters(query) -> list[Fighter]` — case-insensitive `full_name__icontains` lookup
    - `get_next_event() -> Optional[Event]` — nearest future event by `date`
    - `get_event_detail(event_id) -> EventDetail` — event + full fight card + fighter profiles
    - `sync_events_from_api() -> SyncResult` — upserts events and fighters, logs API call
    - _Requirements: 4.2, 4.3, 5.1, 5.4, 5.5_

  - [ ]* 6.4 Write property test for fighter search name matching (Property 7)
    - **Property 7: Fighter search returns only name-matching profiles**
    - Generate random Fighter objects with random names; call `search_fighters(query)`; assert every returned fighter's `full_name` contains the query (case-insensitive) and no non-matching fighter is included
    - **Validates: Requirements 4.2**

  - [x] 6.5 Implement scheduled sync task in `apps/events/tasks.py`
    - APScheduler job (dev): `IntervalTrigger(hours=24)` calling `sync_events_from_api()`
    - Celery task (prod): `@shared_task` with `beat_schedule` entry at 24-hour interval
    - _Requirements: 5.5_

  - [x] 6.6 Implement views in `apps/events/views.py`
    - `FighterListView`: search form, results list, "no results" message
    - `FighterDetailView`: all profile fields + past fight results
    - `EventCalendarView`: returns JSON array of events for the JS calendar widget
    - `EventDetailView`: full fight card, venue, broadcast info, fighter profile links
    - `CountdownAPIView`: JSON `{event_id, name, date, seconds_remaining}` polled by frontend
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.4_

  - [x] 6.7 Create events templates and calendar JS widget
    - `templates/events/fighter_list.html`, `fighter_detail.html`, `event_calendar.html`, `event_detail.html`
    - Vanilla JS calendar widget in `static/js/calendar.js`: fetches `EventCalendarView` JSON, renders month grid
    - Vanilla JS countdown widget in `static/js/countdown.js`: polls `CountdownAPIView` every second, displays days/hours/minutes/seconds; advances to next event when timer reaches zero
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 12.1, 12.2_

  - [x] 6.8 Wire `events` URLs and create Django migrations
    - Paths: `/events/fighters/`, `/events/fighters/<int:pk>/`, `/events/calendar/`, `/events/<int:pk>/`, `/events/api/countdown/`
    - _Requirements: 4.2, 5.1, 5.2_

- [x] 7. Checkpoint — news and events
  - Run `pytest apps/news/ apps/events/` — all tests pass
  - Verify calendar and countdown render correctly in the browser
  - Ask the user if questions arise.

- [x] 8. `training` app — client-side stopwatch
  - [x] 8.1 Create `training` app views and template
    - `TrainingView` (TemplateView): renders `templates/training/stopwatch.html`
    - Template includes Bootstrap layout with start, stop, reset buttons and a `MM:SS.T` display
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 12.1, 12.2_

  - [x] 8.2 Implement stopwatch logic in `static/js/stopwatch.js`
    - Uses `performance.now()` and `requestAnimationFrame` for sub-second accuracy
    - `start()`: begins interval, updates display every 100 ms
    - `stop()`: clears interval, retains elapsed time
    - `reset()`: clears interval, sets elapsed to 0, updates display
    - No `fetch` calls — entirely client-side
    - _Requirements: 6.2, 6.3, 6.4, 6.5_

  - [ ]* 8.3 Write Jest unit tests for stopwatch in `static/js/__tests__/stopwatch.test.js`
    - Test: start → elapsed time increases after tick
    - Test: stop → elapsed time freezes
    - Test: reset → elapsed time returns to 0
    - Test: `fetch` is never called during any operation (mock `fetch`, assert not called)
    - _Requirements: 6.2, 6.3, 6.4, 6.5_

  - [x] 8.4 Wire `training` URL and add `package.json` with Jest config
    - Path: `/training/`
    - `package.json`: `jest`, `@jest/globals`; test script: `jest --testPathPattern=stopwatch`
    - _Requirements: 6.1_

- [x] 9. `ai_assistant` app — chatbot and training program generation
  - [x] 9.1 Create `ConversationMessage` and `TrainingProgram` models in `apps/ai_assistant/models.py`
    - `ConversationMessage`: `session_key` (db_index), `user` FK, `role` choices, `content`, `created_at`; composite index on `(session_key, created_at)`
    - `TrainingProgram`: `user` FK, `title`, `latex_source`, `pdf_file` (FileField), `generated_at`, `parameters` (JSONField)
    - _Requirements: 7.3, 8.4, 8.5_

  - [x] 9.2 Implement `LLMClient` in `apps/ai_assistant/llm_client.py`
    - Wraps `groq.Groq` SDK; `chat(messages, temperature=0.7) -> str`
    - Handles `groq.APITimeoutError`, `groq.APIConnectionError` → raises `LLMUnavailableError`
    - Handles `groq.RateLimitError` → back off 5 s, retry once; raises `LLMUnavailableError` on second failure
    - _Requirements: 7.2, 7.5_

  - [x] 9.3 Implement `ChatService` in `apps/ai_assistant/services.py`
    - `send_message(session_key, user, message) -> str`
      - Loads conversation history from `ConversationMessage` for the session
      - Prepends system prompt with role context and topic restriction
      - Calls `LLMClient.chat()`; persists user and assistant messages
      - On `LLMUnavailableError`: returns user-friendly error string without saving assistant message
    - `is_on_topic(message) -> bool` — keyword/heuristic check for MMA/fitness topics
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 9.4 Implement `ProgramGeneratorService` in `apps/ai_assistant/services.py`
    - `build_prompt(user_role, params) -> list[dict]` — constructs messages list with role-specific system prompt
      - Amateur: foundational technique, general conditioning keywords
      - Coach: periodization structures, athlete management guidance keywords
    - `generate_training_program(user, params) -> TrainingProgram`
      - Calls `build_prompt`, then `LLMClient.chat()`
      - Parses LaTeX from response; calls `LaTeXCompiler.compile(latex) -> bytes`
      - Saves `TrainingProgram` record with `latex_source`, `pdf_file`, `parameters`
      - Raises `IncompleteParamsError` if params are contradictory/incomplete (triggers clarifying questions)
    - _Requirements: 8.1, 8.2, 8.3, 8.6, 8.7_

  - [ ]* 9.5 Write property test for role context in prompt (Property 3)
    - **Property 3: Role context propagates to AI responses**
    - Generate random role values (amateur/coach); call `build_prompt(user_role, params)`; assert amateur prompt contains foundational keywords and coach prompt contains periodization keywords
    - **Validates: Requirements 2.6, 8.2**

  - [ ]* 9.6 Write property test for training program content matching user role (Property 8)
    - **Property 8: Training program content matches user role**
    - Generate random `ProgramParams`; call `build_prompt` for both roles; assert role-specific keyword presence in each prompt
    - **Validates: Requirements 8.2**

  - [x] 9.7 Implement `LaTeXCompiler` in `apps/ai_assistant/latex_compiler.py`
    - `compile(latex_source) -> bytes`
      - Attempts `pdflatex` subprocess in a temp directory; returns PDF bytes on success
      - Falls back to WeasyPrint if `pdflatex` is unavailable
      - Raises `LaTeXCompilationError` with compiler output on non-zero exit code
    - _Requirements: 8.3_

  - [ ]* 9.8 Write property test for training program round-trip persistence (Property 9)
    - **Property 9: Training program round-trip persistence**
    - Generate random program parameters; call `generate_training_program` (mock LLM and LaTeX compiler); retrieve saved program; assert `latex_source` and `parameters` are identical
    - **Validates: Requirements 8.4, 8.5**

  - [x] 9.9 Implement `ChatView` and `GenerateProgramView` in `apps/ai_assistant/views.py`
    - `ChatView` (POST, login_required): calls `send_message`, returns JSON `{reply}`; on `LLMUnavailableError` returns JSON `{error}`
    - `GenerateProgramView` (POST, login_required): validates params, calls `generate_training_program`, returns JSON `{program_id, download_url}`; asks clarifying questions if `IncompleteParamsError`
    - `ProgramDownloadView` (GET, login_required): serves PDF from `TrainingProgram.pdf_file`; 404 if not owned by requesting user
    - `ProgramListView` (GET, login_required): lists user's saved programs
    - _Requirements: 7.1, 7.2, 7.5, 8.1, 8.3, 8.4, 8.5_

  - [x] 9.10 Create chat UI template and program templates
    - `templates/ai_assistant/chat.html`: Bootstrap card with message history, text input, send button; AJAX POST to `ChatView`; displays assistant reply inline
    - `templates/ai_assistant/program_list.html`: list of saved programs with PDF download links
    - _Requirements: 7.1, 7.3, 8.4, 8.5, 12.1, 12.2_

  - [x] 9.11 Wire `ai_assistant` URLs and create Django migrations
    - Paths: `/ai/chat/`, `/ai/generate-program/`, `/ai/programs/`, `/ai/programs/<int:pk>/download/`
    - _Requirements: 7.1, 8.3, 8.4, 8.5_

- [x] 10. Checkpoint — AI assistant
  - Run `pytest apps/ai_assistant/` — all tests pass
  - Verify chat UI sends and receives messages in the browser
  - Ask the user if questions arise.

- [x] 11. Admin panel — user management, content supervision, API monitoring
  - [x] 11.1 Implement `UserAdmin` in `apps/accounts/admin.py`
    - List display: `username`, `email`, `role`, `date_joined`, `is_suspended`
    - Search fields: `username`, `email`
    - Custom action `suspend_selected_users`: calls `suspend_user` for each selected user (invalidates sessions)
    - _Requirements: 9.1, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 11.2 Write property test for admin-only access enforcement (Property 11)
    - **Property 11: Admin-only access enforcement**
    - Generate random non-admin role values; create a User with that role; make GET requests to each admin URL; assert every response is HTTP 302 redirect to home page
    - **Validates: Requirements 9.1, 9.2**

  - [x] 11.3 Implement `ArticleAdmin` in `apps/news/admin.py`
    - List display: `title`, `source_name`, `category`, `published_at`, `is_hidden`
    - Custom action `hide_selected_articles`: calls `hide_article` for each selected article
    - Custom admin action `trigger_news_refresh`: calls `fetch_and_store_articles()`, displays result message with `new_count` and any errors
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 11.4 Implement `APIMonitorDashboardView` in `apps/core/admin_views.py`
    - Custom Django admin view (registered via `AdminSite.get_urls()`)
    - Queries `APICallLog` for: total calls last 24 h, total calls last 30 d, success rate, last error message
    - Renders `templates/admin/api_monitor.html` with Bootstrap table
    - _Requirements: 11.1_

  - [x] 11.5 Implement `APICallLogAdmin` with CSV export in `apps/core/admin.py`
    - List display: `endpoint`, `status_code`, `latency_ms`, `error_message`, `called_at`
    - Date hierarchy on `called_at`; filter by `status_code`
    - Custom action `export_as_csv`: streams `text/csv` response for selected date range
    - _Requirements: 11.4_

  - [x] 11.6 Register all admin classes and wire custom dashboard URL
    - Register `UserAdmin`, `ArticleAdmin`, `APICallLogAdmin` in respective `admin.py` files
    - Override `AdminSite.index` or add custom URL for `APIMonitorDashboardView`
    - _Requirements: 9.1, 10.1, 11.1_

- [x] 12. Base templates, responsive design, and static assets
  - [x] 12.1 Create `templates/base.html` with Bootstrap 5 CDN, navigation bar, and block structure
    - Navigation: links to Home, News, Events, Training, AI Assistant; login/logout/profile links
    - Responsive navbar with hamburger menu for mobile
    - `{% block content %}` and `{% block extra_js %}` blocks
    - _Requirements: 12.1, 12.2_

  - [x] 12.2 Extend all app templates from `base.html`
    - Update all templates created in tasks 3, 5, 6, 8, 9 to `{% extends "base.html" %}`
    - Ensure all interactive controls have minimum 44×44 CSS pixel touch targets
    - _Requirements: 12.1, 12.2, 12.4_

  - [x] 12.3 Configure static files with HTTP caching headers
    - Set `Cache-Control: max-age=86400` for all static assets via `WhiteNoise` or nginx config
    - Add `ManifestStaticFilesStorage` for cache-busting in production settings
    - _Requirements: 13.3_

  - [x] 12.4 Create `lighthouserc.json` for Lighthouse CI configuration
    - Assert mobile performance score ≥ 70 on: `/`, `/news/`, `/events/calendar/`, `/training/`, `/ai/chat/`
    - _Requirements: 12.3_

- [x] 13. Integration tests
  - [x] 13.1 Write integration test: news fetch cycle
    - Mock `NewsAPIClient` HTTP response; call `fetch_and_store_articles()`; assert articles stored and `APICallLog` created
    - _Requirements: 3.1, 3.2, 11.2_

  - [x] 13.2 Write integration test: admin manual news refresh
    - Log in as admin; POST to admin refresh action; assert `fetch_and_store_articles` triggered and response includes `new_count`
    - _Requirements: 10.3, 10.4_

  - [x] 13.3 Write integration test: chat endpoint
    - Log in as user; POST message to `/ai/chat/`; assert `ConversationMessage` saved and JSON response contains `reply`
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 13.4 Write integration test: CSV export
    - Log in as admin; GET `/admin/core/apicalllog/export/?date_from=...&date_to=...`; assert `Content-Type: text/csv` and correct headers
    - _Requirements: 11.4_

  - [x] 13.5 Write integration test: suspended user cannot log in
    - Create user, suspend via `suspend_user`; attempt login; assert redirect and no session created
    - _Requirements: 9.5_

- [x] 14. Final checkpoint — full test suite
  - Run `pytest` — all Python tests pass
  - Run `npx jest --testPathPattern=stopwatch` — all JS tests pass
  - Run `python manage.py migrate --check` — no pending migrations
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at logical boundaries
- Property tests (Properties 1–12) validate universal correctness guarantees using Hypothesis
- Unit tests validate specific examples and edge cases
- Jest tests cover the client-side stopwatch (Requirement 6)
- The `core` app must be implemented before `news`, `events`, and `ai_assistant` because they all depend on `log_api_call`
