from rest_framework import serializers

class CreateScamRecordInputSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=10, min_length=10)
    description = serializers.CharField(required=False, allow_blank=True)

    
