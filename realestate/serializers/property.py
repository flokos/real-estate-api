from rest_framework import serializers
from ..models import Property
from django.db.models import Q
from decimal import Decimal
class PropertySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Property
        fields = ["id", "user", "title", "district", "estimated_value", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_estimated_value(self, value):
        if self.instance:  # Only on update
            invalid_exists = self.instance.transactions.filter(
                Q(price__lt=(Decimal('0.5') * value)) | Q(price__gt=(Decimal('1.5') * value))
            ).exists()
            if invalid_exists:
                raise serializers.ValidationError(
                    "Updating estimated value would make one or more transactions fall outside the 50%-150% price range."
                )
        return value