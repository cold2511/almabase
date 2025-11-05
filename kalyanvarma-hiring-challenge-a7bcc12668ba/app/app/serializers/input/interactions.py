from rest_framework import serializers

class CreateInteractionInputSerializer(serializers.Serializer):
    receiver_phone = serializers.CharField(required=False, allow_blank=True, max_length=30)
    receiver_user_id = serializers.UUIDField(required=False)
    type = serializers.ChoiceField(choices=["call", "message", "spam_report"])
    metadata = serializers.DictField(required=False, child=serializers.CharField(), allow_empty=True)

    def validate(self, data):
        if not data.get("receiver_user_id") and not data.get("receiver_phone"):
            raise serializers.ValidationError("Provide either receiver_user_id or receiver_phone.")
        return data