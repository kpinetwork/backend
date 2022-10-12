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
