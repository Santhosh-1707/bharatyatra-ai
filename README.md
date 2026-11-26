# 🇮🇳 BharatYatra AI - India Tourism & Local Guides Platform

An AI-powered mobile web application (PWA) that empowers tourists to discover the best destinations across India and instantly connects them directly with verified, licensed local tour guides and operators with zero middleman commissions.

---

## 🌟 Key Features

1. **AI Destination Matcher & Itinerary Planner**:
   - Matches party size (*Family, Couple, Friends, Solo*), budget tier (*Budget, Moderate, Luxury*), duration, and travel style.
   - Dual-engine design: powered by **Google Gemini 2.5 Flash** with an automatic built-in intelligent fallback heuristic engine.
   - Generates tailored **Day-by-Day Itineraries** with regional culinary and cultural recommendations.

2. **Verified Local Tourist Agents Directory**:
   - 21+ certified local guides and operators across 11 Indian states (Himachal Pradesh, Kerala, Rajasthan, Uttar Pradesh, Meghalaya, Goa, Ladakh, Uttarakhand, Jammu & Kashmir, Karnataka, Andaman & Nicobar).
   - Credential badges: *Govt. Approved*, *Top Rated 2026*, *Archaeological Survey of India Certified*, *Himalayan Trek Specialist*, *PADI Master Scuba Trainer*.
   - Direct 1-tap **WhatsApp Deep-Linking** pre-filled with trip dates, passenger counts, and travel notes.
   - Transparent pricing in ₹ (INR) without intermediary commission cuts.

3. **Trip Cost Breakdown Estimator**:
   - Real-time expense breakdown for Accommodation, Private Cab & Transfers, Certified Guide Fees, and Regional Food & Passes based on party size and budget.

4. **1-Click WhatsApp Itinerary Sharing & Export**:
   - Copy a formatted WhatsApp-ready travel plan with daily highlights and local guide contact details in a single tap.
   - Print or save clean travel summary sheets.

5. **Live SQLite Lead & Enquiry Tracker**:
   - Captured enquiries are saved persistently in SQLite (`bharatyatra.db`) with timestamps, destination, traveler details, and assigned guide contacts.
   - Real-time leads drawer accessible from the top bar (`📋 Leads`).

6. **Offline PWA & Mobile Native Experience**:
   - Sleek responsive mobile mockup frame for laptop presentations.
   - Service worker offline caching for remote Himalayan and island locations with poor connectivity.
   - Installable as a native app on iOS & Android ("Add to Home Screen").

---

## 🌐 Live GitHub Pages & Web Deployment

BharatYatra AI includes a static offline fallback mode, allowing it to run directly on **GitHub Pages** without requiring an active Python server:

1. **GitHub Pages URL**: `https://<your-username>.github.io/bharatyatra-ai/`
2. **Setup**:
   - Go to your repository on GitHub: `Settings` > `Pages`.
   - Under **Build and deployment**:
     - **Option 1 (Automated GitHub Actions)**: Select Source `GitHub Actions` (the repository includes `.github/workflows/deploy-pages.yml`).
     - **Option 2 (Branch Deploy)**: Select Source `Deploy from a branch`, Branch `main`, Folder `/ (root)` or `/docs`, and click Save.
3. In GitHub Pages mode:
   - All 12 curated Indian destinations and 21 verified guides load instantly.
   - The client-side recommendation engine generates day-by-day itineraries and cost breakdowns.
   - 1-click WhatsApp deep links connect directly to local guides.
   - Booking leads are stored in browser local storage.

---

## 🚀 How to Run for Demo

### Step 1: Start the Server
```bash
python run_app.py
```

### Step 2: Open in Browser
- **On Laptop / Presentation Screen**: [http://localhost:8000](http://localhost:8000)
- **On Phone **: https://santhosh-1707.github.io/bharatyatra-ai/
- **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Live Leads JSON**: [http://localhost:8000/api/enquiries](http://localhost:8000/api/enquiries)

---

## 🧪 Running Automated Tests

Run the complete 7-step test suite:
```bash
python test_app.py
```
Or run the direct module test:
```bash
python test_direct.py
```

---

## 🛠️ Architecture & Tech Stack

- **Backend**: Python 3 FastAPI (Asynchronous, High-Performance)
- **Database**: SQLite3 with persistent enquiry logging (`backend/app/db.py`)
- **AI Service**: Google Gemini 2.5 Flash via `google-genai` SDK + Heuristic Fallback Engine
- **Frontend**: Mobile-First HTML5, Modern CSS Variables, Vanilla JS, Service Worker (`sw.js`), Web App Manifest
