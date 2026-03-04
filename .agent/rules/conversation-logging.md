---
trigger: always_on
---

# Rule: Mandatory Conversation Logging
- **Objective:** Maintain a persistent record of all agent thoughts, decisions, and chat history.
- **Action:** After every significant turn or task completion, the agent must update a file named `.agent/logs/chat_history.md`.
- **Format:** Use standard Markdown with timestamps. Include:
  - User Input
  - Agent Reasoning (Internal Monologue)
  - Actions Taken
  - Final Response
- **Constraint:** Do not delete existing logs; always append to the bottom of the file.