from django.db import transaction
from rest_framework import viewsets, status, permissions
from ..permissions import IsOwnerOrAdminOrReadOnly
from rest_framework.response import Response
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter
from ..models import Transaction, Property
from ..serializers.transaction import TransactionSerializer
from rest_framework.exceptions import ValidationError
from ..mixins import LoggingMixin
import logging

logger = logging.getLogger('realestate')

class TransactionFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user__id", lookup_expr="exact")
    property_id = filters.NumberFilter(field_name="property__id", lookup_expr="exact")
    district = filters.CharFilter(field_name="property__district", lookup_expr="exact")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_percentage = filters.NumberFilter(field_name="percentage", lookup_expr="gte")
    max_percentage = filters.NumberFilter(field_name="percentage", lookup_expr="lte")
    date_from = filters.IsoDateTimeFilter(field_name="transaction_date", lookup_expr="gte")
    date_to = filters.IsoDateTimeFilter(field_name="transaction_date", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = []  # Explicitly say "no auto-generated filters"

class TransactionViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Transaction.objects.all().select_related('user', 'property')
    serializer_class = TransactionSerializer
    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_class = TransactionFilter
    ordering_fields = ['price', 'transaction_date']
    ordering = ['price', 'transaction_date']
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]

    def _lock_property(self, property_id, user_id, action="create"):
        """Lock a property row and return it, or raise a ValidationError."""
        try:
            locked_property = Property.objects.select_for_update().get(pk=property_id)
            logger.debug(f"Lock acquired for property {property_id} by user {user_id}")
            return locked_property
        except Property.DoesNotExist:
            logger.warning(f"Transaction {action} failed for user {user_id}: Property {property_id} not found.")
            raise ValidationError({"property": "Property does not exist."})

    def _validate_and_get_serializer(self, *, data, context, instance=None, partial=False):
        """Bind and validate a serializer inside a lock with consistent logging."""
        serializer = self.get_serializer(instance, data=data, partial=partial, context=context)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.warning(f"Transaction validation failed for user {self.request.user.id}: {e.detail}")
            raise
        return serializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        property_id = request.data.get('property')
        if not property_id:
            logger.warning(f"Transaction creation failed for user {request.user.id}: Missing property field.")
            raise ValidationError({"property": "This field is required."})

        locked_property = self._lock_property(property_id, request.user.id, "creation")
        serializer = self._validate_and_get_serializer(
            data=request.data,
            context={'locked_property': locked_property, 'request': request}
        )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        #Pre-check: Prevent property change before locking
        if 'property' in request.data and int(request.data['property']) != instance.property.id:
            logger.warning(
                f"User {request.user.id} attempted to change property on transaction {instance.id} "
                f"(from {instance.property.id} to {request.data['property']})."
            )
            raise ValidationError({"property": "You cannot change the property of a transaction."})

        locked_property = self._lock_property(instance.property.id, request.user.id, "update")
        serializer = self._validate_and_get_serializer(
            data=request.data,
            context={'locked_property': locked_property, 'request': request},
            instance=instance,
            partial=partial
        )

        self.perform_update(serializer)
        return Response(serializer.data)