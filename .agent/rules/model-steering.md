---
trigger: always_on
---

# Rule: Model Allocation
- **Trigger:** When the task involves "complex refactoring" or "UI styling".
- **Action:** Request the use of **Claude 3.5 Sonnet** (or 4.6).
- **Trigger:** When the task involves "initial project planning" or "multi-file analysis".
- **Action:** Default to **Gemini 3 Pro**.
- **Constraint:** If Sonnet credits are < 10%, fallback to **Gemini 3 Flash** for documentation tasks.