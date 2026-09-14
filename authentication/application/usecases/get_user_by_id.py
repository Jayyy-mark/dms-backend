from authentication.infrastructure.user_repository import UserRepository
from authentication.application.contracts.user_response import UserResponseContract


class GetUserByIdUserCase:

    def __init__(self, repo : UserRepository):
        self.repo = repo

    def execute(self, user_id:int)->UserResponseContract:
        user = self.repo.getById(user_id)
        return UserResponseContract(
            id=user.id,
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
        )