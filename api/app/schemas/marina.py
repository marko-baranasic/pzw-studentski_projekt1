from pydantic import BaseModel, ConfigDict, Field


class MarinaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)


class MarinaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    city: str | None = Field(default=None, min_length=1, max_length=100)




class MarinaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str
