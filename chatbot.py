import re
from openai import OpenAI
import chromadb
from indexer import LMStudioEmbeddingFunction

client_llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedding_fn = LMStudioEmbeddingFunction()
collection = chroma_client.get_or_create_collection(name="documentos_rag", embedding_function=embedding_fn)

# Historial en memoria: {session_id: [mensajes]}
historiales = {}

SYSTEM_PROMPT = """Eres un asistente virtual estricto y honesto. Tu único objetivo es responder preguntas utilizando exclusivamente el contexto proporcionado abajo.

Reglas obligatorias:
1. Responde SOLO con la información del contexto.
2. Si el contexto no contiene la respuesta, o no es suficiente, di exactamente: "No tengo información sobre eso."
3. No inventes datos, hechos, ni supuestos fuera del contexto.
4. Mantén un tono profesional y directo."""

def detectar_datos_personales(texto: str) -> bool:
    patron_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    patron_nombre = r'\b(?:[A-Z][a-záéíóúñ]+)\s+(?:[A-Z][a-záéíóúñ]+\s+){1,}[A-Z][a-záéíóúñ]+\b'
    patron_telefono = r'(?:\+?\d{1,3})?[\s.-]?\d{9,12}'
    patron_dni = r'\b\d{8}[A-Za-z]\b'
    if re.search(patron_email, texto):
        return True
    if re.search(patron_telefono, texto):
        return True
    if re.search(patron_dni, texto):
        return True
    return False

def chat(pregunta: str, session_id: str) -> dict:
    resultados = collection.query(
        query_texts=[pregunta],
        n_results=3
    )
    
    fragmentos = resultados['documents'][0] if resultados.get('documents') and resultados['documents'][0] else []
    metadatas = resultados['metadatas'][0] if resultados.get('metadatas') and resultados['metadatas'][0] else []
    
    if not fragmentos:
        return {
            "respuesta": "No tengo información sobre eso.",
            "fuentes": [],
            "session_id": session_id,
            "fragmentos_usados": 0
        }
    
    fuentes_usadas = list(set([meta['fuente'] for meta in metadatas]))
    
    contexto_str = "\n\n".join([f"[Fuente: {meta['fuente']}]: {doc}" for doc, meta in zip(fragmentos, metadatas)])
    
    # 3. Gestionar historial de conversación
    if session_id not in historiales:
        historiales[session_id] = []
        
    # Construir los mensajes para el modelo
    mensajes = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCONTEXTO DISPONIBLE:\n{contexto_str}"}]
    
    # Añadir últimas interacciones del historial para dar memoria (ej. últimas 4)
    for msg in historiales[session_id][-4:]:
        mensajes.append(msg)
        
    mensajes.append({"role": "user", "content": pregunta})
    
    # Llamada a LM Studio
    response = client_llm.chat.completions.create(
        model="local-model",
        messages=mensajes,
        temperature=0.0 # Temperatura 0 para evitar alucinaciones
    )
    
    respuesta_texto = response.choices[0].message.content
    
    # Guardar en el historial la interacción real
    historiales[session_id].append({"role": "user", "content": pregunta})
    historiales[session_id].append({"role": "assistant", "content": respuesta_texto})
    
    return {
        "respuesta": respuesta_texto,
        "fuentes": fuentes_usadas if "No tengo información" not in respuesta_texto else [],
        "session_id": session_id,
        "fragmentos_usados": len(fragmentos)
    }