# UniverseLab — Standard „Aufträge synchronisieren“ v0.1

**TASK_ID:** `UL-TASKBOARD-01`  
**Status:** `DRAFT_NOT_ACTIVATED`

## Command

When Stefan writes `Aufträge synchronisieren` in an opened UniverseLab chat:

1. Determine the exact visible name of the current chat. If it is not confirmed, stop with `BLOCKED_CHAT_NAME_UNCONFIRMED`.
2. Resolve the machine label from the chat registry.
3. Search the repository `stefanhasselm74314-byte/UniverseLab` for open Issues containing both `ul-task` and the exact `chat-<slug>` label.
4. Read the Issue body and verify that `ZIELCHAT` exactly equals the visible current chat name.
5. If label and body disagree, do not execute. Report `BLOCKED_ROUTING_CONFLICT` to `Chat Überwachung Master`.
6. Display only tasks in `READY_FOR_TARGET_CHAT`, `IN_PROGRESS`, `WAITING_FOR_DEPENDENCY`, `REVIEW` or `BLOCKED`.
7. Group them as:
   - 🔵 own lead tasks;
   - 🟡 review/support tasks;
   - ⚪ information only.
8. Before starting a task, re-read its current source state and all dependencies. A historical SHA in the Issue is not assumed current.
9. Do not execute tasks belonging to another chat.
10. Do not change the Issue, labels or Project fields unless a separate write authorization exists.
11. Return results to the exact chat named in `RÜCKGABE AN`.

## Query pattern

```text
repo:stefanhasselm74314-byte/UniverseLab is:issue is:open label:ul-task label:chat-<slug>
```

## Local response format

```text
### 🔵 Eigene aktive Aufgaben dieses Chats

TASK_ID =
STATUS =
QUELLE / AUSGANGSSTAND =
ABHÄNGIGKEITEN =
LIEFEROBJEKT =
GENAU NÄCHSTER SCHRITT =
RÜCKGABE AN =

### 🟡 Mitwirkung / Review dieses Chats
...

### ⚪ Fremdaufträge / nur zur Kenntnis
Keine fremden Aufgaben ausführen.
```

## Firewalls

```text
physical_gate_effect     = NONE
physical_evidence_effect = NONE
canonical_effect         = NONE
merge_authorization      = NONE
deployment_authorization = NONE
solver_execution         = NONE
issue_write              = NOT_AUTHORIZED_BY_SYNC_COMMAND
```
