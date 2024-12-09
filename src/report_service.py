import logging
import sqlite3
from typing import Callable, Iterable

from database import get_connection


class Queries:
    blanks_by_date_and_status = \
        "SELECT number, series FROM c_blanks as b WHERE b.date LIKE ? AND b.status = ? ORDER BY series, number"
    new_blanks = \
        "SELECT number, series FROM c_blanks as b WHERE b.created_at LIKE ? ORDER BY series, number"
    clean_blanks_at_month_begin = \
        ("SELECT number, series FROM c_blanks as b "
         "WHERE b.created_at < ? AND (b.date >= ? OR b.date is NULL) ORDER BY series, number")
    clean_blanks_at_month_end = \
        ("SELECT number, series FROM blanks as b "
         "WHERE b.created_at <= ? AND (b.status = 0 OR b.date >= ?) ORDER BY series, number")


class ReportService:
    def __init__(self, _get_connection: Callable[[], sqlite3.Connection] = get_connection):
        self._get_connection = _get_connection
        self._logger = logging.getLogger('report_service')

    def __fetch(self, query: str, params: tuple = tuple()) -> list[tuple[int, str]]:
        with self._get_connection() as conn:
            cur = conn.execute(query, params)
        return cur.fetchall()

    def __get_numbers_by_series(self, raw_numbers: Iterable[tuple[int, str]]) -> dict[str, list]:
        self._logger.log(0, "Gena")
        normalize_ranges = {}
        for number, series in raw_numbers:
            normalize_ranges.setdefault(series, list()).append(number)
        return normalize_ranges

    def __get_ranges(self, raw_range: Iterable[tuple[int, str]]) -> dict[str, list[tuple[int]]]:
        self._logger.log(0, "Gena")
        numbers_by_series_raw = self.__get_numbers_by_series(raw_range)
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

    def get_report(self, year: int, month: int):
        period_template = f'{year}-{month:02}-%'
        period_start = f'{year}-{month:02}-01'
        period_end = f'{year}-{month:02}-31'
        period_next_start = f'{year+int(month/12)}-{month%12+1:02}-01'

        report = {
            "use": self.__get_ranges(
                self.__fetch(
                    Queries.blanks_by_date_and_status, (period_template, 1)
                )
            ),
            "new": self.__get_ranges(
                self.__fetch(
                    Queries.new_blanks, (period_template,)
                )
            ),
            "spoiled": self.__get_ranges(
                self.__fetch(
                    Queries.blanks_by_date_and_status, (period_template, 2)
                )
            ),
            "lost": self.__get_ranges(
                self.__fetch(
                    Queries.blanks_by_date_and_status, (period_template, 3)
                )
            ),
            "clean_at_begin": self.__get_ranges(
                self.__fetch(
                    Queries.clean_blanks_at_month_begin, (period_start, period_start)
                )
            ),
            "clean_at_end": self.__get_ranges(
                self.__fetch(
                    Queries.clean_blanks_at_month_end, (period_end, period_next_start)
                )
            ),
        }
        return report