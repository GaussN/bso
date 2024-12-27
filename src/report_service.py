import logging
import sqlite3
from typing import Callable, Iterable


class Queries:
    blanks_by_date_and_status = \
        (
            "SELECT number, series "
            "FROM c_blanks as b "
            "WHERE b.date LIKE ? AND b.status = ? ORDER BY series, number"
        )
    new_blanks = \
        (
            "SELECT number, series "
            "FROM c_blanks as b "
            "WHERE b.created_at LIKE ? ORDER BY series, number"
        )
    clean_blanks_at_month_begin = \
        (
            "SELECT number, series FROM c_blanks as b "
            "WHERE b.created_at < ? AND "
            "(b.date >= ? OR b.date is NULL) ORDER BY series, number"
        )


class ReportService:
    """Generates report of strict accounting forms(in code - blank)"""
    def __init__(self, get_connection: Callable[[], sqlite3.Connection]):
        self._get_connection = get_connection

    def _fetch(
        self, 
        query: str, 
        params: tuple = tuple()
    ) -> list[tuple[int, str]]:
        with self._get_connection() as conn:
            cur = conn.execute(query, params)
        return cur.fetchall()

    def _goruped_numbers(
        self, 
        numbers: Iterable[tuple[int, str]]
        ) -> dict[str, list]:
        """Grouping numbers by series"""
        grouped_numbers = {}
        for number, series in numbers:
            grouped_numbers.setdefault(series, list()).append(number)
        return grouped_numbers

    def _get_ranges(
        self, 
        numbers: Iterable[tuple[int, str]]
    ) -> dict[str, list[tuple[int]]]:
        """Represents numbers as ranges grouped by series"""
        numbers_by_series_raw = self._goruped_numbers(numbers)
        ranges_by_series = {}
        for series in numbers_by_series_raw:
            numbers = numbers_by_series_raw[series]
            ranges_by_series[series] = list()
            start = end = numbers[0]
            for number in numbers[1:]:
                if number != end + 1:
                    ranges_by_series[series].append((start, end))
                    start = number
                end = number
            ranges_by_series[series].append((start, end))
        return ranges_by_series

    def get_report(self, year: int, month: int) -> dict:
        if not (1 <= month <= 12):
            raise ValueError("month value should be in range [1,12]")

        period_template = f'{year}-{month:02}-%'
        period_start = f'{year}-{month:02}-01'
        period_next_start = f'{year+int(month/12)}-{month%12+1:02}-01'

        report = {
            "use": self._get_ranges(
                self._fetch(
                    Queries.blanks_by_date_and_status, 
                    (period_template, 1)
                )
            ),
            "new": self._get_ranges(
                self._fetch(
                    Queries.new_blanks, 
                    (period_template,)
                )
            ),
            "spoiled": self._get_ranges(
                self._fetch(
                    Queries.blanks_by_date_and_status, 
                    (period_template, 2)
                )
            ),
            "lost": self._get_ranges(
                self._fetch(
                    Queries.blanks_by_date_and_status, 
                    (period_template, 3)
                )
            ),
            "clean_at_begin": self._get_ranges(
                self._fetch(
                    Queries.clean_blanks_at_month_begin, 
                    (period_start, period_start)
                )
            ),
            "clean_at_end": self._get_ranges(
                self._fetch(
                    Queries.clean_blanks_at_month_begin, 
                    (period_next_start, period_next_start)
                )
            ),
        }
        return report
