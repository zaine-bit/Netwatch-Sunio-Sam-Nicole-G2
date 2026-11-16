# Netwatch

Netwatch is a full-stack Django web application concept for home and small-office network owners.

## Technology stack

- Backend: Python and Django
- Frontend: Django Templates (server-rendered HTML)
- Database: Supabase (managed PostgreSQL)
- Application accounts: Custom Netwatch account model, validation, login, logout, and session handling
- Password security: Django password validators and secure password hash/check utilities only
- Configuration: Environment variables loaded from a local .env file

## Current development phase

The project foundation and Account Feature are being developed on feature/supabase-database. The user-facing Netwatch account flow is implemented independently of Django's built-in User model and authentication views/forms. It includes registration, username/email validation, duplicate checks, login by username or email, logout, role-specific dashboards, and profile editing.

Django's password validation and password hashing utilities are retained for password security. Django's authentication middleware and admin integration remain available only for the separate Django backend admin site; the Netwatch account pages identify users through their own account_id session and the custom accounts.Account table.

The feature branch includes a migration that creates the custom account table, copies existing Django users (including their compatible password hashes and staff-to-admin role), and removes the old Profile model that depended on Django's User model.

## Supabase database setup

1. Create a project in Supabase.
2. In the Supabase Dashboard, open Project Settings → Database.
3. Find the Connection string section and choose the Session Pooler option. Use its host, port, database name, username, and password in your local environment file.
4. In the project folder, copy .env.example to .env.
5. Replace DB_HOST, DB_USER, and DB_PASSWORD with the values supplied by Supabase. Keep DB_SSLMODE=require.
6. Generate a strong Django SECRET_KEY. Never commit your .env file.

The example values in .env.example are placeholders, not working credentials.

## Local setup (Windows PowerShell)

1. Install Python 3.11+.
2. Clone the repository and enter its directory.
3. Switch to the correct feature branch:

   git switch feature/supabase-database
   git pull origin feature/supabase-database

4. Create and activate a virtual environment:

   py -m venv venv
   .\venv\Scripts\Activate.ps1

5. Install dependencies:

   pip install -r requirements.txt

6. Configure your local .env file for Supabase.
7. Apply migrations, run the account tests, and start the server:

   python manage.py migrate
   python manage.py test accounts
   python manage.py runserver

## Security notes

- Never commit .env, database passwords, Supabase service-role keys, or Django secret keys.
- Django connects directly to Supabase PostgreSQL using SSL. SQLite is not configured as a fallback.
- Supabase is the hosted PostgreSQL database, not an authentication provider.