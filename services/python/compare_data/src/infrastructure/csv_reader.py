"""CSV file reader adapter."""
import csv
from pathlib import Path

import structlog

from src.application.ports import EquipmentDataPort
from src.domain.exceptions import CSVReadError
from src.domain.models import EquipmentRecord

logger = structlog.get_logger()


class CSVReader(EquipmentDataPort):
    """CSV file reader implementing EquipmentDataPort."""

    def __init__(
        self,
        file_path: Path | str,
        has_header: bool = False,
        encoding: str = "utf-8",
    ) -> None:
        """
        Initialize CSV reader.

        Args:
            file_path: Path to CSV file
            has_header: Whether CSV has header row to skip
            encoding: File encoding (default: utf-8)
        """
        self.file_path = Path(file_path)
        self.has_header = has_header
        self.encoding = encoding
        self._records: list[EquipmentRecord] | None = None

    def load_records(self) -> list[EquipmentRecord]:
        """Load equipment records from CSV file."""
        if self._records is not None:
            return self._records

        if not self.file_path.exists():
            raise CSVReadError(f"CSV file not found: {self.file_path}")

        records: list[EquipmentRecord] = []
        try:
            with open(self.file_path, "r", encoding=self.encoding, newline="") as f:
                reader = csv.reader(f)

                if self.has_header:
                    next(reader)  # Skip header

                for line_num, row in enumerate(reader, start=1):
                    if len(row) < 2:
                        logger.warning(
                            "invalid_row",
                            line=line_num,
                            row=row,
                            reason="expected 2 columns",
                        )
                        continue

                    serial_number = row[0].strip()
                    product_name = row[1].strip()

                    if not serial_number:
                        logger.warning(
                            "empty_serial",
                            line=line_num,
                            reason="empty serial number",
                        )
                        continue

                    records.append(
                        EquipmentRecord(
                            serial_number=serial_number,
                            product_name=product_name,
                        )
                    )

            self._records = records
            logger.info(
                "csv_loaded",
                file=str(self.file_path),
                record_count=len(records),
            )
            return records

        except UnicodeDecodeError as e:
            # Try with different encoding
            if self.encoding != "cp949":
                logger.warning(
                    "encoding_error",
                    encoding=self.encoding,
                    trying="cp949",
                )
                self.encoding = "cp949"
                return self.load_records()
            raise CSVReadError(f"Encoding error: {e}") from e
        except csv.Error as e:
            raise CSVReadError(f"CSV parsing error: {e}") from e

    def get_record_count(self) -> int:
        """Return record count."""
        if self._records is None:
            self.load_records()
        return len(self._records) if self._records else 0
