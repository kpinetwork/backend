class QuerySQL:
    def __init__(self) -> None:
        pass

    def is_valid_table_name(self, name):
        return name and isinstance(name, str) and name.strip()

    def get_select_by_id_query(self, table_name: str, id: str) -> str:
        if self.is_valid_table_name(table_name):
            return "SELECT * FROM {table_name} WHERE id='{id}';".format(
                table_name=table_name, id=id
            )
        else:
            raise Exception("No valid table name")

    def get_select_query(self, table_name: str, offset: int, max_count: int) -> str:
        if self.is_valid_table_name(table_name):
            return """
                SELECT * FROM {table_name}
                LIMIT {limit}
                OFFSET {offset};
            """.format(
                table_name=table_name, limit=max_count, offset=offset
            )
        else:
            raise Exception("No valid table name")
