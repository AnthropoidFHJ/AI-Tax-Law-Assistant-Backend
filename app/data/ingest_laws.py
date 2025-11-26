import os
import asyncio
from pathlib import Path
from app.services.ai_service import AIService, _embed_texts
from app.utils.preprocess import chunk_text, clean_text, parse_pdf
from app.utils.data_clean import encrypt_bytes


class LawIngester:
    def __init__(self):
        self.service = AIService()
        
    async def ingest_law_folder(self, folder_path: str = "app/data"):
        folder = Path(folder_path)
        if not folder.exists():
            print(f"Folder {folder_path} not found")
            return

        for file_path in folder.glob("*.txt"):
            await self.ingest_law_file(str(file_path))
        for file_path in folder.glob("*.pdf"):
            await self.ingest_law_file(str(file_path))

        laws_folder = folder / "laws"
        if laws_folder.exists():
            for file_path in laws_folder.glob("*.txt"):
                await self.ingest_law_file(str(file_path))
            for file_path in laws_folder.glob("*.pdf"):
                await self.ingest_law_file(str(file_path))
            
    async def ingest_law_file(self, file_path: str):
        print(f"Ingesting: {file_path}")
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            text = parse_pdf(pdf_bytes)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
        text = clean_text(text)
        if not text.strip():
            print(f"No text extracted from {file_path}")
            return
            
        chunks = chunk_text(text)
        embeddings = _embed_texts(chunks)
        
        if self.service.index:
            filename = Path(file_path).stem
            vectors = [
                (f"{filename}-{i}", embeddings[i], {
                    "source": filename,
                    "chunk_id": i,
                    "content": chunks[i][:200]  # preview
                })
                for i in range(len(chunks))
            ]
            self.service.index.upsert(vectors=vectors)
            print(f"✓ Upserted {len(vectors)} vectors for {filename}")
        else:
            print("Pinecone not initialized")

async def main():
    ingester = LawIngester()
    await ingester.ingest_law_folder()
    print("Knowledge base ingestion complete!")

if __name__ == "__main__":
    asyncio.run(main())