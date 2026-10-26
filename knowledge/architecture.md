# Architecture notes (Mermaid)

## Agent loop

```mermaid
stateDiagram-v2
    [*] --> Plan
    Plan --> Act: exposures + thresholds read
    Act --> Observe: breaches classified, repeats suppressed
    Observe --> Plan: ledger appended, summary built
    Observe --> [*]: operator stops the loop
```

## Data flow through the guard

```mermaid
flowchart LR
    Agent -->|SELECT via views| Auth[SQLite authorizer]
    Auth -->|allowed view| Views[Views]
    Auth -->|anything else| Deny[Denied]
    Views --> Tables[(Base tables)]
    Agent -->|append only| Ledger[(run_ledger / alert_log)]
```

## Checkpoint flow for a high breach

```mermaid
sequenceDiagram
    participant A as Agent
    participant G as Confirmation gate
    participant H as Named human
    A->>A: Detect high breach
    A->>A: Proposal status = awaiting_acknowledgement
    H->>G: Acknowledgement with full name
    G->>A: Acknowledged; proposal may be shown as ready
    Note over A: The agent still does not act;<br/>a human decides elsewhere.
```
