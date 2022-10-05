from base_exception import AppError
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

    def update_tags_from_tag_panel(self, tags_data: dict) -> bool:
        is_empty = not any(
            filter(
                lambda tag: tag.get("name")
                or tag.get("companies_to_delete")
                or tag.get("companies_to_add"),
                tags_data.values(),
            )
        )
        if is_empty:
            raise AppError("There isn't data to modify")

        return self.repository.update_tags(tags_data)

    def update_company_tags(self, company_tags_data: dict) -> bool:
        is_empty = not (
            company_tags_data.get("company_id")
            and (
                company_tags_data.get("tags_to_delete")
                or company_tags_data.get("tags_to_add")
            )
        )
        if is_empty:
            raise AppError("There isn't data to modify")

        return self.repository.update_company_tags(
            company_tags_data.get("company_id"),
            company_tags_data.get("tags_to_add"),
            company_tags_data.get("tags_to_delete"),
        )

    def update_tags(self, tags_body: dict) -> bool:
        if "tags" in tags_body:
            return self.update_tags_from_tag_panel(tags_body.get("tags"))

        return self.update_company_tags(tags_body.get("company"))
