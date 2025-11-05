from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404

from app.serializers.input.interaction import CreateInteractionInputSerializer
from app.serializers.output.interaction import InteractionOutputSerializer
from app.models.interaction import Interaction
from app.models.user import User
from app.utils.phone import normalize_phone  # reuse existing helper if available

class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class CreateInteraction(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    input_serializer_class = CreateInteractionInputSerializer
    output_serializer_class = InteractionOutputSerializer

    def post(self, request):
        serializer = self.input_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        initiator = request.user

        receiver_phone = data.get("receiver_phone")
        if receiver_phone:
            try:
                receiver_phone = normalize_phone(receiver_phone)
            except Exception:
                import re
                digits = re.sub(r"\D", "", receiver_phone)
                receiver_phone = digits[-10:] if len(digits) >= 10 else digits

        receiver_user = None
        if data.get("receiver_user_id"):
            receiver_user = get_object_or_404(User, id=data["receiver_user_id"])

        with transaction.atomic():
            inter = Interaction.objects.create(
                initiator=initiator,
                receiver_user=receiver_user,
                receiver_phone=receiver_phone,
                type=data["type"],
                metadata=data.get("metadata", {}) or {}
            )

        out = self.output_serializer_class(inter)
        return Response(out.data, status=status.HTTP_201_CREATED)

class RecentInteractions(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    pagination_class = StandardPagination
    output_serializer_class = InteractionOutputSerializer

    def get(self, request):
        itype = request.query_params.get("type")
        qs = Interaction.objects.filter(initiator=request.user)
        if itype:
            qs = qs.filter(type=itype)
        qs = qs.order_by("-timestamp")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        serializer = self.output_serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class TopContacts(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        n = int(request.query_params.get("n", 5))
        include_external = request.query_params.get("include_external", "false").lower() == "true"

        top_users = (
            Interaction.objects.filter(initiator=request.user, receiver_user__isnull=False)
            .values("receiver_user")
            .annotate(count=Count("id"))
            .order_by("-count")[:n]
        )

        results = []
        for r in top_users:
            user_id = r["receiver_user"]
            user = User.objects.filter(id=user_id).first()
            if user:
                results.append({
                    "type": "user",
                    "id": str(user.id),
                    "name": user.get_full_name(),
                    "phone_number": getattr(user, "phone_number", None),
                    "count": r["count"]
                })

        if include_external and len(results) < n:
            remaining = n - len(results)
            top_external = (
                Interaction.objects.filter(initiator=request.user, receiver_user__isnull=True, receiver_phone__isnull=False)
                .values("receiver_phone")
                .annotate(count=Count("id"))
                .order_by("-count")[:remaining]
            )
            for r in top_external:
                results.append({
                    "type": "external",
                    "phone_number": r["receiver_phone"],
                    "count": r["count"]
                })

        return Response(results, status=status.HTTP_200_OK)

class SpamAggregation(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        limit = int(request.query_params.get("limit", 100))

        qs = Interaction.objects.filter(type=Interaction.SPAM_REPORT)
        if start:
            qs = qs.filter(timestamp__gte=start)
        if end:
            qs = qs.filter(timestamp__lte=end)

        agg_by_phone = (
            qs.values("receiver_phone")
            .annotate(reports=Count("id"))
            .order_by("-reports")[:limit]
        )

        agg_by_user = (
            qs.filter(receiver_user__isnull=False)
            .values("receiver_user")
            .annotate(reports=Count("id"))
            .order_by("-reports")[:limit]
        )

        return Response({
            "by_phone": list(agg_by_phone),
            "by_user": list(agg_by_user)
        }, status=status.HTTP_200_OK)