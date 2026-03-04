---
trigger: always_on
---

# Rule: Terminal Security Policy
- **RESTRICTED_COMMANDS:** The following commands are strictly prohibited for auto-execution: `git push`, `git remote`, `rm -rf /`.
- **BEHAVIOR:** If a task requires pushing code, you must stop and ask the user to perform the action manually in their own terminal.
- **LOCAL_ONLY:** All git operations must be limited to `git add` and `git commit`.