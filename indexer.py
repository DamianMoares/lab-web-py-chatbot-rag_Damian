import os
import glob
import tiktoken
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from utils import chunk_text

client_llm = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

chroma_client = chromadb.PersistentClient(path="./chroma_db")

class LMStudioEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        try:
            response = client_llm.embeddings.create(
                model="local-model",
                input=input
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"\n❌ ERROR: No se puede conectar a LM Studio en http://localhost:1234")
            print(f"   Asegúrate de que LM Studio está abierto y el servidor está activo.")
            print(f"   Error: {str(e)}\n")
            raise

embedding_fn = LMStudioEmbeddingFunction()
collection = chroma_client.get_or_create_collection(
    name="documentos_rag", 
    embedding_function=embedding_fn
)

def contar_tokens(texto: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(texto))

def indexar_documentos():
    archivos = glob.glob("docs/*.txt")
    total_chunks = 0
    total_tokens = 0
    
    print(f"🔍 Encontrados {len(archivos)} archivos para indexar.")
    
    for ruta_archivo in archivos:
        nombre_archivo = os.path.basename(ruta_archivo)
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        total_tokens += contar_tokens(contenido)
        chunks = chunk_text(contenido)
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{nombre_archivo}_chunk_{idx}"
            
            collection.upsert(
                documents=[chunk],
                metadatas=[{"fuente": nombre_archivo, "chunk_id": idx}],
                ids=[chunk_id]
            )
            total_chunks += 1

    coste_estimado = total_tokens * 0.0001 / 1000 if total_tokens > 0 else 0

    print("\n🚀 --- RESUMEN DE INDEXACIÓN ---")
    print(f"📄 Documentos procesados: {len(archivos)}")
    print(f"🧩 Total de chunks creados: {total_chunks}")
    print(f"🔤 Tokens totales procesados: {total_tokens}")
    print(f"💰 Coste estimado API: ${coste_estimado:.4f} ({'Ejecución Local' if coste_estimado == 0 else 'Aprox. OpenAI text-embedding-ada-002'})")
    print("---------------------------------\n")

if __name__ == "__main__":
    indexar_documentos()