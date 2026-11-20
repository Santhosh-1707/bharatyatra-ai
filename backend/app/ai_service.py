import os
import json
from typing import Dict, Any, List
from .models import AIRecommendationRequest, Destination, TouristAgent
from .data import DESTINATIONS, AGENTS

def _load_env_file():
    """Auto-load variables from .env in project root if present."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_file = os.path.join(root_dir, ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

def get_agents_for_destination(destination_id: str) -> List[TouristAgent]:
    return [agent for agent in AGENTS if agent.destination_id == destination_id]

def get_destination_by_id(dest_id: str) -> Destination:
    for d in DESTINATIONS:
        if d.id == dest_id:
            return d
    return DESTINATIONS[0]

def build_smart_itinerary(dest: Destination, duration_days: int, companions: str) -> List[Dict[str, str]]:
    """Builds a contextual day-by-day travel plan based on destination and party size."""
    itinerary = []
    highlights = dest.highlights

    for day in range(1, duration_days + 1):
        if day == 1:
            title = f"Arrival in {dest.name.split('&')[0].strip()} & Scenic Welcome"
            activity = f"Arrive and check in to your stay. Spend a relaxed afternoon exploring the local town center, taking in the atmosphere, and sampling authentic regional delicacies for {companions} travelers."
            tips = "Rest well to acclimatize and settle in."
        elif day == duration_days:
            title = "Souvenir Shopping & Farewell Departure"
            activity = f"Morning visit to local markets for traditional handicrafts and spices. Enjoy a scenic farewell breakfast before heading for your return journey."
            tips = "Coordinate with your local tourist agent for smooth departure transit."
        else:
            hl_idx = (day - 2) % len(highlights)
            hl = highlights[hl_idx]
            title = f"Day {day}: Experience {hl}"
            activity = f"Full day guided exploration: Head out early to experience {hl}. Engage with local culture and capture breathtaking memories suited for {companions}."
            tips = "Book through your verified local agent to avoid peak crowd lines."

        itinerary.append({
            "day": day,
            "title": title,
            "activity": activity,
            "tips": tips
        })
    return itinerary

def generate_local_recommendations(req: AIRecommendationRequest) -> Dict[str, Any]:
    """Fallback intelligent recommendation engine when Gemini API key is not configured."""
    scored_destinations = []

    for d in DESTINATIONS:
        score = 10
        # Category/vibe match
        if req.vibe and req.vibe.lower() != "any":
            if req.vibe.lower() in d.category or d.category in req.vibe.lower():
                score += 15
            elif req.vibe.lower() in ["adventure", "trekking"] and d.category == "mountains":
                score += 15
            elif req.vibe.lower() in ["relaxation", "peace"] and d.category in ["nature", "beaches"]:
                score += 12
            elif req.vibe.lower() in ["culture", "history"] and d.category in ["heritage", "spiritual"]:
                score += 15

        # Companions match
        if req.companions == "couple" and d.id in ["munnar", "manali", "jaipur_udaipur", "goa", "kashmir", "andaman"]:
            score += 10
        elif req.companions == "family" and d.id in ["jaipur_udaipur", "munnar", "rishikesh", "varanasi", "kashmir", "andaman", "jaisalmer"]:
            score += 10
        elif req.companions == "friends" and d.id in ["manali", "goa", "rishikesh", "ladakh", "meghalaya", "hampi", "andaman", "jaisalmer"]:
            score += 10
        elif req.companions == "solo" and d.id in ["varanasi", "rishikesh", "meghalaya", "ladakh", "hampi"]:
            score += 10

        # Region match
        if req.preferred_region and req.preferred_region.lower() != "all":
            if req.preferred_region.lower() == d.region.lower():
                score += 20

        # Custom prompt keywords
        if req.prompt:
            p_lower = req.prompt.lower()
            if any(k in p_lower for k in ["kashmir", "shikara", "gulmarg", "pahalgam"]) and d.id == "kashmir":
                score += 35
            if any(k in p_lower for k in ["andaman", "havelock", "scuba", "island", "coral", "radhanagar"]) and d.id == "andaman":
                score += 35
            if any(k in p_lower for k in ["hampi", "gokarna", "ruin", "boulder", "om beach"]) and d.id == "hampi":
                score += 35
            if any(k in p_lower for k in ["jaisalmer", "thar", "desert", "camel", "dunes", "golden fort"]) and d.id == "jaisalmer":
                score += 35
            if any(k in p_lower for k in ["snow", "cold", "mountain", "himalaya"]) and d.category == "mountains":
                score += 20
            if any(k in p_lower for k in ["beach", "sea", "ocean", "coastal", "islands"]) and d.category == "beaches":
                score += 20
            if any(k in p_lower for k in ["temple", "spiritual", "peace", "ganga"]) and d.category == "spiritual":
                score += 20
            if any(k in p_lower for k in ["waterfall", "nature", "cloud", "green"]) and d.category in ["nature", "northeast"]:
                score += 20
            if any(k in p_lower for k in ["palace", "fort", "king", "rajasthan"]) and d.category == "heritage":
                score += 20

        scored_destinations.append((score, d))

    # Sort descending by score
    scored_destinations.sort(key=lambda x: x[0], reverse=True)
    top_destinations = [d for _, d in scored_destinations[:3]]

    primary_dest = top_destinations[0]
    agents = get_agents_for_destination(primary_dest.id)
    itinerary = build_smart_itinerary(primary_dest, req.duration_days, req.companions)

    ai_narrative = (
        f"Based on your preference for a {req.vibe} trip traveling as {req.companions} with a {req.budget} budget, "
        f"**{primary_dest.name}** in {primary_dest.state} is your ideal destination in India! "
        f"With highlights like {', '.join(primary_dest.highlights[:3])}, this place guarantees an authentic and unforgettable experience."
    )

    return {
        "engine": "Dynamic Expert Travel Engine",
        "primary_destination": primary_dest.model_dump(),
        "alternative_destinations": [d.model_dump() for d in top_destinations[1:]],
        "ai_narrative": ai_narrative,
        "suggested_itinerary": itinerary,
        "recommended_agents": [a.model_dump() for a in agents],
        "travel_tips": [
            f"Best season for {primary_dest.name}: {primary_dest.best_time}.",
            f"Expected weather: {primary_dest.weather_summary}.",
            "Book verified local agents directly via WhatsApp for guaranteed fair local rates."
        ]
    }

def generate_gemini_recommendations(req: AIRecommendationRequest, api_key: str) -> Dict[str, Any]:
    """Uses Google Gemini 2.5 Flash to generate personalized Indian travel recommendations."""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        dest_context = [
            {"id": d.id, "name": d.name, "state": d.state, "category": d.category, "highlights": d.highlights, "best_time": d.best_time}
            for d in DESTINATIONS
        ]

        prompt_text = f"""
You are BharatYatra AI, the premier expert on travel in India.
Analyze this user request:
- User Prompt: "{req.prompt or 'Find me the best destination in India'}"
- Travel Vibe: {req.vibe}
- Budget Level: {req.budget}
- Duration: {req.duration_days} days
- Companions: {req.companions}
- Preferred Region: {req.preferred_region}

Available curated destinations catalog:
{json.dumps(dest_context, indent=2)}

Pick the SINGLE BEST matching destination from the catalog ('primary_destination_id', must match an existing destination id from the catalog like 'manali', 'munnar', 'jaipur_udaipur', 'varanasi', 'meghalaya', 'goa', 'ladakh', 'rishikesh', 'kashmir', 'hampi', 'andaman', 'jaisalmer').
Also choose 2 runner-up destination IDs ('alternative_destination_ids').
Write a compelling personal travel narrative explaining why this destination fits their specific party and vibe.
Generate a structured day-by-day itinerary ({req.duration_days} days) with day number, title, rich activities, and local culinary advice.
Provide 3 practical traveler tips (weather, local customs, transport).

Return ONLY valid JSON with this exact schema:
{{
  "primary_destination_id": "string",
  "alternative_destination_ids": ["string", "string"],
  "ai_narrative": "string",
  "suggested_itinerary": [
     {{"day": 1, "title": "string", "activity": "string", "tips": "string"}}
  ],
  "travel_tips": ["string", "string", "string"]
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            )
        )

        res_json = json.loads(response.text)
        primary_id = res_json.get("primary_destination_id", "munnar")
        primary_dest = get_destination_by_id(primary_id)
        alt_ids = res_json.get("alternative_destination_ids", [])
        alt_dests = [get_destination_by_id(aid) for aid in alt_ids if aid != primary_id]

        agents = get_agents_for_destination(primary_dest.id)

        return {
            "engine": "Google Gemini 2.5 Flash",
            "primary_destination": primary_dest.model_dump(),
            "alternative_destinations": [d.model_dump() for d in alt_dests],
            "ai_narrative": res_json.get("ai_narrative", ""),
            "suggested_itinerary": res_json.get("suggested_itinerary", []),
            "recommended_agents": [a.model_dump() for a in agents],
            "travel_tips": res_json.get("travel_tips", [])
        }

    except Exception as e:
        # Graceful fallback to smart local engine if API call fails or key is invalid
        fallback = generate_local_recommendations(req)
        fallback["engine"] += f" (Gemini Fallback: {str(e)})"
        return fallback

def get_travel_recommendation(req: AIRecommendationRequest, custom_api_key: str = None) -> Dict[str, Any]:
    api_key = custom_api_key or os.environ.get("GEMINI_API_KEY")
    if api_key:
        return generate_gemini_recommendations(req, api_key)
    return generate_local_recommendations(req)
