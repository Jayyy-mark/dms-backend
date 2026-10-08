from authentication.models import Feature, Module
from authentication.infrastructure.mappers.feature_mapper import FeatureMapper
from authentication.domain.feature_entity import FeatureEntity


class FeatureRepository:

    @staticmethod
    def all() -> list[FeatureEntity]:
        features = Feature.objects.select_related("module").all().order_by("id")
        return [FeatureMapper.toEntity(f) for f in features]

    @staticmethod
    def get_by_id(feature_id: int) -> FeatureEntity:
        feature = Feature.objects.select_related("module").get(id=feature_id)
        return FeatureMapper.toEntity(feature)

    @staticmethod
    def update_status(feature_id: int, status: bool) -> FeatureEntity:
        feature = Feature.objects.select_related("module").get(id=feature_id)
        feature.status = status
        feature.save(update_fields=["status"])
        return FeatureMapper.toEntity(feature)

    @staticmethod
    def bulk_update_status(status: bool) -> None:
        Feature.objects.all().update(status=status)

    @staticmethod
    def reset_all() -> None:
        Feature.objects.all().update(status=True)

    @staticmethod
    def get_all_grouped():
        """Returns modules with their features for the permission matrix."""
        modules = Module.objects.prefetch_related("features").all().order_by("id")
        result = []
        for module in modules:
            features = module.features.all().order_by("id")
            result.append({
                "module": module,
                "features": list(features),
            })
        return result
