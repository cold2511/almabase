from rest_framework import serializers
from app.models.interaction import Interaction
from app.serializers.output import UserOutputSerializer

class InteractionOutputSerializer(serializers.ModelSerializer):
    initiator = UserOutputSerializer(read_only=True)
    receiver_user = UserOutputSerializer(read_only=True)
    receiver_phone = serializers.CharField(allow_null=True)

    class Meta:
        model = Interaction
        fields = (
            "id",
            "initiator",
            "receiver_user",
            "receiver_phone",
            "type",
            "timestamp",
            "metadata",
        )