# 📖 Manual: Ejecutar Chatbot RAG con LM Studio
## Hardware: 8GB RAM + Intel i5-8ª Gen

---

## ⚠️ Consideraciones Previas de Hardware

### Tu configuración:
- **RAM**: 8GB (Limitada)
- **CPU**: Intel i5-8ª generación
- **GPU**: No disponible (CPU only)
- **Implicación**: Necesitas modelos pequeños y optimizados

### ¿Por qué esto importa?
- Modelos grandes (>7B parámetros) van a ser **muy lentos** (5-30 segundos por respuesta)
- Con 8GB necesitas modelos que no superen **3-4GB de VRAM**
- La CPU será el cuello de botella, no la RAM

### Recomendación de modelos:
✅ **IDEALES**:
- `Llama 2 7B` (3.5GB)
- `Mistral 7B` (3.5GB)  
- `Neural Chat 7B` (3.5GB)
- `bge-small-en-v1.5` para embeddings (pequeño, rápido)

❌ **EVITAR**:
- Modelos 13B o superiores
- `bge-large-en-v1.5` para embeddings (demasiado pesado)

---

## 🔧 Paso 1: Instalar LM Studio

### Windows:
1. Descarga desde: https://lmstudio.ai/
2. Instala normalmente (recomendado C:\Program Files\LM Studio)
3. Ejecuta la aplicación
4. Espera a que abra la interfaz web

### Pasos post-instalación:
1. Ve a la sección **"Models"** en la izquierda
2. Busca un modelo recomendado (ej: "mistral-7b")
3. Haz clic en el botón de descarga (⬇️)
4. Espera a que descargue completamente

---

## 🎯 Paso 2: Descargar Modelos Optimizados

### Opción A: Modelo LLM Principal (respuestas)
**Recomendado: Mistral 7B Instruct**

Pasos en LM Studio:
1. **Left panel** → `Models` → Buscador
2. Escribe: `mistral-7b-instruct-v0.1`
3. Selecciona la versión **GGUF** (formato optimizado)
4. Busca una versión de **4-bit quantized** (menor tamaño)
5. Haz clic en ⬇️ para descargar

**Tamaño esperado**: ~3.5-4GB

### Opción B: Modelo de Embeddings (búsqueda)
**Recomendado: bge-small-en-v1.5**

Pasos en LM Studio:
1. En el buscador escribe: `bge-small-en-v1.5`
2. Descarga la versión GGUF
3. **Tamaño**: ~130MB (muy ligero)

---

## 🚀 Paso 3: Configurar LM Studio para tu Chatbot

### Opción A: Activar servidor (recomendado)

1. En LM Studio, ve a **"Local Server"** (izquierda)
2. Selecciona el modelo `mistral-7b-instruct` en el dropdown
3. Haz clic en el botón **"Start Server"** (verde)
4. Verás un mensaje: `Server running on http://localhost:1234`
5. **Importante**: Deja LM Studio abierto mientras uses el chatbot

### Opción B: Configuración avanzada (opcional)
Si quieres ajustar performance, haz clic en ⚙️ (Settings):

```
Thread count: Pon el número de núcleos de tu i5 (típicamente 4-6)
Batch size: 1-2 (importante para 8GB RAM)
GPU layers: 0 (no hay GPU, todo en CPU)
Context length: 1024-2048 (no pongas 4096+)
```

---

## 💻 Paso 4: Preparar tu Proyecto Python

### 1. Activar el entorno virtual

**Si usas CMD o PowerShell:**
```bash
.venv\Scripts\activate
```

**Si usas Git Bash (MINGW64):**
```bash
source .venv/Scripts/activate
```

Deberías ver `(.venv)` al inicio de la línea

### 2. Instalar dependencias
```bash
pip install fastapi uvicorn openai chromadb pydantic
```

**Nota**: OpenAI SDK también funciona con LM Studio local (no necesita clave real)

### 3. Indexar los documentos (PRIMERA VEZ SOLO)
```bash
python indexer.py
```

Esto:
- Lee los archivos en `docs/`
- Crea embeddings con bge-small
- Guarda en base de datos ChromaDB (`./chroma_db/`)
- Toma 1-2 minutos

---

## ⚡ Paso 5: Ejecutar el Chatbot

### 1. Asegúrate que LM Studio está corriendo
- Debe estar abierto y mostrando "Server running on http://localhost:1234"

### 2. Ejecuta el servidor FastAPI
```bash
python api.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Accede a la API
- **Swagger UI**: http://localhost:8000/docs
- **API endpoint**: POST http://localhost:8000/chat

---

## 📝 Ejemplo: Hacer una pregunta al chatbot

### Opción A: Desde Swagger UI (interfaz web)
1. Ve a http://localhost:8000/docs
2. Haz clic en POST `/chat`
3. Haz clic en "Try it out"
4. Rellena el JSON:
```json
{
  "pregunta": "¿Cuál es la historia de Tenerife?",
  "session_id": "usuario_1"
}
```
5. Haz clic en "Execute"
6. **Espera 10-30 segundos** (procesamiento normal en i5-8)

### Opción B: Desde terminal (curl)
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"¿Cuál es la historia de Tenerife?","session_id":"usuario_1"}'
```

### Opción C: Script Python
```python
import requests

url = "http://localhost:8000/chat"
payload = {
    "pregunta": "¿Cuál es la historia de Tenerife?",
    "session_id": "usuario_1"
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## 🐛 Solución de Problemas

### Problema: "ConnectionError: http://localhost:1234"
**Causa**: LM Studio no está corriendo
**Solución**: Abre LM Studio → Local Server → Start Server

### Problema: "La respuesta tarda 30+ segundos"
**Causa**: Normal en i5-8 con modelos 7B
**Soluciones**:
1. Reduce `context_length` en LM Studio settings
2. Usa un modelo más pequeño (3B)
3. Aumenta `thread_count` en settings

### Problema: "Out of Memory" o crash
**Causa**: Modelo muy grande para 8GB
**Soluciones**:
1. Descarga un modelo **quantized 4-bit** (no 8-bit)
2. Cambia a un modelo más pequeño
3. Aumenta memoria virtual (no es ideal pero funciona)

### Problema: ChromaDB tardan en actualizar después de cambios
**Solución**: Elimina la carpeta `chroma_db/` y vuelve a ejecutar `indexer.py`

---

## 📊 Performance: Qué esperar

| Acción | Tiempo Aprox | Notas |
|--------|-------------|-------|
| Indexar documentos (primera vez) | 1-2 min | Solo una vez |
| Hacer pregunta simple | 8-15 seg | Depende de la pregunta |
| Cargar modelo en memoria | 5-10 seg | Al iniciar servidor |
| ChromaDB búsqueda vectorial | < 1 seg | Muy rápido |

**Optimización**: Con i5-8 + 8GB, espera respuestas en **10-20 segundos**. Esto es normal, no es un bug.

---

## 🔒 Seguridad y Privacidad

Tu chatbot tiene protecciones incorporadas:
- ✅ Detecta emails y datos personales
- ✅ No conecta a internet (todo local)
- ✅ Rate limiting (10 requests/minuto por IP)
- ✅ Responde SOLO con información de los documentos (no inventa)

---

## 📚 Estructura del Proyecto

```
project/
├── api.py              # Servidor FastAPI
├── chatbot.py          # Lógica principal del chatbot
├── indexer.py          # Indexar documentos (generar embeddings)
├── chroma_db/          # Base de datos vectorial (creado automáticamente)
├── docs/               # Tus documentos de referencia
│   ├── Historia de Tenerife.txt
│   ├── Historia de Gran canaria.txt
│   └── ...
└── requirements.txt    # Dependencias Python
```

---

## 🎓 Próximos Pasos (Opcional)

1. **Usa diferentes modelos**: Experimenta con Llama 2, Neural Chat
2. **Ajusta el prompt**: Edita `SYSTEM_PROMPT` en `chatbot.py`
3. **Añade más documentos**: Copia archivos .txt a `docs/` y re-indexa
4. **Crea una interfaz web**: Usa Streamlit o React frontend

---

## ⚙️ Comandos Rápidos (Resumen)

```bash
# Activar entorno virtual (Git Bash)
source .venv/Scripts/activate

# Activar entorno virtual (CMD/PowerShell)
# .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Primera ejecución: indexar documentos
python indexer.py

# Ejecutar el servidor
python api.py

# Test rápido (en otra terminal)
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"pregunta":"¿Qué sabes de Canarias?","session_id":"test"}'
```

---

## 📞 Si Algo Falla

1. **Revisa logs**: Busca mensajes de error en la terminal
2. **Reinicia LM Studio**: Cierra y abre de nuevo
3. **Limpia caché**: Elimina carpeta `chroma_db/` y re-indexa
4. **Verifica puerto 1234**: `netstat -ano | findstr :1234` (Windows)

---

**Última actualización**: Mayo 2026
**Testado con**: i5-8ª Gen + 8GB RAM
