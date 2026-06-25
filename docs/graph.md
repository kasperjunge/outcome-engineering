# Concept Graph

The Outcome Engineering graph connects product concepts by meaning, not just by process order.

## High-Level Graph

```mermaid
flowchart TD
  Vision[Product Vision]
  Strategy[Product Strategy]
  OKRs[OKR Hierarchy]
  Objective[Objective]
  KR[Key Result]
  Outcome[Outcome]

  OST[Opportunity Solution Tree]
  Opportunity[Opportunity]
  Solution[Solution]
  Assumption[Assumption / Risk]
  Experiment[Experiment]

  Evidence[Evidence]
  Learning[Learning]
  Decision[Product Decision]

  PRD[PRD]
  Story[User Story]
  AC[Acceptance Criteria]
  Task[Technical Task / Design]
  Code[Code]
  Test[Test]
  Release[Released Product]
  Observed[Observed Behavior]

  HumanDiscovery[Human User Discovery]
  QuantData[Quantitative Data]
  AnyBelief[Any Product Belief]

  Vision --> Strategy
  Strategy --> OKRs
  OKRs --> Objective
  Objective --> KR
  KR --> Outcome
  Outcome --> OST
  OST --> Opportunity
  Opportunity --> Solution
  Solution --> Assumption
  Assumption --> Experiment
  Experiment --> Evidence

  Vision -. is a belief .-> AnyBelief
  Strategy -. is a belief .-> AnyBelief
  Outcome -. is a belief .-> AnyBelief
  Opportunity -. is a belief .-> AnyBelief
  Solution -. is a belief .-> AnyBelief
  Assumption -. is a belief .-> AnyBelief
  Story -. is a belief .-> AnyBelief
  Code -. is a belief .-> AnyBelief
  AnyBelief -. can produce or require .-> Evidence

  HumanDiscovery --> Evidence
  QuantData --> Evidence

  Evidence --> Learning
  Learning --> Decision
  Decision --> PRD
  PRD --> Story
  Story --> AC
  AC --> Task
  Task --> Code
  Code --> Test
  Test --> Release
  Release --> Observed
  Observed --> HumanDiscovery
  Observed --> QuantData

  Learning -. updates .-> Strategy
  Learning -. updates .-> OKRs
  Learning -. updates .-> Outcome
  Learning -. updates .-> Opportunity
  Learning -. updates .-> Solution
  Learning -. updates .-> Assumption
  Learning -. updates .-> PRD
  Learning -. updates .-> Story
  Learning -. updates .-> Code
```

## Objective, Key Result, Outcome

Objective, key result, and outcome are related, but not the same.

```text
Objective = the qualitative direction
Key Result = the measurable proof of progress
Outcome = the actual change in user, customer, or business behavior/state
```

Example:

```text
Objective:
Make onboarding feel effortless for new teams.

Key Results:
- Increase activation rate from 38% to 55%.
- Reduce median time-to-first-value from 2 days to 30 minutes.
- Reduce onboarding-related support tickets by 40%.

Outcomes:
- New users complete setup without help.
- Teams invite coworkers during the first session.
- Users reach the first valuable moment faster.
```

A key result often measures an outcome. It is not itself the outcome.

## Edge Meanings

```text
Vision -> Strategy
Strategy chooses how to pursue the vision.

Strategy -> OKRs
OKRs express the current strategic focus.

Objective -> Key Result
Key results define how progress toward an objective is measured.

Key Result -> Outcome
Outcomes describe the real-world change that should move the key result.

Outcome -> OST
An opportunity solution tree explores how to create the outcome.

Opportunity -> Solution
Solutions are possible interventions for a discovered opportunity.

Solution -> Assumption
Assumptions are the beliefs that must be true for the solution to work.

Assumption -> Experiment
Experiments are designed to produce evidence about assumptions.

Evidence -> Learning
Evidence changes what the team believes.

Learning -> Decision
Decisions apply learning to the product graph.

Decision -> PRD
The PRD captures the chosen direction for delivery.

PRD -> User Story
Stories express the product behavior to build.

User Story -> Acceptance Criteria
Acceptance criteria define how the behavior is verified.

Acceptance Criteria -> Code
Code implements the accepted behavior.

Code -> Test
Tests verify implementation against expected behavior.
```

## Distributed Evidence

Evidence can attach anywhere in the graph. It should not be modeled as only post-release telemetry.

```mermaid
flowchart LR
  Belief[Any Product Belief]
  Evidence[Evidence]
  Learning[Learning]
  Update[Graph Update]

  Belief --> Evidence
  Evidence --> Learning
  Learning --> Update
  Update --> Belief
```

Examples of product beliefs:

- An opportunity is real.
- A solution is desirable.
- An assumption is risky.
- A prototype is understandable.
- A technical approach is feasible.
- A released change moved the outcome.
