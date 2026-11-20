import os
import urllib.parse
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import (
    Destination,
    TouristAgent,
    AIRecommendationRequest,
    EnquiryRequest
)
from .data import DESTINATIONS, AGENTS
from .ai_service import get_travel_recommendation
from .db import init_db, save_enquiry, get_all_enquiries, get_enquiries_count

# Initialize SQLite database
init_db()

app = FastAPI(
    title="BharatYatra AI - India Tourism & Local Guides Platform",
    description="Intelligent destination recommendations and verified tourist agent connection across India.",
    version="1.1.0"
)

# Enable CORS for mobile apps, emulators, and local web views
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "BharatYatra AI",
        "gemini_api_configured": bool(os.environ.get("GEMINI_API_KEY")),
        "destinations_count": len(DESTINATIONS),
        "agents_count": len(AGENTS),
        "enquiries_logged": get_enquiries_count()
    }

@app.get("/api/stats")
def platform_stats():
    """Live stats for platform transparency, trust badges, and executive demo dashboard."""
    unique_states = sorted(list({d.state for d in DESTINATIONS}))
    avg_rating = round(sum(a.rating for a in AGENTS) / len(AGENTS), 2) if AGENTS else 4.9
    total_reviews = sum(a.review_count for a in AGENTS)
    
    return {
        "total_destinations": len(DESTINATIONS),
        "total_verified_agents": len(AGENTS),
        "states_covered": len(unique_states),
        "states_list": unique_states,
        "average_agent_rating": avg_rating,
        "total_verified_reviews": total_reviews,
        "enquiries_captured": get_enquiries_count(),
        "zero_commission_guarantee": True
    }

@app.get("/api/enquiries")
def list_enquiries():
    """Returns persistent booking enquiries & operator leads captured."""
    return get_all_enquiries()

@app.get("/api/destinations", response_model=List[Destination])
def get_destinations(
    category: Optional[str] = None,
    region: Optional[str] = None
):
    results = DESTINATIONS
    if category and isinstance(category, str) and category.lower() != "all":
        results = [d for d in results if d.category.lower() == category.lower()]
    if region and isinstance(region, str) and region.lower() != "all":
        results = [d for d in results if d.region.lower() == region.lower()]
    return results

@app.get("/api/destinations/{dest_id}")
def get_destination_details(dest_id: str):
    dest = next((d for d in DESTINATIONS if d.id == dest_id), None)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    assigned_agents = [a for a in AGENTS if a.destination_id == dest_id]
    return {
        "destination": dest,
        "agents": assigned_agents
    }

@app.get("/api/agents", response_model=List[TouristAgent])
def get_agents(
    destination_id: Optional[str] = None,
    state: Optional[str] = None
):
    results = AGENTS
    if destination_id and isinstance(destination_id, str) and destination_id.lower() != "all":
        results = [a for a in results if a.destination_id == destination_id]
    if state and isinstance(state, str) and state.lower() != "all":
        results = [a for a in results if a.state.lower() == state.lower()]
    return results

@app.get("/api/agents/{agent_id}", response_model=TouristAgent)
def get_agent_by_id(agent_id: str):
    agent = next((a for a in AGENTS if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Tourist Agent not found")
    return agent

@app.post("/api/recommend")
def recommend_travel(
    req: AIRecommendationRequest,
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key")
):
    """
    AI Endpoint: Evaluates travel preferences and suggests the best places in India,
    paired with verified local tourist guides and day-by-day itineraries.
    """
    return get_travel_recommendation(req, custom_api_key=x_gemini_api_key)

@app.post("/api/enquiry")
def submit_enquiry(enquiry: EnquiryRequest):
    """
    Connects a customer with a chosen tourist agent.
    Returns contact verification and pre-formatted WhatsApp direct message link.
    """
    agent = next((a for a in AGENTS if a.id == enquiry.agent_id), None)
    dest = next((d for d in DESTINATIONS if d.id == enquiry.destination_id), None)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    dest_name = dest.name if dest else "India Tour"
    
    # Generate pre-filled WhatsApp link
    msg = (
        f"Namaste {agent.name}! I found your profile on BharatYatra AI.\n"
        f"I am planning a trip to *{dest_name}* for {enquiry.num_travelers} people.\n"
        f"Traveler Name: {enquiry.traveler_name}\n"
        f"Dates: {enquiry.travel_dates or 'Flexible'}\n"
        f"Notes: {enquiry.notes or 'Looking forward to customized packages and quotes.'}"
    )
    encoded_msg = urllib.parse.quote(msg)
    whatsapp_url = f"https://wa.me/{agent.whatsapp}?text={encoded_msg}"
    
    enq_count = get_enquiries_count()
    record = {
        "id": f"ENQ-{enq_count + 1:04d}",
        "destination_id": enquiry.destination_id,
        "destination_name": dest_name,
        "agent_id": agent.id,
        "agent_name": agent.name,
        "agency_name": agent.agency_name,
        "traveler_name": enquiry.traveler_name,
        "traveler_phone": enquiry.traveler_phone,
        "travel_dates": enquiry.travel_dates or "Flexible",
        "num_travelers": enquiry.num_travelers,
        "notes": enquiry.notes or "Looking forward to customized packages and quotes.",
        "whatsapp_url": whatsapp_url,
        "status": "New Lead"
    }
    saved_record = save_enquiry(record)
    
    return {
        "status": "success",
        "message": f"Enquiry successfully registered for {agent.name} at {agent.agency_name}!",
        "enquiry_id": saved_record["id"],
        "whatsapp_chat_url": whatsapp_url,
        "agent_contact": {
            "name": agent.name,
            "agency": agent.agency_name,
            "phone": agent.phone,
            "badge": agent.badge
        }
    }

# Mount static files for the frontend mobile client
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_mobile_app():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "BharatYatra AI Backend running. Static frontend not yet compiled."}

@app.get("/service-worker.js")
def serve_service_worker():
    sw_path = os.path.join(frontend_dir, "service-worker.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Service worker not found")
