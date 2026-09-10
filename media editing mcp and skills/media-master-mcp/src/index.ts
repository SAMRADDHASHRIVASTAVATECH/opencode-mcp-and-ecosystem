#!/usr/bin/env node
import{run}from'./mcp/server.js';run().catch(e=>{console.error(e);process.exit(1)})
