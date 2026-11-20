from typing import List, Optional
from pydantic import BaseModel, Field

class DestinationFilter(BaseModel):
    category: Optional[str] = "all"  # mountains, beaches, heritage, spiritual, northeast, wildlife
    budget: Optional[str] = None     # budget, moderate, luxury
    season: Optional[str] = None     # winter, summer, monsoon, autumn
    duration_days: Optional[int] = None
    travelers_type: Optional[str] = None # solo, couple, family, friends

class AIRecommendationRequest(BaseModel):
    prompt: Optional[str] = None
    vibe: Optional[str] = "any"       # adventure, relaxation, cultural, spiritual, romantic, nature
    budget: Optional[str] = "moderate" # budget, moderate, luxury
    duration_days: int = 4
    companions: str = "couple"        # solo, couple, family, friends
    month_or_season: Optional[str] = "current"
    preferred_region: Optional[str] = "all" # north, south, east, west, northeast, central

class TouristAgent(BaseModel):
    id: str
    name: str
    agency_name: str
    destination_id: str
    destination_name: str
    state: str
    phone: str
    whatsapp: str
    rating: float
    review_count: int
    badge: str # "Govt. Approved", "Top Rated 2026", "Verified Local Expert", "Trek Specialist"
    languages: List[str]
    specialties: List[str]
    price_starts_from: int # in INR
    price_unit: str # per day or per package
    bio: str
    experience_years: int

class Destination(BaseModel):
    id: str
    name: str
    state: str
    region: str # North, South, East, West, Northeast, Central
    tagline: str
    category: str # mountains, beaches, heritage, spiritual, northeast, wildlife
    best_time: str
    ideal_duration: str
    estimated_budget: str
    highlights: List[str]
    overview: str
    image_url: str
    weather_summary: str
    agents_count: int = 0

class EnquiryRequest(BaseModel):
    destination_id: str
    agent_id: str
    traveler_name: str
    traveler_phone: str
    traveler_email: Optional[str] = None
    travel_dates: Optional[str] = None
    num_travelers: int = 2
    notes: Optional[str] = None
