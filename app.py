from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import json
import random
import datetime
from pymongo import MongoClient

load_dotenv()

# Conexión a MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["chocolates_bot"]
pedidos_collection = db["pedidos"]

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"

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
    response = requests.post(API_URL, headers=headers, json=data)
    print("Status:", response.status_code)
    print("Response:", response.text)

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
        # Mostrar nombre legible sin guion bajo
        codigo_legible = pid.replace("_", " ")
        mensaje += f"• {info['nombre']} - ${info['precio']:,}\n  → escribe: *{codigo_legible}*\n\n"
    mensaje += "📦 Escribí *ver carrito* para ver tu pedido\n📋 Escribí *categorias* para volver al menú"
    enviar_texto(numero, mensaje)

def buscar_producto(texto):
    """Busca un producto de forma flexible"""
    texto_limpio = texto.lower().strip()
    
    # Buscar coincidencia exacta (con guion bajo o espacio)
    if texto_limpio in PRODUCTOS:
        return texto_limpio
    
    # Buscar reemplazando espacios por guion bajo
    texto_con_guion = texto_limpio.replace(" ", "_")
    if texto_con_guion in PRODUCTOS:
        return texto_con_guion
    
    # Buscar por nombre del producto
    for pid, info in PRODUCTOS.items():
        if texto_limpio == info["nombre"].lower():
            return pid
    
    # Buscar coincidencia parcial
    for pid, info in PRODUCTOS.items():
        if texto_limpio in pid or texto_limpio in info["nombre"].lower():
            return pid
    
    return None



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
    enviar_botones_continuar(numero)

def enviar_botones_continuar(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "¿Qué deseas hacer ahora?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "ver_categorias", "title": "🛒 Seguir comprando"}},
                    {"type": "reply", "reply": {"id": "finalizar", "title": "💳 Finalizar pedido"}}
                ]
            }
        }
    }
    response = requests.post(API_URL, headers=headers, json=data)
    print("Botones continuar:", response.status_code)

def mostrar_menu(numero):
    enviar_lista_categorias(numero)

def mostrar_carrito(numero):
    carrito = carritos.get(numero, {})
    items = carrito.get("items", [])
    
    if not items:
        enviar_texto(numero, "🧺 Tu carrito está vacío.")
        return

    mensaje = "🧺 *Tu pedido:*\n\n"
    total = 0
    for item in items:
        subtotal = item["precio"] * item["cantidad"]
        mensaje += f"• {item['cantidad']} x {item['producto']} → ${subtotal:,.0f}\n"
        total += subtotal

    mensaje += f"\n🧾 *Subtotal:* ${total:,.0f}"
    
    carritos[numero]["subtotal"] = total
    
    enviar_texto(numero, mensaje)
    enviar_opciones_entrega(numero)

def enviar_opciones_entrega(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🚚 *¿Cómo deseas recibir tu pedido?*\n\n• Domicilio en Tunja: +$7,000\n• Recoger en tienda: Gratis"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "entrega_domicilio", "title": "🏠 Domicilio"}},
                    {"type": "reply", "reply": {"id": "entrega_recoger", "title": "🏪 Recoger en tienda"}}
                ]
            }
        }
    }
    requests.post(API_URL, headers=headers, json=data)

def pedir_direccion(numero):
    if carritos[numero].get("tipo_entrega") == "domicilio":
        enviar_texto(numero, "📍 Ahora escribe tu *dirección completa* en Tunja:")
        carritos[numero]["esperando"] = "direccion"
    else:
        pedir_telefono(numero)

def pedir_telefono(numero):
    enviar_texto(numero, "📱 Escribe tu *número de teléfono* de contacto:")
    carritos[numero]["esperando"] = "telefono"

def mostrar_resumen_final(numero):
    carrito = carritos[numero]
    items = carrito.get("items", [])
    costo_envio = carrito.get("costo_envio", 0)
    tipo_entrega = carrito.get("tipo_entrega", "domicilio")
    
    mensaje = "📋 *RESUMEN DE TU PEDIDO*\n"
    mensaje += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    mensaje += "*Productos:*\n"
    total = 0
    for item in items:
        subtotal = item["precio"] * item["cantidad"]
        mensaje += f"• {item['cantidad']} x {item['producto']} - ${subtotal:,.0f}\n"
        total += subtotal
    
    mensaje += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    mensaje += f"🧾 Subtotal: ${total:,.0f}\n"
    
    if tipo_entrega == "domicilio":
        mensaje += f"🚚 Domicilio: $7,000\n"
    else:
        mensaje += f"🏪 Recoger en tienda: Gratis\n"
    
    mensaje += f"💰 *TOTAL: ${total + costo_envio:,.0f}*\n"
    mensaje += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if tipo_entrega == "domicilio":
        mensaje += "*Datos de envío:*\n"
        mensaje += f"👤 {carrito.get('nombre', '')}\n"
        mensaje += f"📍 {carrito.get('direccion', '')}\n"
        mensaje += f"📱 {carrito.get('telefono', '')}\n"
    else:
        mensaje += "*Datos de contacto:*\n"
        mensaje += f"👤 {carrito.get('nombre', '')}\n"
        mensaje += f"📱 {carrito.get('telefono', '')}\n"
        mensaje += f"\n🏪 *Recoger en:* Cra 9 #24-20, Las Nieves, Tunja\n"
    
    enviar_texto(numero, mensaje)
    enviar_botones_confirmar(numero)

def enviar_botones_confirmar(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "¿Los datos están correctos?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "confirmar_pedido", "title": "✅ Confirmar"}},
                    {"type": "reply", "reply": {"id": "corregir_datos", "title": "✏️ Corregir"}},
                    {"type": "reply", "reply": {"id": "cancelar_pedido", "title": "❌ Cancelar"}}
                ]
            }
        }
    }
    requests.post(API_URL, headers=headers, json=data)

def enviar_opciones_corregir(numero):
    carrito = carritos.get(numero, {})
    tipo_entrega = carrito.get("tipo_entrega", "domicilio")
    
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    
    if tipo_entrega == "domicilio":
        rows = [
            {"id": "corregir_nombre", "title": "👤 Nombre"},
            {"id": "corregir_direccion", "title": "📍 Dirección"},
            {"id": "corregir_telefono", "title": "📱 Teléfono"}
        ]
    else:
        rows = [
            {"id": "corregir_nombre", "title": "👤 Nombre"},
            {"id": "corregir_telefono", "title": "📱 Teléfono"}
        ]
    
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "✏️ *¿Qué dato deseas corregir?*"},
            "action": {
                "button": "Seleccionar",
                "sections": [{"title": "Datos", "rows": rows}]
            }
        }
    }
    requests.post(API_URL, headers=headers, json=data)

def enviar_metodos_pago(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "💳 *Selecciona tu método de pago:*\n\nElige cómo deseas realizar el pago de tu pedido."},
            "action": {
                "button": "Ver métodos de pago",
                "sections": [{
                    "title": "Métodos de pago",
                    "rows": [
                        {"id": "pago_bancolombia", "title": "Bancolombia", "description": "Cuenta de ahorros"},
                        {"id": "pago_davivienda", "title": "Davivienda", "description": "Cuenta de ahorros"},
                        {"id": "pago_nequi", "title": "Nequi", "description": "Transferencia Nequi"},
                        {"id": "pago_daviplata", "title": "Daviplata", "description": "Transferencia Daviplata"}
                    ]
                }]
            }
        }
    }
    requests.post(API_URL, headers=headers, json=data)

def enviar_datos_pago(numero, metodo):
    carrito = carritos.get(numero, {})
    costo_envio = carrito.get("costo_envio", 0)
    total = carrito.get("subtotal", 0) + costo_envio
    
    datos_pago = {
        "pago_bancolombia": {
            "banco": "Bancolombia",
            "tipo": "Cuenta de Ahorros",
            "numero": "123-456789-00",
            "titular": "Chocolates del Castillo SAS",
            "cedula": "900.123.456-7"
        },
        "pago_davivienda": {
            "banco": "Davivienda", 
            "tipo": "Cuenta de Ahorros",
            "numero": "456-789012-34",
            "titular": "Chocolates del Castillo SAS",
            "cedula": "900.123.456-7"
        },
        "pago_nequi": {
            "banco": "Nequi",
            "tipo": "Número Nequi",
            "numero": "300 123 4567",
            "titular": "Chocolates del Castillo",
            "cedula": ""
        },
        "pago_daviplata": {
            "banco": "Daviplata",
            "tipo": "Número Daviplata", 
            "numero": "300 765 4321",
            "titular": "Chocolates del Castillo",
            "cedula": ""
        }
    }
    
    pago = datos_pago.get(metodo, datos_pago["pago_bancolombia"])
    
    mensaje = f"🏦 *DATOS PARA PAGO*\n"
    mensaje += "━━━━━━━━━━━━━━━━━━━━\n\n"
    mensaje += f"💰 *Total a pagar: ${total:,.0f}*\n\n"
    mensaje += f"🏛️ *{pago['banco']}*\n"
    mensaje += f"📋 {pago['tipo']}\n"
    mensaje += f"🔢 *{pago['numero']}*\n"
    mensaje += f"👤 {pago['titular']}\n"
    if pago['cedula']:
        mensaje += f"🆔 NIT: {pago['cedula']}\n"
    mensaje += "\n━━━━━━━━━━━━━━━━━━━━\n\n"
    mensaje += "📸 *Envía el comprobante de pago* a este chat para confirmar tu pedido.\n\n"
    mensaje += "⏰ Tu pedido será procesado una vez confirmemos el pago."
    
    enviar_texto(numero, mensaje)
    carritos[numero]["esperando"] = "comprobante"

def generar_numero_pedido():
    fecha = datetime.datetime.now().strftime("%d%m")
    aleatorio = random.randint(1000, 9999)
    return f"CHC-{fecha}-{aleatorio}"

def procesar_comprobante(numero):
    carrito = carritos.get(numero, {})
    tipo_entrega = carrito.get("tipo_entrega", "domicilio")
    
    # Generar número de pedido
    numero_pedido = generar_numero_pedido()
    
    # Guardar pedido en MongoDB
    pedido_data = {
        "numero_pedido": numero_pedido,
        "cliente": carrito.get("nombre", ""),
        "telefono": carrito.get("telefono", ""),
        "direccion": carrito.get("direccion", ""),
        "tipo_entrega": tipo_entrega,
        "items": carrito.get("items", []),
        "subtotal": carrito.get("subtotal", 0),
        "costo_envio": carrito.get("costo_envio", 0),
        "total": carrito.get("subtotal", 0) + carrito.get("costo_envio", 0),
        "estado": "Pago recibido - En preparación",
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "wa_id": numero
    }
    pedidos_collection.insert_one(pedido_data)
    
    mensaje = "✅ *¡PEDIDO CONFIRMADO!*\n\n"
    mensaje += f"🔖 *Número de pedido:* {numero_pedido}\n"
    mensaje += "_(Guarda este número para seguimiento)_\n\n"
    mensaje += "Hemos recibido tu comprobante de pago.\n\n"
    
    if tipo_entrega == "domicilio":
        mensaje += "📦 Tu pedido será preparado y enviado a:\n"
        mensaje += f"📍 {carrito.get('direccion', '')}\n\n"
    else:
        mensaje += "📦 Tu pedido será preparado para recoger en:\n"
        mensaje += "🏪 Cra 9 #24-20, Las Nieves, Tunja\n"
        mensaje += "⏰ Te avisaremos cuando esté listo\n\n"
    
    mensaje += "Te contactaremos al número:\n"
    mensaje += f"📱 {carrito.get('telefono', '')}\n\n"
    mensaje += "📍 *Para consultar tu pedido* escribe:\n"
    mensaje += f"*estado {numero_pedido}*\n\n"
    mensaje += "¡Gracias por tu compra! 🍫\n"
    mensaje += "_Chocolates del Castillo_"
    
    enviar_texto(numero, mensaje)
    
    # Limpiar carrito
    if numero in carritos:
        del carritos[numero]

def consultar_estado_pedido(numero, numero_pedido):
    pedido = pedidos_collection.find_one({"numero_pedido": numero_pedido.upper()})
    
    if not pedido:
        enviar_texto(numero, f"❌ No encontramos el pedido *{numero_pedido}*\n\nVerifica el número e intenta de nuevo.")
        return
    
    mensaje = f"📋 *ESTADO DEL PEDIDO*\n"
    mensaje += "━━━━━━━━━━━━━━━━━━━━\n\n"
    mensaje += f"🔖 *Pedido:* {pedido['numero_pedido']}\n"
    mensaje += f"📅 *Fecha:* {pedido['fecha']}\n"
    mensaje += f"👤 *Cliente:* {pedido['cliente']}\n\n"
    mensaje += f"📦 *Estado:* {pedido['estado']}\n\n"
    
    if pedido['tipo_entrega'] == "domicilio":
        mensaje += f"🚚 *Envío a:* {pedido['direccion']}\n"
    else:
        mensaje += "🏪 *Recoger en:* Cra 9 #24-20, Las Nieves, Tunja\n"
    
    mensaje += f"\n💰 *Total:* ${pedido['total']:,.0f}"
    
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
                    enviar_texto(numero, "📦 Por favor escribe *estado* seguido de tu número de pedido.\n\nEjemplo: *estado CHC-0802-1234*")
                elif reply_id == "asesor":
                    enviar_texto(numero, "🗣️ Un asesor se pondrá en contacto contigo pronto.")
                elif reply_id == "ver_categorias":
                    enviar_lista_categorias(numero)
                elif reply_id == "ya_se_que_pedir":
                    enviar_texto(numero, "✅ Perfecto! Escribí el nombre del producto que querés (ej: *praga*, *chocobombs_x2*, *mr_genial*)\n\n📋 O escribí *categorias* para ver todas las opciones.")
                elif reply_id.startswith("cat_"):
                    categoria_id = reply_id.replace("cat_", "")
                    enviar_productos_categoria(numero, categoria_id)
                elif reply_id == "finalizar":
                    mostrar_carrito(numero)
                elif reply_id == "entrega_domicilio":
                    carritos[numero]["tipo_entrega"] = "domicilio"
                    carritos[numero]["costo_envio"] = 7000
                    enviar_texto(numero, "🏠 *Entrega a domicilio en Tunja*\n\n📝 Por favor escribe tu *nombre completo*:")
                    carritos[numero]["esperando"] = "nombre"
                elif reply_id == "entrega_recoger":
                    carritos[numero]["tipo_entrega"] = "recoger"
                    carritos[numero]["costo_envio"] = 0
                    enviar_texto(numero, "🏪 *Recoger en tienda*\n\n📍 Dirección: Cra 9 #24-20, Las Nieves, Tunja\n⏰ Horario: Lunes a Sábado 9am - 7pm\n\n📝 Por favor escribe tu *nombre completo*:")
                    carritos[numero]["esperando"] = "nombre"
                elif reply_id == "confirmar_pedido":
                    enviar_metodos_pago(numero)
                elif reply_id == "corregir_datos":
                    enviar_opciones_corregir(numero)
                elif reply_id == "corregir_nombre":
                    enviar_texto(numero, "📝 Escribe tu *nombre completo* nuevamente:")
                    carritos[numero]["esperando"] = "nombre_correccion"
                elif reply_id == "corregir_direccion":
                    enviar_texto(numero, "📍 Escribe tu *dirección completa* nuevamente:")
                    carritos[numero]["esperando"] = "direccion_correccion"
                elif reply_id == "corregir_telefono":
                    enviar_texto(numero, "📱 Escribe tu *número de teléfono* nuevamente:")
                    carritos[numero]["esperando"] = "telefono_correccion"
                elif reply_id == "cancelar_pedido":
                    if numero in carritos:
                        del carritos[numero]
                    enviar_texto(numero, "❌ Pedido cancelado. Escribe *menu* para comenzar de nuevo.")
                elif reply_id.startswith("pago_"):
                    enviar_datos_pago(numero, reply_id)
                else:
                    enviar_texto(numero, "Opción no reconocida. Escribí *menu* para comenzar.")
                return "ok", 200

            # Detectar si es imagen (comprobante de pago)
            if mensaje.get("type") == "image":
                if numero in carritos and carritos[numero].get("esperando") == "comprobante":
                    procesar_comprobante(numero)
                    return "ok", 200
                else:
                    enviar_texto(numero, "📷 Recibimos tu imagen. Si es un comprobante de pago, primero debes completar un pedido.\n\nEscribe *menu* para comenzar.")
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

            # 3. Consultar estado de pedido
            elif texto.startswith("estado "):
                numero_pedido = texto.replace("estado ", "").strip().upper()
                consultar_estado_pedido(numero, numero_pedido)
                return "ok", 200

            # 4. Ver carrito
            elif texto == "ver carrito":
                mostrar_carrito(numero)
                return "ok", 200

            # 4. Elegir producto (búsqueda flexible)
            producto_encontrado = buscar_producto(texto)
            if producto_encontrado:
                preguntar_cantidad(numero, producto_encontrado)
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

            # 6. Flujo de datos de envío
            elif numero in carritos and "esperando" in carritos[numero]:
                esperando = carritos[numero]["esperando"]
                texto_original = mensaje.get("text", {}).get("body", "").strip()
                
                if esperando == "nombre":
                    carritos[numero]["nombre"] = texto_original
                    pedir_direccion(numero)
                elif esperando == "direccion":
                    carritos[numero]["direccion"] = texto_original
                    pedir_telefono(numero)
                elif esperando == "telefono":
                    carritos[numero]["telefono"] = texto_original
                    del carritos[numero]["esperando"]
                    mostrar_resumen_final(numero)
                elif esperando == "nombre_correccion":
                    carritos[numero]["nombre"] = texto_original
                    del carritos[numero]["esperando"]
                    mostrar_resumen_final(numero)
                elif esperando == "direccion_correccion":
                    carritos[numero]["direccion"] = texto_original
                    del carritos[numero]["esperando"]
                    mostrar_resumen_final(numero)
                elif esperando == "telefono_correccion":
                    carritos[numero]["telefono"] = texto_original
                    del carritos[numero]["esperando"]
                    mostrar_resumen_final(numero)
                elif esperando == "comprobante":
                    procesar_comprobante(numero)
                
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
