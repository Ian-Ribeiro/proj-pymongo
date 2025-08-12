from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict
from models import MercadoDB

app = FastAPI(title="Mercado API (FastAPI wrapper)")

mercado = MercadoDB()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/collections")
def get_collections():
    try:
        return mercado.list_collections_api()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/template/{collection_name}")
def get_template(collection_name: str):
    try:
        return mercado.get_template_api(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{collection_name}")
def list_documents(collection_name: str):
    try:
        return mercado.list_documents_api(collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{collection_name}/{doc_id}")
def get_document(collection_name: str, doc_id: str):
    try:
        doc = mercado.get_document_api(collection_name, doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insert/{collection_name}")
def insert_document(collection_name: str, data: Dict[str, Any]):
    try:
        return mercado.inserir_api(collection_name, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/update/{collection_name}/{doc_id}")
def update_document(collection_name: str, doc_id: str, update: Dict[str, Any]):
    try:
        return mercado.update_api(collection_name, doc_id, update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/replace/{collection_name}/{doc_id}")
def replace_document(collection_name: str, doc_id: str, new_doc: Dict[str, Any]):
    try:
        return mercado.replace_api(collection_name, doc_id, new_doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/delete/{collection_name}/{doc_id}")
def delete_document(collection_name: str, doc_id: str):
    try:
        return mercado.delete_api(collection_name, doc_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))