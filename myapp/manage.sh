#!/bin/bash

APP_NAME="my_automation_app"
OLLAMA_PID_FILE=".ollama.pid"

start() {
  echo "🟢 Lancement de Ollama..."
  ollama run codellama:7b-instruct > /dev/null 2>&1 &
  echo $! > "$OLLAMA_PID_FILE"
  echo "✅ Ollama lancé avec PID $(cat "$OLLAMA_PID_FILE")"

  echo "🐳 Lancement de Docker..."
  docker compose up --build -d
  echo "✅ Docker lancé"
}

stop() {
  echo "🛑 Arrêt de Docker..."
  docker compose down

  if [ -f "$OLLAMA_PID_FILE" ]; then
    OLLAMA_PID=$(cat "$OLLAMA_PID_FILE")
    echo "🛑 Arrêt de Ollama (PID $OLLAMA_PID)..."
    kill "$OLLAMA_PID" && rm "$OLLAMA_PID_FILE"
    echo "✅ Ollama arrêté"
  else
    echo "⚠️  Pas de processus Ollama enregistré"
  fi
}

restart() {
  stop
  sleep 2
  start
}

status() {
  echo "📦 Docker :"
  docker compose ps

  echo ""
  if [ -f "$OLLAMA_PID_FILE" ]; then
    echo "🤖 Ollama PID : $(cat "$OLLAMA_PID_FILE")"
    ps -p "$(cat "$OLLAMA_PID_FILE")" >/dev/null && echo "✅ Ollama en cours d'exécution" || echo "❌ Ollama inactif"
  else
    echo "❌ Ollama non lancé"
  fi
}

case "$1" in
  start) start ;;
  stop) stop ;;
  restart) restart ;;
  status) status ;;
  *)
    echo "Usage : $0 {start|stop|restart|status}"
    ;;
esac
