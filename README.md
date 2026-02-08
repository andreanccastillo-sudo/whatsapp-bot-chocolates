# 🤖 WhatsApp Bot en Python

Este es un bot básico de WhatsApp usando la Cloud API oficial de Meta.

## 🚀 Pasos para usar

1. Instala dependencias:
```
pip install -r requirements.txt
```

2. Agrega tu token y ID en el archivo `.env`.

3. Inicia el bot:
```
python app.py
```

4. Expón tu servidor local con ngrok:
```
ngrok http 5000
```

5. Copia la URL HTTPS y configúrala en Meta Developers como Webhook con el token: `miverificacion123`.

6. Envía mensajes al número de prueba con "1", "2" o "3".

## ✅ Opciones del menú

- `1`: Información de productos
- `2`: Estado del pedido
- `3`: Hablar con un asesor
