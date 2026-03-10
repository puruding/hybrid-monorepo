"""Domain exceptions hierarchy."""


class CompareDataError(Exception):
    """Base exception for the comparison tool."""

    pass


class DataLoadError(CompareDataError):
    """Failed to load data."""

    pass


class CSVReadError(DataLoadError):
    """Failed to read CSV file."""

    pass


class DatabaseConnectionError(DataLoadError):
    """Failed to connect to database."""

    pass


class ValidationError(CompareDataError):
    """Data validation failed."""

    pass


class ReportGenerationError(CompareDataError):
    """Failed to generate report."""

    pass
