import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from schemas import Contact as ContactSchema, Project as ProjectSchema
from database import create_document, get_documents, db

app = FastAPI(title="Portfolio API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start_time) * 1000)
    method = request.method
    path = request.url.path
    status = response.status_code
    print(f"{method} {path} -> {status} [{duration_ms}ms]")
    return response


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    if not doc:
        return {}
    out = dict(doc)
    _id = out.get("_id")
    if isinstance(_id, ObjectId):
        out["id"] = str(_id)
        del out["_id"]
    # Convert datetimes to isoformat if present
    for k, v in list(out.items()):
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
    return out


@app.get("/")
def read_root():
    return {"message": "Portfolio API running"}


@app.get("/api/health")
def health():
    """Basic health check"""
    return {"status": "ok"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ------------------------
# Contact Form Endpoint
# ------------------------
@app.post("/api/contact")
def submit_contact(payload: ContactSchema):
    """Accept contact form submissions and persist to DB"""
    try:
        inserted_id = create_document("contact", payload)
        return {"status": "success", "message": "Message received!", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")


# ------------------------
# Projects Endpoints
# ------------------------
@app.get("/api/projects")
def list_projects() -> List[dict]:
    """Return all projects; seed a few if collection is empty"""
    try:
        docs = get_documents("project")
        if not docs:
            seed = [
                {
                    "title": "Luxury Portfolio Website",
                    "description": "A dark, elegant personal site with Spline 3D hero and smooth animations.",
                    "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&q=80&auto=format&fit=crop",
                    "link": "https://example.com/portfolio"
                },
                {
                    "title": "E-commerce Starter",
                    "description": "Minimal storefront with cart, checkout, and product gallery.",
                    "image_url": "https://images.unsplash.com/photo-1519337265831-281ec6cc8514?w=1200&q=80&auto=format&fit=crop",
                    "link": "https://example.com/shop"
                },
                {
                    "title": "Realtime Chat App",
                    "description": "Socket-powered chat with presence and message history.",
                    "image_url": "https://images.unsplash.com/photo-1517816743773-6e0fd518b4a6?w=1200&q=80&auto=format&fit=crop",
                    "link": "https://example.com/chat"
                }
            ]
            # Insert seed items
            for item in seed:
                create_document("project", item)
            docs = get_documents("project")
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@app.post("/api/projects")
def add_project(payload: ProjectSchema):
    """Add a new project (admin use)"""
    try:
        inserted_id = create_document("project", payload)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add project: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
