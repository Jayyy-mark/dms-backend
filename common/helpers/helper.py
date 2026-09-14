class BaseRepository:

    @staticmethod
    def create(model, mapper,entity):
        model_data = mapper.toModel(entity)
        instance = model.objects.create(**model_data)

        return mapper.toEntity(instance)