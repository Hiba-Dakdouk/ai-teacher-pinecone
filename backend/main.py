from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import File
from pdf_parser import extract_text_from_pdf
from rag import index_document, search
from models import ChatRequest
from chat import get_chat_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,    
    allow_origins=[
    "http://localhost:5173",                          # local dev
    "https://ai-teacher-pinecone.vercel.app"          # production
    ], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Teacher API is running!"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        reply = get_chat_response(request.messages)
        return {"reply": reply}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong")
    
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    # accpet file upload
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        file_bytes = await file.read()
        text = extract_text_from_pdf(file_bytes)
        num_chunks = index_document(text)
        return {"message": f"File uploaded and indexed successfully! Total chunks: {num_chunks}"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the uploaded file")

@app.post("/admin/upload")
async def upload(file: UploadFile = File(...)):
    # accpet file upload
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        file_bytes = await file.read()
        text = extract_text_from_pdf(file_bytes)
        num_chunks = index_document(text, collection_name="owner_docs")
        return {"message": f"File uploaded and indexed successfully! Total chunks: {num_chunks}"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the uploaded file")
