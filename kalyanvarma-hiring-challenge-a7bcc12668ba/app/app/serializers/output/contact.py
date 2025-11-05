from rest_framework import serializers
from app.models.contact import Contact
from app.models.scam import ScamRecord

class ContactOutputSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    spammed_by_count = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'id', 
            'first_name', 
            'last_name', 
            'full_name', 
            'spammed_by_count',
            'phone_number', 
        )

    def get_spammed_by_count(self, obj: Contact):
        return ScamRecord.objects.filter(phone_number=obj.phone_number).count()

    def get_full_name(self, obj: Contact):
        return obj.get_full_name()