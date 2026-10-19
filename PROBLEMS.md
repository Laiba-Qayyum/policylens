# Problems log

| Date | Problem | Cause | Fix | Lesson |
|---|---|---|---|---|
| 2026-10-19 | Installing dev tools took over 5 minutes and the command timed out. | Slow network while pip downloaded packages into a fresh venv. | Ran the install in the background and pinned the versions it installed. | Expect the first install to be slow; pin versions once so later installs are predictable. |
| 2026-10-20 | CLAUDE.md was on GitHub even after adding it to .gitignore. | .gitignore only affects untracked files; CLAUDE.md was already in two pushed commits. | `git rm --cached CLAUDE.md`, then rewrote history with `git filter-branch` and force-pushed. | Decide what stays private before the first push. Removing a file later means rewriting history. |
| 2026-10-20 | Force-push failed with "cannot parse expected object name". | `--force-with-lease=main:<short id>` used a short commit ID that git could no longer find after cleanup. | Used the full 40-character commit ID. | Use full commit IDs in commands that check the remote state. |
| 2026-10-20 | pre-commit crashed with "path is on mount 'C:', start on mount 'D:'". | pre-commit only checks files inside the repo, and the test files were on another drive. | Created the test files in a temporary folder inside the repo, then deleted it. | Test hooks with files inside the repo. |
