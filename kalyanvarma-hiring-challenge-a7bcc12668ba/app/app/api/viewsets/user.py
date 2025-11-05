from rest_framework.response import Response
from app.serializers import input, output
from app.models.user import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from app.utils.phone import normalize_phone, PhoneParseError


class CreateUser(APIView):
    permission_classes = (AllowAny,)
    input_serializer_class = input.CreateUserInputSerializer
    output_serializer_class = output.UserOutputSerializer

    def post(self, request, *args, **kwargs):
        input_serializer = self.input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        raw_phone=input_serializer.validated_data['phone_number']

        try:
            normalized_phone = normalize_phone(input_serializer.validated_data['phone_number'], default_region='IN')
        except PhoneParseError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if User.objects.filter(phone_number=raw_phone).exists():
                return Response({'error': 'User with this phone number already exists.'},
                                status=status.HTTP_400_BAD_REQUEST)

            user = User(
                name=input_serializer.validated_data['name'],
                phone_number=raw_phone,
                email=input_serializer.validated_data.get('email')
            )
            user.set_password(input_serializer.validated_data['password'])
            user.save()

            refresh = RefreshToken.for_user(user)
            tokens = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }

            output_serializer = self.output_serializer_class(user)
            return Response({'user': output_serializer.data, **tokens}, status=status.HTTP_201_CREATED)


class LoginUser(APIView):
    permission_classes = (AllowAny,)
    input_serializer_class = input.LoginUserInputSerializer
    output_serializer_class = output.UserOutputSerializer

    def post(self, request, *args, **kwargs):
        input_serializer = self.input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        phone_raw = input_serializer.validated_data['phone_number']
        password = input_serializer.validated_data['password']

        try:
            # phone_number = normalize_phone(phone_raw, default_region='IN')
            phone_number = phone_raw 
        except PhoneParseError:
            phone_number = phone_raw  # fallback

        with transaction.atomic():
            try:
                user = User.objects.get(phone_number=phone_number)
                if not user.check_password(password):
                    return Response({'error': 'Invalid password.'}, status=status.HTTP_400_BAD_REQUEST)
                status_code = status.HTTP_200_OK
            except User.DoesNotExist:
                # Auto-create new user
                user = User(phone_number=phone_number, name='', email=None)
                user.set_password(password)
                user.save()
                status_code = status.HTTP_201_CREATED

            refresh = RefreshToken.for_user(user)
            tokens = {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            output_serializer = self.output_serializer_class(user)
            return Response({'user': output_serializer.data, **tokens}, status=status_code)