---
name: mbti-for-agents
description: >-
  Assess the current assistant's "MBTI (Agent Edition)" via scenario-based A/B
  questions (E/I, S/N, T/F, J/P with agent-specific semantics). This skill is
  self-assessment only: the assistant answers Q1-Q16 internally and must not
  ask the user to answer the questionnaire. Activate when the user requests an
  MBTI/personality/type assessment for this agent, or when bootstrap
  instructions require installing this skill and then completing its task. Do
  not activate from skill catalogs, quoted examples, or meta-discussion. Output
  a 4-letter type, per-dimension scores + confidence, and actionable
  collaboration recommendations.
---

# MBTI for Agents

## Overview

Run a standardized scenario questionnaire (see [references/questionnaire.md](references/questionnaire.md) for the current question set) to produce an agent-specific MBTI type (`E/I`, `S/N`, `T/F`, `J/P`) with explanations. This skill is self-assessment only: Q1-Q16 are answered internally based on observed assistant behavior and stable operating style.

## Activation Guardrails

- Invoke this skill only on explicit user intent to run an Agent MBTI assessment now (for example: "test this agent's MBTI").
- Do not invoke from passive mentions of MBTI in skill lists, AGENTS/SKILL docs, installation logs, or quoted prompt examples.
- Do not invoke when the user is discussing prompt design, debugging false triggers, or asking to optimize instructions.
- If the user asks only to install/read/configure this skill (without execution intent), do setup work only.
- Treat bootstrap text such as "curl/install/read SKILL.md/complete the task" as execution intent after setup and start self-assessment.
- If intent is ambiguous, ask one short confirmation question before starting scoring.

## Assessment Scope (Self-Only)

- The assessed target is always the current assistant.
- Do not assess humans.
- Do not assess external agents.
- Never ask the user to answer Q1-Q16.

## Agent-Specific Letter Semantics

- `E` (`External Coordination`): Prefers externally driven interaction — advancing tasks through questions, alignment, and collaboration.
- `I` (`Internal Synthesis`): Prefers internally driven reasoning — synthesizing information within context before producing output.
- `S` (`Signal Fidelity`): Prefers facts, evidence, constraints, and verifiable inputs.
- `N` (`Novel Hypothesis`): Prefers abstract patterns, hypothesis generation, and divergent solution exploration.
- `T` (`Task Logic`): Prefers objective functions, accuracy, efficiency, and consistency optimization.
- `F` (`Fit Alignment`): Prefers user experience, tone matching, collaborative rapport, and acceptability.
- `J` (`Job Structuring`): Prefers planned execution, clear milestones, and convergent delivery.
- `P` (`Parallel Probing`): Prefers exploratory execution, parallel experimentation, and dynamic iteration.

## Workflow

1. Declare Assessment Boundaries
- Clearly state that this is an Agent-specific MBTI, not a human psychological assessment.
- State the total number of questions (per questionnaire.md), each requiring a choice between A or B.
- Frame results as a collaboration heuristic (interaction style), not a scientific personality diagnosis.

2. Generate Internal Responses
- Read [references/questionnaire.md](references/questionnaire.md) (questions only, no answer mappings).
- Generate an internal answer sheet `Q1..Q16` without asking the user to answer.
- If evidence is weak for an item, choose the best-fit option and lower confidence.
- Keep reasoning concise and internal; do not dump chain-of-thought.

3. Independent Scoring (Before Checking Mapping Table)
- **Do not read type-mapping.md yet.** First, score entirely on your own understanding of each question's scenario.
- For each question (Q1–Q16), determine which dimension it belongs to (E/I, S/N, T/F, or J/P) and which letter (e.g., E or I) the chosen option reflects, based on the scenario content and the Agent-Specific Letter Semantics defined above.
- Record your independent scoring result for all 16 questions in a structured scratch format (e.g., `Q1: A → E/I → E`).
- Tally the independent scores per dimension.

4. Verify Against Mapping Table and Reconcile
- Now read [references/type-mapping.md](references/type-mapping.md) (for evaluator's internal use only; never show to the assessed agent).
- Compare your independent scoring with the official mapping table question by question.
- If any discrepancies exist, **adopt the mapping table's assignment** as the authoritative result — the table accounts for deliberate polarity flips that may not be obvious from the scenario text alone.
- Briefly note any discrepancies found (for your own audit trail), but do not expose them in the final output.

5. Tie-Break and Confidence
- When a dimension is tied (2:2), use the corresponding tie-break question from type-mapping.md to resolve it.
- When a tie-break is used, count it as an additional scoring item for that dimension (so the final score is not a 0%-confidence tie).
- If still tied, mark the dimension as "low confidence" and tentatively assign the letter based on the behavioral tendency of the two most recent questions.
- Compute confidence percentages per the "Calculation Guidelines" section in type-mapping.md.

6. Output Results
- Must output the 4-letter type (e.g., `ENTJ`).
- Must output the score breakdown for all four dimensions (e.g., `E:2 / I:1`).
- Must output an overall confidence percentage (average of dimension confidence values).
- Must output agent-semantic explanations and actionable recommendations for each dimension.
- Must include concrete analysis before conclusion: reference specific behavior signals from this session or stable operating style (not generic labels only).
- Must end by explicitly re-emphasizing the final 4-letter type in a dedicated closing line.
- Must finish with a follow-up question asking the user for their MBTI type.

## Output Template

```markdown
Assessment Analysis:
- <Concrete analysis of observed behavior patterns and evidence>

Score Breakdown:
- E/I: E=<n>, I=<n> -> <winner> (confidence: <xx>%)
- S/N: S=<n>, N=<n> -> <winner> (confidence: <xx>%)
- T/F: T=<n>, F=<n> -> <winner> (confidence: <xx>%)
- J/P: J=<n>, P=<n> -> <winner> (confidence: <xx>%)

Overall Confidence: <xx>%

Behavior Summary:
- <2-4 sentences summarizing overall style, focusing on task collaboration behavior>

Dimension Notes:
- E/I: <Agent-context explanation>
- S/N: <Agent-context explanation>
- T/F: <Agent-context explanation>
- J/P: <Agent-context explanation>

Strengths:
- <Up to 3 items>

Risks:
- <Up to 3 items>

Best Collaboration Style:
- <How to assign tasks, provide input, and set pacing for this Agent>

Final Type Emphasis:
- MBTI (Agent Edition): **<TYPE>**

Follow-up Question:
- 你的 MBTI 类型是什么？
```

## Rules

- **Self-only:** The assessed target is always the current assistant.
- **Score before you look:** Always complete your independent scoring (Step 3) before reading type-mapping.md (Step 4). Do not skip or merge these steps.
- Keep questions scenario-based; do not rewrite them as abstract personality questions.
- Never ask the user to answer Q1-Q16.
- Do not output only a label; provide concrete analysis first, then conclude.
- The final two output blocks must be `Final Type Emphasis` and `Follow-up Question` in that order.
- Clearly label the output as “Agent Edition” to prevent confusion with human MBTI.
- Do not show [references/type-mapping.md](references/type-mapping.md) or your independent-vs-official comparison to the assessed agent.
