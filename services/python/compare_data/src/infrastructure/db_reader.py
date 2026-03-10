"""Database reader adapter for LGU MariaDB."""
from collections.abc import Sequence

import structlog
from sqlalchemy import Row, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.application.ports import EquipmentDataPort
from src.domain.exceptions import DatabaseConnectionError
from src.domain.models import EquipmentRecord

logger = structlog.get_logger()

# SQL query for loading equipment records
# Conditions:
# - EqpmTbl.delYn <> 'y' (not deleted)
# - CscoEqpmTbl.delYn <> 'y' (not deleted)
# - EqpmTbl.owns = '0' (임대인 제품만)
# - EqpmTbl.eqpmGrpCd NOT IN (52, 82) (회선, 웹서버 제외)
# - EqpmTbl.rcgnNo NOT LIKE '%VIP%' (VIP 제품 제외)
EQUIPMENT_QUERY = """
SELECT
    a.rcgnNo AS serial_number,
    b.eqpmNm AS product_name
FROM EqpmTbl a
INNER JOIN CscoEqpmTbl b
    ON a.cscoEqpmCd = b.cscoEqpmCd
    AND a.eqpmCd = b.eqpmCd
WHERE a.delYn <> 'y'
  AND b.delYn <> 'y'
  AND a.owns = '0'
  AND a.eqpmGrpCd NOT IN (52, 82)
  AND a.rcgnNo NOT LIKE '%VIP%'
"""


class DBReader(EquipmentDataPort):
    """Database reader implementing EquipmentDataPort."""

    def __init__(
        self,
        connection_string: str,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        """
        Initialize database reader.

        Args:
            connection_string: SQLAlchemy connection string
            pool_size: Connection pool size
            max_overflow: Max overflow connections
        """
        self.connection_string = connection_string
        self._engine: Engine | None = None
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._records: list[EquipmentRecord] | None = None

    def _get_engine(self) -> Engine:
        """Get or create database engine."""
        if self._engine is None:
            try:
                self._engine = create_engine(
                    self.connection_string,
                    pool_size=self._pool_size,
                    max_overflow=self._max_overflow,
                    pool_pre_ping=True,
                )
            except SQLAlchemyError as e:
                raise DatabaseConnectionError(
                    f"Failed to create database engine: {e}"
                ) from e
        return self._engine

    def load_records(self) -> list[EquipmentRecord]:
        """Load equipment records from database."""
        if self._records is not None:
            return self._records

        engine = self._get_engine()
        records: list[EquipmentRecord] = []

        try:
            with engine.connect() as conn:
                result: Sequence[Row[tuple[str, str]]] = conn.execute(
                    text(EQUIPMENT_QUERY)
                ).fetchall()

                for row in result:
                    serial_number: str = row[0]
                    product_name: str = row[1]

                    if serial_number:
                        records.append(
                            EquipmentRecord(
                                serial_number=serial_number.strip(),
                                product_name=product_name.strip() if product_name else "",
                            )
                        )

            self._records = records
            logger.info(
                "db_loaded",
                source="LGU",
                record_count=len(records),
            )
            return records

        except SQLAlchemyError as e:
            raise DatabaseConnectionError(f"Database query failed: {e}") from e

    def get_record_count(self) -> int:
        """Return record count."""
        if self._records is None:
            self.load_records()
        return len(self._records) if self._records else 0

    def close(self) -> None:
        """Close database connection."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
