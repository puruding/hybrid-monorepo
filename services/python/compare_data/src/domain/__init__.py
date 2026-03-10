"""Domain layer - pure business logic with zero dependencies."""
from src.domain.aggregator import aggregate_by_product
from src.domain.comparator import compare_datasets
from src.domain.exceptions import (
    CompareDataError,
    CSVReadError,
    DatabaseConnectionError,
    DataLoadError,
    ReportGenerationError,
    ValidationError,
)
from src.domain.models import (
    ComparisonResult,
    ComparisonSummary,
    DuplicateRecord,
    EquipmentRecord,
    MatchStatus,
    ProductCount,
)

__all__ = [
    # Models
    "MatchStatus",
    "EquipmentRecord",
    "ComparisonResult",
    "ProductCount",
    "DuplicateRecord",
    "ComparisonSummary",
    # Functions
    "compare_datasets",
    "aggregate_by_product",
    # Exceptions
    "CompareDataError",
    "DataLoadError",
    "CSVReadError",
    "DatabaseConnectionError",
    "ValidationError",
    "ReportGenerationError",
]
