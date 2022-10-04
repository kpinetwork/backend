from tags_repository import TagsRepository


class TagsService:
    def __init__(self, session, query_builder, response_sql, logger) -> None:
        self.logger = logger
        self.session = session
        self.query_builder = query_builder
        self.response_sql = response_sql
        self.repository = TagsRepository(session, query_builder, response_sql, logger)

    def get_companies_by_tag(self, tags: list) -> list:
        records = dict()
        for tag in tags:
            tag_data = dict()
            company_data = dict()
            tag_id = tag["id"]
            companies = []
            company_data["id"] = tag["company_id"]
            company_data["name"] = tag["company_name"]
            tag_data["id"] = tag_id
            tag_data["name"] = tag["name"]
            if tag_id in records:
                companies = records[tag_id]["companies"]
            companies.append(company_data)
            tag_data["companies"] = companies
            records[tag_id] = tag_data
        return records

    def get_all_tags(self, offset=0, max_count=None) -> dict:
        try:
            total_tags = self.repository.get_total_number_of_tags().get("count")
            tags = self.repository.get_tags_with_companies(offset, max_count)
            result = self.get_companies_by_tag(tags)

            return {"total": total_tags, "tags": result}
        except Exception as error:
            self.logger.error(error)
            return []
