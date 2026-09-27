import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.agents.copywriter import copywriter_agent
from backend.agents.designer import design_agent
from backend.agents.coder import code_generator_agent
from backend.agents.critics import critic_panel
from backend.services.hindsight_service import hindsight_service

logger = logging.getLogger("orchestrator")

class OrchestrationAgent:
    """
    Coordinates the iterative generation, critic evaluation, Hindsight reflection,
    and self-correction loop.
    """

    def __init__(self):
        self.max_healing_iterations = 3

    def run_pipeline(self, business_data: Dict[str, Any], initial_prompt: Optional[str] = None) -> Dict[str, Any]:
        workflow_id = f"wf-{int(datetime.now().timestamp())}"
        logs = []

        def log_event(stage: str, message: str, details: Any = None):
            entry = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "stage": stage,
                "message": message,
                "details": details
            }
            logs.append(entry)
            logger.info(f"[{stage}] {message}")

        instruction_summary = f" Instructions: '{initial_prompt}'" if initial_prompt else ""
        log_event("Intake", f"Received business profile: {business_data.get('name')} in {business_data.get('location')} ({business_data.get('category')}).{instruction_summary}")

        # Step 1: Retain business context in Hindsight as World Facts
        hindsight_service.retain(
            content=f"Business profile: {business_data.get('name')} located in {business_data.get('location')}. Category: {business_data.get('category')}. WhatsApp: {business_data.get('whatsapp', business_data.get('phone'))}.{instruction_summary}",
            tags=["business_intake", business_data.get("category", "local_biz").lower()],
            metadata={"type": "world", "workflow_id": workflow_id}
        )

        # Step 2: Hindsight Memory Recall for best patterns
        recalled = hindsight_service.recall(
            query=f"design copy functionality directives for {business_data.get('category')} {initial_prompt or ''}",
            tags=["pattern", "directive"]
        )
        log_event("Hindsight Recall", f"Retrieved {len(recalled)} historical directives and observations from memory", recalled)

        # Step 3: Run Copywriter & Designer (passing voice instructions!)
        log_event("Copywriter Agent", f"Generating copy incorporating voice instructions: '{initial_prompt or 'Default'}'...")
        copy_data = copywriter_agent.generate_copy(business_data, instructions=initial_prompt)

        log_event("Design Agent", f"Selecting design system and color palette for {business_data.get('category')}...")
        design_system = design_agent.choose_design_system(business_data.get("category", "default"), instructions=initial_prompt)

        # Step 4: Initial Code Generation (passing voice instructions!)
        log_event("Code Generator Agent", "Assembling tailored HTML/Tailwind/JS with active Live Chat...")
        current_html = code_generator_agent.generate_website(
            business_data,
            copy_data,
            design_system,
            instructions=initial_prompt
        )

        # Step 5: Multi-Critic Reflection & Self-Healing Loop
        iteration = 1
        healed = False
        critic_results = None

        while iteration <= self.max_healing_iterations:
            log_event("Critic Panel", f"Running 4-Critic evaluation (Iteration {iteration})...")
            evaluation = critic_panel.evaluate_all(current_html, business_data)
            critic_results = evaluation

            log_event(
                "Critic Evaluation",
                f"Evaluation Score: {evaluation['average_score']}% (Passed: {evaluation['passed']})",
                evaluation['critic_results']
            )

            if evaluation["passed"]:
                log_event("Self-Correction Router", "All critics approved code! Passing to deployment.")
                healed = True
                
                # Retain success pattern in Hindsight
                hindsight_service.retain(
                    content=f"Successfully approved website layout for {business_data.get('name')} with score {evaluation['average_score']}%. Theme: {design_system['theme_name']}. Primary CTA: {copy_data.get('cta_primary')}.",
                    tags=["success_pattern", "approved"],
                    metadata={"type": "experience", "score": str(evaluation["average_score"])}
                )
                break
            else:
                # Flaws detected! Feed to Hindsight Memory & Reflect
                issues_summary = "; ".join(evaluation["all_issues"])
                log_event("Hindsight Retain", f"Retaining critic flaws into memory bank: {issues_summary}")
                
                hindsight_service.retain(
                    content=f"Critic evaluation rejected code in iteration {iteration} due to: {issues_summary}",
                    tags=["critic_rejection", "mistake_guard"],
                    metadata={"type": "experience", "iteration": str(iteration)}
                )

                log_event("Hindsight Reflect", "Reflecting on flaws against architectural directives to formulate patch...")
                reflection_patch = hindsight_service.reflect(
                    query=f"How to heal these specific code flaws: {issues_summary}",
                    context=f"Business: {business_data.get('name')}, Category: {business_data.get('category')}"
                )
                log_event("Self-Correction Patch", "Hindsight generated actionable healing instructions", reflection_patch)

                # Self-healing regeneration
                iteration += 1
                if iteration <= self.max_healing_iterations:
                    log_event("Code Generator Agent", f"Applying self-healing patch for Iteration {iteration}...")
                    current_html = code_generator_agent.generate_website(
                        business_data,
                        copy_data,
                        design_system,
                        instructions=initial_prompt,
                        critique_patch_instructions=reflection_patch
                    )

        return {
            "workflow_id": workflow_id,
            "business_data": business_data,
            "copy_data": copy_data,
            "design_system": design_system,
            "html": current_html,
            "iterations_count": iteration if healed else self.max_healing_iterations,
            "healed": healed,
            "final_evaluation": critic_results,
            "recalled_memories": recalled,
            "logs": logs
        }

orchestration_agent = OrchestrationAgent()
