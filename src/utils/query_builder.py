from enum import Enum


class QuerySQLBuilder:
    query: str

    def __init__(self) -> None:
        self.query = ""
        self.table_name = ""
        self.values_alias = ""
        self.select_conditions = []
        self.set_conditions = []
        self.values = []
        self.join_clauses = []
        self.where_conditions_conj = []
        self.where_conditions_disj = []
        self.limit = None
        self.offset = None
        self.group_by = []
        self.order_by: tuple[list, self.Order] = None

    class Order(Enum):
        DESC = "DESC"
        ASC = "ASC"

    class JoinType(Enum):
        JOIN = "INNER"
        LEFT = "LEFT"
        RIGTH = "RIGHT"

    def __is_valid_name(self, name: str):
        no_invalid_strings = name != "''" and name != "'None'"
        return name and isinstance(name, str) and name.strip() and no_invalid_strings

    def __is_valid_number(self, number: int):
        return number is not None and isinstance(number, int)

    def __get_join_table_name(self, table_name: str, join_type: JoinType):
        if self.__is_valid_name(table_name):
            return f"{join_type.value} JOIN {table_name}"
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

    def add_from_values_statement(self, values: dict = None, alias: str = ""):
        self.values_alias = alias
        if values:
            for k, v in values.items():
                value = f"('{k}',{v})"
                self.values.append(value)
        return self

    def add_set_conditions(self, conditions: dict = None):
        if conditions:
            for k, v in conditions.items():
                if self.__is_valid_name(k):
                    condition = f"{k} = {v}"
                    self.set_conditions.append(condition)
        return self

    def add_join_clause(
        self, clauses: dict = None, join_type: JoinType = JoinType.JOIN
    ):
        try:
            if clauses:
                for table_name, values in clauses.items():
                    join = self.__get_join_table_name(table_name, join_type)
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
                if isinstance(v, list):
                    values = [
                        element
                        for element in v
                        if self.__is_valid_name(element) and len(v) > 0
                    ]
                    if values:
                        joined_values = "(" + ", ".join(values) + ")"
                        condition = f"{k} IN {joined_values}"
                        self.where_conditions_disj.append(condition)
                else:
                    if isinstance(v, bool) or self.__is_valid_name(v):
                        condition = f"{k} = {v}"
                        self.where_conditions_conj.append(condition)
        return self

    def add_sql_group_by_condition(self, columns: list):
        if columns:
            self.group_by = columns
            return self
        else:
            raise Exception("No valid columns for group by")

    def add_sql_limit_condition(self, limit):
        if limit is None or self.__is_valid_number(limit):
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

    def add_sql_order_by_condition(self, attributes: list, order: Order):
        if attributes:
            self.order_by = (attributes, order.name)
        return self

    def __build_select(self):
        if len(self.select_conditions) < 1:
            self.select_conditions.append("*")
        return ",".join(self.select_conditions)

    def __build_set(self):
        set_query = ""
        if len(self.set_conditions) > 0:
            set_query += "SET " + ", ".join(self.set_conditions)
        return set_query

    def __build_from_values_statement(self):
        if len(self.values) > 0 and self.values_alias != "":
            return (
                "FROM "
                + "(values "
                + ",".join(self.values)
                + ") "
                + f"as {self.values_alias}"
            )
        elif len(self.values) > 0 and self.values_alias == "":
            return "FROM " + "(values " + ",".join(self.values) + ") "
        else:
            return ""

    def __build_join(self):
        return """ """.join(self.join_clauses)

    def __build_where(self):
        where_query = ""
        if len(self.where_conditions_conj) > 0:
            where_query += "WHERE " + " AND ".join(self.where_conditions_conj)
            if len(self.where_conditions_disj) > 0:
                where_query += " AND " + " AND ".join(self.where_conditions_disj)
        if not len(self.where_conditions_conj):
            if len(self.where_conditions_disj) > 0:
                where_query += "WHERE " + " AND ".join(self.where_conditions_disj)
        return where_query

    def __build_group_by(self):
        if len(self.group_by) > 0:
            groups = ", ".join(self.group_by)
            return f"GROUP BY {groups}"
        else:
            return ""

    def __build_offset(self):
        if (self.limit and self.offset) is not None:
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
            attributes, order = self.order_by
            values = ",".join(attributes)
            return f"ORDER BY {values} {order}"
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

    def build_update(self):
        self.query = """
            UPDATE {table_name}
            {set_clause}
            {from_statement}
            {where_conditions}
        """.format(
            table_name=self.table_name,
            set_clause=self.__build_set(),
            from_statement=self.__build_from_values_statement(),
            where_conditions=self.__build_where(),
        )
        return self

    def __clear(self):
        self.query = ""
        self.table_name = ""
        self.select_conditions = []
        self.set_conditions = []
        self.values = []
        self.where_conditions_conj = []
        self.where_conditions_disj = []
        self.order_by = None
        self.group_by = []
        self.limit = None
        self.offset = None
        self.join_clauses = []

    def get_query(self):
        query = self.query
        self.__clear()
        return query
