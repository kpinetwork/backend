from collections import defaultdict

from tags_repository import TagsRepository
from base_exception import AppError


class TagsService:
    def __init__(self, logger, repository: TagsRepository) -> None:
        self.logger = logger
        self.repository = repository

    def get_all_tags_response(self, total_tags: int, tags: list) -> dict:
        return {"total": total_tags, "tags": tags}

    def get_companies_by_tag(self, tags: list) -> list:
        records = defaultdict(dict)
        for tag in tags:
            companies = []
            tag_id = tag["id"]
            tag_data = {"id": tag_id, "name": tag["name"]}
            if tag_id in records:
                companies = records[tag_id]["companies"]
            if tag.get("company_id") and tag.get("company_name"):
                companies.append({"id": tag["company_id"], "name": tag["company_name"]})
            records[tag_id].update(tag_data)
            records[tag_id]["companies"] = companies
        return list(records.values())

    def get_all_tags(
        self, access: bool, offset: int = 0, max_count: int = None
    ) -> dict:
        try:
            total_tags = self.repository.get_total_number_of_tags().get("count")

            if not access:
                return self.get_all_tags_response(
                    total_tags, self.repository.get_tags(offset, max_count)
                )

            return self.get_all_tags_response(
                total_tags,
                self.get_companies_by_tag(
                    self.repository.get_tags_with_companies(offset, max_count)
                ),
            )

        except Exception as error:
            self.logger.error(error)
            raise AppError("Can't get tags")

    def get_tags_by_company(self, company_id: str) -> list:
        try:
            if not company_id and not company_id.strip():
                raise AppError("Invalid company ID")
            return self.repository.get_tags_by_company(company_id)
        except Exception as error:
            self.logger.error(error)
            raise AppError(f"Can't get tags: {error}")

    def add_tag(self, tag: dict) -> dict:
        try:
            return self.repository.add_tag(tag)
        except Exception as error:
            self.logger.error(error)
            raise AppError(f"Cannot add new tag: {error}")

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

    def delete_tags(self, tag_ids: list) -> bool:
        if not tag_ids:
            raise AppError("No tags to delete")
        return self.repository.delete_tags(tag_ids)
