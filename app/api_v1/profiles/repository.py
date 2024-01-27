from app.api_v1.profiles import Profile
from app.api_v1.repositories.base_repository import SQLAlchemyRepository


class ProfileRepository(SQLAlchemyRepository):
    model = Profile



