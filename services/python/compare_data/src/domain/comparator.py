"""Comparison algorithm - core business logic."""
import re
from collections import defaultdict

from src.domain.models import (
    ComparisonResult,
    ComparisonSummary,
    DuplicateRecord,
    EquipmentRecord,
    MatchStatus,
)


def normalize_product_name(name: str) -> str:
    """
    Normalize product name for comparison.

    Rules:
    - Convert to lowercase for case-insensitive comparison
    - "fg-" prefix → "fortigate-" (e.g., FG-100F → fortigate-100f)

    Args:
        name: Original product name

    Returns:
        Normalized product name (lowercase)
    """
    # Convert to lowercase first
    lower_name = name.lower()

    # fg-XXX → fortigate-XXX
    if re.match(r"^fg-", lower_name):
        return re.sub(r"^fg-", "fortigate-", lower_name)
    return lower_name


def _extract_duplicates(
    records: list[EquipmentRecord],
    source: str,
) -> tuple[list[EquipmentRecord], list[DuplicateRecord]]:
    """
    Extract and separate duplicate records (Fault-Tolerant).

    Strategy:
    - Keep only the first record for each duplicate serial (deterministic)
    - Separate remaining duplicates into a duplicate list

    Args:
        records: Records to validate
        source: Data source identifier ("source" or "target")

    Returns:
        Tuple of (deduplicated records, duplicate record info list)
    """
    # Group records by serial number
    serial_groups: dict[str, list[EquipmentRecord]] = defaultdict(list)
    for record in records:
        serial_groups[record.serial_number].append(record)

    clean_records: list[EquipmentRecord] = []
    duplicate_records: list[DuplicateRecord] = []

    for serial, group in serial_groups.items():
        if len(group) == 1:
            # Unique record - use as-is
            clean_records.append(group[0])
        else:
            # Duplicate found
            # First record is used for comparison
            clean_records.append(group[0])

            # Record duplicate information
            duplicate_records.append(
                DuplicateRecord(
                    serial_number=serial,
                    product_names=[r.product_name for r in group],
                    occurrence_count=len(group),
                    source=source,
                )
            )

    return clean_records, duplicate_records


def _calculate_summary(
    results: list[ComparisonResult],
    total_source: int,
    total_target: int,
    extra_duplicate_source_count: int,
    extra_duplicate_target_count: int,
    unique_source_count: int,
    unique_target_count: int,
) -> ComparisonSummary:
    """Calculate comparison summary from results."""
    matched_count = sum(1 for r in results if r.status == MatchStatus.MATCHED)
    name_mismatch_count = sum(
        1 for r in results if r.status == MatchStatus.NAME_MISMATCH
    )
    source_only_count = sum(1 for r in results if r.status == MatchStatus.SOURCE_ONLY)
    target_only_count = sum(1 for r in results if r.status == MatchStatus.TARGET_ONLY)

    return ComparisonSummary(
        total_source=total_source,
        total_target=total_target,
        extra_duplicate_source_count=extra_duplicate_source_count,
        extra_duplicate_target_count=extra_duplicate_target_count,
        unique_source_count=unique_source_count,
        unique_target_count=unique_target_count,
        matched_count=matched_count,
        name_mismatch_count=name_mismatch_count,
        source_only_count=source_only_count,
        target_only_count=target_only_count,
    )


def compare_datasets(
    source_records: list[EquipmentRecord],
    target_records: list[EquipmentRecord],
) -> tuple[
    list[ComparisonResult],
    list[DuplicateRecord],
    ComparisonSummary,
    list[EquipmentRecord],
    list[EquipmentRecord],
]:
    """
    Compare two datasets (Fault-Tolerant).

    Duplicate serial handling:
    - Does not abort on duplicates
    - Excludes duplicates from comparison, stores them in separate list
    - Uses first record only for comparison (deterministic)

    Time complexity: O(n + m) where n=source, m=target
    Space complexity: O(n + m)

    Returns:
        Tuple of (comparison results, duplicate records, summary,
                  source_clean, target_clean)
    """
    # 1. Detect and separate duplicates O(n)
    source_clean, source_duplicates = _extract_duplicates(source_records, "source")
    target_clean, target_duplicates = _extract_duplicates(target_records, "target")

    # 2. Convert deduplicated data to dict O(n) + O(m)
    source_map: dict[str, EquipmentRecord] = {
        r.serial_number: r for r in source_clean
    }
    target_map: dict[str, EquipmentRecord] = {
        r.serial_number: r for r in target_clean
    }

    results: list[ComparisonResult] = []

    # 3. Compare based on source O(n)
    for serial, source_rec in source_map.items():
        if serial in target_map:
            target_rec = target_map[serial]
            # Compare using normalized product names
            source_normalized = normalize_product_name(source_rec.product_name)
            target_normalized = normalize_product_name(target_rec.product_name)
            if source_normalized == target_normalized:
                status = MatchStatus.MATCHED
            else:
                status = MatchStatus.NAME_MISMATCH
            results.append(
                ComparisonResult(
                    serial_number=serial,
                    status=status,
                    source_product_name=source_rec.product_name,
                    target_product_name=target_rec.product_name,
                )
            )
        else:
            results.append(
                ComparisonResult(
                    serial_number=serial,
                    status=MatchStatus.SOURCE_ONLY,
                    source_product_name=source_rec.product_name,
                )
            )

    # 4. Find Target Only O(m)
    for serial, target_rec in target_map.items():
        if serial not in source_map:
            results.append(
                ComparisonResult(
                    serial_number=serial,
                    status=MatchStatus.TARGET_ONLY,
                    target_product_name=target_rec.product_name,
                )
            )

    # 5. Calculate summary
    all_duplicates = source_duplicates + target_duplicates
    summary = _calculate_summary(
        results,
        total_source=len(source_records),
        total_target=len(target_records),
        extra_duplicate_source_count=sum(
            d.occurrence_count - 1 for d in source_duplicates
        ),
        extra_duplicate_target_count=sum(
            d.occurrence_count - 1 for d in target_duplicates
        ),
        unique_source_count=len(source_clean),
        unique_target_count=len(target_clean),
    )

    return results, all_duplicates, summary, source_clean, target_clean
