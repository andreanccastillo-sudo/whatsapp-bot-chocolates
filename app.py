from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# Categorías de productos
CATEGORIAS = {
    "fruchetas": "🍓 Fruchetas",
    "para_ellas": "🎀 Para Ellas",
    "para_ellos": "🎁 Para Ellos",
    "chocobombs": "🍫 Choco Bombs",
    "desayunos": "☕ Desayunos",
    "fresas_flores": "💐 Fresas y Flores",
    "navidad": "🎄 Navidad",
}

# Productos organizados por categoría
PRODUCTOS = {
    # === FRUCHETAS ===
    "bran": {"nombre": "Bran", "precio": 1900, "categoria": "fruchetas"},
    "praga": {"nombre": "Praga", "precio": 4400, "categoria": "fruchetas"},
    "osaka": {"nombre": "Osaka", "precio": 5000, "categoria": "fruchetas"},
    "loira": {"nombre": "Loira", "precio": 5500, "categoria": "fruchetas"},
    "chillon": {"nombre": "Chillon", "precio": 5900, "categoria": "fruchetas"},
    "moguer": {"nombre": "Moguer", "precio": 12700, "categoria": "fruchetas"},
    "edimburgo": {"nombre": "Edimburgo", "precio": 13800, "categoria": "fruchetas"},
    "san_pedro": {"nombre": "San Pedro", "precio": 17100, "categoria": "fruchetas"},
    "miramare": {"nombre": "Miramare", "precio": 31000, "categoria": "fruchetas"},
    "celebra_comparte": {"nombre": "Celebra y Comparte", "precio": 46000, "categoria": "fruchetas"},
    
    # === PARA ELLAS ===
    "suspiro_chocolate": {"nombre": "Suspiro de Chocolate", "precio": 28000, "categoria": "para_ellas"},
    "caprichito_chocolate": {"nombre": "Caprichito de Chocolate", "precio": 32000, "categoria": "para_ellas"},
    "estuche_bombones_x6": {"nombre": "Estuche Bombones x6", "precio": 35000, "categoria": "para_ellas"},
    "bouquet_ilusion": {"nombre": "Bouquet Ilusion", "precio": 37000, "categoria": "para_ellas"},
    "deleite_chocolate": {"nombre": "Deleite Chocolate", "precio": 52000, "categoria": "para_ellas"},
    "bouquet_fantasia": {"nombre": "Bouquet Fantasia", "precio": 61000, "categoria": "para_ellas"},
    "tentacion_chocolate": {"nombre": "Tentacion de Chocolate", "precio": 63000, "categoria": "para_ellas"},
    "caja_12_fresas": {"nombre": "Caja 12 Fresas", "precio": 64000, "categoria": "para_ellas"},
    "dulce_sorpresa": {"nombre": "Dulce Sorpresa", "precio": 69000, "categoria": "para_ellas"},
    "cajita_feliz": {"nombre": "Cajita Feliz", "precio": 70000, "categoria": "para_ellas"},
    "dulce_amor": {"nombre": "Dulce Amor", "precio": 74000, "categoria": "para_ellas"},
    "dulce_corazon": {"nombre": "Dulce Corazon", "precio": 76000, "categoria": "para_ellas"},
    "corazon_deluxe": {"nombre": "Corazon Deluxe", "precio": 85000, "categoria": "para_ellas"},
    "caja_trufas_fresas": {"nombre": "Caja Trufas y Fresas", "precio": 85000, "categoria": "para_ellas"},
    "celebracion": {"nombre": "Celebracion", "precio": 92000, "categoria": "para_ellas"},
    "puro_amor": {"nombre": "Puro Amor", "precio": 98000, "categoria": "para_ellas"},
    "sueno_imperial": {"nombre": "Sueño Imperial", "precio": 100000, "categoria": "para_ellas"},
    "caja_imperial": {"nombre": "Caja Imperial", "precio": 131000, "categoria": "para_ellas"},
    
    # === PARA ELLOS ===
    "caja_junior": {"nombre": "Caja Junior", "precio": 35000, "categoria": "para_ellos"},
    "mr_genial": {"nombre": "Mr Genial", "precio": 37000, "categoria": "para_ellos"},
    "mr_original": {"nombre": "Mr Original", "precio": 45000, "categoria": "para_ellos"},
    "medio_metro_felicidad": {"nombre": "1/2 Metro de Felicidad", "precio": 45000, "categoria": "para_ellos"},
    "metro_felicidad": {"nombre": "Metro de Felicidad", "precio": 74000, "categoria": "para_ellos"},
    "mr_magico": {"nombre": "Mr Magico", "precio": 86000, "categoria": "para_ellos"},
    "mr_increible": {"nombre": "Mr Increible", "precio": 98000, "categoria": "para_ellos"},
    "mr_amoroso": {"nombre": "Mr Amoroso", "precio": 103000, "categoria": "para_ellos"},
    "caja_aniversario": {"nombre": "Caja Aniversario", "precio": 109000, "categoria": "para_ellos"},
    "caja_bombones_x30": {"nombre": "Caja Bombones x30", "precio": 134000, "categoria": "para_ellos"},
    "mr_asombroso": {"nombre": "Mr Asombroso", "precio": 162000, "categoria": "para_ellos"},
    
    # === CHOCO BOMBS ===
    "chocobombs_x1": {"nombre": "Choco Bombs x1", "precio": 10500, "categoria": "chocobombs"},
    "chocobombs_x2": {"nombre": "Choco Bombs x2", "precio": 22500, "categoria": "chocobombs"},
    "chocobombs_x4": {"nombre": "Choco Bombs x4", "precio": 42000, "categoria": "chocobombs"},
    "chocobombs_x6": {"nombre": "Choco Bombs x6", "precio": 65000, "categoria": "chocobombs"},
    
    # === DESAYUNOS ===
    "desayuno_dejame_cuidarte": {"nombre": "Desayuno Dejame Cuidarte", "precio": 125000, "categoria": "desayunos"},
    "desayuno_feliz_despertar": {"nombre": "Desayuno Feliz Despertar", "precio": 137000, "categoria": "desayunos"},
    "desayuno_lleno_amor": {"nombre": "Desayuno Lleno de Amor", "precio": 154000, "categoria": "desayunos"},
    "desayuno_boyacense": {"nombre": "Desayuno Boyacense", "precio": 156000, "categoria": "desayunos"},
    "desayuno_dulce_despertar": {"nombre": "Desayuno Dulce Despertar", "precio": 156000, "categoria": "desayunos"},
    
    # === FRESAS Y FLORES ===
    "caja_celebracion": {"nombre": "Caja Celebracion", "precio": 165000, "categoria": "fresas_flores"},
    "caja_deluxe": {"nombre": "Caja Deluxe", "precio": 193000, "categoria": "fresas_flores"},
    
    # === NAVIDAD ===
    "chococuchara_navidad": {"nombre": "ChocoCuchara Navideña", "precio": 19000, "categoria": "navidad"},
    "torta_envinada": {"nombre": "Torta Envinada", "precio": 45000, "categoria": "navidad"},
    "caja_estrella_navidad": {"nombre": "Caja Estrella Navideña", "precio": 71000, "categoria": "navidad"},
    "caja_alegria_navidad": {"nombre": "Caja Alegria Navideña", "precio": 74000, "categoria": "navidad"},
    "caja_dulce_navidad": {"nombre": "Caja Dulce Navidad", "precio": 118000, "categoria": "navidad"},
    "caja_arbol_navidad": {"nombre": "Caja Arbol Navidad", "precio": 129000, "categoria": "navidad"},
}
# Carritos por usuario
carritos = {}

# --- ENVÍOS DE RESPUESTAS ---

def enviar_texto(numero, texto):
    if numero == "+15556634041":
        return
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(API_URL, headers=headers, json=data)

def enviar_mensaje_con_botones(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🍫 *Bienvenido a Chocolates del Castillo* 🍫\n¿Qué quieres hacer hoy?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "comprar", "title": "🛍 Comprar"}},
                    {"type": "reply", "reply": {"id": "estado", "title": "📦 Estado del pedido"}},
                    {"type": "reply", "reply": {"id": "asesor", "title": "🗣️ Hablar con asesor"}}
                ]
            }
        }
    }
    response =requests.post(API_URL, headers=headers, json=data)
    print(response.status_code)

def enviar_botones_post_compra(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "🛍 Elegí una opción para continuar:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "ver_categorias",
                            "title": "📋 Ver categorías"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "ya_se_que_pedir",
                            "title": "✅ Ya sé qué pedir"
                        }
                    }
                ]
            }
        }
    }
    response = requests.post(API_URL, headers=headers, json=data)
    print("Respuesta botones post compra:", response.status_code, response.text)

def enviar_lista_categorias(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    sections = [{
        "title": "Categorías",
        "rows": [
            {"id": f"cat_{cat_id}", "title": cat_nombre[:24]}
            for cat_id, cat_nombre in CATEGORIAS.items()
        ]
    }]
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "🍫 *Chocolates del Castillo*\n\nElige una categoría para ver los productos disponibles:"},
            "action": {
                "button": "Ver categorías",
                "sections": sections
            }
        }
    }
    response = requests.post(API_URL, headers=headers, json=data)
    print("Lista categorías:", response.status_code, response.text)

def enviar_productos_categoria(numero, categoria_id):
    productos_cat = {pid: p for pid, p in PRODUCTOS.items() if p.get("categoria") == categoria_id}
    if not productos_cat:
        enviar_texto(numero, "No hay productos en esta categoría.")
        return
    
    cat_nombre = CATEGORIAS.get(categoria_id, "Productos")
    mensaje = f"{cat_nombre}\n\n"
    for pid, info in productos_cat.items():
        mensaje += f"• {info['nombre']} - ${info['precio']:,}\n  → escribe: *{pid}*\n\n"
    mensaje += "📦 Escribí *ver carrito* para ver tu pedido\n📋 Escribí *categorias* para volver al menú"
    enviar_texto(numero, mensaje)



# --- LÓGICA DE PEDIDO ---

def preguntar_cantidad(numero, producto_id):
    nombre = PRODUCTOS[producto_id]["nombre"]
    enviar_texto(numero, f"¿Cuántas unidades de '{nombre}' querés agregar al carrito?")
    carritos[numero] = carritos.get(numero, {})
    carritos[numero]["esperando_producto"] = producto_id

def agregar_al_carrito(numero, cantidad):
    producto_id = carritos[numero].get("esperando_producto")
    if not producto_id or producto_id not in PRODUCTOS:
        enviar_texto(numero, "No se encontró el producto seleccionado.")
        return
    producto = PRODUCTOS[producto_id]
    pedido = {"producto": producto["nombre"], "precio": producto["precio"], "cantidad": cantidad}
    carritos[numero].setdefault("items", []).append(pedido)
    del carritos[numero]["esperando_producto"]
    enviar_texto(numero, f"✅ Se agregaron {cantidad} x {producto['nombre']} al carrito.")

def mostrar_menu(numero):
    enviar_lista_categorias(numero)

def mostrar_carrito(numero):
    carrito = carritos.get(numero, {})
    items = carrito.get("items", [])
    
    if not items:
        enviar_texto(numero, "🧺 Tu carrito está vacío.")
        return

    mensaje = "🧺 Tu pedido:\n"
    total = 0
    for item in items:
        subtotal = item["precio"] * item["cantidad"]
        mensaje += f"{item['cantidad']} x {item['producto']} → ${subtotal:,.0f}\n"
        total += subtotal

    mensaje += f"\n🧾 Subtotal: ${total:,.0f}"

    # Guardamos el estado de espera por la ubicación
    carritos[numero]["esperando_domicilio"] = True

    mensaje += (
        "\n\n📍 ¿Estás en Tunja? (responde *sí* o *no*)"
    )

    enviar_texto(numero, mensaje)



# --- WEBHOOK ---

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == "miverificacion123":
            return request.args.get("hub.challenge"), 200
        return "No autorizado", 403

    if request.method == "POST":
        data = request.json
        print("Webhook completo recibido:")
        print(json.dumps(data, indent=2))
        try:
            entry = data["entry"][0]["changes"][0]["value"]
            if "messages" not in entry:
                return "ok", 200
            mensaje = entry["messages"][0]
            numero = mensaje["from"]

            if numero == "+15556634041":
                return "ok", 200

            # Procesar respuestas interactivas primero
            if mensaje.get("type") == "interactive":
                interactive = mensaje["interactive"]
                reply_id = (
                    interactive["button_reply"]["id"]
                    if "button_reply" in interactive
                    else interactive["list_reply"]["id"]
                )
                print("Botón seleccionado:", reply_id)

                if reply_id == "comprar":
                    enviar_botones_post_compra(numero)
                elif reply_id == "estado":
                    enviar_texto(numero, "📦 Por favor escribinos tu número de pedido y lo consultamos.")
                elif reply_id == "asesor":
                    enviar_texto(numero, "🗣️ Un asesor se pondrá en contacto contigo pronto.")
                elif reply_id == "ver_categorias":
                    enviar_lista_categorias(numero)
                elif reply_id == "ya_se_que_pedir":
                    enviar_texto(numero, "✅ Perfecto! Escribí el nombre del producto que querés (ej: *praga*, *chocobombs_x2*, *mr_genial*)\n\n📋 O escribí *categorias* para ver todas las opciones.")
                elif reply_id.startswith("cat_"):
                    categoria_id = reply_id.replace("cat_", "")
                    enviar_productos_categoria(numero, categoria_id)
                else:
                    enviar_texto(numero, "Opción no reconocida. Escribí *menu* para comenzar.")
                return "ok", 200

            # Luego procesamos texto plano
            texto = mensaje.get("text", {}).get("body", "").strip().lower()

            # 1. Saludo / menú
            if texto in ["menu", "hola", "inicio"]:
                enviar_mensaje_con_botones(numero)
                return "ok", 200

            # 2. Ver categorías
            elif texto in ["categorias", "categorías", "productos"]:
                enviar_lista_categorias(numero)
                return "ok", 200

            # 3. Ver carrito
            elif texto == "ver carrito":
                mostrar_carrito(numero)
                return "ok", 200

            # 4. Elegir producto
            elif texto in PRODUCTOS:
                preguntar_cantidad(numero, texto)
                return "ok", 200

            # 5. Ingresar cantidad esperada
            elif numero in carritos and "esperando_producto" in carritos[numero]:
                try:
                    cantidad = int(texto)
                    if cantidad <= 0:
                        raise ValueError()
                    agregar_al_carrito(numero, cantidad)
                except ValueError:
                    enviar_texto(numero, "Por favor escribí un número válido de unidades.")
                return "ok", 200

            # 6. Confirmar domicilio
            elif numero in carritos and "esperando_domicilio" in carritos[numero]:
                if texto in ["sí", "si"]:
                    carrito = carritos[numero]
                    total = sum(item["precio"] * item["cantidad"] for item in carrito["items"])
                    total_final = total + 7000
                    mensaje = (
                        f"🧾 Subtotal: ${total:,.0f}\n"
                        f"🚚 Domicilio en Tunja: $7.000\n"
                        f"💰 Total final: ${total_final:,.0f}\n\n"
                        "💬 Envíanos el comprobante de tu pago:\n"
                        "Banco: Bancolombia\n"
                        "Tipo Cuenta: Ahorros\n"
                        "No. Cuenta: 91246075366\n"
                        "Titular: Edwin Rojas\n"
                        "C.C No. 74.245.220."
                    )
                    enviar_texto(numero, mensaje)
                elif texto == "no":
                    mostrar_carrito(numero)
                else:
                    enviar_texto(numero, "Por favor respondé *sí* o *no* para aplicar domicilio.")
                
                del carritos[numero]["esperando_domicilio"]
                return "ok", 200

            # 7. Default
            else:
                enviar_texto(numero, "No entendí tu mensaje 🤔\n\nEscribí:\n• *menu* - para comenzar\n• *categorias* - para ver productos\n• *ver carrito* - para revisar tu pedido")
                return "ok", 200

        except Exception as e:
            print("Error:", e)
            return "ok", 200


if __name__ == "__main__":
    app.run(port=5000)
