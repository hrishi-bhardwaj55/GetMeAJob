# Rule: Local-Only Incremental Development
- **Local Commits:** After completing a sub-task, run `git add .` and `git commit -m "[message]"`.
- **NO REMOTE ACCESS:** Do NOT run `git push` or `git pull` from remote.
- **Review Protocol:** All changes must remain in the local repository. The user will handle pushing to GitHub/GitLab after a manual review of the final local state.
- **Verification:** Before committing, the agent should run `git status` to ensure only intended files are staged.