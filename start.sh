#!/bin/bash
set -e

echo "==> Starting CompanyIntel..."

# Backend
cd backend
if [ ! -d ".venv" ]; then
  echo "==> Creating Python venv..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -q -r requirements.txt
  playwright install chromium --with-deps 2>/dev/null || playwright install chromium
else
  source .venv/bin/activate
fi

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo ""
  echo "⚠️  Created backend/.env — add your ANTHROPIC_API_KEY before continuing."
  echo "   Optionally add REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET for Reddit data."
  echo ""
fi

echo "==> Starting FastAPI backend on http://localhost:8000 ..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Frontend
cd ../frontend
echo "==> Starting Next.js frontend on http://localhost:3001 ..."
PORT=3001 npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers running:"
echo "   Frontend → http://localhost:3001"
echo "   Backend  → http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both."

wait $BACKEND_PID $FRONTEND_PID
