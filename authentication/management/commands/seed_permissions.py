from django.core.management.base import BaseCommand
from authentication.models import Module, Feature, UserRole, UserRolePermission


class Command(BaseCommand):
    help = "Seed initial modules, features, user roles, and default permissions"

    def handle(self, *args, **options):
        self.stdout.write("Seeding modules and features...")
        self._seed_modules_and_features()

        self.stdout.write("Seeding user roles...")
        self._seed_user_roles()

        self.stdout.write("Seeding default permissions...")
        self._seed_default_permissions()

        self.stdout.write(self.style.SUCCESS("Seed completed successfully!"))

    def _seed_modules_and_features(self):
        modules_data = [
            {
                "id": 1,
                "name": "Staffs & HR Information",
                "features": [
                    "employees", "staff_types", "roles", "ranks",
                    "promotions", "transfers", "training", "overseas",
                    "awards", "punishments", "reports",
                ],
            },
            {
                "id": 2,
                "name": "Documents Management",
                "features": [
                    "documents", "archives", "recycle_bin",
                    "dtypes", "categories", "deepsearch",
                ],
            },
            {
                "id": 3,
                "name": "Departments & Facilities",
                "features": ["departments", "buildings", "rooms"],
            },
            {
                "id": 4,
                "name": "User Management & AI",
                "features": ["users", "chatbot"],
            },
            {
                "id": 5,
                "name": "System & Activity Records",
                "features": ["locations", "calendar", "logs"],
            },
        ]

        feature_id_counter = 1

        for mod_data in modules_data:
            module, created = Module.objects.get_or_create(
                id=mod_data["id"],
                defaults={"name": mod_data["name"], "status": True},
            )
            if created:
                self.stdout.write(f"  Created module: {module.name}")
            else:
                self.stdout.write(f"  Module already exists: {module.name}")

            for feature_name in mod_data["features"]:
                feature, f_created = Feature.objects.get_or_create(
                    name=feature_name,
                    defaults={
                        "id": feature_id_counter,
                        "status": True,
                        "module": module,
                    },
                )
                if f_created:
                    self.stdout.write(f"    Created feature: {feature_name} (id={feature_id_counter})")
                else:
                    self.stdout.write(f"    Feature already exists: {feature_name}")
                feature_id_counter += 1

    def _seed_user_roles(self):
        default_roles = [
            {"id": 1, "name": "Admin"},
            {"id": 2, "name": "Super Admin"},
            {"id": 3, "name": "User"},
        ]

        for role_data in default_roles:
            role, created = UserRole.objects.get_or_create(
                id=role_data["id"],
                defaults={"name": role_data["name"]},
            )
            if created:
                self.stdout.write(f"  Created role: {role.name}")
            else:
                self.stdout.write(f"  Role already exists: {role.name}")

    def _seed_default_permissions(self):
        roles = UserRole.objects.all()
        features = Feature.objects.all()

        perm_id_counter = (
            UserRolePermission.objects.order_by("-id")
            .values_list("id", flat=True)
            .first()
            or 0
        ) + 1

        for role in roles:
            existing_feature_ids = set(
                UserRolePermission.objects.filter(userRole=role).values_list("feature_id", flat=True)
            )
            is_full_access = role.name.lower() in ["admin", "super admin"]

            permissions_to_create = []
            for feature in features:
                if feature.id not in existing_feature_ids:
                    permissions_to_create.append(
                        UserRolePermission(
                            id=perm_id_counter,
                            userRole=role,
                            feature=feature,
                            can_view=True,
                            can_create=is_full_access,
                            can_edit=is_full_access,
                            can_delete=is_full_access,
                        )
                    )
                    perm_id_counter += 1

            if permissions_to_create:
                UserRolePermission.objects.bulk_create(permissions_to_create)
                self.stdout.write(
                    f"  Created {len(permissions_to_create)} missing permissions for role '{role.name}'"
                )
            else:
                self.stdout.write(
                    f"  All permissions already exist for role '{role.name}'. Skipping."
                )
