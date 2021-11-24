from enum import Enum


class QuerySQLBuilder:
    query: str

    def __init__(self) -> None:
        self.query = ""
        self.table_name = ""
        self.select_conditions = []
        self.join_clauses = []
        self.where_conditions = []
        self.limit = None
        self.offset = None
        self.group_by = []
        self.order_by = None

    class Order(Enum):
        DESC = "DESC"
        ASC = "ASC"

    def __is_valid_name(self, name: str):
        no_invalid_strings = name != "''" and name != "'None'"
        return name and isinstance(name, str) and name.strip() and no_invalid_strings

    def __is_valid_number(self, number: int):
        return number is not None and isinstance(number, int)

    def __get_join_table_name(self, table_name: str):
        if self.__is_valid_name(table_name):
            return f"JOIN {table_name}"
        else:
            raise Exception("No valid table name")

    def __get_alias_table_clause(self, alias: str):
        if self.__is_valid_name(alias):
            return f"AS {alias}"
        else:
            return ""

    def __get_on_join_condition_clause(self, values: dict):
        from_value = values.get("from")
        to_value = values.get("to")
        if self.__is_valid_name(from_value) and self.__is_valid_name(to_value):
            return f"ON {from_value} = {to_value}"
        else:
            raise Exception("No valid on clause in JOIN")

    def add_table_name(self, table_name: str):
        if self.__is_valid_name(table_name):
            self.table_name = table_name
            return self
        else:
            raise Exception("No valid table name")

    def add_select_conditions(self, columns: list = None):
        columns = columns if columns else ["*"]
        self.select_conditions.extend(columns)
        return self

    def add_join_clause(self, clauses: dict = None):
        try:
            if clauses:
                for table_name, values in clauses.items():
                    join = self.__get_join_table_name(table_name)
                    alias = self.__get_alias_table_clause(values.get("alias", ""))
                    on = self.__get_on_join_condition_clause(values)

                    join_clause = f"""
                        {join}
                        {alias}
                        {on}
                    """
                    self.join_clauses.append(join_clause)
            return self
        except Exception as error:
            raise error

    def add_sql_where_equal_condition(self, conditions: dict = None):
        if conditions:
            for k, v in conditions.items():
                if self.__is_valid_name(v):
                    condition = f"{k} = {v}"
                    self.where_conditions.append(condition)
        return self

    def add_sql_group_by_condition(self, columns: list):
        if columns:
            self.group_by = columns
            return self
        else:
            raise Exception("No valid columns for group by")

    def add_sql_limit_condition(self, limit):
        if self.__is_valid_number(limit):
            self.limit = limit
            return self
        else:
            raise Exception("No valid limit value")

    def add_sql_offset_condition(self, offset):
        if self.__is_valid_number(offset):
            self.offset = offset
            return self
        else:
            raise Exception("No valid offset value")

    def add_sql_order_by_condition(self, attribute: str, order: Order):
        self.order_by = (attribute, order.name)
        return self

    def __build_select(self):
        if len(self.select_conditions) < 1:
            self.select_conditions.append("*")
        return ",".join(self.select_conditions)

    def __build_join(self):
        return """ """.join(self.join_clauses)

    def __build_where(self):
        if len(self.where_conditions) > 0:
            return "WHERE " + " AND ".join(self.where_conditions)
        else:
            return ""

    def __build_group_by(self):
        if len(self.group_by) > 0:
            groups = ", ".join(self.group_by)
            print(groups)
            return f"GROUP BY {groups}"
        else:
            return ""

    def __build_offset(self):
        if self.offset is not None:
            return "OFFSET {offset}".format(offset=self.offset)
        else:
            return ""

    def __build_limit(self):
        if self.limit is not None:
            return "LIMIT {limit}".format(limit=self.limit)
        else:
            return ""

    def __build_order_by(self):
        if self.order_by:
            attribute, order = self.order_by
            return f"ORDER BY {attribute} {order}"
        else:
            return ""

    def build(self):
        self.query = """
            SELECT {select_conditions} FROM {table_name}
            {join_clauses}
            {where_conditions}
            {group_by_condition}
            {order_by_condition}
            {offset_condition}
            {limit_condition}
        """.format(
            table_name=self.table_name,
            select_conditions=self.__build_select(),
            join_clauses=self.__build_join(),
            where_conditions=self.__build_where(),
            group_by_condition=self.__build_group_by(),
            order_by_condition=self.__build_order_by(),
            offset_condition=self.__build_offset(),
            limit_condition=self.__build_limit(),
        )
        return self

    def __clear(self):
        self.query = ""
        self.table_name = ""
        self.select_conditions = []
        self.where_conditions = []
        self.order_by = None
        self.group_by = []
        self.limit = None
        self.offset = None
        self.join_clauses = []

    def get_query(self):
        query = self.query
        self.__clear()
        return query
