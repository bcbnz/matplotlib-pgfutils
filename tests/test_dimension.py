import pytest
from pytest import approx

from pgfutils import DimensionError, parse_dimension


class TestDimension:
    def test_parse(self):
        """Dimension parser with valid inputs"""
        assert parse_dimension("1") == approx(1)
        assert parse_dimension("3.2") == approx(3.2)
        assert parse_dimension("2.54cm") == approx(1)
        assert parse_dimension("2.54 cm") == approx(1)
        assert parse_dimension("2.54\tcm") == approx(1)

    def test_unknown_unit(self):
        """Dimension parser rejects unknown units"""
        with pytest.raises(DimensionError):
            parse_dimension("1.2kg")

    def test_dimension_empty(self):
        """Dimension cannot be empty string"""
        with pytest.raises(DimensionError):
            parse_dimension("")
        with pytest.raises(DimensionError):
            parse_dimension("     ")

    def test_dimension_not_parsing(self):
        """Dimension parser rejects invalid strings..."""
        with pytest.raises(DimensionError):
            parse_dimension("cm1.2")
        with pytest.raises(DimensionError):
            parse_dimension("1.2.2cm")

    def test_dimension_inches(self):
        """Dimensions without units are treated as inches..."""
        assert parse_dimension("7") == approx(7)
        assert parse_dimension("2.7") == approx(2.7)

    def test_dimension_negative(self):
        """Negative dimensions are rejected..."""
        with pytest.raises(DimensionError):
            parse_dimension("-1.2")
        with pytest.raises(DimensionError):
            parse_dimension("-1.2cm")
