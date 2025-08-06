import logging
logger = logging.getLogger('realestate')

class LoggingMixin:
    """
    Logs CRUD actions and assigns request.user automatically if the model supports it.
    """
    def perform_create(self, serializer):
        # Only set `user` if the serializer has that field
        if 'user' in serializer.fields:
            instance = serializer.save(user=self.request.user)
        else:
            instance = serializer.save()

        user_id = getattr(self.request.user, 'id', 'Anonymous')
        logger.info(f"[CREATE] {instance.__class__.__name__} ID={instance.id} by User ID={user_id}")
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        user_id = getattr(self.request.user, 'id', 'Anonymous')
        logger.info(f"[UPDATE] {instance.__class__.__name__} ID={instance.id} by User ID={user_id}")
        return instance

    def perform_destroy(self, instance):
        user_id = getattr(self.request.user, 'id', 'Anonymous')
        logger.warning(f"[DELETE] {instance.__class__.__name__} ID={instance.id} by User ID={user_id}")
        return super().perform_destroy(instance)