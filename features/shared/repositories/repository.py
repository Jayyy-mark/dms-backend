class BaseRepository:

    def __init__(self, model, mapper):
        self.model = model
        self.mapper = mapper

    def create(self, entity):
        model_data = self.mapper.toModel(entity)
        try:
            instance = self.model.create(**model_data)
            return instance
        except Exception as e:
            return e
        