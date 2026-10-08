from authentication.models import UserRole
from authentication.infrastructure.mappers.user_role_mapper import UserRoleMapper
from authentication.domain.user_role_entity import UserRoleEntity


class UserRoleRepository:

    @staticmethod
    def all() -> list[UserRoleEntity]:
        roles = UserRole.objects.all().order_by("id")
        return [UserRoleMapper.toEntity(role) for role in roles]

    @staticmethod
    def get_by_id(role_id: int) -> UserRoleEntity:
        role = UserRole.objects.get(id=role_id)
        return UserRoleMapper.toEntity(role)

    @staticmethod
    def get_by_name(name: str):
        try:
            role = UserRole.objects.get(name__iexact=name)
            return UserRoleMapper.toEntity(role)
        except UserRole.DoesNotExist:
            return None

    @staticmethod
    def create(name: str) -> UserRoleEntity:
        max_id = UserRole.objects.order_by("-id").values_list("id", flat=True).first() or 0
        role = UserRole(id=max_id + 1, name=name)
        role.save(force_insert=True)
        return UserRoleMapper.toEntity(role)

    @staticmethod
    def delete(role_id: int) -> None:
        UserRole.objects.filter(id=role_id).delete()
