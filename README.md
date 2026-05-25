![logo_ironhack_blue 7](https://user-images.githubusercontent.com/23629340/40541063-a07a0a8a-601a-11e8-91b5-2f13e4e6b441.png)

# 🏝️ Chatbot RAG - Historia de las Islas Canarias

## 📋 Descripción del Proyecto

Este es un **chatbot inteligente basado en RAG (Retrieval Augmented Generation)** que responde preguntas sobre la historia, geografía y características de las Islas Canarias. El sistema utiliza modelos de lenguaje local (LM Studio) para mantener la privacidad de los datos y proporciona respuestas basadas exclusivamente en los documentos de referencia.

### Características principales:
- ✅ **RAG (Retrieval Augmented Generation)**: Recupera fragmentos relevantes de documentos antes de generar respuestas
- ✅ **Modelos Locales**: Integración con LM Studio para embeddings y LLM sin depender de APIs externas
- ✅ **ChromaDB**: Base de datos vectorial persistente para almacenar embeddings de documentos
- ✅ **API REST**: Interfaz FastAPI con documentación interactiva (Swagger UI)
- ✅ **Rate Limiting**: Protección contra abuso (máx 10 peticiones/minuto por IP)
- ✅ **Detección de Privacidad**: Alertas cuando la pregunta contiene datos personales (emails, etc.)
- ✅ **Historial de Sesiones**: Mantiene el contexto de conversación por sesión
- ✅ **Metadatos de Fuentes**: Indica qué documentos se usaron en cada respuesta

## 📚 Dataset

El proyecto incluye **9 documentos históricos** sobre las Islas Canarias:
- `Historia de Tenerife.txt`
- `Historia de Gran canaria.txt`
- `Historia de Lanzarote.txt`
- `Historia de la Palma.txt`
- `Historia de la Gomera.txt`
- `Historia del Hierro.txt`
- `Historia de Fuerteventura.txt`
- `Historia de la Graciosa.txt`
- `La historia de las Islas Canarias e.txt`

## 🚀 Instalación y Setup

### Requisitos previos
- **Python 3.8+**
- **LM Studio** instalado y corriendo con un modelo de embeddings (ej: bge-large-en-v1.5)
- El servidor de LM Studio debe estar activo en `http://localhost:1234`

### Pasos de instalación

```bash
# 1. Clonar el repositorio
cd lab-web-py-chatbot-rag_Damian

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install fastapi uvicorn openai chromadb python-dotenv tiktoken

# 5. Guardar dependencias
pip freeze > requirements.txt
```

### Indexar los documentos

Antes de usar el chatbot, debes indexar todos los documentos:

```bash
python indexer.py
```

**Salida esperada:**
```
🔍 Encontrados 9 archivos para indexar.
✅ Indexación completa:
   - 9 documentos
   - ~X chunks creados
   - ~Y tokens procesados
   - Coste estimado: $Z
```

Este proceso:
1. Lee todos los archivos `.txt` de la carpeta `docs/`
2. Fragmenta documentos largos en chunks de ~500 caracteres
3. Crea embeddings usando LM Studio
4. Almacena todo en ChromaDB de forma persistente (`./chroma_db/`)

## 🏗️ Arquitectura del Sistema

```
lab-web-py-chatbot-rag_Damian/
├── docs/                    ← Documentos fuente sobre Islas Canarias
│   ├── Historia de Tenerife.txt
│   ├── Historia de Gran canaria.txt
│   └── ... (9 documentos totales)
├── chroma_db/               ← Base de datos vectorial persistente (se crea al indexar)
├── indexer.py               ← Script de indexación (crea embeddings y ChromaDB)
├── chatbot.py               ← Lógica RAG + LLM (responde preguntas)
├── api.py                   ← FastAPI REST (interfaz del chatbot)
└── requirements.txt         ← Dependencias del proyecto
```

## 📖 Componentes del Proyecto

### 1️⃣ **indexer.py** - Indexador de Documentos
**Responsabilidades:**
- Lee todos los archivos `.txt` de la carpeta `docs/`
- Fragmenta documentos largos en chunks (máx 500 caracteres, 100 de solapamiento)
- Crea embeddings usando LM Studio
- Almacena vectores y metadatos en ChromaDB

**Uso:**
```bash
python indexer.py
```

### 2️⃣ **chatbot.py** - Motor RAG
**Responsabilidades:**
- Recupera fragmentos relevantes de ChromaDB (top-3)
- Construye prompts con contexto para el LLM
- Mantiene historial de conversación por sesión
- Detecta intentos de suplantación de identidad (emails)
- Devuelve respuestas con fuentes citadas

**Función principal:**
```python
chat(pregunta: str, session_id: str) -> dict
# Retorna:
# {
#   "respuesta": "...",
#   "fuentes": ["archivo1.txt", "archivo2.txt"],
#   "session_id": "...",
#   "fragmentos_usados": 3
# }
```

**Reglas de respuesta:**
- ✅ Responde SOLO con información del contexto indexado
- ✅ Si no hay contexto relevante, responde: "No tengo información sobre eso."
- ❌ NUNCA inventa datos fuera del contexto
- ❌ NUNCA alucinaciones o suposiciones

### 3️⃣ **api.py** - API REST con FastAPI
**Endpoints disponibles:**

#### `POST /chat` - Hacer una pregunta
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuáles son las principales islas Canarias?",
    "session_id": "usuario_123"
  }'
```
**Respuesta:**
```json
{
  "respuesta": "Las principales islas Canarias son Tenerife, Gran Canaria, Lanzarote...",
  "fuentes": ["Historia Tenerife.txt", "Historia de Gran canaria.txt"],
  "session_id": "usuario_123",
  "fragmentos_usados": 3
}
```

#### `GET /chat/history/{session_id}` - Ver historial de sesión
```bash
curl "http://localhost:8000/chat/history/usuario_123"
```

#### `GET /documentos` - Listar documentos indexados
```bash
curl "http://localhost:8000/documentos"
```

#### `GET /docs` - Documentación interactiva (Swagger UI)
Accede a: `http://localhost:8000/docs`

**Medidas de seguridad implementadas:**
- 🔒 Rate limiting: Máx 10 peticiones/minuto por IP
- 🔒 Validación de entrada: Preguntas limitadas a 500 caracteres
- 🔒 Detección de privacidad: Alerta si hay emails en la pregunta
- 📝 Logging: Todas las solicitudes se registran (sin exponer datos sensibles)

## ▶️ Cómo usar el proyecto

### Paso 1: Preparar LM Studio
1. Abre LM Studio
2. Carga un modelo de embeddings (ej: `bge-large-en-v1.5`)
3. Inicia el servidor local en `http://localhost:1234`
4. Asegúrate que el servidor esté corriendo

### Paso 2: Indexar documentos
```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows

# Indexar todos los documentos de docs/
python indexer.py
```

### Paso 3: Ejecutar la API
```bash
# Activar entorno virtual (si no está activado)
venv\Scripts\activate  # Windows

# Iniciar servidor FastAPI
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Salida esperada:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Paso 4: Probar el chatbot
Abre en tu navegador: **http://localhost:8000/docs**

Se abrirá Swagger UI donde puedes:
- 📝 Escribir preguntas sobre las Islas Canarias
- 📊 Ver respuestas con fuentes citadas
- 🔍 Explorar el historial de conversaciones

**Ejemplo de preguntas:**
```
"¿Cuál es la capital de Tenerife?"
"¿Qué puedes decirme sobre la geografía de Lanzarote?"
"¿Cuáles son las Islas Canarias principales?"
```

## 🧪 Ejemplos de uso (curl)

### Hacer una pregunta
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Qué islas forman parte del archipiélago canario?",
    "session_id": "usuario_001"
  }'
```

### Ver historial de sesión
```bash
curl "http://localhost:8000/chat/history/usuario_001"
```

### Listar documentos indexados
```bash
curl "http://localhost:8000/documentos"
```

## 🔧 Configuración

### Parámetros de chunking (en `indexer.py`)
```python
def chunk_text(text: str, max_chars: int = 500, overlap: int = 100):
    # max_chars: tamaño máximo de cada fragmento
    # overlap: caracteres de solapamiento entre fragmentos (para contexto)
```

### Rate Limiting (en `api.py`)
```python
RATE_LIMIT = 10  # máximas peticiones
RATE_LIMIT_WINDOW = 60  # en segundos
```

## 📊 Estructura de datos en ChromaDB

Cada documento se almacena con:
```json
{
  "document": "fragmento de texto...",
  "metadata": {
    "fuente": "Historia de Tenerife.txt",
    "chunk_id": 0
  },
  "embedding": [0.123, -0.456, ..., 0.789]
}
```

## 🛡️ Privacidad y seguridad

✅ **Implementado:**
- Modelos locales (datos no enviados a servidores externos)
- Detección de emails en preguntas
- Rate limiting por IP
- Validación de longitud de entrada
- Logging sin exposición de datos sensibles
- ChromaDB persistente pero privado

⚠️ **Consideraciones:**
- Los documentos de `docs/` se indexan completamente (protege estos archivos)
- El historial de sesiones se guarda en memoria (se pierde al reiniciar)
- Para producción, considera base de datos persistente para sesiones

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| `Connection refused: localhost:1234` | LM Studio no está corriendo. Inicia LM Studio y asegúrate el servidor esté activo |
| `No module named 'fastapi'` | Instala dependencias: `pip install -r requirements.txt` |
| `ChromaDB not found` | Ejecuta primero `python indexer.py` para crear la BD |
| `Error: documents not indexed` | Verifica que la carpeta `docs/` existe y tiene archivos `.txt` |
| `Too many requests` | Has superado el límite de 10 peticiones/minuto. Espera 60 segundos |

## 📝 Autor y Licencia

Proyecto de laboratorio de Ironhack - Módulo Python & Web Development  
Realizado por: Damian M.

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [LM Studio](https://lmstudio.ai/)
- [RAG Pattern - NVIDIA](https://blogs.nvidia.com/blog/2023/11/retrieval-augmented-generation-working-examples/)

