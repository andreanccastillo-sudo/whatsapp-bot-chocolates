from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import json
import random
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import pytz

load_dotenv()

# Zona horaria Colombia
COLOMBIA_TZ = pytz.timezone('America/Bogota')

# Conexión a Supabase (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Almacenamiento temporal en memoria (backup)
pedidos_memoria = {}
DB_DISPONIBLE = False

# Usuarios que pidieron hablar con asesor (el bot no les responde)
usuarios_con_asesor = set()

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error conexión DB: {e}")
        return None

# Crear tabla si no existe
try:
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id SERIAL PRIMARY KEY,
                numero_pedido VARCHAR(50) UNIQUE,
                cliente VARCHAR(255),
                telefono VARCHAR(50),
                direccion TEXT,
                tipo_entrega VARCHAR(50),
                items JSONB,
                subtotal INTEGER,
                costo_envio INTEGER,
                total INTEGER,
                estado VARCHAR(100),
                fecha TIMESTAMP WITH TIME ZONE,
                wa_id VARCHAR(50)
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        DB_DISPONIBLE = True
        print("Supabase conectado exitosamente")
except Exception as e:
    print(f"Supabase no disponible, usando memoria: {e}")

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"

# Categorías de productos con links
CATEGORIAS = {
    "fruchetas": {"nombre": "🍓 Fruchetas", "url": "https://www.chocolatesdelcastillo.com/fruchetas"},
    "para_ellas": {"nombre": "🎀 Para Ellas", "url": "https://www.chocolatesdelcastillo.com/paraellas"},
    "para_ellos": {"nombre": "🎁 Para Ellos", "url": "https://www.chocolatesdelcastillo.com/paraellos"},
    "chocobombs": {"nombre": "🍫 Choco Bombs", "url": "https://www.chocolatesdelcastillo.com/chocobombs"},
    "desayunos": {"nombre": "☕ Desayunos", "url": "https://www.chocolatesdelcastillo.com/desayunos"},
    "fresas_flores": {"nombre": "💐 Fresas y Flores", "url": "https://www.chocolatesdelcastillo.com/fresasyflores"},
    "navidad": {"nombre": "🎄 Navidad", "url": "https://www.chocolatesdelcastillo.com/navidad"},
}

# Productos organizados por categoría (códigos simples)
PRODUCTOS = {
    # === FRUCHETAS ===
    "bran": {"nombre": "Bran", "precio": 1900, "categoria": "fruchetas"},
    "praga": {"nombre": "Praga", "precio": 4400, "categoria": "fruchetas"},
    "osaka": {"nombre": "Osaka", "precio": 5000, "categoria": "fruchetas"},
    "loira": {"nombre": "Loira", "precio": 5500, "categoria": "fruchetas"},
    "chillon": {"nombre": "Chillon", "precio": 5900, "categoria": "fruchetas"},
    "moguer": {"nombre": "Moguer", "precio": 12700, "categoria": "fruchetas"},
    "edimburgo": {"nombre": "Edimburgo", "precio": 13800, "categoria": "fruchetas"},
    "sanpedro": {"nombre": "San Pedro", "precio": 17100, "categoria": "fruchetas"},
    "miramare": {"nombre": "Miramare", "precio": 31000, "categoria": "fruchetas"},
    "comparte": {"nombre": "Celebra y Comparte", "precio": 46000, "categoria": "fruchetas"},
    
    # === PARA ELLAS ===
    "suspiro": {"nombre": "Suspiro de Chocolate", "precio": 28000, "categoria": "para_ellas"},
    "caprichito": {"nombre": "Caprichito de Chocolate", "precio": 32000, "categoria": "para_ellas"},
    "bombones6": {"nombre": "Estuche Bombones x6", "precio": 35000, "categoria": "para_ellas"},
    "ilusion": {"nombre": "Bouquet Ilusion", "precio": 37000, "categoria": "para_ellas"},
    "deleite": {"nombre": "Deleite Chocolate", "precio": 52000, "categoria": "para_ellas"},
    "fantasia": {"nombre": "Bouquet Fantasia", "precio": 61000, "categoria": "para_ellas"},
    "tentacion": {"nombre": "Tentacion de Chocolate", "precio": 63000, "categoria": "para_ellas"},
    "fresas12": {"nombre": "Caja 12 Fresas", "precio": 64000, "categoria": "para_ellas"},
    "sorpresa": {"nombre": "Dulce Sorpresa", "precio": 69000, "categoria": "para_ellas"},
    "feliz": {"nombre": "Cajita Feliz", "precio": 70000, "categoria": "para_ellas"},
    "amor": {"nombre": "Dulce Amor", "precio": 74000, "categoria": "para_ellas"},
    "corazon": {"nombre": "Dulce Corazon", "precio": 76000, "categoria": "para_ellas"},
    "deluxe": {"nombre": "Corazon Deluxe", "precio": 85000, "categoria": "para_ellas"},
    "trufas": {"nombre": "Caja Trufas y Fresas", "precio": 85000, "categoria": "para_ellas"},
    "celebracion": {"nombre": "Celebracion", "precio": 92000, "categoria": "para_ellas"},
    "puroamor": {"nombre": "Puro Amor", "precio": 98000, "categoria": "para_ellas"},
    "imperial": {"nombre": "Sueño Imperial", "precio": 100000, "categoria": "para_ellas"},
    "cajaimperial": {"nombre": "Caja Imperial", "precio": 131000, "categoria": "para_ellas"},
    
    # === PARA ELLOS ===
    "junior": {"nombre": "Caja Junior", "precio": 35000, "categoria": "para_ellos"},
    "genial": {"nombre": "Mr Genial", "precio": 37000, "categoria": "para_ellos"},
    "original": {"nombre": "Mr Original", "precio": 45000, "categoria": "para_ellos"},
    "mediometro": {"nombre": "1/2 Metro de Felicidad", "precio": 45000, "categoria": "para_ellos"},
    "metro": {"nombre": "Metro de Felicidad", "precio": 74000, "categoria": "para_ellos"},
    "magico": {"nombre": "Mr Magico", "precio": 86000, "categoria": "para_ellos"},
    "increible": {"nombre": "Mr Increible", "precio": 98000, "categoria": "para_ellos"},
    "amoroso": {"nombre": "Mr Amoroso", "precio": 103000, "categoria": "para_ellos"},
    "aniversario": {"nombre": "Caja Aniversario", "precio": 109000, "categoria": "para_ellos"},
    "bombones30": {"nombre": "Caja Bombones x30", "precio": 134000, "categoria": "para_ellos"},
    "asombroso": {"nombre": "Mr Asombroso", "precio": 162000, "categoria": "para_ellos"},
    
    # === CHOCO BOMBS ===
    "bombs1": {"nombre": "Choco Bombs x1", "precio": 10500, "categoria": "chocobombs"},
    "bombs2": {"nombre": "Choco Bombs x2", "precio": 22500, "categoria": "chocobombs"},
    "bombs4": {"nombre": "Choco Bombs x4", "precio": 42000, "categoria": "chocobombs"},
    "bombs6": {"nombre": "Choco Bombs x6", "precio": 65000, "categoria": "chocobombs"},
    
    # === DESAYUNOS ===
    "cuidarte": {"nombre": "Desayuno Dejame Cuidarte", "precio": 125000, "categoria": "desayunos"},
    "despertar": {"nombre": "Desayuno Feliz Despertar", "precio": 137000, "categoria": "desayunos"},
    "llenoamor": {"nombre": "Desayuno Lleno de Amor", "precio": 154000, "categoria": "desayunos"},
    "boyacense": {"nombre": "Desayuno Boyacense", "precio": 156000, "categoria": "desayunos"},
    "dulcedespertar": {"nombre": "Desayuno Dulce Despertar", "precio": 156000, "categoria": "desayunos"},
    
    # === FRESAS Y FLORES ===
    "cajacelebracion": {"nombre": "Caja Celebracion", "precio": 165000, "categoria": "fresas_flores"},
    "cajadeluxe": {"nombre": "Caja Deluxe", "precio": 193000, "categoria": "fresas_flores"},
    
    # === NAVIDAD ===
    "cuchara": {"nombre": "ChocoCuchara Navideña", "precio": 19000, "categoria": "navidad"},
    "torta": {"nombre": "Torta Envinada", "precio": 45000, "categoria": "navidad"},
    "estrella": {"nombre": "Caja Estrella Navideña", "precio": 71000, "categoria": "navidad"},
    "alegria": {"nombre": "Caja Alegria Navideña", "precio": 74000, "categoria": "navidad"},
    "dulcenavidad": {"nombre": "Caja Dulce Navidad", "precio": 118000, "categoria": "navidad"},
    "arbol": {"nombre": "Caja Arbol Navidad", "precio": 129000, "categoria": "navidad"},
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
            "body": {"text": "🍫 *Bienvenido a Chocolates del Castillo* 🍫\n\n¿Qué quieres hacer hoy?\n\n_En cualquier momento puedes escribir *asesor* o *vendedor* si deseas hablar con una persona._"},
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
            {"id": f"cat_{cat_id}", "title": cat_info["nombre"][:24]}
            for cat_id, cat_info in CATEGORIAS.items()
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
    """Envía solo el link de la categoría y luego botones de opciones"""
    cat_info = CATEGORIAS.get(categoria_id, {"nombre": "Productos", "url": ""})
    cat_nombre = cat_info["nombre"]
    cat_url = cat_info["url"]
    
    # Guardar categoría actual y limpiar estados anteriores
    carritos.setdefault(numero, {})
    carritos[numero]["categoria_actual"] = categoria_id
    if "esperando" in carritos[numero]:
        del carritos[numero]["esperando"]
    if "esperando_producto" in carritos[numero]:
        del carritos[numero]["esperando_producto"]
    
    mensaje = f"{cat_nombre}\n\n"
    mensaje += f"🔗 *Mira los productos aquí:*\n{cat_url}"
    
    enviar_texto(numero, mensaje)
    
    # Enviar botones de opciones
    enviar_opciones_categoria(numero)

def enviar_opciones_categoria(numero):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "¿Qué deseas hacer?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "hacer_pedido", "title": "🛍 Hacer pedido"}},
                    {"type": "reply", "reply": {"id": "ver_otra_categoria", "title": "📋 Otra categoría"}},
                    {"type": "reply", "reply": {"id": "asesor", "title": "🗣️ Hablar con asesor"}}
                ]
            }
        }
    }
    requests.post(API_URL, headers=headers, json=data)

def enviar_lista_productos_para_pedir(numero):
    """Envía la lista numerada de productos de la categoría actual"""
    categoria_id = carritos.get(numero, {}).get("categoria_actual")
    if not categoria_id:
        enviar_lista_categorias(numero)
        return
    
    productos_cat = {pid: p for pid, p in PRODUCTOS.items() if p.get("categoria") == categoria_id}
    if not productos_cat:
        enviar_texto(numero, "No hay productos en esta categoría.")
        return
    
    cat_info = CATEGORIAS.get(categoria_id, {"nombre": "Productos", "url": ""})
    cat_nombre = cat_info["nombre"]
    
    # Limpiar estados anteriores y guardar lista de productos
    if "esperando" in carritos[numero]:
        del carritos[numero]["esperando"]
    if "esperando_producto" in carritos[numero]:
        del carritos[numero]["esperando_producto"]
    carritos[numero]["productos_lista"] = list(productos_cat.keys())
    
    mensaje = f"📝 *{cat_nombre} - Lista de productos:*\n\n"
    
    for i, (pid, info) in enumerate(productos_cat.items(), 1):
        mensaje += f"*{i}.* {info['nombre']} - ${info['precio']:,}\n"
    
    mensaje += "\n_Escribe el *número* del producto que quieres pedir._"
    
    enviar_texto(numero, mensaje)

def buscar_producto(texto):
    """Busca un producto de forma flexible"""
    texto_limpio = texto.lower().strip().replace(" ", "")
    
    # Si es solo un número de 6 dígitos, es consulta de pedido
    if texto_limpio.isdigit() and len(texto_limpio) == 6:
        return None
    
    # Buscar coincidencia exacta
    if texto_limpio in PRODUCTOS:
        return texto_limpio
    
    # Buscar por nombre del producto
    for pid, info in PRODUCTOS.items():
        nombre_limpio = info["nombre"].lower().replace(" ", "")
        if texto_limpio == nombre_limpio:
            return pid
    
    return None



# --- LÓGICA DE PEDIDO ---

def preguntar_cantidad(numero, producto_id):
    nombre = PRODUCTOS[producto_id]["nombre"]
    enviar_texto(numero, f"¿Cuántas unidades de '{nombre}' quieres agregar al carrito?")
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
    if numero not in carritos:
        carritos[numero] = {}
    carrito = carritos[numero]
    costo_envio = carrito.get("costo_envio", 0)
    total = carrito.get("subtotal", 0) + costo_envio
    print(f"enviar_datos_pago - Carrito antes: {carritos.get(numero, {})}")
    
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
    print(f"enviar_datos_pago - Carrito despues: {carritos.get(numero, {})}")

def generar_numero_pedido():
    """Genera número único de 6 dígitos verificando en la base de datos"""
    while True:
        numero = str(random.randint(100000, 999999))
        # Verificar que no exista
        if DB_DISPONIBLE:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT 1 FROM pedidos WHERE numero_pedido = %s', (numero,))
                existe = cur.fetchone()
                cur.close()
                conn.close()
                if not existe:
                    return numero
            except:
                return numero
        else:
            if numero not in pedidos_memoria:
                return numero

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
    if DB_DISPONIBLE:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            fecha_colombia = datetime.datetime.now(COLOMBIA_TZ)
            cur.execute('''
                INSERT INTO pedidos (numero_pedido, cliente, telefono, direccion, tipo_entrega, items, subtotal, costo_envio, total, estado, fecha, wa_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                numero_pedido,
                pedido_data["cliente"].upper(),
                pedido_data["telefono"],
                pedido_data["direccion"].upper(),
                pedido_data["tipo_entrega"].upper(),
                json.dumps(pedido_data["items"]),
                pedido_data["subtotal"],
                pedido_data["costo_envio"],
                pedido_data["total"],
                pedido_data["estado"].upper(),
                fecha_colombia,
                pedido_data["wa_id"]
            ))
            conn.commit()
            cur.close()
            conn.close()
            print(f"Pedido guardado en Supabase: {numero_pedido}")
        except Exception as e:
            print(f"Error Supabase, guardando en memoria: {e}")
            pedidos_memoria[numero_pedido] = pedido_data
    else:
        pedidos_memoria[numero_pedido] = pedido_data
        print(f"Pedido guardado en memoria: {numero_pedido}")
    
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
    mensaje += f"*{numero_pedido}*\n\n"
    mensaje += "¡Gracias por tu compra! 🍫\n"
    mensaje += "_Chocolates del Castillo_"
    
    enviar_texto(numero, mensaje)
    
    # Limpiar carrito
    if numero in carritos:
        del carritos[numero]

def consultar_estado_pedido(numero, numero_pedido):
    pedido = None
    print(f"Consultando pedido: {numero_pedido.upper()}, DB_DISPONIBLE: {DB_DISPONIBLE}")
    if DB_DISPONIBLE:
        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('SELECT * FROM pedidos WHERE numero_pedido = %s', (numero_pedido.upper(),))
            pedido = cur.fetchone()
            print(f"Resultado DB: {pedido}")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error Supabase consulta: {e}")
    
    if not pedido:
        pedido = pedidos_memoria.get(numero_pedido.upper())
        print(f"Resultado memoria: {pedido}")
    
    if not pedido:
        enviar_texto(numero, f"❌ No encontramos el pedido *{numero_pedido}*\n\nVerifica el número e intenta de nuevo.")
        return
    
    # Formatear fecha en hora Colombia
    fecha = pedido['fecha']
    if isinstance(fecha, datetime.datetime):
        if fecha.tzinfo is None:
            fecha = pytz.utc.localize(fecha)
        fecha_colombia = fecha.astimezone(COLOMBIA_TZ)
        fecha_str = fecha_colombia.strftime("%d/%m/%Y %I:%M %p")
    else:
        fecha_str = str(fecha)
    
    mensaje = f"📋 *ESTADO DEL PEDIDO*\n"
    mensaje += "━━━━━━━━━━━━━━━━━━━━\n\n"
    mensaje += f"🔖 *Pedido:* {pedido['numero_pedido']}\n"
    mensaje += f"📅 *Fecha:* {fecha_str}\n"
    mensaje += f"👤 *Cliente:* {pedido['cliente']}\n\n"
    mensaje += f"📦 *Estado:* {pedido['estado']}\n\n"
    
    tipo_entrega = pedido['tipo_entrega'].lower() if pedido['tipo_entrega'] else ''
    if tipo_entrega == "domicilio":
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

            # Si el usuario está con asesor, el bot no responde
            if numero in usuarios_con_asesor:
                print(f"Usuario {numero} está con asesor, bot no responde")
                return "ok", 200

            # Detectar si quiere hablar con asesor (en cualquier momento)
            texto_check = ""
            if mensaje.get("type") == "text":
                texto_check = mensaje.get("text", {}).get("body", "").strip().lower()
            
            palabras_asesor = ["asesor", "vendedor", "hablar con un vendedor", "quiero hablar con un vendedor", "persona", "humano", "agente"]
            if any(palabra in texto_check for palabra in palabras_asesor):
                usuarios_con_asesor.add(numero)
                # Limpiar carrito si existe
                if numero in carritos:
                    del carritos[numero]
                enviar_texto(numero, "🧑‍💼 *¡Entendido!*\n\nUn asesor se comunicará contigo pronto.\n\nEl bot ha sido pausado para que puedas hablar directamente con una persona.\n\n_Si deseas volver al bot, escribe *menu*_")
                return "ok", 200

            # Si escribe "menu", reactivar el bot
            if texto_check == "menu" and numero in usuarios_con_asesor:
                usuarios_con_asesor.remove(numero)

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
                    enviar_texto(numero, "📦 Escribe tu *número de pedido* (6 dígitos).\n\nEjemplo: *123456*")
                elif reply_id == "asesor":
                    usuarios_con_asesor.add(numero)
                    if numero in carritos:
                        del carritos[numero]
                    enviar_texto(numero, "🧑‍💼 *¡Entendido!*\n\nUn asesor se comunicará contigo pronto.\n\nEl bot ha sido pausado para que puedas hablar directamente con una persona.\n\n_Si deseas volver al bot, escribe *menu*_")
                elif reply_id == "ver_categorias":
                    enviar_lista_categorias(numero)
                elif reply_id == "ver_otra_categoria":
                    enviar_lista_categorias(numero)
                elif reply_id == "ver_carrito_btn":
                    mostrar_carrito(numero)
                elif reply_id == "hacer_pedido":
                    enviar_lista_productos_para_pedir(numero)
                elif reply_id == "ya_se_que_pedir":
                    enviar_lista_categorias(numero)
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
                    enviar_texto(numero, "Opción no reconocida. Escribe *menu* para comenzar.")
                return "ok", 200

            # Detectar si es imagen o documento (comprobante de pago)
            tipo_mensaje = mensaje.get("type")
            if tipo_mensaje in ["image", "document"]:
                print(f"Imagen/documento recibido. Carrito: {carritos.get(numero, {})}")
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
                # Limpiar carrito y estados anteriores
                if numero in carritos:
                    del carritos[numero]
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

            # 4. Flujo de datos de envío (ANTES de consultar pedido para evitar confusión con direcciones numéricas)
            if numero in carritos and "esperando" in carritos[numero]:
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
                    enviar_texto(numero, "📸 Por favor envía una *imagen* o *foto* del comprobante de pago.\n\n_No podemos procesar texto, necesitamos ver el comprobante._")
                    return "ok", 200
                
                return "ok", 200

            # 5. Ingresar cantidad esperada
            if numero in carritos and "esperando_producto" in carritos[numero]:
                try:
                    cantidad = int(texto)
                    if cantidad <= 0:
                        raise ValueError()
                    agregar_al_carrito(numero, cantidad)
                except ValueError:
                    enviar_texto(numero, "Por favor escribe un número válido mayor a 0.")
                return "ok", 200

            # 5b. Seleccionar producto por número de la lista
            if numero in carritos and "productos_lista" in carritos[numero]:
                if texto.isdigit():
                    indice = int(texto) - 1
                    productos_lista = carritos[numero]["productos_lista"]
                    if 0 <= indice < len(productos_lista):
                        producto_id = productos_lista[indice]
                        preguntar_cantidad(numero, producto_id)
                        return "ok", 200
                    else:
                        enviar_texto(numero, f"❌ Número inválido. Escribe un número del 1 al {len(productos_lista)}.")
                        return "ok", 200

            # 6. Consultar estado de pedido (solo número de 6 dígitos)
            if texto.isdigit() and len(texto) == 6:
                consultar_estado_pedido(numero, texto)
                return "ok", 200
            
            # 6b. Consultar con "estado" + número
            if texto.startswith("estado "):
                numero_pedido = texto.replace("estado ", "").strip()
                consultar_estado_pedido(numero, numero_pedido)
                return "ok", 200

            # 7. Elegir producto (búsqueda flexible)
            producto_encontrado = buscar_producto(texto)
            if producto_encontrado:
                preguntar_cantidad(numero, producto_encontrado)
                return "ok", 200

            # 8. Default
            enviar_texto(numero, "No entendí tu mensaje 🤔\n\nEscribe:\n• *menu* - para comenzar\n• *categorias* - para ver productos\n• *ver carrito* - para revisar tu pedido")
            return "ok", 200

        except Exception as e:
            print("Error:", e)
            return "ok", 200


if __name__ == "__main__":
    app.run(port=5000)
