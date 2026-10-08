from authentication.models import MogUser
from .user_mapper import UserMapper
from authentication.domain.user_entity import UserEntity


class UserRepository:

    @staticmethod
    def all() -> list[UserEntity]:
        users = MogUser.objects.all()
        return [UserMapper.toEntity(user) for user in users]

    @staticmethod
    def getById(id: int) -> UserEntity:
        user = MogUser.objects.get(id=id)
        return UserMapper.toEntity(user)

    @staticmethod
    def delete(id: int) -> bool:
        obj = MogUser.objects.get(id=id)
        obj.delete()
        return True

    @staticmethod
    def update(id: int, username: str = None, email: str = None, role: str = None, is_active: bool = None, password: str = None) -> UserEntity:
        obj = MogUser.objects.get(id=id)
        if username is not None:
            obj.username = username
        if email is not None:
            obj.email = email
        if role is not None:
            obj.role = role
        if is_active is not None:
            if isinstance(is_active, str):
                is_active = is_active.lower() in ["true", "1", "yes"]
            obj.is_active = bool(is_active)
        if password:
            obj.set_password(password)
        obj.save()
        return UserMapper.toEntity(obj)
