# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

---

## OTP Sign-in Flow

This app uses a simple OTP authentication flow backed by the FastAPI server at `http://localhost:8000`.

- POST `/auth/request-otp` with `{ email }` to get an OTP (it will be emailed when SMTP is configured or printed to server console in dev).
- POST `/auth/verify-otp` with `{ email, otp }` to verify and receive a session token saved in `localStorage`.

Run the backend with environment variables from `backend/.env.example` if you want real emails to be sent. For local dev, leaving SMTP unset will print OTPs to the backend console.
