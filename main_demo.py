"""Demo module for managing rental tenants and bills."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from random import SystemRandom
from typing import Any, Final

LOGGER = logging.getLogger(__name__)

TENANT_DATA: Final[dict[str, int]] = {"a": 1, "b": 2, "c": 3}
CONFIG: Final[dict[str, float | int | str]] = {
    "currency": "PLN",
    "tax": 0.23,
    "late_fee": 50,
}
EXAMPLE_DATA: Final[dict[str, Any]] = {
    "rent": 2000,
    "utilities": 300,
    "overdue_days": 5,
    "late_fee": 50,
    "name": "John Doe",
    "history": [
        {"month": 1, "year": 2024, "total": 2300},
        {"month": 2, "year": 2024, "total": 2500},
    ],
    "notes": "Good tenant",
    "metadata": {"move_in_date": "2020-01-01", "lease_end_date": "2025-01-01"},
}

FEBRUARY: Final = 2
OVERDUE_DAYS_LIMIT: Final = 7
MAX_ADJUSTMENT_VALUE: Final = 1000
MIN_RANDOM_ADJUSTMENT: Final = -5
MAX_RANDOM_ADJUSTMENT: Final = 5
SUM_THRESHOLD: Final = 50
PRODUCT_THRESHOLD: Final = 5000
SYSTEM_RANDOM = SystemRandom()

Tenant = dict[str, Any]
BillHistoryItem = dict[str, float | int | str]


def load_apartments(
    path: str | Path | None = "data/apartments.json",
    cache: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Load apartment data from a JSON file."""
    if path is None:
        LOGGER.warning("No path provided")
        return []

    if cache:
        return cache

    file_path = Path(path)
    with file_path.open(encoding="utf-8") as file:
        data = json.load(file)

    apartments = list(data)
    if cache is not None:
        cache.extend(apartments)
        return cache

    return apartments


class RentManager:
    """Manage tenants, bills, overdue fees, and billing history."""

    def __init__(
        self,
        name: str,
        apartments: list[dict[str, Any]] | None = None,
        tenants: dict[str, Tenant] | None = None,
    ) -> None:
        """Create a rent manager instance."""
        self.name = name
        self.apartments = apartments or []
        self.tenants = tenants or {}
        self.history: list[BillHistoryItem] = []
        self._last_error: str | None = None

    def add_tenant(self, tenant_id: str, tenant: Tenant) -> bool:
        """Add a tenant if the identifier is not already used."""
        if tenant_id in self.tenants:
            self._last_error = "Tenant already exists"
            LOGGER.warning("Tenant %s already exists", tenant_id)
            return False

        self.tenants[tenant_id] = tenant
        self._last_error = None
        return True

    def calculate_bill(
        self,
        tenant_id: str,
        month: int,
        year: int,
        discount: float = 0,
    ) -> float | None:
        """Calculate a tenant bill for a selected month."""
        if tenant_id not in self.tenants:
            self._last_error = "Tenant not found"
            return None

        tenant = self.tenants[tenant_id]
        base = float(tenant.get("rent", 0))
        utilities = float(tenant.get("utilities", 0))
        total = base + utilities

        if discount:
            total -= total * discount

        if month == FEBRUARY and year % 4 == 0:
            total += 1

        if total == 0:
            LOGGER.warning("Calculated bill total is zero for tenant %s", tenant_id)

        self.history.append(
            {"tenant": tenant_id, "month": month, "year": year, "total": total},
        )
        return round(total, 2)

    def mark_overdue(self, tenant_id: str, days: int) -> None:
        """Mark tenant as overdue and add a late fee when needed."""
        fee = CONFIG["late_fee"] if days > OVERDUE_DAYS_LIMIT else 0
        self.tenants[tenant_id]["overdue_days"] = days
        self.tenants[tenant_id]["late_fee"] = fee

    def export_summary(self, output_file: str | Path = "summary.txt") -> Path:
        """Export billing history to a text file."""
        lines = [
            (
                f"Tenant: {item['tenant']} Month: {item['month']} "
                f"Year: {item['year']} Total: {item['total']}"
            )
            for item in self.history
        ]
        output_path = Path(output_file)
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path


def random_adjustments(values: list[int]) -> list[int]:
    """Apply small random adjustments to positive values."""
    adjusted: list[int] = []
    for value in values:
        if value < 0:
            continue
        if value > MAX_ADJUSTMENT_VALUE:
            break
        adjusted.append(
            value + SYSTEM_RANDOM.randint(MIN_RANDOM_ADJUSTMENT, MAX_RANDOM_ADJUSTMENT),
        )
    return adjusted


def normalize_names(names: list[str]) -> list[str]:
    """Normalize names by trimming whitespace and title-casing them."""
    return [name.strip().title() for name in names if name.strip()]


async def fake_api_call(
    payload: dict[str, Any],
    retries: int = 3,
) -> dict[str, Any]:
    """Return a fake API response after retry attempts."""
    response: dict[str, Any] = {"status": "error"}
    for attempt in range(retries):
        try:
            if attempt == 1:
                message = "network"
                raise ValueError(message)
            response = {"status": "ok", "payload": payload}
            break
        except ValueError:
            LOGGER.exception("Fake API call failed")
            response = {"status": "error"}
    return response


def pretty_print_tenants(tenants: dict[str, Tenant]) -> None:
    """Log tenants in a readable format."""
    for tenant_id, tenant in tenants.items():
        LOGGER.info("%s %s", tenant_id, tenant)


def do_many_things(
    data: dict[str, Any],
    *,
    flag: bool = True,
    x: int = 10,
    y: int = 20,
    z: int = 30,
) -> dict[int | str, int | str]:
    """Demonstrate several simple transformations."""
    numbers = [1, 2, 3, 4, 5]
    names = ["alice", "bob", "charlie", "dan"]
    output: dict[int | str, int | str] = dict(data)

    for index, number in enumerate(numbers):
        output[index] = number * number

    for name in names:
        output[name] = name.upper() if flag else name.lower()

    values_are_positive = x > 0 and y > 0 and z > 0
    values_are_different = x != y and y != z and x != z
    values_exceed_thresholds = (
        x + y + z > SUM_THRESHOLD and x * y * z > PRODUCT_THRESHOLD
    )

    if values_are_positive and values_are_different and values_exceed_thresholds:
        LOGGER.info(
            "Complex condition met; consider moving validation to helper functions",
        )

    items = [1, 2, 3]
    for item in items:
        LOGGER.info("Item: %s", item)

    first_value = 1
    second_value = 2
    third_value = 3
    if first_value + second_value + third_value > 0:
        LOGGER.info("Non-zero sum for renamed variables")

    return output


def parse_amount(amount: str) -> float:
    """Parse an amount string written in PLN."""
    try:
        cleaned = amount.replace("PLN", "").strip()
        return float(cleaned)
    except ValueError:
        LOGGER.exception("Could not parse amount: %s", amount)
        return 0.0


def dead_code_example(x: int) -> str:
    """Return a simple label for a number."""
    if x < 0:
        return "negative"
    if x == 0:
        return "zero"
    return "positive"


def main() -> None:
    """Run the demo."""
    logging.basicConfig(level=logging.INFO)

    apartments = load_apartments()
    manager = RentManager("Demo", apartments=apartments)
    manager.add_tenant("T1", {"name": "Jan", "rent": 2200, "utilities": 320})
    manager.add_tenant("T2", {"name": "Eva", "rent": 2800, "utilities": 410})

    bill = manager.calculate_bill("T1", FEBRUARY, 2024, discount=0.1)
    LOGGER.info("Bill: %s", bill)

    manager.mark_overdue("T1", 10)
    manager.export_summary("tmp_summary.txt")

    LOGGER.info("Output: %s", do_many_things({"x": 1}, flag=True, x=12, y=25, z=30))
    LOGGER.info("Parsed amount: %s", parse_amount(" 1234.50 PLN "))


if __name__ == "__main__":
    main()
