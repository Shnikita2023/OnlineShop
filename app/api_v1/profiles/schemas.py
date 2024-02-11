from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    user_id: int = Field(default=1)
    first_name: str | None
    last_name: str | None
    bio: str | None


class ProfileShow(ProfileCreate):
    model_config = ConfigDict(strict=True)
    id: int


class ProfileUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    bio: str | None
