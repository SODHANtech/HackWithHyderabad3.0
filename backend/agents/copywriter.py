import json
from typing import Dict, Any, List
from backend.services.llm_service import llm_service
from backend.services.hindsight_service import hindsight_service

class CopywriterAgent:
    """Generates high-converting copy, headlines, services list, and Local SEO schema."""

    def generate_copy(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        name = business_data.get("name", "Apex Solutions")
        category = business_data.get("category", "Local Service")
        location = business_data.get("location", "Downtown")
        services = business_data.get("services", "Consulting, Support, Repairs")
        phone = business_data.get("phone", "+1 555-0199")
        whatsapp = business_data.get("whatsapp", phone)

        # Recall Hindsight memory regarding high-converting copy in this niche
        memories = hindsight_service.recall(
            query=f"high converting copy headlines value propositions for {category}",
            tags=["copywriting", "conversion"],
            max_results=3
        )
        memory_context = "\n".join([f"- {m['content']}" for m in memories])

        prompt = f"""
You are an expert Local Business Copywriter.
Create compelling, conversion-focused website copy for:
Business Name: {name}
Category: {category}
Location: {location}
Offered Services: {services}
WhatsApp Contact: {whatsapp}

Historical Insights from Hindsight Memory:
{memory_context}

Return a valid JSON object strictly matching this schema:
{{
  "headline": "High-impact main headline (under 10 words)",
  "subheadline": "Action-oriented value proposition (1-2 sentences)",
  "cta_primary": "Call to action label (e.g. 'Book Your Free Inspection')",
  "cta_secondary": "Secondary action label (e.g. 'Chat on WhatsApp')",
  "services": [
    {{"title": "Service 1", "description": "Brief benefit description"}},
    {{"title": "Service 2", "description": "Brief benefit description"}},
    {{"title": "Service 3", "description": "Brief benefit description"}}
  ],
  "why_choose_us": [
    "Reason 1 with local credibility",
    "Reason 2 with rapid response",
    "Reason 3 with satisfaction guarantee"
  ],
  "testimonials": [
    {{"name": "Local Client 1", "quote": "Compelling authentic praise", "rating": 5}},
    {{"name": "Local Client 2", "quote": "Great response time and service", "rating": 5}}
  ],
  "seo_meta": {{
    "title": "{name} | Leading {category} in {location}",
    "description": "Top-rated {category} in {location}. Verified experts, same-day appointments, and transparent pricing. Contact us today."
  }}
}}
Return ONLY valid JSON. No markdown wrappers or explanation.
"""
        response = llm_service.complete(prompt, system_prompt="You generate strictly formatted JSON copywriting data.")
        
        try:
            # Clean markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return data
        except Exception:
            # Fallback high quality structured copy
            return {
                "headline": f"Austin's Trusted #{category} Specialists",
                "subheadline": f"Providing reliable, high-grade {category.lower()} in {location}. Transparent pricing, licensed pros, and 24/7 emergency response.",
                "cta_primary": "Schedule Appointment",
                "cta_secondary": "Instant WhatsApp Chat",
                "services": [
                    {"title": f"Comprehensive {category}", "description": f"Full inspection, diagnostic, and certified service tailored to {location} residents."},
                    {"title": "Emergency Dispatch", "description": "Rapid arrival within 60 minutes for urgent service requests."},
                    {"title": "Preventative Maintenance", "description": "Long-term maintenance plans ensuring peak reliability and peace of mind."}
                ],
                "why_choose_us": [
                    f"Over 10+ years serving homeowners and businesses in {location}",
                    "Transparent upfront pricing with zero hidden fees",
                    "Licensed, insured, and background-checked technicians"
                ],
                "testimonials": [
                    {"name": "Sarah Jenkins", "quote": f"The fastest and most courteous {category.lower()} team in {location}. Solved our issue within an hour!", "rating": 5},
                    {"name": "David Miller", "quote": "Extremely professional, fair quote, and clean workmanship. Highly recommended!", "rating": 5}
                ],
                "seo_meta": {
                    "title": f"{name} - #1 {category} in {location}",
                    "description": f"Top-rated {category} in {location}. Same-day bookings, certified experts, and upfront pricing. Call or WhatsApp {name} today."
                }
            }

copywriter_agent = CopywriterAgent()
