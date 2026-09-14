from rest_framework import views
from rest_framework import status
from features.departments.serializers import DepartmentSerializer
from features.shared.helpers.helper import generateId, removeNoneValue
from features.departments.models import Department

class DepartmentView(views.APIView):

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.initial_data["department_id"] = generateId(Department, "department_id", "D")
        serializer.is_valid(raise_exception=True)
        department = serializer.save()
        res = DepartmentSerializer(department).data
        return views.Response({"department": res, "message": "Created successfully!"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        if request.query_params:
            filters = removeNoneValue({
                "id": request.query_params.get("id"),
                "department_id": request.query_params.get("department_id"),
                "department_name": request.query_params.get("department_name"),
                "room_id": request.query_params.get("room_id"),
            })
            departments = Department.objects.select_related("room").filter(**filters)
        else:
            departments = Department.objects.select_related("room").all()

        return views.Response({"departments": DepartmentSerializer(departments, many=True).data})

    def put(self, request, id):
        department = Department.objects.get(id=id)
        serializer = DepartmentSerializer(instance=department, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        department = serializer.save()

        return views.Response({
            "department": DepartmentSerializer(department).data,
            "message": "Updated successfully!",
        })

    def delete(self, request, id):
        try:
            department = Department.objects.get(id=id)
            department.delete()
            return views.Response({"message": "Deleted successfully!"})
        except Department.DoesNotExist:
            return views.Response({"message": "Failed to delete!"}, status=status.HTTP_400_BAD_REQUEST)

class GetDepartmentByIdView(views.APIView):

    def get(self, request, id: int):
        try:
            department = Department.objects.get(id=id)
            return views.Response({
                "department": DepartmentSerializer(department).data
            })
        except Department.DoesNotExist:
            return views.Response({"message": "Department not found"}, status=status.HTTP_404_NOT_FOUND)
