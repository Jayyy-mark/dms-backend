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
    def update(id: int, username: str, email: str, role: str) -> UserEntity:
        obj = MogUser.objects.get(id=id)
        obj.username = username
        obj.email = email
        obj.role = role
        obj.save()
        return UserMapper.toEntity(obj)
