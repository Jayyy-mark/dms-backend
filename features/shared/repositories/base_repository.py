from django.db import IntegrityError, transaction
from features.shared.exceptions.createException import CreateException
from features.roles.models import Role

class BaseRepository:

    def __init__(self, model, mapper):
        self.model = model
        self.mapper = mapper

    def generateId(self, field, prefix)->str:
        last_id = self.model.objects.order_by(f"-{field}").values_list(field, flat=True).first()
        if last_id:
            number = int(last_id.split("-")[1]) + 1
            return f"{prefix}-{number:03d}"
        else:
            number = 1
        return f"{prefix}-{number:03d}"

    def all(self):
        instances = self.model.objects.all()
        return [self.mapper.toEntity(i) for i in instances]
    
    def getById(self, id):
        instance = self.model.objects.get(id=id)
        return self.mapper.toEntity(instance)
    
    def getAllByColumns(self, entity):
        model_data = self.mapper.toModel(entity)
        instances = self.model.objects.filter(**model_data)
        return [ self.mapper.toEntity(i) for i in instances ]
    
    def existByName(self, entity)->bool:
        model_data = self.mapper.toModel(entity)
        return self.model.objects.filter(**model_data).exists()

    def create(self, entity):
        model_data = self.mapper.toModel(entity)
        instance = self.model.objects.create(**model_data)
        
        return self.mapper.toEntity(instance)
    
    def update(self, entity):
        instance = self.model.objects.get(id=entity.id)
        model_data = self.mapper.toModel(entity)
        for field, value in model_data.items():
            setattr(instance,field,value)
        
        instance.save()
        return self.mapper.toEntity(instance)
    
    def delete(self, entity)->bool:
        delete_count,_ = self.model.objects.filter(id=entity.id).delete()

        return delete_count > 0
        

    

