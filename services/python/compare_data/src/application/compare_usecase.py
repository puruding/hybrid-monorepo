"""Compare use case - orchestrates the comparison process."""
from dataclasses import dataclass
from pathlib import Path

import structlog

from src.application.ports import EquipmentDataPort
from src.domain.aggregator import aggregate_by_product
from src.domain.comparator import compare_datasets
from src.domain.models import (
    ComparisonResult,
    ComparisonSummary,
    DuplicateRecord,
    ProductCount,
)
from src.infrastructure.report_writer import ReportWriter

logger = structlog.get_logger()


@dataclass
class CompareResult:
    """Result of comparison use case."""

    summary: ComparisonSummary
    product_counts: list[ProductCount]
    comparison_results: list[ComparisonResult]
    duplicates: list[DuplicateRecord]
    report_paths: list[Path]


class CompareUseCase:
    """Use case for comparing source and target data."""

    def __init__(
        self,
        source_port: EquipmentDataPort,
        target_port: EquipmentDataPort,
        report_writer: ReportWriter,
        output_format: str = "xlsx",
    ) -> None:
        """
        Initialize compare use case.

        Args:
            source_port: Source data port (CSV)
            target_port: Target data port (DB)
            report_writer: Report writer instance
            output_format: Output format ('xlsx', 'csv', or 'both')
        """
        self.source_port = source_port
        self.target_port = target_port
        self.report_writer = report_writer
        self.output_format = output_format

    def execute(self) -> CompareResult:
        """
        Execute the comparison.

        Returns:
            CompareResult with all comparison data and report paths
        """
        logger.info("comparison_started")

        # 1. Load source data (CSV)
        logger.info("loading_source_data")
        source_raw = self.source_port.load_records()
        logger.info("source_data_loaded", count=len(source_raw))

        # 2. Load target data (DB)
        logger.info("loading_target_data")
        target_raw = self.target_port.load_records()
        logger.info("target_data_loaded", count=len(target_raw))

        # 3. Compare datasets
        logger.info("comparing_datasets")
        results, duplicates, summary, source_clean, target_clean = compare_datasets(
            source_raw, target_raw
        )
        logger.info(
            "comparison_complete",
            matched=summary.matched_count,
            mismatch=summary.name_mismatch_count,
            source_only=summary.source_only_count,
            target_only=summary.target_only_count,
            duplicates=len(duplicates),
        )

        # Log duplicate warnings
        if summary.extra_duplicate_source_count > 0:
            logger.warning(
                "source_duplicates_found",
                count=summary.extra_duplicate_source_count,
            )
        if summary.extra_duplicate_target_count > 0:
            logger.warning(
                "target_duplicates_found",
                count=summary.extra_duplicate_target_count,
            )

        # 4. Aggregate by product (using clean data)
        logger.info("aggregating_products")
        product_counts = aggregate_by_product(source_clean, target_clean)
        logger.info("aggregation_complete", product_count=len(product_counts))

        # 5. Generate reports
        logger.info("generating_reports", format=self.output_format)
        report_paths: list[Path] = []

        if self.output_format in ("xlsx", "both"):
            xlsx_path = self.report_writer.write_excel_report(
                summary, product_counts, results, duplicates
            )
            report_paths.append(xlsx_path)

        if self.output_format in ("csv", "both"):
            csv_paths = self.report_writer.write_csv_reports(
                summary, product_counts, results, duplicates
            )
            report_paths.extend(csv_paths)

        logger.info("comparison_finished", report_count=len(report_paths))

        return CompareResult(
            summary=summary,
            product_counts=product_counts,
            comparison_results=results,
            duplicates=duplicates,
            report_paths=report_paths,
        )
