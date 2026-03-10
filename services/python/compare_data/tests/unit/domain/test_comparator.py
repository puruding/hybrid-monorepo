"""Unit tests for comparator module."""
import time

import pytest
from src.domain.comparator import compare_datasets
from src.domain.models import EquipmentRecord, MatchStatus


class TestComparator:
    """Test cases for compare_datasets function."""

    def test_all_matched(self) -> None:
        """All records match exactly."""
        source = [EquipmentRecord("SN001", "Product A")]
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.matched_count == 1
        assert summary.name_mismatch_count == 0
        assert len(duplicates) == 0

    def test_name_mismatch(self) -> None:
        """Serial matches but product name differs."""
        source = [EquipmentRecord("SN001", "Product A")]
        target = [EquipmentRecord("SN001", "Product B")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.name_mismatch_count == 1
        assert results[0].source_product_name == "Product A"
        assert results[0].target_product_name == "Product B"

    def test_source_only(self) -> None:
        """Record exists only in source."""
        source = [EquipmentRecord("SN001", "Product A")]
        target: list[EquipmentRecord] = []

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.source_only_count == 1

    def test_target_only(self) -> None:
        """Record exists only in target."""
        source: list[EquipmentRecord] = []
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.target_only_count == 1

    def test_duplicate_serial_in_source(self) -> None:
        """Duplicate serial in source - first record used, rest in duplicate list."""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN002", "Product B"),
            EquipmentRecord("SN001", "Product C"),  # Duplicate!
        ]
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # Duplicate detected
        assert len(duplicates) == 1
        assert duplicates[0].serial_number == "SN001"
        assert duplicates[0].occurrence_count == 2
        assert duplicates[0].product_names == ["Product A", "Product C"]
        assert duplicates[0].source == "source"

        # First record used for comparison
        assert summary.matched_count == 1  # SN001 Product A matches
        assert summary.extra_duplicate_source_count == 1  # Extra duplicate (2nd only)
        assert summary.total_source == 3  # Original total
        assert summary.unique_source_count == 2  # Unique serials (SN001, SN002)

    def test_duplicate_serial_in_target(self) -> None:
        """Duplicate serial in target - first record used for comparison."""
        source = [EquipmentRecord("SN001", "Product A")]
        target = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN001", "Product B"),  # Duplicate!
        ]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # Duplicate detected
        assert len(duplicates) == 1
        assert duplicates[0].serial_number == "SN001"
        assert duplicates[0].source == "target"
        assert summary.extra_duplicate_target_count == 1
        assert summary.total_target == 2
        assert summary.unique_target_count == 1

    def test_multiple_duplicates(self) -> None:
        """Multiple serials are duplicated - all reported separately."""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN001", "Product B"),  # Duplicate1
            EquipmentRecord("SN002", "Product C"),
            EquipmentRecord("SN002", "Product D"),  # Duplicate2
        ]
        target: list[EquipmentRecord] = []

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # 2 duplicate groups detected
        assert len(duplicates) == 2
        duplicate_serials = {d.serial_number for d in duplicates}
        assert "SN001" in duplicate_serials
        assert "SN002" in duplicate_serials

        # Total extra duplicate record count
        assert summary.extra_duplicate_source_count == 2  # (2-1) + (2-1) = 2
        assert summary.total_source == 4
        assert summary.unique_source_count == 2

    def test_duplicate_first_record_used_in_comparison(self) -> None:
        """Verify first record is used when duplicates exist."""
        source = [
            EquipmentRecord("SN001", "Product A"),  # First
            EquipmentRecord("SN001", "Product B"),  # Duplicate
        ]
        target = [EquipmentRecord("SN001", "Product A")]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        # First record (Product A) is compared and matched
        assert summary.matched_count == 1
        match_result = next(r for r in results if r.status == MatchStatus.MATCHED)
        assert match_result.source_product_name == "Product A"

    def test_mixed_scenarios(self) -> None:
        """Test with mixed scenarios: matched, mismatch, source-only, target-only."""
        source = [
            EquipmentRecord("SN001", "Product A"),  # Match
            EquipmentRecord("SN002", "Product B"),  # Name mismatch
            EquipmentRecord("SN003", "Product C"),  # Source only
        ]
        target = [
            EquipmentRecord("SN001", "Product A"),  # Match
            EquipmentRecord("SN002", "Product X"),  # Name mismatch
            EquipmentRecord("SN004", "Product D"),  # Target only
        ]

        results, duplicates, summary, _, _ = compare_datasets(source, target)

        assert summary.matched_count == 1
        assert summary.name_mismatch_count == 1
        assert summary.source_only_count == 1
        assert summary.target_only_count == 1
        assert len(duplicates) == 0

    def test_summary_mathematical_consistency(self) -> None:
        """Test that summary maintains mathematical consistency."""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN001", "Product B"),  # Duplicate
            EquipmentRecord("SN002", "Product C"),
            EquipmentRecord("SN003", "Product D"),
        ]
        target = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN004", "Product E"),
        ]

        _, _, summary, _, _ = compare_datasets(source, target)

        # Validate mathematical consistency
        assert summary.validate_consistency()

        # Manual verification
        # total_source = unique_source_count + extra_duplicate_source_count
        assert summary.total_source == summary.unique_source_count + summary.extra_duplicate_source_count
        # total_target = unique_target_count + extra_duplicate_target_count
        assert summary.total_target == summary.unique_target_count + summary.extra_duplicate_target_count
        # unique_source_count = matched + name_mismatch + source_only
        assert summary.unique_source_count == summary.matched_count + summary.name_mismatch_count + summary.source_only_count
        # unique_target_count = matched + name_mismatch + target_only
        assert summary.unique_target_count == summary.matched_count + summary.name_mismatch_count + summary.target_only_count

    def test_empty_datasets(self) -> None:
        """Test with both empty datasets."""
        source: list[EquipmentRecord] = []
        target: list[EquipmentRecord] = []

        results, duplicates, summary, source_clean, target_clean = compare_datasets(
            source, target
        )

        assert len(results) == 0
        assert len(duplicates) == 0
        assert summary.total_source == 0
        assert summary.total_target == 0
        assert len(source_clean) == 0
        assert len(target_clean) == 0

    def test_returns_clean_data(self) -> None:
        """Test that clean (deduplicated) data is returned."""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN001", "Product B"),  # Duplicate
            EquipmentRecord("SN002", "Product C"),
        ]
        target = [
            EquipmentRecord("SN003", "Product D"),
            EquipmentRecord("SN003", "Product E"),  # Duplicate
        ]

        _, _, _, source_clean, target_clean = compare_datasets(source, target)

        # Source clean should have 2 unique serials
        assert len(source_clean) == 2
        source_serials = {r.serial_number for r in source_clean}
        assert source_serials == {"SN001", "SN002"}

        # Target clean should have 1 unique serial
        assert len(target_clean) == 1
        assert target_clean[0].serial_number == "SN003"

    @pytest.mark.slow
    def test_large_dataset_performance(self) -> None:
        """Performance test with 100k records."""
        source = [
            EquipmentRecord(f"SN{i:06d}", f"Product {i % 100}")
            for i in range(100_000)
        ]
        target = source.copy()

        start = time.time()
        results, duplicates, summary, _, _ = compare_datasets(source, target)
        elapsed = time.time() - start

        assert elapsed < 5.0  # Should complete within 5 seconds
        assert summary.matched_count == 100_000
        assert summary.extra_duplicate_source_count == 0
        assert summary.total_source == 100_000
        assert summary.unique_source_count == 100_000
