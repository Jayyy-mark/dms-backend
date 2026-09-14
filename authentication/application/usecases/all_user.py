from authentication.infrastructure.user_repository import UserRepository
from authentication.application.contracts.user_response import UserResponseContract
class AllUserUseCase:

    def __init__(self, repo : UserRepository):
        self.repo = repo

    def execute(self)->list[UserResponseContract]:
        
        users = self.repo.all();

        return [
            UserResponseContract(
                id=user.id,
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_staff=user.is_staff,
                last_login=user.last_login
            )
            for user in users
        ]