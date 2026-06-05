# Deployment Plan

This document outlines the step-by-step instructions to deploy the **SBI Mutual Fund FAQ Assistant** architecture:
- **Backend**: FastAPI + Groq RAG pipeline deployed on **Railway**.
- **Frontend**: React (Vite) + Tailwind CSS v3 SPA deployed on **Vercel**.

---

## 1. Deployment Order

> [!IMPORTANT]
> Always deploy the Backend first. The Frontend requires the live Backend URL to compile and bind the fetch calls correctly.

1. **Backend Deployment (Railway)**: Deploy the FastAPI application to get a public HTTP domain (e.g., `https://sbi-chatbot-backend.up.railway.app`).
2. **Frontend Deployment (Vercel)**: Deploy the React SPA, passing the Railway backend URL into the environment configuration.

---

## 2. Railway Setup (Backend)

Railway is used to deploy the Python FastAPI backend. It automatically builds from the Git repository using the configuration in `pyproject.toml` or `requirements.txt`.

### Step-by-Step Configuration:
1. Log in to [Railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your repository and choose the `main` or `master` branch.
4. Click **Add Variables** to configure environment variables.
5. Railway will automatically detect the Python project and run the build command.
6. Once the build finishes, go to the **Settings** tab and click **Generate Domain** under the Public Networking section. Copy this URL.

---

## 3. Railway Environment Variables

Configure these variables in the Railway dashboard under **Variables**:

| Variable | Value | Description |
| :--- | :--- | :--- |
| **`GROQ_API_KEY`** | `gsk_...` | Your live Groq API key. |
| **`MODEL_PROVIDER`** | `groq` | Set Groq as the default LLM provider. |
| **`CHAT_MODEL`** | `llama-3.3-70b-versatile` | The active production model ID. |
| **`GROQ_API_BASE`** | `https://api.groq.com/openai/v1` | Groq's compatibility API endpoint. |
| **`HOST`** | `0.0.0.0` | Bind to all network interfaces. |
| **`PORT`** | `10000` | Railway injects a dynamic port into the environment, but setting it explicitly as a fallback is good practice. |
| **`APP_ENV`** | `production` | Enables production mode settings. |

---

## 4. Railway Start Command

Under **Settings** -> **Deploy** -> **Start Command** in the Railway service settings, specify the following:

```bash
.venv/bin/uvicorn sbi_fund_faq.__main__:app --host 0.0.0.0 --port $PORT
```
*(Note: Railway automatically populates the `$PORT` environment variable at runtime).*

---

## 5. Vercel Setup (Frontend)

Vercel is used to host the static React frontend built with Vite.

### Step-by-Step Configuration:
1. Log in to [Vercel.com](https://vercel.com).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. Set the **Framework Preset** to **Vite** (Vercel usually auto-detects this).
5. Set the **Root Directory** to `frontend`.
6. Under **Build & Development Settings**, verify:
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
7. Expand the **Environment Variables** section and add `VITE_API_URL`.
8. Click **Deploy**.

---

## 6. Vercel Environment Variables

Configure the following variable in the Vercel dashboard:

| Variable | Value | Description |
| :--- | :--- | :--- |
| **`VITE_API_URL`** | `https://your-railway-domain.up.railway.app` | The public URL of the deployed Railway backend (without a trailing slash). |

---

## 7. Connecting Frontend to Backend URL

The frontend fetches data dynamically by loading the API endpoint at runtime. 
Inside [App.jsx](file:///Users/rushikeshkale/Desktop/Nextleap%20AI%20Course/RAG%20Chatbot/frontend/src/App.jsx):
```javascript
const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const response = await fetch(`${baseUrl}/query`, { ... });
```
During the Vercel build step (`npm run build`), Vite embeds the `VITE_API_URL` environment variable directly into the client assets.

---

## 8. Post-Deployment Testing Checklist

Once both services are deployed, perform the following validation checks:

- [ ] **Health Check**: Open `https://your-railway-domain.up.railway.app/health` in your browser and check for `{"status":"ok"}`.
- [ ] **CORS Verification**: Open the Vercel app, submit a question, and check the browser console (F12) to verify there are no CORS preflight errors.
- [ ] **Factual Query Test**: Submit: *"What is the exit load of SBI Flexicap Fund?"* Verify that the UI displays a factual response along with source citations and grounding scores.
- [ ] **Advice Refusal Guardrail**: Submit: *"Should I buy SBI Large Cap Fund?"* Verify that the UI displays the warning card showing the advice refusal message.
- [ ] **Ambiguity Handler**: Submit: *"What is the expense ratio?"* Verify that the UI requests clarification, prompting you with scheme selection options.

---

## 9. Common Deployment Issues and Fixes

### 1. CORS Errors (Cross-Origin Resource Sharing)
* **Symptom**: Fetch fails in the browser console showing `CORS Policy Blocked`.
* **Fix**: Ensure [main.py](file:///Users/rushikeshkale/Desktop/Nextleap%20AI%20Course/RAG%20Chatbot/src/sbi_fund_faq/api/main.py) has `CORSMiddleware` active, allowing Vercel's domain. If troubleshooting, configure it temporarily to allow `*`:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

### 2. Vite Env Variable is Undefined
* **Symptom**: Frontend continues to call `http://127.0.0.1:8000/query` instead of the production backend.
* **Fix**: Make sure the environment variable is named exactly `VITE_API_URL` (Vite ignores variables that do not start with the `VITE_` prefix) and rebuild the project on Vercel.

### 3. Startup Verification Failures on Backend
* **Symptom**: Railway deployment logs show critical error: `Startup validation failed: Vector store files not found` and crash.
* **Fix**: The vector store index files (e.g. index and mapping files) must be committed to the repository under `data/vector_store` or created programmatically during a build step. Ensure `data/vector_store` contains the built vector index files before pushing to Git.
