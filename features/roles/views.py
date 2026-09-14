from rest_framework import views
from rest_framework import status
from features.roles.serializers import RoleSerializer
from features.shared.helpers.helper import generateId, removeNoneValue
from features.roles.models import Role

class RoleView(views.APIView):

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.initial_data["role_id"] = generateId(Role, "role_id", "R")
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        res = RoleSerializer(role).data
        return views.Response({"role": res, "message": "Created successfully!"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        if request.query_params:
            filters = removeNoneValue({
                "id": request.query_params.get("id"),
                "role_id": request.query_params.get("role_id"),
                "role_name": request.query_params.get("role_name"),
            })
            roles = Role.objects.filter(**filters)
        else:
            roles = Role.objects.all()

        return views.Response({"roles": RoleSerializer(roles, many=True).data})

    def put(self, request, id):
        role = Role.objects.get(id=id)
        serializer = RoleSerializer(instance=role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()

        return views.Response({
            "role": RoleSerializer(role).data,
            "message": "Updated successfully!",
        })

    def delete(self, request, id):
        try:
            role = Role.objects.get(id=id)
            role.delete()
            return views.Response({"message": "Deleted successfully!"})
        except Role.DoesNotExist:
            return views.Response({"message": "Failed to delete!"}, status=status.HTTP_400_BAD_REQUEST)

class GetRoleByIdView(views.APIView):

    def get(self, request, id: int):
        try:
            role = Role.objects.get(id=id)
            return views.Response({
                "role": RoleSerializer(role).data
            })
        except Role.DoesNotExist:
            return views.Response({"message": "Role not found"}, status=status.HTTP_404_NOT_FOUND)
