from authentication.domain.module_entity import ModuleEntity
from authentication.models import Module
from authentication.application.contracts.module_contracts import ModuleCreateContract


class ModuleMapper:

    @staticmethod
    def toEntity(module: Module):
        return ModuleEntity(id=module.id, name=module.name, status=module.status)

    @staticmethod
    def toModel(contract: ModuleCreateContract):

        return Module(name=contract.name, status=contract.status)
