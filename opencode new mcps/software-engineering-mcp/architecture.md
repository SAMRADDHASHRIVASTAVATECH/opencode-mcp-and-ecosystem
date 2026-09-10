# SE MCP — Architecture

```
Agent + Skills (how to decide)
        │
        ▼
software-engineering-mcp   ← this package
        │
        ├── local adapters: env, scaffold, detect, build, test, audit
        ├── ascii_tree + lang_templates (Tree Creator, headless)
        ├── sdlc catalog (21 phases, audiences, categories)
        ├── apps/ tkinter GUIs (launch via se_launch_gui)
        └── routing table → office | database | windows | android MCPs
```

Skills live in `/home/user/skills/` (ecosystem-level, not inside one MCP).  
MCP config lives in `/home/user/mcp.json`.
