from rest_framework import serializers
from app.models.scam import ScamRecord
from app.serializers.output import UserOutputSerializer

class ScamRecordOutputSerializer(serializers.ModelSerializer):
    reported_by = UserOutputSerializer()
    spammed_by_count = serializers.SerializerMethodField()
    class Meta:
        model = ScamRecord
        fields = (
            'id',
            'phone_number',
            'spammed_by_count',
            'description',
            'reported_by',
            'created_at',
            'updated_at'
        )

    def get_spammed_by_count(self, obj: ScamRecord):
        return ScamRecord.objects.filter(phone_number=obj.phone_number).count()