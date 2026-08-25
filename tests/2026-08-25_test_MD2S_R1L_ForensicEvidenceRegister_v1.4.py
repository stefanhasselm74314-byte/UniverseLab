#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'registry/2026-08-25_MD2S_R1L_ForensicEvidenceRegister_v1.4.json'
AUDIT = ROOT / 'recovery/2026-08-25_MD2S_R1L_RecoveryAudit_v2.0.md'
UUID_RE = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
LOCKED = {
    'official_MD2S_solver': 'NOT_AUTHORIZED',
    'PHYSICAL_BACKGROUND': 'NOT_ESTABLISHED',
    'K1-D': 'NOT_RELEASED',
    'K1-E': 'NOT_ADMISSIBLE',
    'physical_evidence_effect': 'NONE',
    'physical_gate_effect': 'NONE',
}


def main():
    raw = REG.read_text(encoding='utf-8')
    data = json.loads(raw)
    audit = AUDIT.read_text(encoding='utf-8')

    assert data['schema'] == 'universelab.md2s.r1l.forensic-evidence-register.v1'
    assert data['version'] == '1.4.0'
    assert data['status'] == 'PARTIALLY_UNBLOCKED_PRIMARY_FGKL_RECOVERED_BUT_SOURCE_IDENTICAL_TWO_JUNCTION_REPLAY_STILL_BLOCKED'
    assert data['governance'] == LOCKED

    bundle = data['recovery_bundle']
    assert bundle['classification'] == 'E9_RECOVERY_BUNDLE_BYTES_VERIFIED'
    assert bundle['size_bytes'] == 14884
    assert bundle['sha256'] == 'dbee345414409f29f6fee5cc161807fd3f8a2d4b337460d3cf9bb8a307c3dff9'
    assert bundle['zip_entry_count'] == 12
    assert bundle['internal_manifest_entries'] == 11
    assert bundle['internal_manifest_hashes_valid'] == 11
    assert bundle['internal_manifest_hashes_invalid'] == 0
    assert bundle['source_chat_title_for_B14K_B14L'] == 'Hyperzeit Projektstatus Update'
    assert bundle['recovery_workflow_chat_title'] == 'Kontoanalyse ChatGPT'
    assert bundle['private_conversation_identifiers_committed'] is False

    transcript = data['historical_transcript']
    assert transcript['classification'] == 'E10_VERIFIED_HISTORICAL_TRANSCRIPT_REPORT'
    assert transcript['official_export_source_surfaced'] is True
    assert transcript['B1.4K_message_report_recovered'] is True
    assert transcript['B1.4L_message_report_recovered'] is True
    assert transcript['private_conversation_identifiers_committed'] is False

    primary = data['primary_package_recovery']
    assert primary['B1.4K']['sha256'] == '9cf13cd51baaef94258fcfa1690036798977565482acf2709a69494b0ed6e648'
    assert primary['B1.4K']['internal_manifest_hashes_valid'] == 11
    assert primary['B1.4K']['internal_manifest_hashes_invalid'] == 0
    assert primary['B1.4K']['numeric_reproduction'] == 'PASS_SELECTED_PACKAGE_CLAIMS'
    assert primary['B1.4L']['sha256'] == 'd5faf820ca984b40a78bb643aec23885aae8f753733054fc65eff0a6366eca0b'
    assert primary['B1.4L']['internal_manifest_hashes_valid'] == 12
    assert primary['B1.4L']['internal_manifest_hashes_invalid'] == 0
    assert primary['B1.4L']['numeric_reproduction'] == 'PASS_SELECTED_PACKAGE_CLAIMS'

    iface = data['two_sided_interface']
    assert iface['classification'] == 'E5_MISSING_SURVIVING_ARCHIVE'
    assert iface['source_identical_historical_replay'] == 'STILL_BLOCKED'
    for field in ['A_prime_bulk','A_prime_cap','Lprime_over_L_bulk','Lprime_over_L_cap']:
        assert field in iface['required_historical_fields']

    policy = data['promotion_policy']
    assert policy['primary_package_recovery_implies_official_solver_authorization'] is False
    assert policy['primary_package_recovery_implies_physical_background'] is False
    assert policy['recovered_B14K_B14L_packages_close_source_identical_two_junction_replay'] is False
    assert policy['C1_or_rebuild_data_may_fill_historical_missing_fields'] is False

    assert 'PARTIALLY_UNBLOCKED_PRIMARY_FGKL_RECOVERED_BUT_SOURCE_IDENTICAL_TWO_JUNCTION_REPLAY_STILL_BLOCKED' in audit
    assert '9cf13cd51baaef94258fcfa1690036798977565482acf2709a69494b0ed6e648' in audit
    assert 'd5faf820ca984b40a78bb643aec23885aae8f753733054fc65eff0a6366eca0b' in audit
    assert 'SOURCE_IDENTICAL_HISTORICAL_TWO_JUNCTION_REPLAY = STILL_BLOCKED' in audit

    # Public-repository privacy guard: no UUID-shaped chat/message IDs.
    assert UUID_RE.search(raw) is None
    assert UUID_RE.search(audit) is None

    print('PASS_MD2S_R1L_FORENSIC_EVIDENCE_REGISTER_V1_4')


if __name__ == '__main__':
    main()
