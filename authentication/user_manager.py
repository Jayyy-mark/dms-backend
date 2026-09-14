from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def generate_user_id(self):
        """
        Auto-generate sequential user_id like USR-001, USR-002
        """
        last_user = self.model.objects.order_by("-id").first()
        if last_user and last_user.user_id:
            # Extract the numeric part and increment
            last_number = int(last_user.user_id.split("-")[1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"USR-{new_number:03d}"  # zero-padded, e.g., USR-001

    def create_user(self, email, password=None, **extraFields):
        if not email:
            raise ValueError("Email is required!")
        
        extraFields.setdefault("role", "user")
        
        if "user_id" not in extraFields or not extraFields["user_id"]:
            extraFields["user_id"] = self.generate_user_id()

        self.email = self.normalize_email(email=email)
        user = self.model(email=self.email, **extraFields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extraFields):
        print("Super user is about to create!")
        extraFields.setdefault("is_staff",True)
        extraFields.setdefault("is_superuser", True)
        extraFields.setdefault("role", "admin")
        return self.create_user(email=email, password=password, **extraFields)