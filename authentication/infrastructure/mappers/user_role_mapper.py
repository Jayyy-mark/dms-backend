from authentication.domain.user_role_entity import UserRoleEntity
from authentication.models import UserRole


class UserRoleMapper:

    @staticmethod
    def toEntity(userRole: UserRole):

        return UserRoleEntity(id=userRole.id, name=userRole.name)
