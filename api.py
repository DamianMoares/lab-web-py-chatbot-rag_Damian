import time
import logging
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel, Field
import chatbot

# Configuración del Logging básico
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="RAG Chatbot Local API", description="API para interactuar con LM Studio usando RAG")

# Almacenamiento básico en memoria para Rate Limiting: {ip: [timestamps]}
registro_peticiones = {}

# Middleware/Verificador manual de Rate Limit
def verificar_rate_limit(ip: str):
    ahora = time.time()
    if ip not in registro_peticiones:
        registro_peticiones[ip] = []
        
    # Filtrar peticiones de hace más de 60 segundos
    registro_peticiones[ip] = [t for t in registro_peticiones[ip] if ahora - t < 60]
    
    if len(registro_peticiones[ip]) >= 10:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Demasiadas peticiones. Límite de 10 por minuto."
        )
    
    registro_peticiones[ip].append(ahora)

# Modelos Pydantic para validación de entrada
class ChatRequest(BaseModel):
    pregunta: str = Field(..., max_length=500, description="La pregunta para el chatbot. Máx 500 caracteres.")
    session_id: str = Field(..., description="ID único de la sesión de chat")

@app.post("/chat")
def post_chat(payload: ChatRequest, request: Request):
    ip_cliente = request.client.host
    verificar_rate_limit(ip_cliente)
    
    # Logging de la llamada sin exponer el contenido interno de la base de datos
    logging.info(f"Petición recibida de IP: {ip_cliente} | Sesión: {payload.session_id} | Longitud: {len(payload.pregunta)}")
    
    # Control de privacidad (Advertencia de datos personales)
    if chatbot.detectar_datos_personales(payload.pregunta):
        return {
            "advertencia": "⚠️ PRIVACIDAD: Tu pregunta contiene posibles datos personales (como un email). Por seguridad corporativa, procesa esta información con cuidado.",
            "respuesta": "Petición bloqueada o pausada por motivos de privacidad. Elimina correos electrónicos o datos sensibles de tu consulta.",
            "fuentes": [],
            "session_id": payload.session_id,
            "fragmentos_usados": 0
        }
        
    # Procesar RAG
    resultado = chatbot.chat(payload.pregunta, payload.session_id)
    return resultado

@app.get("/chat/history/{session_id}")
def obtener_historial(session_id: str):
    if session_id not in chatbot.historiales:
        return {"session_id": session_id, "historial": []}
    return {"session_id": session_id, "historial": chatbot.historiales[session_id]}

@app.get("/documentos")
def listar_documentos():
    try:
        # Recuperamos todos los metadatos almacenados en la colección
        datos = chatbot.collection.get()
        if not datos['metadatas']:
            return {"documentos_indexados": []}
        
        # Filtrar nombres únicos de archivos
        archivos_unicos = list(set([meta['fuente'] for meta in datos['metadatas']]))
        return {"documentos_indexados": archivos_unicos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))