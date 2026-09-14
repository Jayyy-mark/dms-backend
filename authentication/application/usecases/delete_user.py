from authentication.infrastructure.user_repository import UserRepository

class DeleteUserUseCase:

    def __init__(self, repo  : UserRepository):
        self.repo = repo

    def execute(self, id:int)->str:
        res = self.repo.delete(id=id)

        if res:
            return "User deleted Successfully!"
        else:
            return "Failed to delete User!"
