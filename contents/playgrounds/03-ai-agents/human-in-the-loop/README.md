# Lesson 8 — Human-in-the-Loop

This playground introduces human oversight as an explicit authority boundary in an agent system.

The central idea is:

> The model can recommend or propose. Human approval grants authority for a specific action.

The main example is a simulated travel assistant. Read-only research may happen automatically, but a non-refundable hotel booking is represented as an `ActionProposal`, validated by host policy, paused for approval, and executed only if the exact reviewed proposal is approved.

No real booking, payment, email, or production change is performed.

## Run the notebook

From the repository's `contents/` course root, activate the shared course environment and start Jupyter:

```powershell
.venv\Scripts\Activate.ps1
jupyter lab
```

Open:

`playgrounds/03-ai-agents/human-in-the-loop/lesson-08-human-in-the-loop.ipynb`

The examples are deterministic and do not require network access or an API key.

## What to observe

Approval is not just a yes/no boolean. A useful production design answers:

- What exact action is being approved?
- Who is authorised to approve it?
- What happens if the action changes?
- How long does the approval remain valid?
- How is the run paused and resumed?
- What happens after denial or modification?
- What state must be revalidated before execution?

The notebook fingerprints the exact proposal to make the binding visible. In a real system you would also persist the checkpoint and approval record, verify approver identity/authority, record an audit trail, enforce expiry, and revalidate current state before executing the side effect.
