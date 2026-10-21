#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

project = json.loads((ROOT / "registry/2026-10-21_UniverseLab_Taskboard_ProjectSchema_v0.1.json").read_text(encoding="utf-8"))
labels = json.loads((ROOT / "registry/2026-10-21_UniverseLab_Taskboard_LabelContract_v0.1.json").read_text(encoding="utf-8"))
chats = json.loads((ROOT / "registry/2026-10-21_UniverseLab_Taskboard_ChatRegistry_v0.1.json").read_text(encoding="utf-8"))
form = yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE/universelab_task.yml").read_text(encoding="utf-8"))
example = yaml.safe_load((ROOT / "governance/taskboard/examples/2026-10-21_UniverseLab_Taskboard_MonitorWorkflow_EXAMPLE_v0.1.yml").read_text(encoding="utf-8"))

errors: list[str] = []

expected_statuses = {"EINGANG","READY_FOR_TARGET_CHAT","IN_PROGRESS","WAITING_FOR_DEPENDENCY","REVIEW","BLOCKED","RETURNED_TO_MASTER","DONE","SUPERSEDED"}
status_field = next((f for f in project["project"]["fields"] if f["name"] == "Status"), None)
if not status_field or set(status_field["options"]) != expected_statuses:
    errors.append("Project status options mismatch")

slugs = [c["slug"] for c in chats["chats"]]
visible = [c["visible_name"] for c in chats["chats"]]
if len(slugs) != len(set(slugs)):
    errors.append("Duplicate chat slug")
if len(visible) != len(set(visible)):
    errors.append("Duplicate visible chat name")

label_names = [x["name"] for x in labels["labels"]]
if len(label_names) != len(set(label_names)):
    errors.append("Duplicate label")
for chat in chats["chats"]:
    if chat["machine_label"] not in label_names:
        errors.append(f"Missing chat label: {chat['machine_label']}")

required_ids = {"task_id","target_chat","source_chat","ownership","status","priority","source_state","dependencies","deliverable","return_to","instruction_download","blockers","next_step","firewall"}
form_ids = {item.get("id") for item in form.get("body", []) if item.get("id")}
missing = required_ids - form_ids
if missing:
    errors.append(f"Missing Issue Form IDs: {sorted(missing)}")

if project["activation"]["project_created"]:
    errors.append("Draft must not claim Project created")
if project["activation"]["monitor_created"]:
    errors.append("Draft must not claim monitor created")

perms = example.get("permissions", {})
if perms.get("issues") != "read" or perms.get("contents") != "read":
    errors.append("Example workflow is not read-only")

if errors:
    print("FAIL")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("PASS")
print(f"confirmed_draft_chats={len(chats['chats'])}")
print(f"declared_labels={len(labels['labels'])}")
print("project_created=false")
print("monitor_created=false")
