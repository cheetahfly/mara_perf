import pytest
from src.utils.time_converter import (
    parse_time,
    format_time,
    time_to_minutes,
    minutes_to_time,
)

class TestParseTime:
    def test_standard_format(self):
        assert parse_time("2:20:00") == 8400

    def test_single_digit_hours(self):
        assert parse_time("1:05:30") == 3930

    def test_no_hours(self):
        assert parse_time("25:00") == 1500  # 半马常用格式

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_time("invalid")

class TestFormatTime:
    def test_standard(self):
        assert format_time(8400) == "2:20:00"

    def test_with_leading_zero(self):
        assert format_time(3930) == "1:05:30"

class TestTimeToMinutes:
    def test_conversion(self):
        assert time_to_minutes(8400) == 140.0

class TestMinutesToTime:
    def test_conversion(self):
        assert minutes_to_time(140.0) == "2:20:00"
