"""Custom exception classes for the catalogador application."""


class CatalogadorError(Exception):
    """Base exception for all catalogador errors."""


class DatabaseError(CatalogadorError):
    """Raised when a database operation fails."""


class ScanError(CatalogadorError):
    """Raised when a file scanning operation fails."""


class HashError(CatalogadorError):
    """Raised when file hashing fails."""


class UnitNotFoundError(CatalogadorError):
    """Raised when a storage unit alias is not found."""


class DuplicateUnitError(CatalogadorError):
    """Raised when attempting to register an alias that already exists."""
