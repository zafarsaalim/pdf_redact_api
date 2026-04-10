from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware  # ✅ ADD THIS

import fitz
import uuid
import os

app = FastAPI(title="PDF Redact API")
# ✅ ADD THIS BLOCK (right after app creation)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing, allows all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Hello World!"}
@app.post("/redact")
async def redact_pdf(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(input_path, "wb") as f:
        f.write(await file.read())

    doc = fitz.open(input_path)
    for page in doc:
        for annot in page.annots(types=[8]):  # highlight annotations only
            rect = annot.rect
            page.add_redact_annot(rect, fill=(0, 0, 0))
        page.apply_redactions()

    output_path = input_path.replace(".pdf", "_redacted.pdf")
    doc.save(output_path)
    doc.close()
    return FileResponse(output_path, filename="redacted.pdf", media_type="application/pdf")
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
