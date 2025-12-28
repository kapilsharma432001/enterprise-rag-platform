# This file will contain the core AI logic: PDF -> Vectors
import os
from typing import List
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from app.config import settings

# innitialize embeddings model
embeddings_model = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

async def process_file(file: UploadFile, tenant_id: str, conn):
    # save the temp file: langchain loaders needs a file path on disk
    # FastAPI will give stream of bytes in memory and langchain needs a file path, it does not accept bytes directly
    file_location = f"/tmp/{file.filename}"

    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    # load and split the PDF
    loader = PyPDFLoader(file_location)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, # we are splitting the documents and if a sentence is split, we want to keep some overlap so that it does not lose the context
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Prcessing chunnsk {len(chunks)} for tenant {tenant_id}")

    # Generate embeddings and store in DB
    data_to_insert = []
    for chunk in chunks:
        # Generate vectors: list of floats
        vector = embeddings_model.embed_query(chunk.page_content)
        data_to_insert.append((tenant_id, 
                               chunk.page_content, 
                               str(vector) # convert list to string for postgres vector format
                               ))
        
        # Bulk insert (Raw SQL for speed)
        query = """
        INSERT INTO documents (tenant_id, content, embedding)
        VALUES ($1, $2, $3)
        """
    await conn.executemany(query, data_to_insert)
    print(f"Inserted {len(data_to_insert)} chunks for tenant {tenant_id}")

    # cleanup temp file
    os.remove(file_location)
    return len(data_to_insert)



