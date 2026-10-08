from authentication.infrastructure.repositories.module_repository import ModuleRepository
from authentication.infrastructure.repositories.feature_repository import FeatureRepository


class ModuleService:

    def __init__(self):
        self.module_repo = ModuleRepository()
        self.feature_repo = FeatureRepository()

    def get_all_modules_with_features(self):
        """Returns all modules with nested features."""
        grouped = self.feature_repo.get_all_grouped()
        result = []
        for group in grouped:
            module = group["module"]
            features = group["features"]
            result.append({
                "id": module.id,
                "name": module.name,
                "status": module.status,
                "features": [
                    {
                        "id": f.id,
                        "name": f.name,
                        "status": f.status,
                    }
                    for f in features
                ],
            })
        return result

    def toggle_feature_status(self, feature_id: int, status: bool):
        entity = self.feature_repo.update_status(feature_id, status)
        return {"id": entity.id, "name": entity.name, "status": entity.status}

    def bulk_update_features(self, status: bool):
        self.feature_repo.bulk_update_status(status)

    def reset_features(self):
        self.feature_repo.reset_all()

    def get_feature_status_map(self):
        """Returns a dict of feature_name -> status for sidebar use."""
        features = self.feature_repo.all()
        return {f.name: f.status for f in features}
