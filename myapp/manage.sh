#!/bin/bash

LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/manage.log"
MODEL="deepseek-r1:32b"
DOCKER_SERVICE="home_soft"

mkdir -p "$LOG_DIR"

log() {
  echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

start() {
  log "🧠 Démarrage d’Ollama avec le modèle : $MODEL"
  nohup ollama run "$MODEL" >> "$LOG_FILE" 2>&1 &

  log "🚀 Lancement du conteneur Docker ($DOCKER_SERVICE)..."
  docker compose up -d 2>&1 | tee -a "$LOG_FILE"

  log "🌐 Application disponible sur http://localhost:8000"
}

stop() {
  log "🛑 Arrêt du conteneur Docker ($DOCKER_SERVICE)..."
  docker compose down 2>&1 | tee -a "$LOG_FILE"

  log "🔒 Tentative d’arrêt de Ollama..."
  pkill -f "ollama run" && log "✅ Ollama arrêté." || log "⚠️ Aucun processus Ollama trouvé."
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  *)
    echo "Usage: $0 {start|stop}"
    ;;
esac
