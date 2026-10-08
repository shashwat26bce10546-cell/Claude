#!/bin/bash
# Prepares a Claude Code cloud session for HyperFrames video work:
# installs the pinned CLI + GSAP and the headless Chrome used for rendering.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

npm install --no-audit --no-fund --loglevel=error
npx --no-install hyperframes browser ensure >/dev/null
echo "HyperFrames $(npx --no-install hyperframes --version) ready (Chrome headless shell installed)."
