// BharatYatra AI Mobile App Logic

const API_BASE = window.location.origin;
let currentCustomKey = localStorage.getItem("bharatyatra_gemini_key") || "";
let allDestinations = [];
let allAgents = [];
let lastRecommendationData = null;

// Register PWA Service Worker for offline capability
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./service-worker.js').catch(() => {
      return navigator.serviceWorker.register('/service-worker.js');
    }).then((reg) => {
      if (reg) console.log('ServiceWorker registered with scope:', reg.scope);
    }).catch((err) => {
      console.log('ServiceWorker registration skipped:', err);
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initClock();
  initNavigation();
  initPlannerForm();
  initExploreTab();
  initAgentsTab();
  initSettings();
  initModal();
  initLeadsTracker();
  initItineraryActions();
  refreshPlatformStats();

  // Trigger initial default recommendation to delight user on first launch
  triggerRecommendation();
});

// Toast notification helper
function showToast(message) {
  const toast = document.getElementById("toast-notification");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

// Real-time simulated status bar clock
function initClock() {
  const timeEl = document.getElementById("status-time");
  function updateTime() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    hours = hours < 10 ? "0" + hours : hours;
    minutes = minutes < 10 ? "0" + minutes : minutes;
    if (timeEl) timeEl.textContent = `${hours}:${minutes}`;
  }
  updateTime();
  setInterval(updateTime, 10000);
}

// Fetch live platform stats for header & trust bar (with static offline fallback)
async function refreshPlatformStats() {
  const destEl = document.getElementById("stat-dest-count");
  const agentEl = document.getElementById("stat-agent-count");
  const leadsCount = document.getElementById("header-leads-count");

  const localLeads = JSON.parse(localStorage.getItem("bharatyatra_leads") || "[]");
  const staticDestCount = (window.STATIC_DESTINATIONS && window.STATIC_DESTINATIONS.length) || 12;
  const staticAgentCount = (window.STATIC_AGENTS && window.STATIC_AGENTS.length) || 21;

  if (destEl) destEl.textContent = staticDestCount;
  if (agentEl) agentEl.textContent = `${staticAgentCount}+`;
  if (leadsCount) leadsCount.textContent = localLeads.length;

  try {
    const res = await fetch(`${API_BASE}/api/stats`);
    if (!res.ok) return;
    const stats = await res.json();
    if (destEl) destEl.textContent = stats.total_destinations;
    if (agentEl) agentEl.textContent = `${stats.total_verified_agents}+`;
    if (leadsCount) leadsCount.textContent = (stats.enquiries_captured || 0) + localLeads.length;
  } catch (err) {
    // Gracefully use static numbers already populated
  }
}

// Navigation between bottom bar tabs
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const tabViews = document.querySelectorAll(".tab-view");

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetId = item.getAttribute("data-target");
      
      navItems.forEach(n => n.classList.remove("active"));
      tabViews.forEach(v => v.classList.remove("active"));

      item.classList.add("active");
      const targetView = document.getElementById(targetId);
      if (targetView) targetView.classList.add("active");

      // Scroll to top on tab change
      document.getElementById("app-body").scrollTop = 0;
    });
  });
}

// Settings & Optional Gemini API Key
function initSettings() {
  const toggleBtn = document.getElementById("api-key-toggle-btn");
  const banner = document.getElementById("api-key-banner");
  const keyInput = document.getElementById("user-gemini-key");
  const saveBtn = document.getElementById("save-key-btn");

  if (currentCustomKey && keyInput) {
    keyInput.value = currentCustomKey;
  }

  toggleBtn.addEventListener("click", () => {
    banner.style.display = banner.style.display === "none" ? "block" : "none";
  });

  saveBtn.addEventListener("click", () => {
    const val = keyInput.value.trim();
    currentCustomKey = val;
    localStorage.setItem("bharatyatra_gemini_key", val);
    banner.style.display = "none";
    showToast("Gemini API Key preference saved!");
  });
}

// Leads & Bookings Tracker Drawer (SQLite backed)
function initLeadsTracker() {
  const leadsBtn = document.getElementById("leads-toggle-btn");
  const leadsModal = document.getElementById("leads-modal");
  const closeLeadsBtn = document.getElementById("close-leads-btn");

  if (leadsBtn) {
    leadsBtn.addEventListener("click", openLeadsModal);
  }

  if (closeLeadsBtn) {
    closeLeadsBtn.addEventListener("click", () => {
      leadsModal.style.display = "none";
    });
  }

  if (leadsModal) {
    leadsModal.addEventListener("click", (e) => {
      if (e.target === leadsModal) leadsModal.style.display = "none";
    });
  }
}

async function openLeadsModal() {
  const modal = document.getElementById("leads-modal");
  const container = document.getElementById("leads-list-container");
  modal.style.display = "flex";
  container.innerHTML = `<p style="padding:15px; color:#94A3B8; font-size:12px; text-align:center;">Loading live leads...</p>`;

  let backendLeads = [];
  try {
    const res = await fetch(`${API_BASE}/api/enquiries`);
    if (res.ok) {
      backendLeads = await res.json();
    }
  } catch (err) {
    // Offline or GitHub Pages
  }

  const localLeads = JSON.parse(localStorage.getItem("bharatyatra_leads") || "[]");
  const combinedLeads = [...localLeads, ...backendLeads];
  
  // Update count in header
  const leadsCount = document.getElementById("header-leads-count");
  if (leadsCount) leadsCount.textContent = combinedLeads.length;

  if (!combinedLeads || combinedLeads.length === 0) {
    container.innerHTML = `
      <div style="text-align:center; padding:30px 10px; color:#64748B;">
        <div style="font-size:32px; margin-bottom:8px;">📭</div>
        <strong style="font-size:14px; color:#0F172A;">No Leads Captured Yet</strong>
        <p style="font-size:12px; margin-top:4px;">Enquire with any verified guide on the platform to log a lead in real-time!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = combinedLeads.map(l => `
    <div class="lead-card">
      <div class="lead-top">
        <span class="lead-id">⚡ ${l.id}</span>
        <span class="lead-time">${l.created_at || 'Just now'}</span>
      </div>
      <div class="lead-dest">📍 ${l.destination_name}</div>
      <div class="lead-agent">🤝 Assigned: ${l.agent_name} (${l.agency_name})</div>
      <div class="lead-traveler">
        👤 <strong>${l.traveler_name}</strong> • ${l.num_travelers} Travelers<br>
        📞 ${l.traveler_phone} • 🗓️ ${l.travel_dates || 'Flexible'}<br>
        <em style="color:#0284C7;">"${l.notes || 'Looking for tour quote'}"</em>
      </div>
    </div>
  `).join("");
}

// 1-Click WhatsApp Copy & Print Plan
function initItineraryActions() {
  const copyBtn = document.getElementById("btn-copy-itinerary");
  const printBtn = document.getElementById("btn-print-itinerary");

  if (copyBtn) {
    copyBtn.addEventListener("click", copyItineraryToWhatsApp);
  }

  if (printBtn) {
    printBtn.addEventListener("click", () => {
      window.print();
    });
  }
}

function copyItineraryToWhatsApp() {
  if (!lastRecommendationData) {
    showToast("Please generate a travel plan first!");
    return;
  }

  const primary = lastRecommendationData.primary_destination;
  const agent = (lastRecommendationData.recommended_agents && lastRecommendationData.recommended_agents[0]) || null;
  const duration = document.getElementById("ai-duration").value || 4;
  const companions = document.getElementById("ai-companions").value || "couple";

  let msg = `🇮🇳 *BharatYatra AI Trip Plan: ${primary.name}*\n`;
  msg += `📍 Region: ${primary.state} • ${primary.region} India\n`;
  msg += `🗓️ Duration: ${duration} Days | Style: ${companions.toUpperCase()}\n`;
  msg += `✨ Best Visiting Months: ${primary.best_time}\n\n`;
  msg += `🗺️ *DAY-BY-DAY ITINERARY:*\n`;

  (lastRecommendationData.suggested_itinerary || []).forEach(item => {
    msg += `\n*Day ${item.day}: ${item.title}*\n${item.activity}\n💡 Tip: ${item.tips}\n`;
  });

  if (agent) {
    msg += `\n🤝 *VERIFIED LOCAL GUIDE:*\n`;
    msg += `• Name: ${agent.name} (${agent.agency_name})\n`;
    msg += `• License/Badge: ${agent.badge} (Rating: ★${agent.rating})\n`;
    msg += `• Direct WhatsApp: https://wa.me/${agent.whatsapp}\n`;
  }

  msg += `\nGenerated with ❤️ on BharatYatra AI (Zero Commission Local Travel)`;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(msg).then(() => {
      showToast("📋 Plan copied! Ready to paste into WhatsApp.");
    }).catch(() => {
      showToast("📋 Plan ready for WhatsApp!");
    });
  } else {
    showToast("📋 Plan formatted!");
  }
}

// AI Trip Planner & Form
function initPlannerForm() {
  const durationSlider = document.getElementById("ai-duration");
  const durationVal = document.getElementById("duration-val");
  const findBtn = document.getElementById("find-destinations-btn");
  const chips = document.querySelectorAll(".quick-chips .chip");

  durationSlider.addEventListener("input", (e) => {
    durationVal.textContent = `${e.target.value} Days`;
    if (lastRecommendationData) {
      renderCostBreakdown(lastRecommendationData);
    }
  });

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");

      const vibe = chip.getAttribute("data-vibe");
      const comp = chip.getAttribute("data-comp");
      const budget = chip.getAttribute("data-budget");
      const days = chip.getAttribute("data-days");

      if (vibe) document.getElementById("ai-vibe").value = vibe;
      if (comp) document.getElementById("ai-companions").value = comp;
      if (budget) document.getElementById("ai-budget").value = budget;
      if (days) {
        document.getElementById("ai-duration").value = days;
        durationVal.textContent = `${days} Days`;
      }

      triggerRecommendation();
    });
  });

  findBtn.addEventListener("click", () => {
    triggerRecommendation();
  });
}

async function triggerRecommendation() {
  const resultsArea = document.getElementById("ai-results-area");
  const findBtn = document.getElementById("find-destinations-btn");

  const prompt = document.getElementById("ai-custom-prompt").value.trim();
  const vibe = document.getElementById("ai-vibe").value;
  const companions = document.getElementById("ai-companions").value;
  const budget = document.getElementById("ai-budget").value;
  const duration_days = parseInt(document.getElementById("ai-duration").value) || 4;

  findBtn.innerHTML = `<span>⏳</span> AI is matching Indian destinations...`;
  findBtn.disabled = true;

  let data = null;
  try {
    const headers = { "Content-Type": "application/json" };
    if (currentCustomKey) {
      headers["X-Gemini-API-Key"] = currentCustomKey;
    }

    const res = await fetch(`${API_BASE}/api/recommend`, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        prompt: prompt || null,
        vibe: vibe,
        companions: companions,
        budget: budget,
        duration_days: duration_days,
        preferred_region: "all"
      })
    });

    if (res.ok) {
      data = await res.json();
    }
  } catch (err) {
    // Backend offline or on GitHub Pages
  }

  // Client-side fallback for GitHub Pages or offline usage
  if (!data) {
    data = generateClientSideRecommendation({ prompt, vibe, companions, budget, duration_days });
  }

  if (data) {
    lastRecommendationData = data;
    renderAIResults(data);
    renderCostBreakdown(data);
    resultsArea.style.display = "block";
    resultsArea.scrollIntoView({ behavior: "smooth" });
  }

  findBtn.innerHTML = `<span class="btn-icon">⚡</span> Suggest Best Place & Local Agents`;
  findBtn.disabled = false;
}

// Client-side heuristic recommendation generator for GitHub Pages & Offline
function generateClientSideRecommendation({ prompt, vibe, companions, budget, duration_days }) {
  const destinations = (allDestinations && allDestinations.length > 0) ? allDestinations : (window.STATIC_DESTINATIONS || []);
  const agents = (allAgents && allAgents.length > 0) ? allAgents : (window.STATIC_AGENTS || []);

  if (!destinations || destinations.length === 0) return null;

  const scored = destinations.map(d => {
    let score = 10;
    const cat = (d.category || "").toLowerCase();
    const v = (vibe || "").toLowerCase();

    if (v && v !== "any") {
      if (v.includes(cat) || cat.includes(v)) score += 15;
      else if (["adventure", "trekking"].includes(v) && cat === "mountains") score += 15;
      else if (["relaxation", "peace"].includes(v) && ["nature", "beaches"].includes(cat)) score += 12;
      else if (["culture", "history"].includes(v) && ["heritage", "spiritual"].includes(cat)) score += 15;
    }

    if (companions === "couple" && ["munnar", "manali", "jaipur_udaipur", "goa", "kashmir", "andaman"].includes(d.id)) score += 10;
    else if (companions === "family" && ["jaipur_udaipur", "munnar", "rishikesh", "varanasi", "kashmir", "andaman", "jaisalmer"].includes(d.id)) score += 10;
    else if (companions === "friends" && ["manali", "goa", "rishikesh", "ladakh", "meghalaya", "hampi", "andaman", "jaisalmer"].includes(d.id)) score += 10;
    else if (companions === "solo" && ["varanasi", "rishikesh", "meghalaya", "ladakh", "hampi"].includes(d.id)) score += 10;

    if (prompt) {
      const p = prompt.toLowerCase();
      if (p.includes(d.id) || p.includes(d.name.toLowerCase()) || p.includes(d.state.toLowerCase())) score += 30;
      if (d.highlights && d.highlights.some(h => p.includes(h.toLowerCase()))) score += 20;
    }

    return { destination: d, score: score };
  });

  scored.sort((a, b) => b.score - a.score);
  const primary = scored[0].destination;
  const alternatives = scored.slice(1, 4).map(s => s.destination);

  const itinerary = [];
  const highlights = primary.highlights || ["Local Sightseeing", "Cultural Experience", "Scenic Sunset"];
  for (let day = 1; day <= duration_days; day++) {
    let title, activity, tips;
    if (day === 1) {
      title = `Arrival in ${primary.name.split('&')[0].trim()} & Scenic Welcome`;
      activity = `Arrive and check in to your stay. Spend a relaxed afternoon exploring the local town center, taking in the atmosphere, and sampling authentic regional delicacies for ${companions} travelers.`;
      tips = "Rest well to acclimatize and settle in.";
    } else if (day === duration_days) {
      title = "Souvenir Shopping & Farewell Departure";
      activity = `Morning visit to local markets for traditional handicrafts and spices. Enjoy a scenic farewell breakfast before heading for your return journey.`;
      tips = "Coordinate with your local tourist agent for smooth departure transit.";
    } else {
      const hl = highlights[(day - 2) % highlights.length];
      title = `Day ${day}: Experience ${hl}`;
      activity = `Full day guided exploration: Head out early to experience ${hl}. Engage with local culture and capture breathtaking memories suited for ${companions}.`;
      tips = "Book through your verified local agent to avoid peak crowd lines.";
    }
    itinerary.push({ day, title, activity, tips });
  }

  const matchedAgents = agents.filter(a => a.destination_id === primary.id);

  return {
    primary_destination: primary,
    suggested_itinerary: itinerary,
    recommended_agents: matchedAgents,
    alternative_destinations: alternatives,
    ai_narrative: `Based on your choice for a ${duration_days}-day trip with ${companions} seeking ${vibe} vibes, ${primary.name} in ${primary.state} offers the optimal blend of activities, verified certified guides, and authentic Indian hospitality.`,
    source: "BharatYatra Static Engine (GitHub Pages Ready)"
  };
}

function renderCostBreakdown(data) {
  const grid = document.getElementById("cost-items-grid");
  const totalBadge = document.getElementById("cost-total-badge");
  if (!grid || !totalBadge) return;

  const budget = document.getElementById("ai-budget").value || "moderate";
  const duration = parseInt(document.getElementById("ai-duration").value) || 4;
  const companions = document.getElementById("ai-companions").value || "couple";

  let numPeople = 2;
  if (companions === "solo") numPeople = 1;
  else if (companions === "couple") numPeople = 2;
  else if (companions === "family") numPeople = 4;
  else if (companions === "friends") numPeople = 4;

  let stayRatePerNight = 2500;
  let cabRatePerDay = 2400;
  let guideRatePerDay = 1600;
  let mealRatePerPerson = 750;

  if (budget === "budget") {
    stayRatePerNight = 1400;
    cabRatePerDay = 1600;
    guideRatePerDay = 1200;
    mealRatePerPerson = 450;
  } else if (budget === "luxury") {
    stayRatePerNight = 6500;
    cabRatePerDay = 4000;
    guideRatePerDay = 2800;
    mealRatePerPerson = 1600;
  }

  const numRooms = Math.max(1, Math.ceil(numPeople / 2));
  const nights = Math.max(1, duration - 1);
  const stayCost = stayRatePerNight * nights * numRooms;
  const cabCost = cabRatePerDay * duration;
  const guideCost = guideRatePerDay * Math.max(1, duration - 1);
  const mealsCost = mealRatePerPerson * numPeople * duration;
  const totalCost = stayCost + cabCost + guideCost + mealsCost;

  totalBadge.textContent = `₹${totalCost.toLocaleString('en-IN')} Total (${numPeople} Travelers)`;

  grid.innerHTML = `
    <div class="cost-item-pill">
      <span class="cost-label">🏨 Stay (${nights} nights, ${numRooms} room)</span>
      <span class="cost-val">₹${stayCost.toLocaleString('en-IN')}</span>
    </div>
    <div class="cost-item-pill">
      <span class="cost-label">🚗 Private Cab & Sightseeing</span>
      <span class="cost-val">₹${cabCost.toLocaleString('en-IN')}</span>
    </div>
    <div class="cost-item-pill">
      <span class="cost-label">🤝 Certified Local Guide</span>
      <span class="cost-val">₹${guideCost.toLocaleString('en-IN')}</span>
    </div>
    <div class="cost-item-pill">
      <span class="cost-label">🍲 Regional Meals & Passes</span>
      <span class="cost-val">₹${mealsCost.toLocaleString('en-IN')}</span>
    </div>
  `;
}

function renderAIResults(data) {
  const enginePill = document.getElementById("ai-engine-pill");
  const narrativeText = document.getElementById("ai-narrative-text");
  const destImg = document.getElementById("primary-dest-img");
  const destName = document.getElementById("primary-dest-name");
  const destRegion = document.getElementById("primary-dest-region");
  const destTagline = document.getElementById("primary-dest-tagline");
  const destSeason = document.getElementById("primary-dest-season");
  const destBudget = document.getElementById("primary-dest-budget");
  const highlightsContainer = document.getElementById("primary-dest-highlights");
  const itineraryList = document.getElementById("itinerary-list");
  const agentsList = document.getElementById("recommended-agents-list");
  const agentCountBadge = document.getElementById("agent-count-badge");
  const altsGrid = document.getElementById("alternatives-grid");

  const primary = data.primary_destination;

  // Engine & narrative
  enginePill.textContent = `✨ ${data.engine}`;
  narrativeText.innerHTML = data.ai_narrative.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Primary Destination Card
  destImg.src = primary.image_url;
  destName.textContent = primary.name;
  destRegion.textContent = `${primary.state} • ${primary.region} India`;
  destTagline.textContent = primary.tagline;
  destSeason.textContent = primary.best_time;
  destBudget.textContent = primary.estimated_budget;

  // Highlights
  highlightsContainer.innerHTML = primary.highlights
    .map(h => `<span class="highlight-pill">${h}</span>`)
    .join("");

  // Itinerary
  itineraryList.innerHTML = data.suggested_itinerary
    .map(item => `
      <div class="day-box">
        <div class="day-num">DAY ${item.day}</div>
        <div class="day-title">${item.title}</div>
        <div class="day-desc">${item.activity}</div>
        <div class="day-tip">💡 Tip: ${item.tips}</div>
      </div>
    `).join("");

  // Recommended Agents
  const agents = data.recommended_agents || [];
  agentCountBadge.textContent = `${agents.length} Verified in ${primary.name.split('&')[0].trim()}`;
  
  if (agents.length === 0) {
    agentsList.innerHTML = `<p style="font-size:12px; color:#64748B;">No local agents registered yet for this spot. More being verified daily!</p>`;
  } else {
    agentsList.innerHTML = agents.map(agent => renderAgentCardHTML(agent, primary.id)).join("");
  }

  // Alternatives
  const alts = data.alternative_destinations || [];
  if (alts.length > 0) {
    altsGrid.innerHTML = alts.map(alt => `
      <div class="dest-item-card" onclick="selectAlternativeDestination('${alt.id}')">
        <img src="${alt.image_url}" alt="${alt.name}">
        <div class="dest-item-info">
          <div class="dest-item-title">${alt.name}</div>
          <div class="dest-item-meta">
            <span>📍 ${alt.state}</span>
            <span>⭐ ${alt.best_time.split('(')[0].trim()}</span>
          </div>
        </div>
      </div>
    `).join("");
    document.getElementById("alternatives-wrapper").style.display = "block";
  } else {
    document.getElementById("alternatives-wrapper").style.display = "none";
  }
}

function renderAgentCardHTML(agent, destinationId) {
  return `
    <div class="agent-card">
      <div class="agent-top-row">
        <div>
          <div class="agent-name">${agent.name}</div>
          <div class="agent-agency">${agent.agency_name}</div>
        </div>
        <span class="agent-badge-pill">🛡️ ${agent.badge}</span>
      </div>

      <div class="agent-rating-row">
        <span class="star-rating">★ ${agent.rating.toFixed(1)}</span>
        <span style="color:var(--text-muted);">(${agent.review_count} reviews)</span>
        <span>•</span>
        <span style="color:#0284C7; font-weight:600;">${agent.experience_years} yrs exp</span>
      </div>

      <div class="agent-specs">
        ${agent.specialties.map(s => `<span class="spec-chip">${s}</span>`).join("")}
      </div>

      <div class="agent-pricing-row">
        <div>
          <div class="price-text">₹${agent.price_starts_from.toLocaleString('en-IN')}</div>
          <div class="price-unit">${agent.price_unit}</div>
        </div>
        <div class="agent-actions">
          <button class="btn-contact" onclick="openEnquiryModal('${agent.id}', '${destinationId}', '${agent.name}', '${agent.agency_name}', '${agent.badge}')">
            Enquire
          </button>
          <a class="btn-whatsapp-sm" href="https://wa.me/${agent.whatsapp}?text=${encodeURIComponent(`Namaste ${agent.name}! I found your profile on BharatYatra AI. Looking to plan a tour.`)}" target="_blank">
            💬 WhatsApp
          </a>
        </div>
      </div>
    </div>
  `;
}

// Explore Tab
async function initExploreTab() {
  const grid = document.getElementById("all-destinations-grid");
  const pills = document.querySelectorAll(".filter-scroll .filter-pill");

  try {
    const res = await fetch(`${API_BASE}/api/destinations`);
    if (res.ok) {
      allDestinations = await res.json();
    } else {
      allDestinations = window.STATIC_DESTINATIONS || [];
    }
  } catch (err) {
    allDestinations = window.STATIC_DESTINATIONS || [];
  }
  renderDestinationsGrid(allDestinations);

  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const cat = pill.getAttribute("data-cat");
      if (cat === "all") {
        renderDestinationsGrid(allDestinations);
      } else {
        const filtered = allDestinations.filter(d => d.category.toLowerCase() === cat.toLowerCase());
        renderDestinationsGrid(filtered);
      }
    });
  });
}

function renderDestinationsGrid(destinations) {
  const grid = document.getElementById("all-destinations-grid");
  grid.innerHTML = destinations.map(d => `
    <div class="dest-item-card" onclick="showDestinationDetail('${d.id}')">
      <img src="${d.image_url}" alt="${d.name}">
      <div class="dest-item-info">
        <div style="font-size:10px; font-weight:700; color:var(--primary); text-transform:uppercase;">${d.state}</div>
        <div class="dest-item-title">${d.name}</div>
        <p style="font-size:12px; color:#475569; margin-bottom:8px;">${d.tagline}</p>
        <div class="dest-item-meta">
          <span>🗓️ ${d.ideal_duration}</span>
          <span style="color:#166534; font-weight:700;">🤝 ${d.agents_count} Verified Guides</span>
        </div>
      </div>
    </div>
  `).join("");
}

// When an alternative destination is clicked from the AI tab
window.selectAlternativeDestination = function(destId) {
  const dest = allDestinations.find(d => d.id === destId);
  if (!dest) return;
  document.getElementById("ai-custom-prompt").value = `Trip to ${dest.name} in ${dest.state}`;
  triggerRecommendation();
};

window.showDestinationDetail = function(destId) {
  const dest = allDestinations.find(d => d.id === destId);
  if (!dest) return;
  const plannerTabBtn = document.querySelector('.nav-item[data-target="tab-planner"]');
  if (plannerTabBtn) plannerTabBtn.click();
  document.getElementById("ai-custom-prompt").value = `Complete plan for ${dest.name}`;
  triggerRecommendation();
};

// Agents Tab
async function initAgentsTab() {
  const list = document.getElementById("all-agents-list");
  const searchInput = document.getElementById("agent-search-input");

  try {
    const res = await fetch(`${API_BASE}/api/agents`);
    if (res.ok) {
      allAgents = await res.json();
    } else {
      allAgents = window.STATIC_AGENTS || [];
    }
  } catch (err) {
    allAgents = window.STATIC_AGENTS || [];
  }
  renderAllAgents(allAgents);

  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
      renderAllAgents(allAgents);
      return;
    }
    const filtered = allAgents.filter(a => 
      a.name.toLowerCase().includes(query) ||
      a.destination_name.toLowerCase().includes(query) ||
      a.state.toLowerCase().includes(query) ||
      a.specialties.some(s => s.toLowerCase().includes(query)) ||
      a.badge.toLowerCase().includes(query)
    );
    renderAllAgents(filtered);
  });
}

function renderAllAgents(agents) {
  const list = document.getElementById("all-agents-list");
  if (agents.length === 0) {
    list.innerHTML = `<p style="text-align:center; padding:20px; font-size:13px; color:var(--text-muted);">No verified agents found matching your query.</p>`;
    return;
  }
  list.innerHTML = agents.map(a => renderAgentCardHTML(a, a.destination_id)).join("");
}

// Modal handling
function initModal() {
  const modal = document.getElementById("enquiry-modal");
  const closeBtn = document.getElementById("close-modal-btn");
  const form = document.getElementById("enquiry-form");

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const agentId = document.getElementById("enq-agent-id").value;
    const destId = document.getElementById("enq-dest-id").value;
    const name = document.getElementById("enq-name").value;
    const phone = document.getElementById("enq-phone").value;
    const date = document.getElementById("enq-date").value;
    const travelers = parseInt(document.getElementById("enq-travelers").value) || 2;
    const notes = document.getElementById("enq-notes").value;

    const agentList = (allAgents && allAgents.length > 0) ? allAgents : (window.STATIC_AGENTS || []);
    const destList = (allDestinations && allDestinations.length > 0) ? allDestinations : (window.STATIC_DESTINATIONS || []);
    const agent = agentList.find(a => a.id === agentId) || {};
    const dest = destList.find(d => d.id === destId) || {};
    const destName = dest.name || destId;

    let whatsappUrl = "";
    if (agent.whatsapp) {
      const rawMsg = `Namaste ${agent.name}! I am ${name}. Found your profile on BharatYatra AI.\nTrip: ${destName}\nTravelers: ${travelers}\nDates: ${date || 'Flexible'}\nNotes: ${notes || 'Looking for quote'}`;
      whatsappUrl = `https://wa.me/${agent.whatsapp}?text=${encodeURIComponent(rawMsg)}`;
    }

    let enquiryId = `ENQ-${Math.floor(1000 + Math.random() * 9000)}`;

    try {
      const res = await fetch(`${API_BASE}/api/enquiry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_id: agentId,
          destination_id: destId,
          traveler_name: name,
          traveler_phone: phone,
          travel_dates: date,
          num_travelers: travelers,
          notes: notes
        })
      });

      if (res.ok) {
        const result = await res.json();
        enquiryId = result.enquiry_id;
        if (result.whatsapp_chat_url) {
          whatsappUrl = result.whatsapp_chat_url;
        }
      }
    } catch (err) {
      console.info("Saved enquiry locally (backend offline or on GitHub Pages).");
    }

    // Save lead locally so it persists and displays in Leads modal
    const localRecord = {
      id: enquiryId,
      destination_id: destId,
      destination_name: destName,
      agent_id: agentId,
      agent_name: agent.name || "Local Guide",
      agency_name: agent.agency_name || "Verified Operator",
      traveler_name: name,
      traveler_phone: phone,
      travel_dates: date || "Flexible",
      num_travelers: travelers,
      notes: notes || "Looking forward to customized packages and quotes.",
      whatsapp_url: whatsappUrl,
      created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const existingLeads = JSON.parse(localStorage.getItem("bharatyatra_leads") || "[]");
    existingLeads.unshift(localRecord);
    localStorage.setItem("bharatyatra_leads", JSON.stringify(existingLeads));

    modal.style.display = "none";
    showToast(`Enquiry registered (${enquiryId})! Opening WhatsApp...`);
    refreshPlatformStats();

    if (whatsappUrl) {
      window.open(whatsappUrl, "_blank");
    }
  });
}

window.openEnquiryModal = function(agentId, destId, agentName, agencyName, badge) {
  const modal = document.getElementById("enquiry-modal");
  const preview = document.getElementById("modal-agent-preview");
  
  document.getElementById("enq-agent-id").value = agentId;
  document.getElementById("enq-dest-id").value = destId || "all";
  document.getElementById("modal-agent-name").textContent = `Connect with ${agentName}`;

  preview.innerHTML = `
    <strong>${agentName}</strong> (${agencyName})<br>
    <span style="color:#0284C7; font-weight:600;">🛡️ ${badge}</span>
  `;

  modal.style.display = "flex";
};
