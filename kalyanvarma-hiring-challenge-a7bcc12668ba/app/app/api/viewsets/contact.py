from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import IntegrityError, transaction

from app.serializers import input, output
from app.models.contact import Contact


def normalize_phone(phone_number: str) -> str:
    """Normalize phone number to store only the 10-digit version."""
    import re
    digits = re.sub(r"\D", "", phone_number)  # remove all non-digits
    return digits[-10:] if len(digits) >= 10 else digits


class CreateContact(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    input_serializer_class = input.CreateContactInputSerializer
    output_serializer_class = output.ContactOutputSerializer

    def post(self, request):
        input_serializer = self.input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user = request.user

        # Normalize phone number before saving
        phone_number = normalize_phone(input_serializer.validated_data['phone_number'])

        if len(phone_number) != 10:
            return Response(
                {"error": "Invalid phone number format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            try:
                contact = Contact.objects.create(
                    first_name=input_serializer.validated_data['first_name'],
                    last_name=input_serializer.validated_data.get('last_name', ''),
                    phone_number=phone_number,
                    created_by=user,
                    updated_by=user,
                )
            except IntegrityError:
                return Response(
                    {"error": "Contact with this phone number already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        output_serializer = self.output_serializer_class(contact)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)