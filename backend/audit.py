"""In-memory audit log — per the Prototype Plan's 'basic audit logs' security
minimum. A real deployment persists this in Postgres; in-memory is enough to
demo the audit trail tonight and resets each server restart, which is fine for
a review demo."""
import time

_LOG: list[dict] = []


def record(action: str, actor: str, details: dict | None = None) -> dict:
    entry = {
        "seq": len(_LOG) + 1,
        "timestamp": time.time(),
        "actor": actor,
        "action": action,
        "details": details or {},
    }
    _LOG.append(entry)
    return entry


def all_entries() -> list[dict]:
    return list(_LOG)
