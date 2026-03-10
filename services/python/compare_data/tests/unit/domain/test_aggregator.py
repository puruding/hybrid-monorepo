"""Unit tests for aggregator module."""

from src.domain.aggregator import aggregate_by_product
from src.domain.models import EquipmentRecord


class TestAggregator:
    """Test cases for aggregate_by_product function."""

    def test_basic_aggregation(self) -> None:
        """Test basic product count aggregation."""
        source = [
            EquipmentRecord("SN001", "FortiGate"),
            EquipmentRecord("SN002", "FortiGate"),
            EquipmentRecord("SN003", "Cisco"),
        ]
        target = [
            EquipmentRecord("SN001", "FortiGate"),
            EquipmentRecord("SN004", "Juniper"),
        ]

        result = aggregate_by_product(source, target)

        # Should be sorted by product name
        assert len(result) == 3

        # Check Cisco (only in source)
        cisco = next(p for p in result if p.product_name == "Cisco")
        assert cisco.source_count == 1
        assert cisco.target_count == 0
        assert cisco.diff == 1

        # Check FortiGate (in both)
        fortigate = next(p for p in result if p.product_name == "FortiGate")
        assert fortigate.source_count == 2
        assert fortigate.target_count == 1
        assert fortigate.diff == 1

        # Check Juniper (only in target)
        juniper = next(p for p in result if p.product_name == "Juniper")
        assert juniper.source_count == 0
        assert juniper.target_count == 1
        assert juniper.diff == -1

    def test_empty_source(self) -> None:
        """Test with empty source."""
        source: list[EquipmentRecord] = []
        target = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN002", "Product B"),
        ]

        result = aggregate_by_product(source, target)

        assert len(result) == 2
        for p in result:
            assert p.source_count == 0
            assert p.target_count == 1
            assert p.diff == -1

    def test_empty_target(self) -> None:
        """Test with empty target."""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN002", "Product B"),
        ]
        target: list[EquipmentRecord] = []

        result = aggregate_by_product(source, target)

        assert len(result) == 2
        for p in result:
            assert p.source_count == 1
            assert p.target_count == 0
            assert p.diff == 1

    def test_empty_both(self) -> None:
        """Test with both empty datasets."""
        source: list[EquipmentRecord] = []
        target: list[EquipmentRecord] = []

        result = aggregate_by_product(source, target)

        assert len(result) == 0

    def test_same_products(self) -> None:
        """Test when both have same product distribution."""
        source = [
            EquipmentRecord("SN001", "Product A"),
            EquipmentRecord("SN002", "Product B"),
        ]
        target = [
            EquipmentRecord("SN003", "Product A"),
            EquipmentRecord("SN004", "Product B"),
        ]

        result = aggregate_by_product(source, target)

        assert len(result) == 2
        for p in result:
            assert p.source_count == 1
            assert p.target_count == 1
            assert p.diff == 0

    def test_result_sorted_by_product_name(self) -> None:
        """Test that results are sorted by product name."""
        source = [
            EquipmentRecord("SN001", "Zebra"),
            EquipmentRecord("SN002", "Apple"),
            EquipmentRecord("SN003", "Mango"),
        ]
        target: list[EquipmentRecord] = []

        result = aggregate_by_product(source, target)

        product_names = [p.product_name for p in result]
        assert product_names == ["Apple", "Mango", "Zebra"]

    def test_multiple_records_same_product(self) -> None:
        """Test counting multiple records of the same product."""
        source = [
            EquipmentRecord(f"SN{i:03d}", "FortiGate") for i in range(10)
        ]
        target = [
            EquipmentRecord(f"SN{i:03d}", "FortiGate") for i in range(5)
        ]

        result = aggregate_by_product(source, target)

        assert len(result) == 1
        assert result[0].product_name == "FortiGate"
        assert result[0].source_count == 10
        assert result[0].target_count == 5
        assert result[0].diff == 5

    def test_negative_diff(self) -> None:
        """Test negative diff when target has more."""
        source = [EquipmentRecord("SN001", "Product A")]
        target = [
            EquipmentRecord("SN002", "Product A"),
            EquipmentRecord("SN003", "Product A"),
            EquipmentRecord("SN004", "Product A"),
        ]

        result = aggregate_by_product(source, target)

        assert len(result) == 1
        assert result[0].source_count == 1
        assert result[0].target_count == 3
        assert result[0].diff == -2

    def test_with_deduplicated_data(self) -> None:
        """Test aggregation with data that's already deduplicated.

        This simulates receiving clean data from Comparator.
        """
        # Simulate deduplicated data (no duplicate serials)
        source = [
            EquipmentRecord("SN001", "FortiGate 100F"),
            EquipmentRecord("SN002", "Cisco ASA"),
        ]
        target = [
            EquipmentRecord("SN001", "FortiGate 100F"),
        ]

        result = aggregate_by_product(source, target)

        assert len(result) == 2

        fortigate = next(p for p in result if p.product_name == "FortiGate 100F")
        assert fortigate.source_count == 1
        assert fortigate.target_count == 1
        assert fortigate.diff == 0

        cisco = next(p for p in result if p.product_name == "Cisco ASA")
        assert cisco.source_count == 1
        assert cisco.target_count == 0
        assert cisco.diff == 1
