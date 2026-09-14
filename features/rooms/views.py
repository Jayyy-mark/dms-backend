from rest_framework import views
from rest_framework import status
from features.rooms.serializers import RoomSerializer
from features.shared.helpers.helper import generateId, removeNoneValue
from features.rooms.models import Room

class RoomView(views.APIView):

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        serializer.initial_data["room_id"] = generateId(Room, "room_id", "R")
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        res = RoomSerializer(room).data
        return views.Response({"room": res, "message": "Created successfully!"}, status=status.HTTP_201_CREATED)

    def get(self, request):
        if request.query_params:
            filters = removeNoneValue({
                "id": request.query_params.get("id"),
                "room_id": request.query_params.get("room_id"),
                "room_name": request.query_params.get("room_name"),
                "room_no": request.query_params.get("room_no"),
                "building_id": request.query_params.get("building_id"),
            })
            rooms = Room.objects.select_related("building").filter(**filters)
        else:
            rooms = Room.objects.select_related("building").all()

        return views.Response({"rooms": RoomSerializer(rooms, many=True).data})

    def put(self, request, id):
        room = Room.objects.get(id=id)
        serializer = RoomSerializer(instance=room, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()

        return views.Response({
            "room": RoomSerializer(room).data,
            "message": "Updated successfully!",
        })

    def delete(self, request, id):
        try:
            room = Room.objects.get(id=id)
            room.delete()
            return views.Response({"message": "Deleted successfully!"})
        except Room.DoesNotExist:
            return views.Response({"message": "Failed to delete!"}, status=status.HTTP_400_BAD_REQUEST)

class GetRoomByIdView(views.APIView):

    def get(self, request, id: int):
        try:
            room = Room.objects.get(id=id)
            return views.Response({
                "room": RoomSerializer(room).data
            })
        except Room.DoesNotExist:
            return views.Response({"message": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
