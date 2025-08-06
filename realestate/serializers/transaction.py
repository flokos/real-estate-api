from rest_framework import serializers
from ..models import Transaction
from django.utils.timezone import now
from django.db.models import Sum
from django.db.models import Q
from decimal import Decimal
import logging

logger = logging.getLogger('realestate')

class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    transaction_date = serializers.DateTimeField()

    class Meta:
        model = Transaction
        fields = ["id", "user", "property", "percentage", "price", "transaction_date", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate(self, data):
        request = self.context.get('request')
        instance = getattr(self, "instance", None)
        user_obj = getattr(instance, 'user', getattr(request, 'user', None))
        property_obj = self.context.get('locked_property')
        percentage = data.get('percentage', getattr(instance, 'percentage', None))
        price = data.get('price', getattr(instance, 'price', None))
        transaction_date = data.get('transaction_date', getattr(instance, 'transaction_date', None))

        logger.debug(
            f"[VALIDATION] user={getattr(user_obj, 'id', None)}, property={getattr(property_obj, 'id', None)}, "
            f"percentage={percentage}, price={price}, date={transaction_date}"
        )

        # 1. Date validation
        if transaction_date > now():
            logger.debug(f"[VALIDATION FAILED] Future transaction date: {transaction_date}")
            raise serializers.ValidationError({"transaction_date":"Transaction date cannot be in the future."})

        results = (Transaction.objects.filter(property=property_obj).
        exclude(id=getattr(instance, "id", None)). #this is to not recalculate the instance being updated since it is added later
        aggregate(
            total=Sum('percentage'),
            user_total=Sum('percentage', filter=Q(user=user_obj))
        ))

        existing_percentage = results['total'] or 0
        user_percentage = results['user_total'] or 0
        logger.debug(f"[VALIDATION] Ownership totals: total={existing_percentage}, user_total={user_percentage}")

        # 2. Total ownership validation
        if existing_percentage + percentage > 100:
            logger.debug(f"[VALIDATION FAILED] Total ownership would exceed 100%: {existing_percentage + percentage}")
            raise serializers.ValidationError({"percentage":"Total ownership percentage exceeds 100%."})

        # 3. User ownership limit
        if user_percentage + percentage > 80:
            logger.debug(f"[VALIDATION FAILED] User ownership would exceed 80%: {user_percentage + percentage}")
            raise serializers.ValidationError({"percentage":"User cannot own more than 80% of a property."})

        # 4. Price validation: within ±50% of estimated value
        min_price = property_obj.estimated_value * Decimal('0.5')
        max_price = property_obj.estimated_value * Decimal('1.5')
        if not (min_price <= price <= max_price):
            logger.debug(f"[VALIDATION FAILED] Price {price} outside range ({min_price} - {max_price})")
            raise serializers.ValidationError({"price":"Price must be between 50% and 150% of property's estimated value."})

        # 4. Price validation: minimum value of 10000
        if price < 10000:
            logger.debug(f"[VALIDATION FAILED] Price {price} below minimum threshold")
            raise serializers.ValidationError({"price":"Minimum transaction amount is €10,000."})

        return data
