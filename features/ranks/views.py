from rest_framework import views
from rest_framework import status
from features.ranks.serializers import RankSerializer
from features.shared.helpers.helper import generateId, removeNoneValue
from features.ranks.models import Rank

class RankView(views.APIView):

    def post(self, request):
        serializer = RankSerializer(data=request.data)
        serializer.initial_data["rank_id"] = generateId(Rank, "rank_id", "R")
        serializer.is_valid(raise_exception=True)
        rank = serializer.save()
        res = RankSerializer(rank).data
        return views.Response({"rank": res, "message": "Created successfully!"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        if request.query_params:
            filters = removeNoneValue({
                "id": request.query_params.get("id"),
                "rank_id": request.query_params.get("rank_id"),
                "rank_name": request.query_params.get("rank_name"),
            })
            ranks = Rank.objects.filter(**filters)
        else:
            ranks = Rank.objects.all()

        return views.Response({"ranks": RankSerializer(ranks, many=True).data})

    def put(self, request, id):
        rank = Rank.objects.get(id=id)
        serializer = RankSerializer(instance=rank, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        rank = serializer.save()

        return views.Response({
            "rank": RankSerializer(rank).data,
            "message": "Updated successfully!",
        })

    def delete(self, request, id):
        try:
            rank = Rank.objects.get(id=id)
            rank.delete()
            return views.Response({"message": "Deleted successfully!"})
        except Rank.DoesNotExist:
            return views.Response({"message": "Failed to delete!"}, status=status.HTTP_400_BAD_REQUEST)

class GetRankByIdView(views.APIView):

    def get(self, request, id: int):
        try:
            rank = Rank.objects.get(id=id)
            return views.Response({
                "rank": RankSerializer(rank).data
            })
        except Rank.DoesNotExist:
            return views.Response({"message": "Rank not found"}, status=status.HTTP_404_NOT_FOUND)
