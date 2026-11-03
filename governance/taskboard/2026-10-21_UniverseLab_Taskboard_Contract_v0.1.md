# UniverseLab Taskboard Contract v0.1

**TASK_ID:** `UL-TASKBOARD-01`  
**Date:** `2026-10-21`  
**Classification:** `DRAFT TASK REGISTRY / NO ACTIVATION`  
**Basis main:** `312e767628f003494a51edf685cf679469e35f13`  
**Basis tree:** `d743643419d812f6f8e8f3830328a3a9d24ed5ed`  
**Repository:** `stefanhasselm74314-byte/UniverseLab`

## 1. Purpose

UniverseLab tasks are represented by one GitHub Issue per task. A GitHub Project named `UniverseLab — Aufgabenregister` may later provide filtered human-readable views. Until owner adoption and technical activation, this package is only a draft contract.

## 2. Source of truth

For an activated taskboard, the authoritative task record is the GitHub Issue body plus its current labels and Project fields. Chat memory, local files and summaries are supporting context only.

Each Issue must contain:

- stable `TASK_ID`;
- exact visible target chat name;
- exact visible source chat name;
- ownership and status;
- priority;
- bound source state;
- dependencies with required statuses;
- deliverable;
- exact return chat;
- instruction download/path;
- blocker;
- exact next step;
- unchanged governance firewall.

## 3. Routing contract

The exact visible chat name in the Issue body and the Project field `Zielchat (sichtbar)` is authoritative. A machine label `chat:<slug>` is only a filter aid. If label and visible name disagree, the task is `BLOCKED_ROUTING_CONFLICT`.

Unknown or unconfirmed visible chat names are fail-closed and may not be guessed.

## 4. Status machine

Allowed states:

`EINGANG → READY_FOR_TARGET_CHAT → IN_PROGRESS → REVIEW/WAITING_FOR_DEPENDENCY/BLOCKED → RETURNED_TO_MASTER → DONE`

`SUPERSEDED` is terminal. Reopening requires a new explicit disposition.

A dependency may promote a task from `WAITING_FOR_DEPENDENCY` to `READY_FOR_TARGET_CHAT` only when the required task status is explicitly present in the taskboard.

## 5. Pull synchronization

Existing ChatGPT sidebar chats are not persistent agents. They do not wake themselves. The command `Aufträge synchronisieren` instructs the opened chat to query GitHub for its exact target label and exact visible name, read only its own open tasks and present a local task summary.

No task is executed solely because it is present. Before work begins, the chat must re-read current sources, dependencies and firewalls.

## 6. Two-hour monitor

A future single central monitor may inspect open Issues every two hours and notify Stefan only about changes. It may not mutate Issues, open PRs, execute tasks, promote scientific status or write into other existing sidebar chats.

This draft does not activate a ChatGPT scheduled task and does not install an active GitHub Actions schedule.

## 7. GitHub Project schema

The proposed Project is not created by this PR. Its fields and saved views are specified in the machine-readable Project schema. Labels are likewise specified but not created by this PR.

## 8. Privacy and public repository boundary

Public Issues must not contain private chat URLs, attachment IDs, account-export metadata, personal email addresses, private file paths or other nonpublic identifiers. Instructions must point only to public repository artifacts or explicitly sanitized public attachments.

## 9. Firewalls

```text
physical_gate_effect     = NONE
physical_evidence_effect = NONE
canonical_effect         = NONE
merge_authorization      = NONE
deployment_authorization = NONE
solver_execution         = NONE
repository_write         = NONE_FROM_TASK_RECORD_ALONE
```

## 10. Activation gates

Before activation:

1. independent QA of Issue form, schemas, labels and exact visible chat names;
2. owner adoption of the Project name, fields, labels and monitor policy;
3. creation of labels and GitHub Project as an explicit separate action;
4. optional creation of one read-only scheduled monitor;
5. pilot with at most three tasks;
6. review of privacy and false-routing failure modes.

Until then:

`TASKBOARD_STATUS = DRAFT_NOT_ACTIVATED`.
