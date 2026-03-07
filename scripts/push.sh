#!/bin/bash
set -e

echo "Mnemonic - Git Push Script"
echo "=========================="

# Check for uncommitted changes
if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit."
    exit 0
fi

# Show status
git status

# Ask for commit message
echo ""
echo "Enter commit message (or press Enter for default):"
read -r MSG

if [ -z "$MSG" ]; then
    MSG="Update: $(date '+%Y-%m-%d %H:%M')"
fi

# Stage all changes
git add -A

# Commit
git commit -m "$MSG"

# Push
echo "Pushing to GitHub..."
git push origin main

echo ""
echo "Done! View at: https://github.com/p-yan-6908/mnemonic"
