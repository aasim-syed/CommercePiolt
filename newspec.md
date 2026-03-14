**CommercePilot Demo Spec**

CommercePilot is a conversational payments operations assistant for merchants. In this demo, a user interacts in natural language to perform payment operations through a guided operator console. The system combines LLM-based intent understanding, session memory, payment-provider orchestration, and event-style status handling in one workflow.

**Live Demo Scope**
1. Create a payment link through Pine Labs / Plural integration.
2. Track payment lifecycle through session-linked payment state.
3. Show merchant balance and system readiness through the operator dashboard.
4. Demonstrate manual event-driven status transitions for reliable hackathon playback.

**Judge Scenario**
A small merchant wants to recover operational time lost in dashboards, support panels, and payment follow-ups.

Flow:
1. Operator asks: “Create payment link for 1200.”
2. CommercePilot generates a live payment link and stores the session-linked payment reference.
3. Operator moves to system controls and simulates a status event like `SUCCESS` or `FAILED`.
4. Operator asks: “Check payment status.”
5. CommercePilot responds using the tracked payment context and updated state.
6. Operator can inspect readiness, provider mode, and latest payment metadata in the system panel.

**Why It’s Novel**
This is not just a chatbot over payments APIs. The novelty is the combination of:
- natural-language merchant operations
- session-aware payment memory
- provider-adapter architecture
- event-driven state updates
- operator-friendly control panel for visibility and recovery

Instead of making merchants jump across tools, CommercePilot turns payment operations into a conversational control surface.

**Proof of Novelty**
- The assistant remembers payment context across turns.
- Payment workflows are normalized behind one backend contract, so providers can be swapped without changing the UI.
- The system combines chat, orchestration, and event-state updates in one merchant workflow.
- The dashboard makes integration state visible, which turns partial infrastructure into an operable product surface rather than a black box.

**Next-Phase Vision**
After the demo, CommercePilot expands into:
- Payment Mood Engine
- Merchant Voice Ledger
- Dead Cart Resurrection
- Split-Pay Arbitration

That gives the product both:
- a focused live MVP
- a larger defensible commerce-operations vision