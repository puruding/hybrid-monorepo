"""Aggregation algorithm - product count by name."""
from collections import Counter

from src.domain.models import EquipmentRecord, ProductCount


def aggregate_by_product(
    source_clean: list[EquipmentRecord],
    target_clean: list[EquipmentRecord],
) -> list[ProductCount]:
    """
    Aggregate count by product name (based on unique data).

    IMPORTANT: This function receives **pure unique** data that has been
    filtered by Comparator to remove duplicates (human error).

    Purpose:
    - Exclude fake inventory (duplicates) to get actual physical holdings
    - Accurate and reliable Source/Target serial-based product distribution comparison

    Args:
        source_clean: Deduplicated pure Source data
        target_clean: Deduplicated pure Target data

    Returns:
        Product-wise source/target count and difference

    Example:
        Input Source: [SN001-FortiGate, SN002-Cisco]  # Deduplicated 2 records
        Input Target: [SN001-FortiGate]               # 1 record

        Result:
        - FortiGate: Source=1, Target=1, Diff=0
        - Cisco:     Source=1, Target=0, Diff=+1
    """
    source_counts: Counter[str] = Counter(r.product_name for r in source_clean)
    target_counts: Counter[str] = Counter(r.product_name for r in target_clean)

    all_products = set(source_counts.keys()) | set(target_counts.keys())

    return [
        ProductCount(
            product_name=product,
            source_count=source_counts.get(product, 0),
            target_count=target_counts.get(product, 0),
            diff=source_counts.get(product, 0) - target_counts.get(product, 0),
        )
        for product in sorted(all_products)
    ]
