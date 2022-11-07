from collections import defaultdict
from decimal import Decimal
from typing import Union

from ranges_repository import RangesRepository
from base_exception import AppError
from base_metrics_config_name import METRICS_CONFIG_NAME


class RangesService:
    def __init__(self, logger, repository: RangesRepository) -> None:
        self.logger = logger
        self.repository = repository

    def __get_all_ranges_response(self, total_ranges: int, ranges: list) -> dict:
        return {"total": total_ranges, "ranges": ranges}

    def is_valid_number(self, number) -> bool:
        return number is not None and isinstance(number, (int, float, Decimal))

    def __get_number(self, number) -> Union[int, None]:
        return int(number) if self.is_valid_number(number) else None

    def __build_ranges_by_metric(self, ranges: list) -> list:
        records = defaultdict(dict)
        metric_range_names = {v: k for k, v in METRICS_CONFIG_NAME.items()}
        for range in ranges:
            ranges_by_metric = []
            range_key = range["type"]
            if range_key in records:
                ranges_by_metric = records[range_key]["ranges"]
            range["min_value"] = self.__get_number(range["min_value"])
            range["max_value"] = self.__get_number(range["max_value"])
            range.pop("type")
            ranges_by_metric.append(range)
            records[range_key].update(
                {"key": range_key, "name": metric_range_names[range_key]}
            )
            records[range_key]["ranges"] = ranges_by_metric
        return list(records.values())

    def get_all_ranges(self, offset: int = 0, max_count: int = None) -> dict:
        try:
            total_ranges = self.repository.get_total_number_of_ranges().get("count")
            return self.__get_all_ranges_response(
                total_ranges,
                self.__build_ranges_by_metric(
                    self.repository.get_ranges(offset, max_count)
                ),
            )

        except Exception as error:
            self.logger.error(error)
            raise AppError("Can't get ranges")

    def __is_valid_metric_name(self, metric: str) -> bool:
        return metric and metric.strip()

    def __build_metric_ranges(self, ranges: list) -> None:
        return [
            {
                "id": range["id"],
                "label": range["label"],
                "min_value": self.__get_number(range["min_value"]),
                "max_value": self.__get_number(range["max_value"]),
            }
            for range in ranges
        ]

    def get_ranges_by_metric(self, metric: str) -> list:
        try:
            if not self.__is_valid_metric_name(metric):
                raise AppError("Invalid metric")
            return self.__build_metric_ranges(
                self.repository.get_ranges_by_metric(metric)
            )
        except Exception as error:
            self.logger.error(error)
            raise error
