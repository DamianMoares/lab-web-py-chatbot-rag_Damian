import os
import glob
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

# Configuración del cliente local (LM Studio)
# Nota: LM Studio debe tener un modelo de embeddings cargado (ej. bge-large-en-v1.5 o similar)
client_llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Configurar ChromaDB persistente
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Usamos una función de embedding personalizada que llame a LM Studio
class LMStudioEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        response = client_llm.embeddings.create(
            model="local-model", # LM Studio ignora este nombre y usa el cargado
            input=input
        )
        return [data.embedding for data in response.data]

embedding_fn = LMStudioEmbeddingFunction()
collection = chroma_client.get_or_create_collection(
    name="documentos_rag", 
    embedding_function=embedding_fn
)

def chunk_text(text: str, max_chars: int = 500, overlap: int = 100) -> list[str]:
    """Fragmenta el texto en chunks basados en caracteres con un solapamiento."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start += max_chars - overlap
    return chunks

def indexar_documentos():
    archivos = glob.glob("docs/*.txt")
    total_chunks = 0
    total_caracteres = 0
    
    print(f"🔍 Encontrados {len(archivos)} archivos para indexar.")
    
    for ruta_archivo in archivos:
        nombre_archivo = os.path.basename(ruta_archivo)
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        total_caracteres += len(contenido)
        chunks = chunk_text(contenido)
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{nombre_archivo}_chunk_{idx}"
            
            # Guardar en ChromaDB con metadatos
            collection.upsert(
                documents=[chunk],
                metadatas=[{"fuente": nombre_archivo, "chunk_id": idx}],
                ids=[chunk_id]
            )
            total_chunks += 1

    # Resumen e información estimada (Al ser local, el coste es 0)
    print("\n🚀 --- RESUMEN DE INDEXACIÓN ---")
    print(f"📄 Documentos procesados: {len(archivos)}")
    print(f"🧩 Total de chunks creados: {total_chunks}")
    print(f"🔤 Caracteres totales: {total_caracteres}")
    print(f"💰 Coste estimado API: $0.00 (¡Ejecución 100% Local!)")
    print("---------------------------------\n")

if __name__ == "__main__":
    indexar_documentos()