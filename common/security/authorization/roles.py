class Roles:
    SUPER_ADMIN = "super admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

    # Roles with full, unfiltered access to all data
    PRIVILEGED = {"super admin", "admin"}
