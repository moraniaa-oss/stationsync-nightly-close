"""Configuration and credential access for the hackathon build.

The API key is never stored in this project. Two sanctioned routes exist:

1. The registered Muse connector `custom.meta-model-api`. Helpers built
   on the custom-connector-setup skill import dynamic_credentials.py,
   which attaches an `hsurr:` surrogate to each request. Muse swaps in
   the real key only on an approved request to api.meta.ai.
2. A local fallback for standalone runs outside Muse: the
   MODEL_API_KEY environment variable. Never hard-code a key, and never
   commit one to this repository.

Live mode is guarded twice on purpose. The CLI needs --live, and the
environment needs HACKATHON_LIVE=1. Until the user's $150 hackathon
credits land (expected Wed Oct 28 2026), a live call would charge his
card, so the default path through this whole project is dry-run.
"""

import os
import sys

CONNECTOR_ID = "custom.meta-model-api"
BASE_URL = "https://api.meta.ai/v1"
ALLOWED_HOSTS = ["api.meta.ai"]
DEFAULT_MODEL = "muse-spark-1.1"

# Where the skill's surrogate helper lives. Importing it is optional: the
# build must still import and run its dry-run path on a bare machine.
_SKILL_BIN = "/opt/muse/skills/custom-connector-setup/bin"


def model_name():
    """The Meta model this build calls. Override with META_MODEL."""
    return os.environ.get("META_MODEL", DEFAULT_MODEL)


def live_requested(cli_flag):
    """True only when the caller passed --live AND the env guard is set."""
    return bool(cli_flag) and os.environ.get("HACKATHON_LIVE") == "1"


def live_block_reason(cli_flag):
    """Explain, in plain words, why a live run is refused."""
    if not cli_flag:
        return "no --live flag given"
    if os.environ.get("HACKATHON_LIVE") != "1":
        return "HACKATHON_LIVE is not set to 1 in the environment"
    return ""


def env_api_key():
    """Fallback key for standalone runs, or None. Never logged anywhere."""
    return os.environ.get("MODEL_API_KEY") or None


def attach_credential(request):
    """Attach the API credential to a urllib request.

    Prefers the connector surrogate from dynamic_credentials.py, which is
    the documented mechanism for the registered connection. Falls back to
    the MODEL_API_KEY environment variable as a bearer token. Raises a
    clear error when neither route is available.
    """
    if _SKILL_BIN not in sys.path:
        sys.path.insert(0, _SKILL_BIN)
    try:
        from dynamic_credentials import add_surrogate_to_request

        add_surrogate_to_request(request, CONNECTOR_ID, allowed_hosts=ALLOWED_HOSTS)
        return "connector surrogate"
    except Exception:
        key = env_api_key()
        if key:
            request.add_header("Authorization", "Bearer " + key)
            return "MODEL_API_KEY environment variable"
        raise RuntimeError(
            "No credential route available. Connect custom.meta-model-api "
            "in Muse, or set MODEL_API_KEY for a standalone run."
        )
