OTP Authentication

- Endpoints:
  - POST /auth/request-otp  { email }
  - POST /auth/verify-otp   { email, otp }
  - GET  /auth/whoami?token=<token>

- Environment variables (see .env.example):
  - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
  - If SMTP settings are not provided, OTPs will be printed to the server console (useful for local dev).

- Run server (recommended inside a virtual env):
  pip install -r requirements.txt
  uvicorn main:app --reload

