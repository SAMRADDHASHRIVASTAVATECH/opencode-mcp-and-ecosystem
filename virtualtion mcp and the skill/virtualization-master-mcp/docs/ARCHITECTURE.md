# Architecture

`OpenCode skill → MCP tools → dynamic capability registry → structured planner → exact approval engine → platform executable → guest controller → verification`.

Level 1 handles VM lifecycle and snapshots through allowlisted native argv. Level 2 operates inside an identified guest through WSL direct execution, SSH, or VirtualBox Guest Additions. Guest commands are argv arrays and never fall back to the host. Discovery reruns native probes rather than persisting unsupported claims. Execution is asynchronous and returns a job; status includes context, target, bounded output, exit code, and timestamps.

State model separates platform detection, VM power state, guest endpoint reachability, authentication, OS detection, and operation-specific readiness. `wait_for_vm` only proves TCP endpoint reachability, not authentication or command readiness; follow with a harmless guest probe.
