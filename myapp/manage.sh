#!/bin/bash

APP_CONTAINER_NAME="home_soft"
MODEL_NAME="codellama:7b-instruct"

start() {
  echo "🧠 Démarrage d’Ollama avec le modèle : $MODEL_NAME"
  ollama run "$MODEL_NAME" &
  OLLAMA_PID=$!
  echo $OLLAMA_PID > .ollama.pid

  echo "🚀 Lancement du conteneur Docker ($APP_CONTAINER_NAME)..."
  docker-compose up -d
  echo "🌐 Application disponible sur http://localhost:8000"
}

stop() {
  echo "🛑 Arrêt de l'application Docker..."
  docker-compose down

  if [ -f .ollama.pid ]; then
    OLLAMA_PID=$(cat .ollama.pid)
    echo "🛑 Arrêt du modèle Ollama (PID $OLLAMA_PID)..."
    kill "$OLLAMA_PID" && rm .ollama.pid
  else
    echo "⚠️ Aucun modèle Ollama détecté en cours."
  fi
}

restart() {
  stop
  sleep 2
  start
}

status() {
  echo "📦 État du conteneur Docker :"
  docker ps --filter "name=$APP_CONTAINER_NAME"
  
  echo
  echo "🧠 État d'Ollama :"
  curl -s http://localhost:11434 || echo "❌ Ollama non actif."
}

help() {
  echo "🛠️  Usage : ./manage.sh {start|stop|restart|status}"
}

case "$1" in
  start) start ;;
  stop) stop ;;
  restart) restart ;;
  status) status ;;
  *) help ;;
esac
