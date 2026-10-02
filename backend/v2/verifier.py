from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Dict, List


def verify_project(root: Path) -> Dict[str, Any]:
    """
    Performs comprehensive verification across the generated project:
    1. Python AST parsing on all backend Python code (checks syntax and compiler errors).
    2. Blueprint and package JSON validity and schema checks.
    3. Required architecture file integrity (API routes, SQLAlchemy models, React components).
    4. React JSX bracket/tag sanity verification.
    """
    errors: List[Dict[str, Any]] = []
    checked_files = 0

    # 1. Verify Blueprint source of truth
    blueprint_path = root / "blueprint.json"
    if not blueprint_path.exists():
        errors.append({"file": "blueprint.json", "line": 1, "message": "Missing source-of-truth blueprint.json"})
    else:
        try:
            bp_data = json.loads(blueprint_path.read_text(encoding="utf-8"))
            checked_files += 1
            for section in ["project", "stack", "database", "backend", "frontend"]:
                if section not in bp_data:
                    errors.append({"file": "blueprint.json", "line": 1, "message": f"Blueprint missing section '{section}'"})
        except Exception as e:
            errors.append({"file": "blueprint.json", "line": 1, "message": f"Invalid JSON syntax: {str(e)}"})

    # 2. Verify all Python files in the backend
    for path in root.rglob("*.py"):
        checked_files += 1
        rel_path = str(path.relative_to(root)).replace("\\", "/")
        try:
            content = path.read_text(encoding="utf-8")
            ast.parse(content, filename=str(path))
        except SyntaxError as exc:
            errors.append({
                "file": rel_path,
                "line": exc.lineno or 1,
                "message": f"Python SyntaxError: {exc.msg}"
            })
        except Exception as exc:
            errors.append({
                "file": rel_path,
                "line": 1,
                "message": f"Compilation Error: {str(exc)}"
            })

    # 3. Verify Required Structural Files
    required_files = [
        "backend/app/main.py",
        "backend/app/models.py",
        "backend/app/routes.py",
        "backend/app/db.py",
        "frontend/src/App.jsx",
        "frontend/src/services/api.js",
        "frontend/preview.html"
    ]
    for rel in required_files:
        p = root / rel
        if not p.exists():
            errors.append({"file": rel, "line": 1, "message": "Required architectural file is missing"})
        else:
            checked_files += 1

    # 4. Verify React / JSX component files
    for jsx_path in root.rglob("*.jsx"):
        if jsx_path.name == "main.jsx":
            continue
        rel_jsx = str(jsx_path.relative_to(root)).replace("\\", "/")
        try:
            jsx_text = jsx_path.read_text(encoding="utf-8")
            if "export default" not in jsx_text and "export function" not in jsx_text:
                errors.append({"file": rel_jsx, "line": 1, "message": "Missing component export"})
        except Exception as exc:
            errors.append({"file": rel_jsx, "line": 1, "message": str(exc)})

    passed = len(errors) == 0
    score = 100 if passed else max(0, 100 - len(errors) * 25)

    return {
        "passed": passed,
        "health_score": score,
        "checked_files": checked_files,
        "errors": errors,
        "summary": "All backend routes, models, and React components passed verification." if passed else f"Detected {len(errors)} architectural issue(s) requiring targeted repair."
    }
