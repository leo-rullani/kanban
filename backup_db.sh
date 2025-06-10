#!/bin/bash

NOW=$(date +"%Y-%m-%d_%H-%M-%S")
SRC="db.sqlite3"
DEST="db_backup_$NOW.sqlite3"

if [ -f "$SRC" ]; then
  cp "$SRC" "backups/$DEST"
  echo "Backup erfolgreich erstellt: backups/$DEST"
else
  echo "Keine db.sqlite3 gefunden!"
fi