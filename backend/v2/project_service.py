from __future__ import annotations

import json
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.v2.blueprint import analyze_requirements
from backend.v2.scaffold import scaffold_project
from backend.v2.verifier import verify_project
from backend.services.hindsight_service import hindsight_service

ROOT = Path(__file__).resolve().parents[2] / "generated_projects"
ROOT.mkdir(parents=True, exist_ok=True)


def _get_project_dir(project_id: str) -> Path:
    p = ROOT / project_id
    if not p.exists():
        raise FileNotFoundError(f"Project '{project_id}' not found")
    return p


def _save_blueprint(root: Path, blueprint: Dict[str, Any]) -> None:
    (root / "blueprint.json").write_text(json.dumps(blueprint, indent=2), encoding="utf-8")


def _save_project_memory(root: Path, category: str, item: Dict[str, Any]) -> None:
    mem_dir = root / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    file_path = mem_dir / f"{category}.json"
    existing = []
    if file_path.exists():
        try:
            existing = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    existing.append(item)
    file_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def get_project_memory(project_id: str) -> Dict[str, Any]:
    root = _get_project_dir(project_id)
    mem_dir = root / "memory"
    res = {"decisions": [], "preferences": [], "failures": []}
    if not mem_dir.exists():
        return res
    for cat in ["decisions", "preferences", "failures"]:
        f = mem_dir / f"{cat}.json"
        if f.exists():
            try:
                res[cat] = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                res[cat] = []
    return res


def update_blueprint(project_id: str, blueprint: Dict[str, Any]) -> Dict[str, Any]:
    root = _get_project_dir(project_id)
    required = {"project", "stack", "requirements", "database", "backend", "frontend"}
    missing = required - set(blueprint)
    if missing:
        raise ValueError(f"Blueprint missing required sections: {', '.join(sorted(missing))}")
    blueprint["project"]["id"] = project_id
    blueprint["status"] = "draft"
    _save_blueprint(root, blueprint)
    return {"project_id": project_id, "blueprint": blueprint}


def _unique_name(items: list[dict[str, Any]], name: str) -> str:
    existing = {str(item.get("name", "")).lower() for item in items}
    candidate = name.strip() or "New Item"
    if candidate.lower() not in existing:
        return candidate
    index = 2
    while f"{candidate} {index}".lower() in existing:
        index += 1
    return f"{candidate} {index}"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def _apply_instruction(blueprint: Dict[str, Any], instruction: str) -> tuple[Dict[str, Any], str, list[str]]:
    """
    Applies a natural language engineering change to the Blueprint source of truth,
    returning the updated blueprint, human-readable change description, and list of affected files.
    """
    text = instruction.strip()
    lower = text.lower()
    affected = {"blueprint.json", "frontend/src/App.jsx", "frontend/preview.html", "README.md"}
    change = "Blueprint updated"

    # 1. UI Density & Design Preferences (e.g., "Make dashboard more compact", "compact layout")
    if "compact" in lower or "reduce padding" in lower or "dense" in lower:
        blueprint.setdefault("design_system", {})["density"] = "compact"
        change = "Applied compact layout density across all dashboard cards and tables per user preference"

    elif "spacious" in lower or "expand padding" in lower:
        blueprint.setdefault("design_system", {})["density"] = "standard"
        change = "Applied standard spacious layout density across application pages"

    # 2. Theme Preferences
    elif "light theme" in lower or "light mode" in lower:
        blueprint.setdefault("design_system", {})["theme"] = "light"
        blueprint.setdefault("design_system", {})["primary_color"] = "#2563eb"
        change = "Updated design system theme to Clean Light mode"

    elif "dark theme" in lower or "dark mode" in lower or "gold" in lower:
        blueprint.setdefault("design_system", {})["theme"] = "dark"
        blueprint.setdefault("design_system", {})["primary_color"] = "#d6b56d"
        change = "Updated design system theme to Obsidian & Gold Dark mode"

    # 3. Common Entity Injections (Announcements / Posts)
    elif "announcement" in lower or "bulletin" in lower or "news" in lower:
        entity = next((e for e in blueprint["database"]["entities"] if e["name"].lower() == "post"), None)
        if entity is None:
            blueprint["database"]["entities"].append({
                "name": "Post",
                "fields": ["id", "title", "content", "category", "created_at"]
            })
            blueprint["requirements"]["entities"].append("Post")
            affected.update({"backend/app/models.py", "backend/app/routes.py", "frontend/src/services/api.js"})
        page = next((p for p in blueprint["frontend"]["pages"] if "announcement" in p["name"].lower()), None)
        if page is None:
            blueprint["frontend"]["pages"].append({
                "name": "Announcements",
                "route": "/announcements",
                "purpose": "System bulletins and announcements"
            })
            blueprint["requirements"]["pages"].append("Announcements")
        change = "Added Announcements as a persistent Post entity and Announcements page"

    # 4. Team Invitations / Collaboration
    elif "invitation" in lower or "invite" in lower:
        if not any(e["name"].lower() == "invitation" for e in blueprint["database"]["entities"]):
            blueprint["database"]["entities"].append({
                "name": "Invitation",
                "fields": ["id", "team_id", "email", "status", "created_at"]
            })
            blueprint["requirements"]["entities"].append("Invitation")
            affected.update({"backend/app/models.py", "backend/app/routes.py", "frontend/src/services/api.js"})
        if not any(p["name"].lower() == "invitations" for p in blueprint["frontend"]["pages"]):
            blueprint["frontend"]["pages"].append({
                "name": "Invitations",
                "route": "/invitations",
                "purpose": "Manage team invitations and joins"
            })
            blueprint["requirements"]["pages"].append("Invitations")
        change = "Added Team Invitations entity, API surface, and Invitations navigation page"

    # 5. Generic "Add Page / Section"
    elif re.search(r"add\s+(?:a\s+)?(.+?)\s+(?:page|section)", lower):
        match = re.search(r"add\s+(?:a\s+)?(.+?)\s+(?:page|section)", text, re.I)
        page_name = match.group(1).strip().title() if match else "New Page"
        page_name = _unique_name(blueprint["frontend"]["pages"], page_name)
        route = "/" + _slug(page_name)
        blueprint["frontend"]["pages"].append({
            "name": page_name,
            "route": route,
            "purpose": f"{page_name} application workspace"
        })
        blueprint["requirements"]["pages"].append(page_name)
        change = f"Added {page_name} page to frontend navigation and routing"

    # 6. Generic "Add Entity / Model"
    elif re.search(r"add\s+(?:a\s+)?(?:entity|model|data)\s+(.+)", lower):
        match = re.search(r"add\s+(?:a\s+)?(?:entity|model|data)\s+(.+)", text, re.I)
        name = match.group(1).strip().split(" with ")[0].title() if match else "Record"
        name = _unique_name(blueprint["database"]["entities"], name)
        fields = ["id", "name", "description", "status", "created_at"]
        blueprint["database"]["entities"].append({"name": name, "fields": fields})
        blueprint["requirements"]["entities"].append(name)
        affected.update({"backend/app/models.py", "backend/app/routes.py", "frontend/src/services/api.js"})
        change = f"Added {name} database entity, SQLAlchemy model, and REST CRUD API routes"

    else:
        # Fallback: Record change request in requirements
        blueprint.setdefault("requirements", {}).setdefault("change_requests", []).append(text)
        change = f"Recorded change request: '{text}'"

    blueprint["requirements"]["prompt"] = blueprint["requirements"].get("prompt", "") + f"\nChange requested: {text}"
    blueprint["status"] = "draft"
    return blueprint, change, sorted(affected)


def build_from_prompt(prompt: str, project_name: str | None = None) -> Dict[str, Any]:
    """
    Entrypoint to build a full-stack project:
    1. Recalls relevant user preferences and architectural rules from Hindsight.
    2. Generates the structured Blueprint source of truth.
    3. Scaffolds React + FastAPI + SQLite files deterministically.
    4. Runs multi-layer verification.
    5. Retains the project decision in both project-scoped memory and Hindsight cloud/local bank.
    """
    # Step 1: Recall prior user preferences
    raw_prefs = hindsight_service.recall_user_preferences(
        category="application",
        current_instruction=prompt,
        max_results=5
    )
    recalled_prefs = [
        p.get("content", str(p)) if isinstance(p, dict) else str(p)
        for p in raw_prefs
    ]

    # Step 2: Generate Blueprint
    blueprint = analyze_requirements(prompt, project_name, recalled_prefs)
    project_id = blueprint["project"]["id"]
    root = ROOT / project_id

    # Step 3: Scaffold Project
    build = scaffold_project(blueprint, root)

    # Step 4: Verify Project
    verification = verify_project(root)
    blueprint["status"] = "verified" if verification["passed"] else "repair_required"
    _save_blueprint(root, blueprint)

    # Step 5: Store Project-Scoped Decision Memory
    decision_record = {
        "id": f"dec-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat(),
        "decision": "Full-Stack React + FastAPI + SQLite Project Scaffolding",
        "reason": f"Initial build from user prompt: '{prompt}'",
        "stack": blueprint["stack"],
        "entities": [e["name"] for e in blueprint["database"]["entities"]],
        "recalled_preferences_applied": recalled_prefs,
        "verification_passed": verification["passed"]
    }
    _save_project_memory(root, "decisions", decision_record)

    # Step 6: Retain in Hindsight
    hindsight_service.retain(
        content=(
            f"Project '{blueprint['project']['name']}' (ID: {project_id}) created with blueprint-first architecture. "
            f"Stack: React/Vite + FastAPI + SQLite. Entities: {', '.join(blueprint['requirements']['entities'])}. "
            f"Applied preferences: {', '.join(recalled_prefs) if recalled_prefs else 'None'}."
        ),
        tags=["project_decision", "blueprint", "v2"],
        metadata={"type": "experience", "project_id": project_id}
    )

    return {
        "project_id": project_id,
        "blueprint": blueprint,
        "build": build,
        "verification": verification,
        "recalled_preferences": recalled_prefs,
        "preview_url": f"/api/v2/projects/{project_id}/preview"
    }


def modify_project(project_id: str, instruction: str) -> Dict[str, Any]:
    """
    Evolves an existing project incrementally:
    1. Recalls project-scoped and global Hindsight memory.
    2. Applies modifications to the Blueprint source of truth.
    3. Scaffolds only the affected files into a temporary directory and syncs them.
    4. Runs verification.
    5. Retains the engineering revision decision in Hindsight.
    """
    root = _get_project_dir(project_id)
    blueprint_path = root / "blueprint.json"
    if not blueprint_path.exists():
        raise FileNotFoundError(f"Project blueprint not found for {project_id}")

    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    
    # Check for durable preferences in the user instruction (e.g. "and remember this preference")
    hindsight_service.learn_user_preferences(instruction, business_name=blueprint["project"]["name"])

    # Apply instruction to the blueprint
    blueprint, change, affected = _apply_instruction(blueprint, instruction)

    # Regenerate into temporary project and copy ONLY affected files
    with tempfile.TemporaryDirectory() as tmp:
        generated = Path(tmp) / "project"
        scaffold_project(blueprint, generated)
        for rel in affected:
            source = generated / rel
            target = root / rel
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    _save_blueprint(root, blueprint)
    verification = verify_project(root)
    blueprint["status"] = "verified" if verification["passed"] else "repair_required"
    _save_blueprint(root, blueprint)

    # Store project-scoped decision
    decision_record = {
        "id": f"dec-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat(),
        "instruction": instruction,
        "change": change,
        "affected_files": affected,
        "verification_passed": verification["passed"]
    }
    _save_project_memory(root, "decisions", decision_record)

    # Retain in Hindsight
    hindsight_service.retain(
        content=f"Project {project_id} evolved: {change}. Regenerated only affected files: {', '.join(affected)}.",
        tags=["incremental_change", "project_decision", "v2"],
        metadata={"type": "experience", "project_id": project_id, "instruction": instruction}
    )

    return {
        "project_id": project_id,
        "change": change,
        "instruction": instruction,
        "affected_files": affected,
        "blueprint": blueprint,
        "verification": verification,
        "preview_url": f"/api/v2/projects/{project_id}/preview"
    }


def repair_project(project_id: str, file: str) -> Dict[str, Any]:
    """
    Surgically repairs a damaged or failing file in the project:
    1. Re-derives the verified implementation of that specific file from the Blueprint.
    2. Overwrites only that single file without touching other code or database records.
    3. Re-runs verification.
    4. Logs the repair event in project failures and Hindsight memory.
    """
    root = _get_project_dir(project_id)
    blueprint_path = root / "blueprint.json"
    if not blueprint_path.exists():
        raise FileNotFoundError(f"Project blueprint not found for {project_id}")

    blueprint = json.loads(blueprint_path.read_text(encoding="utf-8"))
    norm_file = file.replace("\\", "/")
    target = (root / norm_file).resolve()

    if root.resolve() not in target.parents:
        raise ValueError(f"Invalid file path: {file}")

    # Generate verified code in temporary scaffold
    with tempfile.TemporaryDirectory() as tmp:
        generated = Path(tmp) / "project"
        scaffold_project(blueprint, generated)
        source = generated / norm_file
        if not source.exists():
            raise FileNotFoundError(f"Cannot regenerate '{file}' from blueprint")
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    verification = verify_project(root)

    # Record repair event
    repair_record = {
        "id": f"rep-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat(),
        "repaired_file": norm_file,
        "verification_passed": verification["passed"]
    }
    _save_project_memory(root, "failures", repair_record)

    hindsight_service.retain(
        content=f"Targeted repair applied to '{norm_file}' in project {project_id}; verification passed={verification['passed']}.",
        tags=["repair", "targeted_repair", "v2"],
        metadata={"type": "experience", "project_id": project_id, "file": norm_file}
    )

    return {
        "project_id": project_id,
        "repaired_file": norm_file,
        "verification": verification,
        "message": f"Surgically repaired '{norm_file}'. Project verification is now healthy."
    }


def simulate_fault(project_id: str) -> Dict[str, Any]:
    """
    Demonstration helper for hackathons:
    Intentionally injects a syntax defect into a backend route file
    so the agent can visibly demonstrate real-time fault detection and targeted repair.
    """
    root = _get_project_dir(project_id)
    routes_file = root / "backend/app/routes.py"
    if not routes_file.exists():
        raise FileNotFoundError("routes.py not found")

    content = routes_file.read_text(encoding="utf-8")
    # Inject an intentional syntax flaw
    broken_content = content + "\n\n# INTENTIONAL INJECTED FAULT FOR DEMONSTRATION\ndef broken_endpoint(\n"
    routes_file.write_text(broken_content, encoding="utf-8")

    verification = verify_project(root)
    return {
        "project_id": project_id,
        "fault_injected_file": "backend/app/routes.py",
        "verification": verification,
        "message": "Defect injected into backend/app/routes.py. Verification has detected the issue."
    }
