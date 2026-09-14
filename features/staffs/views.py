from rest_framework import views
from rest_framework import status
from django.db.models import Q
from features.staffs.serializers import StaffSerializer
from features.shared.helpers.helper import generateId, removeNoneValue
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

class GetStaffByIdView(views.APIView):

    def get(self, request, id: int):
        try:
            staff = Staff.objects.get(id=id)
            return views.Response({
                "staff": StaffSerializer(staff).data
            })
        except Staff.DoesNotExist:
            return views.Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)
