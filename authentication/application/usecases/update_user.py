from authentication.infrastructure.user_repository import UserRepository
from authentication.domain.user_entity import UserEntity

class UpdateUserUseCase:

    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def execute(self, id: int, username: str = None, email: str = None, role: str = None, is_active: bool = None, password: str = None) -> UserEntity:
        return self.repo.update(id=id, username=username, email=email, role=role, is_active=is_active, password=password)
