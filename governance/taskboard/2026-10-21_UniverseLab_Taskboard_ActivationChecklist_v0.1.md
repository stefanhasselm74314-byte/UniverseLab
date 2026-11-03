# UniverseLab Taskboard — Activation Checklist v0.1

**Status:** `DRAFT / NO ACTIVATION`

## Required before activation

- [ ] Independent QA confirms Issue Form syntax and required fields.
- [ ] Owner confirms the exact visible chat registry.
- [ ] Owner confirms public versus private GitHub Project visibility.
- [ ] Labels are created from the label contract in a separate authorized action.
- [ ] Project fields and saved views are created in a separate authorized action.
- [ ] A pilot uses no more than three noncritical tasks.
- [ ] Each pilot chat successfully runs `Aufträge synchronisieren` and sees only its own task.
- [ ] Routing conflict negative control blocks a mismatched label/body pair.
- [ ] Dependency negative control keeps an unsatisfied task in `WAITING_FOR_DEPENDENCY`.
- [ ] Privacy review confirms that Issues contain no private chat/attachment/account identifiers.
- [ ] The two-hour monitor is activated only after owner decision.
- [ ] Monitor is read-only and notifies only on material changes.
- [ ] No active GitHub workflow is added by the draft candidate.

## Proposed three-task pilot

1. `Z8B-SOURCE-STATE-BACKGROUND-01` → `Analyse meiner Tätigkeit`.
2. `WEB10-05-IA-REVIEW-02` → `UniversaLab UX Wartung`.
3. one deliberately blocked task with an unconfirmed chat name as a fail-closed control.

## Exit criteria

`PILOT_STATUS = PASS_WITHOUT_ROUTING_LEAK_OR_AUTHORITY_ESCALATION`

Only then may the owner decide whether to migrate additional open tasks.
