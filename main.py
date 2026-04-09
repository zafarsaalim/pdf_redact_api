from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import fitz
import uuid
import os

app = FastAPI(title="PDF Redact API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
