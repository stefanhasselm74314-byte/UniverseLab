#!/usr/bin/env python3
"""Canonical JSON and strict Ed25519 verification core. Verification only."""
from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

CONTRACT_ID = "ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.1"
PROFILE_ID = "UL-ED25519-CANONICAL-JSON-v1"
DOMAIN_SEPARATOR = b"UNIVERSELAB-AUTHORITY-ATTESTATION-V1\x00"
RUN_ID = "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4"
TARGET_DIGEST = "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
RUN_PAYLOAD_DIGEST = "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
KEY_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._:-]{2,127}$")
AUTHORITY_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._:-]{2,127}$")
MAX_SAFE_INTEGER = (1 << 53) - 1


class AuthorityVerificationError(RuntimeError):
    """Fail-closed verifier exception with a stable machine-readable code."""

    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}


@dataclass(frozen=True)
class VerificationResult:
    status: str
    artifact_type: str
    authority_id: str
    key_id: str
    signed_bytes_sha256: str
    synthetic_control_only: bool
    operative_authorization_allowed: bool
    physical_evidence_effect: str = "NONE"

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "universelab.authority-attestation-verification-result.v0.1",
            "status": self.status,
            "artifact_type": self.artifact_type,
            "authority_id": self.authority_id,
            "key_id": self.key_id,
            "signed_bytes_sha256": self.signed_bytes_sha256,
            "synthetic_control_only": self.synthetic_control_only,
            "operative_authorization_allowed": self.operative_authorization_allowed,
            "backend_imported": False,
            "solver_executed": False,
            "physical_evidence_effect": self.physical_evidence_effect,
        }


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise AuthorityVerificationError("DUPLICATE_JSON_KEY", f"duplicate JSON key: {key!r}")
        out[key] = value
    return out


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except AuthorityVerificationError:
        raise
    except json.JSONDecodeError as exc:
        raise AuthorityVerificationError("INVALID_JSON", str(exc)) from exc


def load_json(path: str | Path) -> Any:
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise AuthorityVerificationError("UTF8_BOM_FORBIDDEN", f"UTF-8 BOM forbidden: {path}")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise AuthorityVerificationError("INVALID_UTF8", f"invalid UTF-8: {path}") from exc
    return strict_json_loads(text)


def _validate_string(value: str, path: str) -> None:
    for character in value:
        codepoint = ord(character)
        if 0xD800 <= codepoint <= 0xDFFF:
            raise AuthorityVerificationError("UNICODE_SURROGATE_FORBIDDEN", f"surrogate at {path}")


def _validate_canonical_value(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if abs(value) > MAX_SAFE_INTEGER:
            raise AuthorityVerificationError(
                "INTEGER_OUTSIDE_CANONICAL_RANGE",
                f"integer outside ±(2^53-1) at {path}",
                {"value": value},
            )
        return
    if isinstance(value, float):
        raise AuthorityVerificationError("FLOAT_FORBIDDEN_IN_SIGNED_PAYLOAD", f"float at {path}")
    if isinstance(value, str):
        _validate_string(value, path)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_canonical_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise AuthorityVerificationError("NONSTRING_JSON_KEY", f"non-string key at {path}")
            _validate_string(key, f"{path}.<key>")
            _validate_canonical_value(item, f"{path}.{key}")
        return
    raise AuthorityVerificationError("UNSUPPORTED_CANONICAL_TYPE", f"unsupported type at {path}: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    """UniverseLab canonical JSON subset v1.

    The signed subset deliberately forbids floating-point numbers, duplicate
    keys, BOMs, non-UTF-8 input and integers outside the ECMAScript-safe range.
    This avoids cross-runtime numeric canonicalization ambiguity.
    """

    _validate_canonical_value(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise AuthorityVerificationError("INVALID_UTC_TIMESTAMP", f"{field} must be an RFC3339 UTC string ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityVerificationError("INVALID_UTC_TIMESTAMP", f"invalid {field}: {value!r}") from exc
    if parsed.tzinfo is None:
        raise AuthorityVerificationError("INVALID_UTC_TIMESTAMP", f"{field} must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def require_hex64(value: Any, field: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise AuthorityVerificationError("INVALID_SHA256", f"{field} must be 64 lowercase hexadecimal characters")
    return value


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AuthorityVerificationError("MISSING_OR_INVALID_OBJECT", f"{field} must be an object")
    return value


def require_string(value: Any, field: str, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value:
        raise AuthorityVerificationError("MISSING_OR_INVALID_STRING", f"{field} must be a non-empty string")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise AuthorityVerificationError("INVALID_IDENTIFIER", f"invalid {field}: {value!r}")
    return value


# Strict Ed25519 verification, RFC 8032, pure Python/std-lib. No signing API.
_Q = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _Q - 2, _Q)) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)
_IDENTITY = (0, 1, 1, 0)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(_D * y * y + 1, _Q - 2, _Q) % _Q
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = x * _I % _Q
    if (x * x - xx) % _Q != 0:
        raise AuthorityVerificationError("INVALID_ED25519_POINT", "point has no square-root x coordinate")
    return x


_BY = 4 * pow(5, _Q - 2, _Q) % _Q
_BX = _xrecover(_BY)
if _BX & 1:
    _BX = _Q - _BX
_BASE = (_BX, _BY, 1, _BX * _BY % _Q)


def _point_add(p: tuple[int, int, int, int], q: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % _Q
    b = (y1 + x1) * (y2 + x2) % _Q
    c = 2 * _D * t1 * t2 % _Q
    d = 2 * z1 * z2 % _Q
    e = (b - a) % _Q
    f = (d - c) % _Q
    g = (d + c) % _Q
    h = (b + a) % _Q
    return e * f % _Q, g * h % _Q, f * g % _Q, e * h % _Q


def _point_double(p: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x, y, z, _ = p
    a = x * x % _Q
    b = y * y % _Q
    c = 2 * z * z % _Q
    d = -a % _Q
    e = ((x + y) * (x + y) - a - b) % _Q
    g = (d + b) % _Q
    f = (g - c) % _Q
    h = (d - b) % _Q
    return e * f % _Q, g * h % _Q, f * g % _Q, e * h % _Q


def _scalar_mult(point: tuple[int, int, int, int], scalar: int) -> tuple[int, int, int, int]:
    result = _IDENTITY
    addend = point
    n = scalar
    while n:
        if n & 1:
            result = _point_add(result, addend)
        addend = _point_double(addend)
        n >>= 1
    return result


def _affine(point: tuple[int, int, int, int]) -> tuple[int, int]:
    x, y, z, _ = point
    inv_z = pow(z, _Q - 2, _Q)
    return x * inv_z % _Q, y * inv_z % _Q


def _point_equal(p: tuple[int, int, int, int], q: tuple[int, int, int, int]) -> bool:
    return (p[0] * q[2] - q[0] * p[2]) % _Q == 0 and (p[1] * q[2] - q[1] * p[2]) % _Q == 0


def _encode_point(point: tuple[int, int, int, int]) -> bytes:
    x, y = _affine(point)
    encoded = y | ((x & 1) << 255)
    return encoded.to_bytes(32, "little")


def _decode_point(encoded: bytes) -> tuple[int, int, int, int]:
    if len(encoded) != 32:
        raise AuthorityVerificationError("INVALID_ED25519_POINT_LENGTH", "Ed25519 point must be 32 bytes")
    raw = int.from_bytes(encoded, "little")
    sign = raw >> 255
    y = raw & ((1 << 255) - 1)
    if y >= _Q:
        raise AuthorityVerificationError("NONCANONICAL_ED25519_POINT", "encoded y is not canonical")
    x = _xrecover(y)
    if (x & 1) != sign:
        x = _Q - x
    if x == 0 and sign == 1:
        raise AuthorityVerificationError("NONCANONICAL_ED25519_POINT", "negative zero x encoding")
    point = (x, y, 1, x * y % _Q)
    if _encode_point(point) != encoded:
        raise AuthorityVerificationError("NONCANONICAL_ED25519_POINT", "point encoding is not canonical")
    # Strict prime-order subgroup and identity rejection.
    if _point_equal(point, _IDENTITY) or not _point_equal(_scalar_mult(point, _L), _IDENTITY):
        raise AuthorityVerificationError("INVALID_ED25519_SUBGROUP", "point is not a non-identity prime-order point")
    return point


def ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    if len(public_key) != 32 or len(signature) != 64:
        return False
    try:
        a_point = _decode_point(public_key)
        r_encoded = signature[:32]
        r_point = _decode_point(r_encoded)
        scalar_s = int.from_bytes(signature[32:], "little")
        if scalar_s >= _L:
            return False
        challenge = int.from_bytes(hashlib.sha512(r_encoded + public_key + message).digest(), "little") % _L
        lhs = _scalar_mult(_BASE, scalar_s)
        rhs = _point_add(r_point, _scalar_mult(a_point, challenge))
        return _point_equal(lhs, rhs)
    except AuthorityVerificationError:
        return False


