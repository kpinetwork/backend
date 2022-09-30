from tags_repository import TagsRepository


class TagsService:
    def __init__(self, session, query_builder, response_sql, logger) -> None:
        self.logger = logger
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.repository = TagsRepository(session, query_builder, response_sql, logger)

    def get_all_tags(self, offset=0, max_count=None) -> dict:
        try:
            total_tags = self.repository.get_total_number_of_tags().get("count")
            tags = self.repository.get_tags(offset, max_count)

            return {"total": total_tags, "tags": tags}
        except Exception as error:
            self.logger.info(error)
            return []
