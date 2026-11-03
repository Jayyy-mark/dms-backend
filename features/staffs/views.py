from rest_framework import views
from rest_framework import status
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from features.staffs.serializers import StaffSerializer
from features.shared.helpers.helper import generateId, removeNoneValue, paginate_queryset, _to_int
from features.staffs.models import Staff
from common.security.authorization.roles import Roles


def get_staff_department_filter(request) -> Q:
    if request.user.role in Roles.PRIVILEGED:
        return Q()

    staff = getattr(request.user, "staff", None)
    if staff is None or staff.department_id is None:
        return Q(pk__in=[])

    return Q(department_id=staff.department_id)


class StaffView(views.APIView):

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        serializer.initial_data["staff_id"] = generateId(Staff, "staff_id", "S")
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()
        res = StaffSerializer(staff).data
        return views.Response({"staff": res, "message": "Created successfully!"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        dept_filter = get_staff_department_filter(request)

        if request.query_params:
            filters = removeNoneValue({
                "id": request.query_params.get("id"),
                "staff_id": request.query_params.get("staff_id"),
                "staff_name": request.query_params.get("staff_name"),
                "staff_email": request.query_params.get("staff_email"),
                "staff_address": request.query_params.get("staff_address"),
                "staff_ph_number": request.query_params.get("staff_ph_number"),
                "staff_gender": request.query_params.get("staff_gender"),
                "department_id": request.query_params.get("department_id"),
                "role_id": request.query_params.get("role_id"),
                "rank_id": request.query_params.get("rank_id"),
                "stype_id": request.query_params.get("stype_id"),
            })
            staffs = Staff.objects.select_related("department", "role", "rank", "stype").filter(dept_filter).filter(**filters)
        else:
            staffs = Staff.objects.select_related("department", "role", "rank", "stype").filter(dept_filter)

        return views.Response({"staffs": StaffSerializer(staffs, many=True).data})

    def put(self, request, id):
        staff = Staff.objects.get(id=id)
        serializer = StaffSerializer(instance=staff, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        staff = serializer.save()

        return views.Response({
            "staff": StaffSerializer(staff).data,
            "message": "Updated successfully!",
        })

    def delete(self, request, id):
        try:
            staff = Staff.objects.get(id=id)
            staff.delete()
            return views.Response({"message": "Deleted successfully!"})
        except Staff.DoesNotExist:
            return views.Response({"message": "Failed to delete!"}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(never_cache, name="dispatch")
class StaffListView(views.APIView):
    """
    GET staff/list/?limit=10&offset=0&tab=all&search=&snapshot_id=
    Database-level pagination & stats for Staffs.
    """

    def get(self, request):
        dept_filter = get_staff_department_filter(request)
        params = request.query_params

        qs = Staff.objects.select_related("department", "role", "rank", "stype").filter(dept_filter)

        search = (params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(staff_name__icontains=search)
                | Q(staff_email__icontains=search)
                | Q(staff_id__icontains=search)
                | Q(staff_ph_number__icontains=search)
                | Q(department__department_name__icontains=search)
                | Q(role__role_name__icontains=search)
            )

        raw_snapshot = _to_int(params.get("snapshot_id"), 0)
        if raw_snapshot > 0:
            qs = qs.filter(id__lte=raw_snapshot)

        stats = {
            "all": qs.count(),
            "male": qs.filter(staff_gender__iexact="Male").count(),
            "female": qs.filter(staff_gender__iexact="Female").count(),
            "departments": qs.exclude(department_id__isnull=True).values("department_id").distinct().count(),
        }

        tab = (params.get("tab") or "all").strip().lower()
        if tab == "male":
            qs = qs.filter(staff_gender__iexact="Male")
        elif tab == "female":
            qs = qs.filter(staff_gender__iexact="Female")

        qs = qs.order_by("-created_at", "-id")
        page_staffs, pagination = paginate_queryset(qs, Staff, params)

        return views.Response(
            {
                "staffs": StaffSerializer(page_staffs, many=True).data,
                "pagination": pagination,
                "stats": stats,
            }
        )


class GetStaffByIdView(views.APIView):

    def get(self, request, id: int):
        try:
            staff = Staff.objects.get(id=id)
            return views.Response({
                "staff": StaffSerializer(staff).data
            })
        except Staff.DoesNotExist:
            return views.Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
