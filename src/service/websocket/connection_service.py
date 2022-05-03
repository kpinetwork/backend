import uuid


class WebsocketConnectionService:
    def __init__(self, session, logger) -> None:
        self.table = "websocket"
        self.session = session
        self.logger = logger

    def register_connection(
        self, connection_id: str, username: str, filename: str
    ) -> bool:
        try:
            registration_id = str(uuid.uuid4())

            query = """
            INSERT INTO {table}
            VALUES ('{id}', '{connection}', '{filename}', '{user}');
            """.format(
                table=self.table,
                id=registration_id,
                connection=connection_id,
                filename=filename,
                user=username,
            )

            self.session.execute(query)
            self.session.commit()

            return True
        except Exception as error:
            self.logger.info(error)
            return False

    def remove_connection(self, connection_id: str) -> bool:
        try:
            query = """
            DELETE FROM {table}
            WHERE connection_id='{connection}';
            """.format(
                table=self.table, connection=connection_id
            )

            self.session.execute(query)
            self.session.commit()

            return True
        except Exception as error:
            self.logger.info(error)
            return False
