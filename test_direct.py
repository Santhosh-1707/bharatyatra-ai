from backend.app.data import DESTINATIONS, AGENTS
from backend.app.ai_service import get_travel_recommendation
from backend.app.models import AIRecommendationRequest, EnquiryRequest
from backend.app.main import submit_enquiry, get_destinations, get_agents

def run_all_checks():
    print(f"1. DESTINATIONS: Loaded {len(DESTINATIONS)} curated destinations across India.")
    assert len(DESTINATIONS) >= 8

    print(f"2. AGENTS: Loaded {len(AGENTS)} verified local guides & tour operators.")
    assert len(AGENTS) >= 10

    # Test filtering
    mountains = get_destinations(category="mountains")
    print(f"3. FILTER CHECK: Found {len(mountains)} mountain destinations.")
    assert len(mountains) >= 2

    # Test recommendation
    req = AIRecommendationRequest(
        vibe="nature",
        budget="moderate",
        duration_days=5,
        companions="family",
        preferred_region="South"
    )
    rec = get_travel_recommendation(req)
    print("4. AI RECOMMENDATION: Selected Destination ->", rec["primary_destination"]["name"])
    print("   AI Narrative:", rec["ai_narrative"][:90] + "...")
    print(f"   Itinerary: Generated {len(rec['suggested_itinerary'])} days with tips.")
    print(f"   Local Guides Found: {len(rec['recommended_agents'])} verified operators in area.")
    assert rec["primary_destination"]["name"] is not None
    assert len(rec["suggested_itinerary"]) == 5
    assert len(rec["recommended_agents"]) > 0

    # Test Enquiry & WhatsApp Link
    enq = EnquiryRequest(
        destination_id="munnar",
        agent_id="agent_k1",
        traveler_name="Priya Sharma",
        traveler_phone="+919876543210",
        travel_dates="2026-11-20",
        num_travelers=4,
        notes="Need family houseboat package with food"
    )
    res = submit_enquiry(enq)
    print("5. ENQUIRY / WHATSAPP INTEGRATION: Enquiry ID ->", res["enquiry_id"])
    print("   Target Agent:", res["agent_contact"]["name"], f"({res['agent_contact']['agency']})")
    print("   WhatsApp Chat Link:", res["whatsapp_chat_url"][:65] + "...")
    assert "https://wa.me/" in res["whatsapp_chat_url"]

    print("\n✅ ALL BACKEND & AI MODULE TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_all_checks()
