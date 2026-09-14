from authentication.infrastructure.user_repository import UserRepository
from authentication.domain.user_entity import UserEntity

class UpdateUserUseCase:

    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def execute(self, id: int, username: str, email: str, role: str) -> UserEntity:
        return self.repo.update(id=id, username=username, email=email, role=role)
