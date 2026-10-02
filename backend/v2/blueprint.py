from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.services.llm_service import llm_service

logger = logging.getLogger("blueprint_agent")


def _slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "project"


def _has(text: str, *terms: str) -> bool:
    return any(term in text for term in terms)


def _heuristic_analyze(prompt: str, project_name: str | None = None, preferences: Optional[List[str]] = None) -> Dict[str, Any]:
    text = (prompt or "").strip()
    lower = text.lower()
    name = project_name or "AI Generated Application"

    entities: List[Dict[str, Any]] = []

    # Domain entity detection
    if _has(lower, "user", "student", "customer", "member", "participant", "login", "signup", "auth"):
        entities.append({"name": "User", "fields": ["id", "name", "email", "role", "created_at"]})
    if _has(lower, "hackathon", "event", "conference", "competition", "meetup"):
        entities.append({"name": "Event", "fields": ["id", "title", "description", "date", "status", "created_at"]})
    if _has(lower, "team", "group", "squad"):
        entities.append({"name": "Team", "fields": ["id", "name", "leader_name", "member_count", "created_at"]})
    if _has(lower, "project", "submission", "showcase", "portfolio"):
        entities.append({"name": "Project", "fields": ["id", "title", "description", "repo_url", "demo_url", "created_at"]})
    if _has(lower, "task", "todo", "ticket", "issue", "kanban"):
        entities.append({"name": "Task", "fields": ["id", "title", "status", "priority", "assignee", "created_at"]})
    if _has(lower, "product", "item", "inventory", "shop", "ecommerce", "store"):
        entities.append({"name": "Product", "fields": ["id", "name", "price", "category", "stock", "created_at"]})
    if _has(lower, "order", "purchase", "checkout", "cart"):
        entities.append({"name": "Order", "fields": ["id", "customer_name", "total_amount", "status", "created_at"]})
    if _has(lower, "post", "article", "blog", "announcement", "news", "update"):
        entities.append({"name": "Post", "fields": ["id", "title", "content", "category", "created_at"]})
    if _has(lower, "review", "feedback", "rating", "testimonial"):
        entities.append({"name": "Review", "fields": ["id", "author", "rating", "comment", "created_at"]})

    if _has(lower, "doctor", "physician", "therapist", "practitioner"):
        entities.append({"name": "Doctor", "fields": ["id", "name", "specialty", "phone", "created_at"]})
    if _has(lower, "patient", "client"):
        entities.append({"name": "Patient", "fields": ["id", "name", "email", "phone", "created_at"]})
    if _has(lower, "appointment", "booking", "schedule", "reservation", "consultation", "clinic"):
        entities.append({"name": "Appointment", "fields": ["id", "patient_name", "doctor_name", "date", "status", "created_at"]})

    if not entities:
        entities.append({"name": "Item", "fields": ["id", "title", "description", "status", "created_at"]})

    pages = [{"name": "Home", "route": "/", "purpose": "Primary landing and overview"}]
    if _has(lower, "dashboard", "admin", "manage", "workspace", "portal"):
        pages.append({"name": "Dashboard", "route": "/dashboard", "purpose": "Live statistics and resource management"})
    if _has(lower, "event", "hackathon", "conference"):
        pages.append({"name": "Events", "route": "/events", "purpose": "Discover and participate in events"})
    if _has(lower, "team", "group"):
        pages.append({"name": "Teams", "route": "/teams", "purpose": "Team rosters and collaboration"})
    if _has(lower, "project", "submission"):
        pages.append({"name": "Projects", "route": "/projects", "purpose": "Showcase and submission explorer"})
    if _has(lower, "task", "kanban", "todo"):
        pages.append({"name": "Tasks", "route": "/tasks", "purpose": "Task workflow and progress board"})
    if _has(lower, "shop", "product", "store"):
        pages.append({"name": "Catalog", "route": "/catalog", "purpose": "Product browse and ordering"})
    if _has(lower, "announcement", "post", "blog", "news"):
        pages.append({"name": "Announcements", "route": "/announcements", "purpose": "System bulletins and updates"})

    # Always ensure at least 2 pages for meaningful navigation
    if len(pages) == 1:
        pages.append({"name": "Explorer", "route": "/explorer", "purpose": "Browse and inspect records"})

    components = ["Navbar", "Sidebar", "StatsOverview", "DataGrid", "CreateModal", "Footer"]
    for entity in entities:
        components.append(f"{entity['name']}Card")
        components.append(f"{entity['name']}Form")

    routes = []
    for entity in entities:
        res = _slug(entity["name"]) + "s"
        routes.append({"method": "GET", "path": f"/api/{res}", "purpose": f"Retrieve all {entity['name']} records"})
        routes.append({"method": "POST", "path": f"/api/{res}", "purpose": f"Create new {entity['name']}"})
        routes.append({"method": "DELETE", "path": f"/api/{res}/{{id}}", "purpose": f"Delete {entity['name']} record"})

    recommendations = [
        "Include client-side form validation and instant optimistic UI updates.",
        "Add search and filter controls as data scales."
    ]
    if _has(lower, "auth", "login", "signup", "role", "admin"):
        recommendations.append("Role-based access control (Admin vs Student/User) recommended.")
    else:
        recommendations.append("Consider authentication for role-based permissions.")

    conflicts = []
    if _has(lower, "100000", "million", "massive", "high concurrency") and _has(lower, "sqlite"):
        conflicts.append({
            "type": "scale_constraint",
            "message": "High concurrency requested with SQLite.",
            "suggestion": "SQLite is used for rapid local development; design models to migrate cleanly to PostgreSQL."
        })

    # Preferences & design system
    density = "compact" if any("compact" in str(p).lower() for p in (preferences or [])) or "compact" in lower else "standard"
    theme = "dark" if any("dark" in str(p).lower() for p in (preferences or [])) or "dark" in lower or not _has(lower, "light") else "light"

    return {
        "schema_version": "2.0",
        "project": {
            "id": f"proj-{uuid.uuid4().hex[:10]}",
            "name": name,
            "slug": _slug(name),
            "description": text
        },
        "stack": {
            "frontend": "react-vite",
            "backend": "fastapi",
            "database": "sqlite"
        },
        "design_system": {
            "theme": theme,
            "density": density,
            "primary_color": "#d6b56d" if theme == "dark" else "#2563eb",
            "background": "#080808" if theme == "dark" else "#f8fafc"
        },
        "requirements": {
            "prompt": text,
            "entities": [e["name"] for e in entities],
            "pages": [p["name"] for p in pages],
            "preferences_applied": preferences or []
        },
        "database": {"entities": entities},
        "backend": {"routes": routes},
        "frontend": {"pages": pages, "components": components},
        "recommendations": recommendations,
        "conflicts": conflicts,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }


def analyze_requirements(
    prompt: str,
    project_name: str | None = None,
    preferences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyzes user requirements to produce the single-source-of-truth Project Blueprint.
    Uses LLM reasoning when available, falling back to comprehensive heuristics.
    """
    text = (prompt or "").strip()
    name = project_name or "AI Generated Application"

    if llm_service.client and len(text) > 10:
        pref_str = "\n".join(f"- {p}" for p in (preferences or [])) if preferences else "None"
        system_prompt = (
            "You are an Elite Software Architect for the Hindsight Autonomous Application Builder.\n"
            "Given a product description and user preferences, output a strictly valid JSON Project Blueprint.\n"
            "Do NOT include markdown backticks or commentary. Output pure JSON matching this exact structure:\n"
            "{\n"
            '  "project_name": string,\n'
            '  "entities": [{"name": string, "fields": [string]}],\n'
            '  "pages": [{"name": string, "route": string, "purpose": string}],\n'
            '  "components": [string],\n'
            '  "routes": [{"method": "GET"|"POST"|"DELETE", "path": string, "purpose": string}],\n'
            '  "recommendations": [string],\n'
            '  "conflicts": [{"type": string, "message": string, "suggestion": string}],\n'
            '  "design_system": {"theme": "dark"|"light", "density": "compact"|"standard", "primary_color": string}\n'
            "}"
        )
        user_prompt = (
            f"Product Idea: {text}\n"
            f"Requested Name: {name}\n"
            f"Recalled Engineering & Design Preferences:\n{pref_str}\n\n"
            "Generate an architectural blueprint with clear entities (id, name/title, fields), "
            "pages, components, and FastAPI routes."
        )

        try:
            raw_response = llm_service.complete(user_prompt, system_prompt=system_prompt, temperature=0.2)
            clean_json = raw_response.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            parsed = json.loads(clean_json)
            
            # Map LLM output to full Blueprint 2.0 schema
            entities = parsed.get("entities", [])
            for e in entities:
                if "id" not in e.get("fields", []):
                    e["fields"] = ["id"] + [f for f in e.get("fields", []) if f != "id"]
                if "created_at" not in e["fields"]:
                    e["fields"].append("created_at")

            pages = parsed.get("pages", [])
            if not any(p.get("route") == "/" for p in pages):
                pages.insert(0, {"name": "Home", "route": "/", "purpose": "Primary landing and overview"})

            routes = parsed.get("routes", [])
            if not routes:
                for entity in entities:
                    res = _slug(entity["name"]) + "s"
                    routes.append({"method": "GET", "path": f"/api/{res}", "purpose": f"List {entity['name']} records"})
                    routes.append({"method": "POST", "path": f"/api/{res}", "purpose": f"Create {entity['name']}"})

            ds = parsed.get("design_system", {})
            return {
                "schema_version": "2.0",
                "project": {
                    "id": f"proj-{uuid.uuid4().hex[:10]}",
                    "name": parsed.get("project_name") or name,
                    "slug": _slug(parsed.get("project_name") or name),
                    "description": text
                },
                "stack": {
                    "frontend": "react-vite",
                    "backend": "fastapi",
                    "database": "sqlite"
                },
                "design_system": {
                    "theme": ds.get("theme", "dark"),
                    "density": ds.get("density", "compact" if any("compact" in str(p).lower() for p in (preferences or [])) else "standard"),
                    "primary_color": ds.get("primary_color", "#d6b56d"),
                    "background": "#080808" if ds.get("theme", "dark") == "dark" else "#f8fafc"
                },
                "requirements": {
                    "prompt": text,
                    "entities": [e["name"] for e in entities],
                    "pages": [p["name"] for p in pages],
                    "preferences_applied": preferences or []
                },
                "database": {"entities": entities},
                "backend": {"routes": routes},
                "frontend": {
                    "pages": pages,
                    "components": parsed.get("components", ["Navbar", "Sidebar", "DataGrid", "CreateModal"])
                },
                "recommendations": parsed.get("recommendations", ["Server-side validation recommended."]),
                "conflicts": parsed.get("conflicts", []),
                "status": "draft",
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as exc:
            logger.warning(f"LLM blueprint analysis failed ({exc}), falling back to heuristic engine.")

    return _heuristic_analyze(text, name, preferences)
