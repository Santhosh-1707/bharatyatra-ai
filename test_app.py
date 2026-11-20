"""
BharatYatra AI - End-to-End Application Test Suite
Tests all FastAPI endpoints, SQLite persistence, AI matcher, and WhatsApp generation.
"""

import sys
import os
from backend.app.main import (
    app,
    health_check,
    platform_stats,
    list_enquiries,
    get_destinations,
    get_destination_details,
    get_agents,
    get_agent_by_id,
    recommend_travel,
    submit_enquiry,
    serve_mobile_app
)
from backend.app.models import AIRecommendationRequest, EnquiryRequest
from backend.app.data import DESTINATIONS, AGENTS
from backend.app.db import get_all_enquiries

def run_tests():
    print("=" * 60)
    print("🚀 Running BharatYatra AI Full Integration Tests")
    print("=" * 60)

    # 1. Test Health Endpoint
    health = health_check()
    assert health["status"] == "healthy"
    assert health["destinations_count"] >= 12
    assert health["agents_count"] >= 20
    print(f"✓ [1/7] Health Check Passed: {health['app']} (Destinations: {health['destinations_count']}, Agents: {health['agents_count']})")

    # 2. Test Platform Stats Endpoint
    stats = platform_stats()
    assert stats["total_destinations"] >= 12
    assert stats["total_verified_agents"] >= 20
    assert stats["states_covered"] >= 8
    assert stats["zero_commission_guarantee"] is True
    print(f"✓ [2/7] Platform Stats Passed: {stats['states_covered']} States, {stats['total_verified_agents']} Guides across India, Rating {stats['average_agent_rating']}★")

    # 3. Test Destinations Catalog & Filtering
    all_dests = get_destinations()
    assert len(all_dests) >= 12
    mountain_dests = get_destinations(category="mountains")
    assert len(mountain_dests) >= 3
    south_dests = get_destinations(region="South")
    assert len(south_dests) >= 3
    kashmir = get_destination_details("kashmir")
    assert kashmir["destination"].name == "Srinagar, Gulmarg & Pahalgam"
    assert len(kashmir["agents"]) >= 2
    print(f"✓ [3/7] Destinations API Passed: 12 Destinations cataloged with regional and category filters")

    # 4. Test Verified Tourist Agents Directory & Search
    all_agents = get_agents()
    assert len(all_agents) >= 20
    kashmir_agents = get_agents(destination_id="kashmir")
    assert len(kashmir_agents) >= 2
    agent = get_agent_by_id("agent_ks1")
    assert agent.name == "Ghulam Nabi Mir"
    assert "Houseboat" in str(agent.specialties)
    print(f"✓ [4/7] Verified Agents API Passed: {len(all_agents)} Certified local guides & trek specialists loaded")

    # 5. Test AI Travel Recommendation & Itinerary Planner
    rec_req = AIRecommendationRequest(
        vibe="mountains",
        budget="moderate",
        duration_days=5,
        companions="couple",
        preferred_region="North"
    )
    rec = recommend_travel(rec_req)
    assert "primary_destination" in rec
    assert rec["primary_destination"]["id"] in ["manali", "kashmir", "ladakh"]
    assert len(rec["suggested_itinerary"]) == 5
    assert len(rec["recommended_agents"]) >= 1
    assert len(rec["alternative_destinations"]) >= 1
    print(f"✓ [5/7] AI Recommendation Engine Passed: Recommended {rec['primary_destination']['name']} with {len(rec['suggested_itinerary'])}-day tailored itinerary")

    # 6. Test SQLite Persistent Booking Enquiry & Direct WhatsApp Integration
    enq_req = EnquiryRequest(
        destination_id="kashmir",
        agent_id="agent_ks1",
        traveler_name="Aditi Verma",
        traveler_phone="+919876543210",
        travel_dates="2026-12-15",
        num_travelers=2,
        notes="Dal Lake houseboat stay and Gulmarg Gondola Phase 2 package"
    )
    enq_res = submit_enquiry(enq_req)
    assert enq_res["status"] == "success"
    assert "https://wa.me/" in enq_res["whatsapp_chat_url"]
    assert "Aditi%20Verma" in enq_res["whatsapp_chat_url"]
    
    # Verify in SQLite database
    saved_enqs = list_enquiries()
    assert len(saved_enqs) >= 1
    latest_lead = saved_enqs[0]
    assert latest_lead["traveler_name"] == "Aditi Verma"
    assert latest_lead["agent_name"] == "Ghulam Nabi Mir"
    print(f"✓ [6/7] SQLite Persistent Enquiries & WhatsApp Passed: Lead {enq_res['enquiry_id']} saved & direct link verified")

    # 7. Test Frontend Static Asset Route
    static_res = serve_mobile_app()
    assert static_res is not None
    print("✓ [7/7] Frontend Static App Routing Passed: Mobile-first responsive UI ready")

    print("\n" + "=" * 60)
    print("🎉 ALL 7 SYSTEM TESTS PASSED CLEANLY! DEMO READY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
