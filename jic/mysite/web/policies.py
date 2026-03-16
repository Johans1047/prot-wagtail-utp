from wagtail.permission_policies import ModelPermissionPolicy


class SingletonPermissionPolicy(ModelPermissionPolicy):
    """Custom permission policy to ensure only one instance is created."""
    def user_has_permission(self, user, action):
        # Prevent 'add' if an instance already exists
        if action == 'add' and self.model.objects.exists():
            return False
        return super().user_has_permission(user, action)