from rest_framework import serializers
from app.models.user import User
from app.models.contact import Contact
from app.models.scam import ScamRecord


class SearchOutputSerializer(serializers.Serializer):
    """
    Serializer for summarized search results across both Users and Contacts.
    """

    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    phone_number = serializers.CharField()
    spammed_by_count = serializers.SerializerMethodField()

    def get_name(self, obj):
        if isinstance(obj, User) or isinstance(obj, Contact):
            return obj.get_full_name()
        return None

    def get_is_registered(self, obj):
        return isinstance(obj, User)

    def get_spammed_by_count(self, obj):
        phone = getattr(obj, "phone_number", None)
        if not phone:
            return 0

        # Prefer context-based lookup for performance
        spam_counts = self.context.get("spam_counts", {})
        if spam_counts:
            return spam_counts.get(phone, 0)

        # Fallback (in case context not provided)
        return ScamRecord.objects.filter(phone_number=phone).count()


class SearchDetailsUserOutputSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a registered User returned by SearchDetailsView.
    """

    full_name = serializers.SerializerMethodField()
    spammed_by_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "spammed_by_count",
        )

    def get_full_name(self, obj: User):
        return obj.get_full_name()

    def get_spammed_by_count(self, obj: User):
        spam_counts = self.context.get("spam_counts", {})
        return spam_counts.get(obj.phone_number, 0)


class ContactOutputSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a saved Contact returned by SearchDetailsView.
    """

    full_name = serializers.SerializerMethodField()
    spammed_by_count = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "spammed_by_count",
        )

    def get_full_name(self, obj: Contact):
        return obj.get_full_name()

    def get_spammed_by_count(self, obj: Contact):
        spam_counts = self.context.get("spam_counts", {})
        return spam_counts.get(obj.phone_number, 0)