# UniverseLab Taskboard — Two-hour Monitor Prompt v0.1

**Status:** `DRAFT_NOT_SCHEDULED`  
**Recommended timing:** every two hours  
**Mode:** read-only condition watch

## Prompt

Check the GitHub repository `stefanhasselm74314-byte/UniverseLab` for all open Issues carrying the label `ul-task`.

Notify Stefan only when at least one of the following changed since the previous run:

- a new task was created;
- `ZIELCHAT` changed;
- ownership changed;
- status changed;
- a dependency became satisfied or unsatisfied;
- a task became blocked or unblocked;
- a return to `Chat Überwachung Master` is pending;
- the visible target chat name is missing or conflicts with the machine label;
- required firewall fields are missing.

Group the report by the exact visible target chat name. For each changed task show:

```text
TASK_ID
visible target chat
ownership
old status → new status
changed dependency/blocker
exact next step
return chat
```

If nothing materially changed, do not notify.

Do not modify Issues, labels, Projects, files, branches or pull requests. Do not execute any task. Do not infer merge, deployment, canonical, solver or physical authority.

## Proposed schedule

```text
RRULE:FREQ=HOURLY;INTERVAL=2
```

## Activation state

```text
scheduled_task_created = false
monitor_active = false
owner_adoption = OPEN
```
