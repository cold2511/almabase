from rest_framework import serializers


class CreateContactInputSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    phone_number = serializers.CharField(required=True, max_length=10, min_length=10)