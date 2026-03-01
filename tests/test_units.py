"""Tests for storage unit operations (repository layer)."""

import pytest

from catalogador.db.models import StorageUnit
from catalogador.utils.exceptions import DuplicateUnitError, UnitNotFoundError


class TestUnitExceptions:
    """Test that custom exceptions are properly defined."""

    def test_duplicate_unit_error(self):
        with pytest.raises(DuplicateUnitError):
            raise DuplicateUnitError("already exists")

    def test_unit_not_found_error(self):
        with pytest.raises(UnitNotFoundError):
            raise UnitNotFoundError("not found")


class TestStorageUnitModel:
    def test_create_unit(self):
        unit = StorageUnit(alias="nas-office", unit_type="nas")
        assert unit.alias == "nas-office"
        assert unit.unit_type == "nas"

    def test_valid_types(self):
        for t in ("disco_fisico", "nas", "google_drive", "outro"):
            unit = StorageUnit(alias=f"test-{t}", unit_type=t)
            assert unit.unit_type == t
