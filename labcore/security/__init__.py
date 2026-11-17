"""Security helpers (SEC-04 export escaping, SEC-07 API auth policy, etc.)."""

from labcore.security.api_auth_policy import (
    ARTEFACT_ID as API_AUTH_ARTEFACT_ID,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOWED_HEADERS,
    CORS_ALLOWED_METHODS,
    cors_policy_manifest,
    has_bearer_authorization,
    reject_cookie_without_bearer,
)
from labcore.security.formula_escape import (
    FORMULA_TRIGGER_PREFIXES,
    escape_formula_export_cell,
    is_formula_trigger,
)
from labcore.security.upload_guard import (
    ARTEFACT_ID as UPLOAD_GUARD_ARTEFACT_ID,
    XlsxUploadRejected,
    ensure_defused_xml_stdlib,
    inspect_xlsx_archive,
)

__all__ = [
    "API_AUTH_ARTEFACT_ID",
    "CORS_ALLOW_CREDENTIALS",
    "CORS_ALLOWED_HEADERS",
    "CORS_ALLOWED_METHODS",
    "FORMULA_TRIGGER_PREFIXES",
    "UPLOAD_GUARD_ARTEFACT_ID",
    "XlsxUploadRejected",
    "cors_policy_manifest",
    "ensure_defused_xml_stdlib",
    "escape_formula_export_cell",
    "has_bearer_authorization",
    "inspect_xlsx_archive",
    "is_formula_trigger",
    "reject_cookie_without_bearer",
]