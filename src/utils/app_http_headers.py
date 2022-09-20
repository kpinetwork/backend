class AppHttpHeaders:
    def __init__(self, content_type: str, http_methods: str) -> None:
        self.content_type = content_type
        self.http_methods = http_methods

    def get_headers(self) -> dict:
        return {
            "Content-Type": self.content_type,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": self.http_methods,
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'self' *kpinetwork.com; "
            "script-src 'self' *kpinetwork.com; "
            "form-action 'none'; "
            "frame-ancestors 'none'",
        }
