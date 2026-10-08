from authentication.models import Module


class ModuleRepository:

    
    @staticmethod
    def all() -> list[Module]:
        return list(Module.objects.all())

    @staticmethod
    def create(module: Module) -> Module:

        module.save(force_insert=True)
        return module

    @staticmethod
    def update(module: Module) -> Module:

        module.save(
            update_fields=[
                "name",
                "status",
            ],
            force_update=True,
        )

        return module

    @staticmethod
    def delete(module_id: int) -> None:
        Module.objects.filter(id=module_id).delete()
