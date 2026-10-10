# Fresh-clone verification log

## 2026-10-11 · Windows PowerShell

Status: TODO — a clean-clone run was not completed in this environment because the available Python launcher is a Microsoft Store stub. The repository was inspected in place; frontend tests and build passed. The targeted Playwright cold-start test was added but could not run because the local Playwright browser executable is not installed; the test runner explicitly requests `npx playwright install`.

Planned record for the owner to complete:

1. Clone the public repository into a clean temporary directory.
2. Follow README setup commands exactly with placeholder secrets.
3. Run backend tests, frontend tests, build, and UI audit.
4. Start both services, log in as investigator and admin, and follow the judge walkthrough.
5. Repeat live smoke only after configuring a private Token Factory key; never record the key or model output in this log.

Record OS, Python, Node, package-manager versions, each command, outcome, and any README correction here.
