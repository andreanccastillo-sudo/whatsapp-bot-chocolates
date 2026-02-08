#!/bin/bash

echo "🔁 Cerrando posibles sesiones previas de ngrok..."
pkill -f ngrok

echo "🚀 Iniciando ngrok en el puerto 5000..."
# Ejecutar ngrok en segundo plano y guardar salida en log temporal
ngrok http 5000 > ngrok.log &

# Esperar a que ngrok se levante
sleep 2

# Obtener la URL pública desde la API local de ngrok
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o "https://[a-z0-9\-]*\.ngrok-free\.app")

if [ -z "$NGROK_URL" ]; then
  echo "❌ No se pudo obtener la URL de ngrok. Asegurate de que esté instalado correctamente."
else
  echo "✅ URL de webhook: $NGROK_URL/webhook"
  echo "$NGROK_URL/webhook" | pbcopy
  echo "📋 Copiado al portapapeles."

  echo "🌐 Abriendo dashboard de ngrok..."
  open http://localhost:4040
fi
