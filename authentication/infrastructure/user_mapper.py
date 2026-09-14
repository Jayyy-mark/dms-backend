from authentication.domain.user_entity import UserEntity
from authentication.models import MogUser
class UserMapper:

    @staticmethod
    def toEntity(user : MogUser)->UserEntity:
        return UserEntity(
            id=user.id,
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            is_staff=user.is_staff,
            last_login=user.last_login,
        )