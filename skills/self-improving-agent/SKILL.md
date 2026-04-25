---
name: self-improvement
description: "Captures learnings, errors, and corrections to enable continuous improvement. Use when: (1) A command or operation fails unexpectedly, (2) User corrects Claude ('No, that's wrong...', 'Actually...'), (3) User requests a capability that doesn't exist, (4) An external API or tool fails, (5) Claude realizes its knowledge is outdated or incorrect, (6) A better approach is discovered for a recurring task. IMPORTANT: Read .learnings/ files at session start to avoid repeating mistakes."
metadata:
---

# Self-Improvement Skill

Log learnings and errors to markdown files for continuous improvement. Coding agents can later process these into fixes, and important learnings get promoted to project memory.

## ⚠️ CRITICAL: Session Start Routine

**Every session MUST start by reading learning files to avoid repeating mistakes.**

### OpenClaw Setup (Automatic)

Add this to your `AGENTS.md` to ensure learnings are loaded every session:

```markdown
## Every Session

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION**: Also read `MEMORY.md`
5. **Read `.learnings/LEARNINGS.md` and `.learnings/ERRORS.md`** — learn from past mistakes!

Don't ask permission. Just do it.
```

### Why This Matters

| Without Session Loading | With Session Loading |
|------------------------|---------------------|
| ❌ Repeats same mistakes | ✅ Avoids known errors |
| ❌ Forgets optimizations | ✅ Applies learned improvements |
| ❌ No continuity | ✅ Continuous improvement |

---

## Quick Reference

| Situation | Action |
|-----------|--------|
| Command/operation fails | Log to `.learnings/ERRORS.md` |
| User corrects you | Log to `.learnings/LEARNINGS.md` with category `correction` |
| User wants missing feature | Log to `.learnings/FEATURE_REQUESTS.md` |
| API/external tool fails | Log to `.learnings/ERRORS.md` with integration details |
| Knowledge was outdated | Log to `.learnings/LEARNINGS.md` with category `knowledge_gap` |
| Found better approach | Log to `.learnings/LEARNINGS.md` with category `best_practice` |
| Broadly applicable learning | Promote to `CLAUDE.md`, `AGENTS.md`, or `TOOLS.md` |

---

## Workspace Structure

```
~/.openclaw/workspace/
├── AGENTS.md          # ⭐ Add session start routine here!
├── SOUL.md            # Behavioral guidelines
├── USER.md            # User preferences
├── TOOLS.md           # Tool configurations
├── MEMORY.md          # Long-term memory
├── memory/            # Daily memory files
│   └── YYYY-MM-DD.md
└── .learnings/        # This skill's log files
    ├── LEARNINGS.md   # Best practices, corrections
    ├── ERRORS.md      # Failures and fixes
    └── FEATURE_REQUESTS.md
```

---

## Installation

**Via SkillHub (recommended):**
```bash
skillhub install self-improving-agent
```

**Manual:**
```bash
git clone https://github.com/peterskoett/self-improving-agent.git ~/.openclaw/workspace/skills/self-improving-agent
```

### Post-Installation Setup

1. Create learning files:
```bash
mkdir -p ~/.openclaw/workspace/.learnings
touch ~/.openclaw/workspace/.learnings/LEARNINGS.md
touch ~/.openclaw/workspace/.learnings/ERRORS.md
touch ~/.openclaw/workspace/.learnings/FEATURE_REQUESTS.md
```

2. **Add session start routine to AGENTS.md** (see above)

---

## Logging Format

### Learning Entry

Append to `.learnings/LEARNINGS.md`:

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending | resolved | promoted
**Area**: frontend | backend | infra | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2

---
```

### Error Entry

Append to `.learnings/ERRORS.md`:

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending | resolved
**Area**: frontend | backend | infra | docs | config

### Summary
Brief description of what failed

### Error
```
Actual error message or output
```

### Context
- Command/operation attempted
- Environment details if relevant

### Suggested Fix
What might resolve this

### Resolution (when fixed)
- **Resolved**: timestamp
- **Notes**: What was done

---
```

---

## Promotion Targets

When learnings prove broadly applicable, promote them:

| Learning Type | Promote To | Example |
|---------------|------------|---------|
| Behavioral patterns | `SOUL.md` | "Be concise, avoid disclaimers" |
| Workflow improvements | `AGENTS.md` | "Spawn sub-agents for long tasks" |
| Tool gotchas | `TOOLS.md` | "PDF font path: /usr/share/fonts/..." |
| User preferences | `USER.md` | "Show skill usage after each reply" |

### How to Promote

1. **Distill** the learning into a concise rule
2. **Add** to appropriate file
3. **Update** original entry: `**Status**: promoted`

---

## Detection Triggers

Automatically log when you notice:

| Trigger | Action |
|---------|--------|
| "No, that's wrong..." | Log as `correction` |
| Command fails | Log to `ERRORS.md` |
| Found better way | Log as `best_practice` |
| User says "remember this" | Log and promote |

---

## Best Practices

1. **Log immediately** - context is freshest right after the issue
2. **Be specific** - future agents need to understand quickly
3. **Promote aggressively** - if broadly useful, add to workspace files
4. **Read at session start** - avoid repeating mistakes
5. **Link related entries** - use `See Also` for recurring issues

---

## Example: Complete Workflow

### 1. Error Occurs
```
PDF generated with Chinese text shows as garbled characters
```

### 2. Log to ERRORS.md
```markdown
## [ERR-20260317-001] pdf_font_error

**Logged**: 2026-03-17T09:40:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
PDF Chinese text shows as garbled characters due to wrong font path

### Error
Font path /usr/share/fonts/truetype/wqy/wqy-zenhei.ttc does not exist

### Suggested Fix
Use correct font path: /usr/share/fonts/wqy-microhei/wqy-microhei.ttc

---
```

### 3. Fix Applied, Update Entry
```markdown
### Resolution
- **Resolved**: 2026-03-17T09:43:00Z
- **Notes**: Corrected font path, PDF now displays Chinese correctly
```

### 4. Promote to TOOLS.md
```markdown
### PDF Generation
- **Chinese font path**: `/usr/share/fonts/wqy-microhei/wqy-microhei.ttc`
```

### 5. Update Learning Status
```markdown
**Status**: promoted
```

---

## Summary

| Step | Action |
|------|--------|
| 1️⃣ | **Session Start**: Read `.learnings/` files |
| 2️⃣ | **On Error**: Log to `ERRORS.md` |
| 3️⃣ | **On Learning**: Log to `LEARNINGS.md` |
| 4️⃣ | **When Fixed**: Update status to `resolved` |
| 5️⃣ | **When Broad**: Promote to workspace files |

---

For full documentation, see the original SKILL.md or visit:
https://github.com/peterskoett/self-improving-agent
