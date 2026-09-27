# Project Execution Checklist & Progress Tracker

**Project:** Autonomous AI Website Builder with Hindsight Reflection & Self-Healing Loop  
**Goal:** Build a voice/text-driven AI agent that generates production-grade local business websites with a multi-critic panel, self-correction routing, and continuous memory learning powered by Hindsight.

---

## 📊 Status Summary
- **Phase 0: Workspace & Git Setup** — ✅ COMPLETED
- **Phase 1: Architecture & Project Plan** — ✅ COMPLETED
- **Phase 2: Backend & Hindsight Memory Integration** — ⏳ PENDING
- **Phase 3: Multi-Critic & Self-Correction Pipeline** — ⏳ PENDING
- **Phase 4: Frontend Live Preview & Voice Controller** — ⏳ PENDING
- **Phase 5: Deployment & Demo Recording Prep** — ⏳ PENDING

---

## ✅ Phase 0: Workspace & Environment Setup
- [x] Initialized Git repository on `main` branch (`e:\hack`).
- [x] Verified system runtimes (Python 3.14, Node.js v24.18, npm 11.16).
- [x] Added standard `.gitignore`.

---

## ✅ Phase 1: Architecture & Plan
- [x] Defined agent topology based on system architecture diagram:
  - **Business Intake**: User inputs (Name, Category, Location, WhatsApp, Voice/Text instructions).
  - **Orchestration Agent**: Router, workflow state, and iteration manager.
  - **Generation Pipeline**: Copywriter, Designer, and Code Generator.
  - **Critic Panel**: UI/UX Critic, Functionality Critic, Performance Critic, Code Quality Critic.
  - **Hindsight Memory Engine**: Stores World Facts, Experience Facts (mistakes/critiques), and consolidates into Observations & Directives.
  - **Self-Correction Router**: `reflect()`-driven loop instructing regeneration when flaws are identified.
  - **Live Preview & Deployment**: Live browser sandbox with interactive desktop/mobile toggle.
- [x] Documented roadmap and architecture in `README.md` and `CHECKLIST.md`.

---

## ⏳ Phase 2: Backend & Hindsight Core Engine
- [ ] Set up Python backend with FastAPI and Uvicorn.
- [ ] Configure Hindsight client connection (Hindsight Cloud / API key setup).
- [ ] Initialize Memory Bank:
  - Configure **Mission** (Flawless, conversion-focused local business web architect).
  - Configure **Directives** (Zero broken links, mobile viewport mandatory, accessible contrast).
  - Set **Disposition** (High literalism, rigorous quality skepticism).
- [ ] Configure LLM inference client (Groq / OpenRouter with fast models like `gpt-oss-120b` or `qwen3-32b`).
- [ ] Implement `retain()` logic for business context & previous mistakes.
- [ ] Implement `recall()` logic for TEMPR multi-strategy search.
- [ ] Implement `reflect()` reasoning loop for self-correction.

---

## ⏳ Phase 3: Generation & Multi-Critic Self-Healing Pipeline
- [ ] **Copywriter Agent**: Writes headlines, taglines, service descriptions, and local SEO schema.
- [ ] **Design Agent**: Selects theme, typography, color palette, and layout structure.
- [ ] **Code Generator Agent**: Outputs clean, responsive single-file React/Tailwind HTML.
- [ ] **Multi-Critic Evaluation Engine**:
  - [ ] *UI/UX Critic*: Evaluates layout hierarchy, whitespace, and visual balance.
  - [ ] *Functionality Critic*: Checks WhatsApp link format, appointment booking form, interactive modal state.
  - [ ] *Performance & Mobile Critic*: Checks viewport responsiveness and mobile readability.
  - [ ] *Code Quality Critic*: Validates HTML syntax, script errors, and semantic tags.
- [ ] **Self-Correction Loop**: Automatically feed critic flaws to Hindsight $\to$ `reflect()` $\to$ prompt Code Generator with patch instructions until score $\ge 85\%$.

---

## ⏳ Phase 4: Frontend Live Preview & Voice Controller
- [ ] Build interactive web dashboard (React / Vite or clean modern UI).
- [ ] Implement **Voice Input** using browser Web Speech API (instant voice-to-text with zero external dependencies).
- [ ] Build **Interactive Live Preview Sandbox** (responsive iframe with Desktop / Tablet / Mobile viewport switcher).
- [ ] Build **Hindsight Memory & Self-Correction Inspector**:
  - Live feed of memories recalled.
  - Live feed of critic scores (UX, Functionality, Performance, Code).
  - Live self-healing iteration counter (e.g. Iteration 1 $\to$ Iteration 2).
- [ ] Add direct download and copy code buttons.

---

## ⏳ Phase 5: Testing, Demo & Submission Deliverables
- [ ] Test end-to-end flow with realistic business scenarios (e.g., Austin Dental Clinic, Bangalore Cafe, London Plumbing Service).
- [ ] Verify Hindsight before/after improvement:
  - Run 1: Agent catches an issue (e.g., invalid phone format in WhatsApp link).
  - Learning: Retained as Experience Fact & consolidated into an Observation.
  - Run 2: Subsequent generation never makes that mistake again.
- [ ] Record 60-second high-impact demo video.
- [ ] Prepare Hackathon documentation and submission writeup.
