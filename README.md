# Netwatch

Netwatch is a full-stack Django web application concept for home and small-office network owners. It aims to make network activity easier to understand by helping users identify connected devices, review data usage, and receive warnings about unusual activity.

## Technology stack

- **Backend:** Python and Django
- **Frontend:** Django Templates (server-rendered HTML)
- **Database:** Supabase (managed PostgreSQL)
- **Authentication:** Django's built-in authentication framework
- **Configuration:** Environment variables loaded from a local `.env` file

## Current development phase

The initial project foundation is being established. The Account Feature will be developed in separate feature branches:

1. Project setup and Supabase PostgreSQL configuration
2. User registration and validation
3. Login, logout, and protected sessions
4. Role-based Administrator and Network Owner dashboards
5. User profile viewing and editing
6. Account feature testing and documentation

The built-in Django admin is reserved for backend administration. Netwatch will have its own user-facing dashboards and user-management interface.

## Supabase database setup

1. Create a project in [Supabase](https://supabase.com/).
2. In the Supabase Dashboard, open **Project Settings → Database**.
3. Find the **Connection string** section and choose the **Session Pooler** option. Use its host, port, database name, username, and password in your local environment file. The pooler is useful for local development environments that may use IPv4.
4. In the project folder, copy `.env.example` to `.env`.
5. Replace the sample `DB_HOST`, `DB_USER`, and `DB_PASSWORD` values with the exact values supplied by Supabase. Keep `DB_SSLMODE=require`.
6. Generate a strong Django `SECRET_KEY` and replace the placeholder. Never commit your `.env` file.

The example values in `.env.example` are placeholders, not working credentials. Supabase's pooler host and username include details specific to your project.

## Local setup (Windows PowerShell)

1. Install Python 3.11+.
2. Clone the repository and enter its directory.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Complete the Supabase database setup above and ensure your local `.env` file is configured.
6. Apply migrations and run the development server:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

## Security notes

- Never commit `.env`, database passwords, Supabase service-role keys, or Django secret keys.
- The repository ignores local environment files and virtual environments.
- Django connects directly to Supabase's managed PostgreSQL database using SSL. SQLite is not configured as a fallback.
- Netwatch uses Django authentication for application accounts; Supabase is currently the hosted PostgreSQL database, not the application's login provider.
