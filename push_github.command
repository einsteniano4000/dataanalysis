#!/bin/bash
cd "$(dirname "$0")"
rm -f .git/index.lock .git/HEAD.lock .git/objects/maintenance.lock
find .git/objects -name 'tmp_obj_*' -delete 2>/dev/null
git add push_github.command
git commit -m "Aggiungi script di utilità per il push su GitHub"
echo ""
echo "Pushing su GitHub..."
git push origin main
echo ""
echo "Fatto. Premi invio per chiudere."
read
