# Netwatch

Netwatch is a full-stack Django web application concept for home and small-office network owners. It aims to make network activity easier to understand by helping users identify connected devices, review data usage, and receive warnings about unusual activity.

## Technology stack

- **Backend:** Python and Django
- **Frontend:** Django Templates (server-rendered HTML)
- **Database:** Supabase (managed PostgreSQL)
- **Application accounts:** Custom Netwatch account model, validation, registration, login, and session handling
- **Password validation:** Django's configured password validators (the only permitted built-in account validation)
- **Configuration:** Environment variables loaded from a local `.env` file

## Account implementation

Netwatch does not use Django's built-in `User` model, `UserCreationForm`, `AuthenticationForm`, `login()`, `logout()`, `LoginView`, or `LogoutView` for application accounts.

- Usernames are validated by Netwatch's own validator and checked for case-insensitive uniqueness.
- Email addresses are normalized, validated, and checked for case-insensitive uniqueness.
- Registration and login are implemented in `accounts/views.py`.
- Passwords are hashed with Django's secure password-hashing utilities and verified with `check_password`; plaintext passwords are never stored.
- Authenticated account identity is stored in the Django session under `account_id`, and protected views use Netwatch's own account decorator.
- Django's built-in password validation is retained as explicitly allowed.

The Django admin and Django authentication package remain installed for backend administration and password utilities; they are not used as Netwatch's application-account system.

## Current development phase

1. Project setup and Supabase PostgreSQL configuration
2. Custom user registration and validation
3. Custom login, logout, and protected sessions
4. Role-based Administrator and Network Owner dashboards
5. User profile viewing and editing
6. Account feature testing and documentation

## Supabase database setup

1. Create a project in [Supabase](https://supabase.com/).
2. In the Supabase Dashboard, open **Project Settings → Database**.
3. Find **Connection string** and choose **Session Pooler**. Use its host, port, database name, username, and password in your local environment file.
4. Copy `.env.example` to `.env`.
5. Replace the sample `DB_HOST`, `DB_USER`, and `DB_PASSWORD` values with the exact values supplied by Supabase. Keep `DB_SSLMODE=require`.
6. Generate a strong Django `SECRET_KEY`. Never commit your `.env` file.

The example values in `.env.example` are placeholders, not working credentials.

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

5. Configure your local `.env` file using the Supabase setup above.
6. Apply migrations and run the development server:

   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```

Registration: `/accounts/register/`  
Login: `/accounts/login/`

## Security notes

- Never commit `.env`, database passwords, Supabase service-role keys, or Django secret keys.
- Supabase is the hosted PostgreSQL database, not the application's login provider.
- Application passwords are securely hashed and never stored as plaintext.
