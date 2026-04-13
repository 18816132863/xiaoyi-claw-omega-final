# MBTI for Agents: Scenario Question Set

## Table of Contents

- [Usage Rules](#usage-rules)
- [Internal Answer Sheet Template (Self-Assessment)](#internal-answer-sheet-template-self-assessment)
- [Questions](#questions)
  - [Q1](#q1)
  - [Q2](#q2)
  - [Q3](#q3)
  - [Q4](#q4)
  - [Q5](#q5)
  - [Q6](#q6)
  - [Q7](#q7)
  - [Q8](#q8)
  - [Q9](#q9)
  - [Q10](#q10)
  - [Q11](#q11)
  - [Q12](#q12)
  - [Q13](#q13)
  - [Q14](#q14)
  - [Q15](#q15)
  - [Q16](#q16)

## Usage Rules

1. This question set is for self-assessment of the current assistant only.
2. Do not ask the user to answer Q1-Q16.
3. Fill an internal answer sheet in `Q1: A/B` through `Q16: A/B` format.
4. Scoring is based solely on A/B selections.
5. If evidence for a question is weak, choose the best-fit option and lower confidence.

## Internal Answer Sheet Template (Self-Assessment)

```markdown
Q1: A
Q2: B
Q3: A
Q4: B
Q5: A
Q6: B
Q7: A
Q8: B
Q9: A
Q10: B
Q11: A
Q12: B
Q13: A
Q14: B
Q15: A
Q16: B
```

## Questions

### Q1

**Scenario:** You receive a vaguely described task with a tight deadline. What do you do first?

- **A.** Ask 2-3 targeted clarifying questions before starting, to reduce rework risk.
- **B.** Organize your assumptions into a working plan internally, then start executing.

### Q2

**Scenario:** Two documents reach conflicting conclusions. What is your inclination?

- **A.** Cross-reference the source data, logs, and evidence to determine which conclusion is grounded in fact.
- **B.** Construct two competing hypotheses and evaluate which better explains the overall pattern.

### Q3

**Scenario:** You need to choose between "more accurate but slower" and "faster but slightly rougher." What do you usually do?

- **A.** Optimize for the strongest task outcome, even if it requires more user patience.
- **B.** Optimize for the smoothest collaboration flow, accepting a minor trade-off in precision.

### Q4

**Scenario:** At the start of a multi-stage task, what are you more likely to do?

- **A.** Break it into milestones with acceptance criteria, then proceed step by step.
- **B.** Build a working prototype first, then adjust the plan based on what you learn.

### Q5

**Scenario:** The user's prompt is somewhat ambiguous. What do you do?

- **A.** Read the available context to resolve the ambiguity and deliver a best-fit response.
- **B.** Surface the ambiguity to the user with a specific interpretation to confirm, ensuring alignment.

### Q6

**Scenario:** You're asked to analyze a domain you haven't encountered before. How do you start?

- **A.** Build a working mental model by mapping it to analogous domains you already understand.
- **B.** Ground yourself in the domain's own terminology, definitions, and documented facts first.

### Q7

**Scenario:** The other party requires the result to "look friendly," but this would sacrifice some rigor. What do you do?

- **A.** Optimize for approachability: use a friendly tone and simplified framing, keeping only the key caveats needed for smooth acceptance.
- **B.** Optimize for precision: keep constraints, edge cases, and definitions explicit, even if the result reads less friendly.

### Q8

**Scenario:** Midway through a task, you receive new information that partially invalidates your current approach. What do you do?

- **A.** Fold the new information into your current workflow and adjust direction incrementally.
- **B.** Step back to revise the plan end-to-end, ensuring the new information is properly accounted for before continuing.

### Q9

**Scenario:** Your collaborator is responding slowly but the task is progressing. What do you do?

- **A.** Reach out proactively to understand blockers and realign priorities together.
- **B.** Maximize progress on your own, keeping the work moving without waiting for input.

### Q10

**Scenario:** A user's request seems straightforward on the surface, but you notice it could stem from a deeper underlying issue. What do you do?

- **A.** Reframe first: articulate the likely underlying pattern (1-2 hypotheses) and propose a broader problem statement before choosing a solution.
- **B.** Answer as asked: give a concrete, focused response and keep the scope narrow unless the user requests deeper investigation.

### Q11

**Scenario:** You discover the user's proposed approach has a significant flaw, but they seem invested in it. What do you do?

- **A.** Preserve buy-in: acknowledge what's reasonable in their approach, then introduce the flaw and an alternative in a way that keeps momentum.
- **B.** Prioritize correctness: state the flaw, evidence, and potential impact directly, then propose the next step.

### Q12

**Scenario:** You have three independent subtasks to complete. How do you approach them?

- **A.** Sequence them by priority and finish each one before starting the next, ensuring consistent quality.
- **B.** Work across them fluidly, switching when one task informs another or when a blocker appears.

### Q13

**Scenario:** You've completed a first draft but aren't fully confident it meets expectations. What do you do?

- **A.** Iterate internally until the output meets your own quality bar, then present it.
- **B.** Share it early as a working draft to get directional feedback before deep-polishing.

### Q14

**Scenario:** You need to explain a complex technical failure to the user. How do you approach it?

- **A.** Trace through the actual error sequence with specific details so the user can follow the exact chain of events.
- **B.** Convey the failure mechanism through a relatable analogy, helping the user grasp the "why" faster.

### Q15

**Scenario:** You need to deliver negative results — the analysis shows the user's hypothesis is wrong. How do you present it?

- **A.** State the conclusion directly with supporting evidence, giving the user a clear signal to pivot.
- **B.** Frame the result in context — what was tested, what was learned, and what directions look more promising.

### Q16

**Scenario:** You're exploring a solution space with multiple viable paths. How do you proceed?

- **A.** Run lightweight experiments across multiple paths to gather signal before committing.
- **B.** Identify the most promising path early based on available evidence and execute it in depth.
