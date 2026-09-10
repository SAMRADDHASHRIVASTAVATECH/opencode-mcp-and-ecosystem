# Backup and restore
`pdp backup FILE.zip` uses SQLite's online backup API after WAL checkpoint and includes identity/config. `pdp restore FILE.zip --force` is destructive and therefore requires the explicit flag. Always run `pdp doctor` after restore.
