# Netwatch

Netwatch is a full-stack Django web application concept for home and small-office network owners. It aims to make network activity easier to understand by helping users identify connected devices, review data usage, and receive warnings about unusual activity.

## Technology stack

- **Backend:** Python and Django
- **Frontend:** Django Templates (server-rendered HTML)
- **Database:** PostgreSQL
- **Authentication:** Django's built-in authentication framework
- **Configuration:** Environment variables loaded from a local `.env` file

## Current development phase

The initial project foundation is being established. The Account Feature will be developed in separate feature branches:

1. Project setup and PostgreSQL configuration
2. User registration and validation
3. Login, logout, and protected sessions
4. Role-based Administrator and Network Owner dashboards
5. User profile viewing and editing
6. Account feature testing and documentation

The built-in Django admin is reserved for backend administration. Netwatch will have its own user-facing dashboards and user-management interface.

## Local setup (Windows PowerShell)

1. Install Python 3.11+ and PostgreSQL.
2. Create a PostgreSQL database (default name: `netwatch_db`).
3. Clone the repository and enter its directory.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env` and enter your own PostgreSQL credentials and a secure Django secret key.
7. Apply migrations and run the development server:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

## Security notes

- Never commit `.env`, database passwords, Supabase keys, or secret keys.
- The repository ignores local environment files and virtual environments.
- PostgreSQL is configured as the project database; SQLite is not configured as a fallback.
