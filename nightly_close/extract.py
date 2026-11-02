"""Stage 2, extract: turn raw night material into clean money facts.

Every figure becomes a Decimal built from its string form, so no float
ever touches money anywhere in this pipeline. That is the whole trick
behind tying to the penny.

Dry-run extraction reads the structured bundle directly. The crew sheet
in the bundle stands in for the photo a crew would send in production.

Live extraction (extract_live) is the one place the Meta Model API is
called: Muse Spark reads the crew sheet text and returns the same fact
shape. It is implemented for the live phase and is never invoked by the
dry-run path.
"""

import json
import urllib.request
from decimal import Decimal

from . import config


def money(value):
    """Parse a money figure into a Decimal, exactly as written."""
    return Decimal(str(value))


def _fuel_total(pos):
    return money(pos["fuel"]["total_dollars"])


def extract(bundle):
    """Normalize a night bundle into the fact dict the later stages share."""
    crew = bundle["crew_sheet"]
    pos = bundle["pos_closing"]
    tenders = pos["tenders"]
    departments = {name: money(v) for name, v in pos["departments"].items()}

    lottery_sales = money(pos["lottery_online_sales"]) + money(pos["lottery_instant_sales"])
    total_rung = (
        money(pos["merchandise_sales"])
        + money(pos["sales_tax"])
        + lottery_sales
        + _fuel_total(pos)
    )

    facts = {
        "store_name": bundle["store"]["name"],
        "business_date": bundle["store"]["business_date"],
        "departments": departments,
        "merchandise_sales": money(pos["merchandise_sales"]),
        "sales_tax": money(pos["sales_tax"]),
        "lottery_online_pos": money(pos["lottery_online_sales"]),
        "lottery_instant_pos": money(pos["lottery_instant_sales"]),
        "lottery_cashes_pos": money(pos["lottery_cashes"]),
        "fuel_dollars_pos": _fuel_total(pos),
        "total_rung": total_rung,
        "tender_card": money(tenders["card"]),
        "tender_ebt": money(tenders["ebt"]),
        "tender_cash": money(tenders["cash"]),
        "crew_cash_counted": money(crew["cash_counted"]),
        "crew_card_batch": money(crew["card_batch_total"]),
        "crew_lottery_online": money(crew["lottery_online_sales"]),
        "crew_lottery_instant": money(crew["lottery_instant_sales"]),
        "crew_lottery_cashes": money(crew["lottery_cashes"]),
        "crew_fuel_totalizer": money(crew["fuel_totalizer_dollars"]),
        "journal": bundle["journal"],
    }
    return facts


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so an authenticated request never leaks onward."""

    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def extract_live(sheet_text):
    """Read a crew sheet with Muse Spark and return extracted facts.

    Live phase only. Sends the sheet text to POST /v1/chat/completions on
    the Meta Model API and parses the JSON the model returns. The caller
    (agent.run) reaches this only when --live and HACKATHON_LIVE=1 are
    both set. The dry-run path never calls it.
    """
    prompt = (
        "Extract the closing figures from this convenience store crew "
        "sheet. Reply with JSON only, using string values for money, "
        "with keys: cash_counted, card_batch_total, lottery_online_sales, "
        "lottery_instant_sales, lottery_cashes, fuel_totalizer_dollars.\n\n"
        + sheet_text
    )
    payload = {
        "model": config.model_name(),
        "messages": [{"role": "user", "content": prompt}],
    }
    request = urllib.request.Request(
        config.BASE_URL + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    config.attach_credential(request)
    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    content = result["choices"][0]["message"]["content"]
    return json.loads(content)
