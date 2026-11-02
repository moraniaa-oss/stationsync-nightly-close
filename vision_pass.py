#!/usr/bin/env python3
"""Vision pass: Muse Spark reads a PHOTO of the crew close sheet.

The rest of the build feeds the extract stage structured text. Production
crews do not send text — they send a photo of a paper sheet. This pass
proves the live pipeline end to end from a photo:

  1. fixtures/sample_sheet.png (the fictional Sample Mart close sheet,
     rendered from fixtures/sample_night.json) is sent to the Meta Model
     API as an image.
  2. The six crew figures the model reads off the photo are compared,
     field by field, against the fixture's crew_sheet values.
  3. Those vision-read figures are then fed through the real pipeline
     (extract shape -> reconcile -> fraud_scan -> report) to show the
     close still ties from photo-read numbers alone.

Guarded like the rest of the build: this script refuses to call the API
unless HACKATHON_LIVE=1 is set in the environment. The credential is
attached only through nightly_close.config.attach_credential, and
redirects are refused (extract.NoRedirect), exactly as in extract_live.

Fictional data only. Nothing here ever touches a real store.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nightly_close import config, extract, fraud_scan, intake, reconcile, report

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, "fixtures", "sample_night.json")
SHEET_PNG = os.path.join(HERE, "fixtures", "sample_sheet.png")

# Vision JSON key -> fact key the pipeline expects.
FIELD_MAP = {
    "cash_counted": "crew_cash_counted",
    "card_batch_total": "crew_card_batch",
    "lottery_online_sales": "crew_lottery_online",
    "lottery_instant_sales": "crew_lottery_instant",
    "lottery_cashes": "crew_lottery_cashes",
    "fuel_totalizer_dollars": "crew_fuel_totalizer",
}

PROMPT = (
    "This is a photo of a convenience store crew close sheet. Extract "
    "the closing figures written on it. Reply with JSON only, using "
    "string values for money (digits and a decimal point, no dollar "
    "signs, no commas), with keys: cash_counted, card_batch_total, "
    "lottery_online_sales, lottery_instant_sales, lottery_cashes, "
    "fuel_totalizer_dollars."
)


class ApiError(Exception):
    """An API call failed; status is None for a network-level failure."""

    def __init__(self, status, body):
        super().__init__("HTTP %s: %s" % (status, body))
        self.status = status
        self.body = body


def _post(url, payload, extra_headers=None):
    """POST JSON with the connector credential; redirects refused."""
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    config.attach_credential(request)
    opener = urllib.request.build_opener(extract.NoRedirect())
    try:
        with opener.open(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ApiError(exc.code, exc.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        raise ApiError(None, str(exc))


def _transient(err):
    return err.status is None or err.status == 429 or (
        err.status is not None and 500 <= err.status < 600
    )


def read_sheet_openai(image_b64):
    """OpenAI chat format: text part + image_url data-URI part."""
    payload = {
        "model": config.model_name(),
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64," + image_b64
                        },
                    },
                ],
            }
        ],
    }
    result = _post(config.BASE_URL + "/chat/completions", payload)
    return result["choices"][0]["message"]["content"]


def read_sheet_anthropic(image_b64):
    """Fallback: Anthropic messages format with a base64 image block."""
    payload = {
        "model": config.model_name(),
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_b64,
                        },
                    },
                ],
            }
        ],
    }
    result = _post(
        config.BASE_URL + "/messages",
        payload,
        extra_headers={"anthropic-version": "2023-06-01"},
    )
    for block in result["content"]:
        if block.get("type") == "text":
            return block["text"]
    raise RuntimeError("no text block in Anthropic response: %r" % (result,))


def read_sheet(image_b64):
    """Read the sheet, with the build's retry/fallback discipline.

    Returns (raw_reply_text, format_used). Transient failures retry once.
    A 400 (the OpenAI vision format being rejected) falls back to the
    Anthropic image format exactly once. 401/403 stop immediately.
    """
    try:
        return read_sheet_openai(image_b64), "OpenAI chat/completions image_url"
    except ApiError as err:
        if err.status in (401, 403):
            raise
        if _transient(err):
            print("transient API error (%s); retrying once..." % err)
            return read_sheet_openai(image_b64), "OpenAI image_url (after retry)"
        if err.status == 400:
            print(
                "OpenAI image_url format rejected (HTTP 400): %s" % err.body
            )
            print("falling back to the Anthropic /v1/messages image format...")
            return read_sheet_anthropic(image_b64), "Anthropic messages image"
        raise


def _parse_json_reply(text):
    """Parse the model's JSON reply, tolerating a code-fence wrapper."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


def main():
    if os.environ.get("HACKATHON_LIVE") != "1":
        print(
            "Vision pass refused: HACKATHON_LIVE is not set to 1 in the "
            "environment. No API call was made."
        )
        return 2

    bundle = intake.load_bundle(FIXTURE)
    truth = bundle["crew_sheet"]

    with open(SHEET_PNG, "rb") as handle:
        image_b64 = base64.b64encode(handle.read()).decode("ascii")

    print("Vision pass — model: %s" % config.model_name())
    print("Sheet photo: %s" % SHEET_PNG)
    print("")

    try:
        raw_reply, fmt_used = read_sheet(image_b64)
    except ApiError as err:
        print("API ERROR — status: %s" % err.status)
        print("Response body: %s" % err.body)
        return 1
    print("API format that worked: %s" % fmt_used)
    print("Raw model reply: %s" % raw_reply)
    print("")

    vision = _parse_json_reply(raw_reply)

    print("%-24s %-14s %-14s %s" % ("FIELD", "ON SHEET", "VISION READ", "RESULT"))
    all_match = True
    for key in FIELD_MAP:
        sheet_val = extract.money(truth[key])
        vision_val = extract.money(vision[key])
        ok = sheet_val == vision_val
        all_match = all_match and ok
        print(
            "%-24s %-14s %-14s %s"
            % (key, sheet_val, vision_val, "MATCH" if ok else "MISMATCH")
        )
    print("")
    print(
        "Per-field result: %s"
        % ("all 6 figures read exactly" if all_match else "MISMATCHES PRESENT")
    )
    print("")

    # Prove the point end to end: the vision-read figures drive the close.
    facts = extract.extract(bundle)
    for vision_key, fact_key in FIELD_MAP.items():
        facts[fact_key] = extract.money(vision[vision_key])
    checks = reconcile.reconcile(facts)
    findings = fraud_scan.scan(facts["journal"])
    tied = sum(1 for c in checks if c.get("ok"))
    print(
        "Vision-fed close: %d of %d checks tied, over/short %s"
        % (tied, len(checks), reconcile.over_short(checks))
    )
    print("")
    print(report.render(facts, checks, findings))
    return 0 if all_match and tied == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
