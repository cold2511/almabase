from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import IntegrityError, transaction

from app.serializers import input, output
from app.models.scam import ScamRecord
from app.utils.phone import normalize_phone


class CreateScamRecord(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    input_serializer_class = input.CreateScamRecordInputSerializer
    output_serializer_class = output.ScamRecordOutputSerializer

    def post(self, request):
        input_serializer = self.input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        user = request.user

        phone = normalize_phone(input_serializer.validated_data["phone_number"])

        # Prevent duplicates
        if ScamRecord.objects.filter(reported_by=user, phone_number=phone).exists():
            return Response(
                {"error": "You have already reported this number as spam."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            try:
                scam = ScamRecord.objects.create(
                    reported_by=user,
                    created_by=user,
                    updated_by=user,
                    phone_number=phone,
                    description=input_serializer.validated_data.get("description", ""),
                )
            except IntegrityError:
                return Response(
                    {"error": "Failed to record spam report."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        output_serializer = self.output_serializer_class(scam)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)