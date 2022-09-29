from strenum import StrEnum
from decimal import Decimal
import numpy


class ProfileType(StrEnum):
    SIZE = "size profile"
    GROWTH = "growth profile"


class ProfileRange:
    def __init__(self, session, query_builder, logger, response_sql) -> None:
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.logger = logger
        self.table = "value_range"

    def is_valid_number(self, number) -> bool:
        return number is not None and isinstance(number, (int, float, Decimal))

    def get_profile_ranges(self, type: str) -> list:
        try:
            query = (
                self.query_builder.add_table_name(self.table)
                .add_select_conditions(["label, min_value, max_value"])
                .add_sql_where_equal_condition({f"{self.table}.type": f"'{type}'"})
                .build()
                .get_query()
            )
            result = self.session.execute(query).fetchall()
            return self.response_sql.process_query_list_results(result)
        except Exception as error:
            self.logger.info(error)
            return []

    def verify_range(self, range, revenue):
        max_value = range.get("max_value")
        min_value = range.get("min_value")
        coincidences = []
        if max_value is not None:
            coincidences.append(revenue < max_value)
        if min_value is not None:
            coincidences.append(revenue >= min_value)
        return coincidences and all(coincidences)

    def get_range_from_value(
        self,
        value: float,
        profile: str = "size profile",
        ranges: list = None,
    ) -> None:
        if not ranges:
            ranges = self.get_profile_ranges(profile)
        if not self.is_valid_number(value):
            return "NA"
        else:
            metric_ranges = list(
                filter(
                    lambda range: self.verify_range(range, value),
                    ranges,
                )
            )
            profile_range = (
                metric_ranges[-1]
                if (len(metric_ranges) == 1 and metric_ranges[0])
                else {"label": "NA"}
            )

            return profile_range.get("label")

    def get_intervals(self, values: list) -> list:
        values = [float(value) for value in values if self.is_valid_number(value)]
        if len(values) < 5:
            return values
        percentiles = [0.20, 0.40, 0.60, 0.8]

        return [numpy.quantile(values, percentil) for percentil in percentiles]

    def __get_first_range(self, min_value: float) -> dict:
        return {
            "label": f"<${round(min_value)} million",
            "min_value": None,
            "max_value": round(min_value),
        }

    def __get_last_range(self, max_value: float) -> dict:
        return {
            "label": f"${round(max_value)} million+",
            "min_value": round(max_value),
            "max_value": None,
        }

    def __get_range(self, value: float, prior_value: float) -> dict:
        return {
            "label": f"${round(prior_value)}-<${round(value)} million",
            "min_value": round(prior_value),
            "max_value": round(value),
        }

    def build_ranges_from_values(self, values: list) -> list:
        if not values or all(value is None or value == "NA" for value in values):
            return []
        values = list(filter(lambda value: self.is_valid_number(value), values))
        intervals = self.get_intervals(values)
        min_value = min(intervals)
        max_value = max(intervals)
        ranges = []
        for index in range(len(intervals)):
            value = intervals[index]
            if value == min_value:
                ranges.append(self.__get_first_range(min_value))
            else:
                ranges.append(self.__get_range(value, intervals[index - 1]))
        ranges.append(self.__get_last_range(max_value))
        return ranges
