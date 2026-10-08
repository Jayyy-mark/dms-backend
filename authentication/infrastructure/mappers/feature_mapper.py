from authentication.domain.feature_entity import FeatureEntity
from authentication.domain.module_entity import ModuleEntity
from authentication.models import Feature


class FeatureMapper:

    @staticmethod
    def toEntity(feature: Feature):
        module_entity = None
        if feature.module:
            module_entity = ModuleEntity(
                id=feature.module.id,
                name=feature.module.name,
                status=feature.module.status,
            )
        return FeatureEntity(
            id=feature.id,
            name=feature.name,
            module=module_entity,
            status=feature.status,
        )
