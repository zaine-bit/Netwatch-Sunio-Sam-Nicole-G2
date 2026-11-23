# Netwatch

Netwatch is a full-stack Django web application for home and small-office network owners who want a simple way to understand which of their registered devices is using unusually high data.

The system records daily usage values entered or imported by the owner (with clearly labelled sample data for demonstrations), compares each device's usage with its own historical average, and presents understandable warnings. It is not a live router-monitoring or packet-inspection tool.

## Technology stack
- Backend: Python and Django
- Frontend: Django Templates (server-rendered HTML)
- Database: Supabase (managed PostgreSQL)
- Application accounts: Custom Netwatch account model, validation, login, logout, and session handling
- Password security: Django password validators and secure password hash/check utilities
- Configuration: Environment variables loaded from a local .env file

## Development status

### Phase 1 — Account feature
The project foundation and custom account flow are implemented. The application uses its own accounts.Account model and account_id session rather than Django's built-in User model for Netwatch users. The account feature includes registration, username/email validation, duplicate checks, login by username or email, logout, role-specific dashboards, and profile editing.

Django's password validation and password hashing utilities are used for password security. Django's admin integration is separate from the Netwatch account pages.

### Phase 2 — Network usage features
Phase 2 is being prepared in separate feature branches. Planned features are:
- Device inventory management for each Network Owner.
- Daily usage records associated with an owner's device.
- Device-specific historical averages and threshold-based warnings.
- A simple owner dashboard for devices, recorded usage, and alerts.

The approved ERD/SDD must confirm database entities, fields, relationships, constraints, and delete behavior before models and migrations are implemented. Until then, the Phase 2 planning documents are specifications, not completed database features.

## Supabase database setup
1. Create a project in Supabase.
2. In the Supabase Dashboard, open Project Settings → Database.
3. Find the Connection string section and choose the Session Pooler option.
4. Copy the host, port, database name, username, and password into your local environment file.
5. Copy .env.example to .env in the project root (beside manage.py).
6. Replace the placeholder database values and set a strong Django SECRET_KEY. Keep DB_SSLMODE=require.

The example values in .env.example are placeholders, not working credentials. Never share or commit your local .env file.

## Local setup (Windows PowerShell)
1. Install Python 3.11+ and Git.
2. Clone the repository and enter the project directory.
3. Switch to the branch you intend to work on. For example:

   ```powershell
   git switch feature/device-management
   git pull origin feature/device-management
   ```

   Use feature/usage-dashboard-alerts when working on the usage/alerts feature.

4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation for this session, run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

   If you use uv, use your existing uv workflow or install the requirements with uv pip.

6. Copy and configure the environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

7. Apply migrations only after confirming the branch's database changes and the approved ERD/SDD. Run tests and start the server:

   ```powershell
   python manage.py test --keepdb
   python manage.py runserver 127.0.0.1:8080
   ```

Stop the development server with Ctrl+C in the terminal running it.

## Security notes
- Never commit .env, database passwords, Supabase service-role keys, or Django secret keys.
- .env.example should contain placeholders only.
- Django connects to Supabase PostgreSQL using SSL; SQLite is not configured as a fallback.
- Supabase provides the hosted PostgreSQL database; it is not the Netwatch account-authentication provider.
