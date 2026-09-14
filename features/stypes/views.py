from rest_framework import views
from rest_framework import status
from features.stypes.serializers import StypeSerializer
from features.shared.helpers.helper import generateId, removeNoneValue
from features.stypes.models import Stype

class StypeView(views.APIView):

    def post(self, request):
        serializer = StypeSerializer(data=request.data)
        serializer.initial_data["stype_id"] = generateId(Stype, "stype_id", "ST")
        serializer.is_valid(raise_exception=True)
        stype = serializer.save()
        res = StypeSerializer(stype).data
        return views.Response({"stype": res, "message": "Created successfully!"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        if request.query_params:
            filters = removeNoneValue({
                "id": request.query_params.get("id"),
                "stype_id": request.query_params.get("stype_id"),
                "stype_name": request.query_params.get("stype_name"),
            })
            stypes = Stype.objects.filter(**filters)
        else:
            stypes = Stype.objects.all()

        return views.Response({"stypes": StypeSerializer(stypes, many=True).data})

    def put(self, request, id):
        stype = Stype.objects.get(id=id)
        serializer = StypeSerializer(instance=stype, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        stype = serializer.save()

        return views.Response({
            "stype": StypeSerializer(stype).data,
            "message": "Updated successfully!",
        })

    def delete(self, request, id):
        try:
            stype = Stype.objects.get(id=id)
            stype.delete()
            return views.Response({"message": "Deleted successfully!"})
        except Stype.DoesNotExist:
            return views.Response({"message": "Failed to delete!"}, status=status.HTTP_400_BAD_REQUEST)

class GetStypeByIdView(views.APIView):

    def get(self, request, id: int):
        try:
            stype = Stype.objects.get(id=id)
            return views.Response({
                "stype": StypeSerializer(stype).data
            })
        except Stype.DoesNotExist:
            return views.Response({"message": "Stype not found"}, status=status.HTTP_404_NOT_FOUND)
