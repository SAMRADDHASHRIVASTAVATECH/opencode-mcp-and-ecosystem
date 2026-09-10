---
name: cli-applications
description: Designs command-line tools with stable exit codes and tests. Use when building CLIs in Python, Node, C, Go, Rust, or Java.
---

# CLI applications

- argparse / process.argv / flags first.
- Exit 0 success, non-zero failure.
- stdout for data, stderr for errors.
- Template via `se_create_project` (`python-cli`, `node-cli`, `c-cli`, `go-cli`, `rust-cli`, `java-cli`).
- Test by calling `main(argv)` or the binary, not only screenshots of terminals.
