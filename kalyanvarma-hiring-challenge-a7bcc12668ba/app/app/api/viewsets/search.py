from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from app.models import User, contact, ScamRecord
from app.serializers import output
from app.utils.phone import normalize_phone


class SearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


def get_query_type(query: str):
    if not query:
        return None
    query = query.strip()
    return "phone_number" if query[0].isdigit() else "full_name"


class SearchView(APIView):
    """
    GET /api/search?q=<query>
    - Search global directory by name or phone number.
    - Supports fuzzy name search & exact phone number match.
    - Returns deduplicated, paginated results with spam stats.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    output_serializer_class = output.SearchOutputSerializer
    pagination_class = SearchPagination

    def get(self, request):
        query = request.query_params.get("q", None)
        if not query or not query.strip():
            return Response({"error": "Search query is required."}, status=400)

        query_type = get_query_type(query)
        results = []

        if query_type == "phone_number":
            normalized_query = normalize_phone(query)
            # Search exact phone match across Users and Contacts
            user_matches = list(User.objects.filter(phone_number=normalized_query))
            contact_matches = list(Contact.objects.filter(phone_number=normalized_query))
            results = user_matches + contact_matches

        elif query_type == "full_name":
            # Startswith matches (rank 1)
            user_starts = User.objects.filter(
                Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
            )
            contact_starts = Contact.objects.filter(
                Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
            )

            # Contains matches (rank 2)
            user_contains = User.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).exclude(id__in=user_starts)
            contact_contains = Contact.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).exclude(id__in=contact_starts)

            # Combine with ranking priority
            results = list(user_starts) + list(contact_starts) + list(user_contains) + list(contact_contains)

        else:
            return Response({"error": "Invalid search query."}, status=400)

        # Remove duplicates by phone number
        unique_results = []
        seen_numbers = set()
        for r in results:
            if r.phone_number not in seen_numbers:
                unique_results.append(r)
                seen_numbers.add(r.phone_number)

        # Annotate spam count efficiently
        spam_counts = dict(
            ScamRecord.objects.values_list("phone_number")
            .annotate(count=Count("id"))
            .values_list("phone_number", "count")
        )

        # Attach spam counts via serializer context
        paginator = self.pagination_class()
        paginated_results = paginator.paginate_queryset(unique_results, request)
        serializer = self.output_serializer_class(
            paginated_results, many=True, context={"spam_counts": spam_counts}
        )
        return paginator.get_paginated_response(serializer.data)


class SearchDetailsView(APIView):
    """
    GET /api/search/detail/<uuid:id>
    - Returns full details of a user/contact by ID.
    - Email hidden unless requester has them in their contacts.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    output_user_serializer_class = output.SearchDetailsUserOutputSerializer
    output_contact_serializer_class = output.ContactOutputSerializer

    def get(self, request, id):
        # Try User first
        try:
            user = User.objects.get(id=id)
            # Hide email unless in request.user's contacts
            in_contacts = Contact.objects.filter(
                created_by=request.user, phone_number=user.phone_number
            ).exists()
            if not in_contacts:
                user.email = None
            serializer = self.output_user_serializer_class(user)
            return Response(serializer.data, status=200)
        except User.DoesNotExist:
            pass

        # Then try Contact
        try:
            contact = Contact.objects.get(id=id)
            serializer = self.output_contact_serializer_class(contact)
            return Response(serializer.data, status=200)
        except Contact.DoesNotExist:
            return Response({"error": "Record not found."}, status=404)