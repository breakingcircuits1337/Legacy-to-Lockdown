# L2L — Legacy-to-Lockdown
## What This Project Is
L2L is a reusable IBM Bob pipeline for modernizing legacy Java 
applications. It ships as a set of Bob configuration files that 
users install into their own repo. Bob becomes the engine that 
drives audit, transformation, verification, and documentation — 
consistently, across any target codebase.

## What L2L Is NOT
- It is not tied to any specific legacy application.
- It is not a one-time migration script.
- It is not a static analysis tool that replaces Bob.
  Bob IS the intelligence layer. L2L gives Bob structure.

## Pipeline Phases
  AUDIT      → map CVEs, complexity, coverage, API gaps
  PLAN       → prioritize migration order, define contracts
  TRANSFORM  → module-by-module refactoring with safety gates
  VERIFY     → behavioral equivalence tests before proceeding
  DOCUMENT   → change ledger, ADRs, OpenAPI spec, score delta

## Configuration
All target-specific values live in pipeline/l2l.config.json.
Bob rules and mode definitions are target-agnostic.

## Bob Modes Active in This Project
  /l2l-audit       → read-only analysis, generates AUDIT_REPORT.md
  /l2l-transform   → safe module refactoring with contract gates
  /l2l-verify      → test generation and equivalence checking
