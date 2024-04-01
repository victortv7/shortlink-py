from pydantic import BaseModel, HttpUrl


class URL(BaseModel):
    long_url: str
    short_link: str
    access_count: int = 0


class CreateLinkRequest(BaseModel):
    long_url: HttpUrl


class CreateLinkResponse(BaseModel):
    short_link: str


class LinkStatsResponse(BaseModel):
    long_url: str
    short_link: str
    access_count: int
