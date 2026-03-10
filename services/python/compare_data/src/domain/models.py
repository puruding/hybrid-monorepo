"""Domain models for the comparison tool."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MatchStatus(Enum):
    """Comparison result status."""

    MATCHED = "matched"
    NAME_MISMATCH = "name_mismatch"
    SOURCE_ONLY = "source_only"
    TARGET_ONLY = "target_only"


@dataclass(frozen=True)
class EquipmentRecord:
    """Equipment record (immutable)."""

    serial_number: str
    product_name: str


@dataclass
class ComparisonResult:
    """Individual comparison result."""

    serial_number: str
    status: MatchStatus
    source_product_name: Optional[str] = None
    target_product_name: Optional[str] = None


@dataclass
class ProductCount:
    """Product count by product name."""

    product_name: str
    source_count: int
    target_count: int
    diff: int


@dataclass
class DuplicateRecord:
    """Duplicate record information."""

    serial_number: str
    product_names: list[str]
    occurrence_count: int
    source: str  # "source" or "target"


@dataclass
class ComparisonSummary:
    """Comparison summary with mathematical consistency.

    Mathematical invariants:
    - total_source = unique_source_count + extra_duplicate_source_count
    - total_target = unique_target_count + extra_duplicate_target_count
    - unique_source_count = matched_count + name_mismatch_count + source_only_count
    - unique_target_count = matched_count + name_mismatch_count + target_only_count
    """

    # Original data counts (including duplicates)
    total_source: int
    total_target: int

    # Duplicate statistics (extra duplicates only, first occurrence excluded)
    extra_duplicate_source_count: int
    extra_duplicate_target_count: int

    # Unique serial counts after deduplication
    unique_source_count: int
    unique_target_count: int

    # Comparison results (based on unique serials)
    matched_count: int
    name_mismatch_count: int
    source_only_count: int
    target_only_count: int

    def validate_consistency(self) -> bool:
        """Validate mathematical consistency of the summary."""
        # Check source consistency
        source_total_check = (
            self.total_source
            == self.unique_source_count + self.extra_duplicate_source_count
        )
        # Check target consistency
        target_total_check = (
            self.total_target
            == self.unique_target_count + self.extra_duplicate_target_count
        )
        # Check unique source breakdown
        source_breakdown_check = (
            self.unique_source_count
            == self.matched_count + self.name_mismatch_count + self.source_only_count
        )
        # Check unique target breakdown
        target_breakdown_check = (
            self.unique_target_count
            == self.matched_count + self.name_mismatch_count + self.target_only_count
        )

        return (
            source_total_check
            and target_total_check
            and source_breakdown_check
            and target_breakdown_check
        )
