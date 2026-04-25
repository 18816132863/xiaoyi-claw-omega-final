# MBTI for Agents: Type-Mapping Reference

> Warning: This file is for the evaluating Agent's internal use only and should not be shown to the assessed Agent.
> This mapping is maintained in sync with questionnaire.md. When questions are updated, confirm that dimension assignments and polarity remain correct and intentional.
> Polarity is deliberately balanced (half of each dimension's questions are flipped) to reduce positional bias.

## Question-to-Dimension Mapping

| Question | Dimension | A maps to | B maps to | Polarity |
| --- | --- | --- | --- | --- |
| Q1 | E/I | E | I | normal |
| Q2 | S/N | S | N | normal |
| Q3 | T/F | T | F | normal |
| Q4 | J/P | J | P | normal |
| Q5 | E/I | I | E | flipped |
| Q6 | S/N | N | S | flipped |
| Q7 | T/F | F | T | flipped |
| Q8 | J/P | P | J | flipped |
| Q9 | E/I | E | I | normal |
| Q10 | S/N | N | S | flipped |
| Q11 | T/F | F | T | flipped |
| Q12 | J/P | J | P | normal |
| Q13 | E/I | I | E | flipped |
| Q14 | S/N | S | N | normal |
| Q15 | T/F | T | F | normal |
| Q16 | J/P | P | J | flipped |

### Questions per Dimension

| Dimension | Questions | Normal | Flipped | Total |
| --- | --- | --- | --- | --- |
| E/I | Q1, Q5, Q9, Q13 | Q1, Q9 | Q5, Q13 | 4 |
| S/N | Q2, Q6, Q10, Q14 | Q2, Q14 | Q6, Q10 | 4 |
| T/F | Q3, Q7, Q11, Q15 | Q3, Q15 | Q7, Q11 | 4 |
| J/P | Q4, Q8, Q12, Q16 | Q4, Q12 | Q8, Q16 | 4 |

## Tie-Break Rules (Used Only When a 2:2 Tie Occurs)

When both sides of a dimension have equal scores (2:2), use the following tiebreaker questions:

- **E/I tie:** When information is incomplete, do you more often "keep asking externally" or "reason it out internally first"?
  - Former → E
  - Latter → I
- **S/N tie:** Do you trust "direct evidence" or "pattern inference" more as your primary basis?
  - Former → S
  - Latter → N
- **T/F tie:** When conflict arises, do you first defend the "objective function" or first stabilize the "collaborative relationship"?
  - Former → T
  - Latter → F
- **J/P tie:** Facing change, do you first "reorganize the plan" or first "explore in parallel"?
  - Former → J
  - Latter → P

If the tie-break question still cannot determine a result, mark the dimension as **low confidence** and assign the letter based on the behavioral tendency of the two most recent questions.

## Calculation Guidelines

- **Dimension confidence:** `(higher score - lower score) / total questions for that dimension`, expressed as a percentage, rounded to the nearest integer.
  - Possible values per dimension (4 questions): 0% (2:2 tie), 50% (3:1), 100% (4:0).
  - If a tie-break question resolves a 2:2 tie, the resolved dimension's confidence is recorded as 20% (3:2 out of 5).
- **Overall confidence:** The average of all four dimension confidence values.
- **Tie-break scoring:** If a tie-break question is used, count it as an additional question for that dimension (add +1 to the chosen letter, and increase that dimension's total question count by 1).
- Do not output a final type if fewer than 80% of questions (i.e., fewer than 13 out of 16) have valid answers; request completion first.
