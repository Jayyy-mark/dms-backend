from rest_framework.views import APIView, Request, Response,status
from features.buildings.models import Building
from features.buildings.serializers import BuildingSerializer
from features.shared.helpers.helper import generateId

class BuildingView(APIView):

    def toApiResponse(self,data)->Response:
        return Response(data=data, status=status.HTTP_200_OK)
    
    def get(self, request: Request)->Response:
        
        buildings = Building.objects.all()
        return self.toApiResponse({
            "buildings" : BuildingSerializer(buildings, many=True).data
        })
    
    def post(self, request:Request)->Response:
        serializer = BuildingSerializer(data=request.data)
        serializer.initial_data["building_id"] = generateId(Building, "building_id", "B")
        serializer.is_valid(raise_exception=True)
        building = serializer.save()
        res = BuildingSerializer(building).data
        return self.toApiResponse({
            "building" : res,
            "message" : f"Created Successfully!"
        })
    
    def put(self, request:Request, id:int)->Response:
        building = Building.objects.get(id=id)
        serializer = BuildingSerializer(instance=building, data=request.data)
        serializer.is_valid(raise_exception=True)
        building = serializer.save()
        res = BuildingSerializer(building).data
        print("this is building update data : ", res)
        return self.toApiResponse({
            "building" : res,
            "message" : f"{res['building_name']} has been updated successfully!"
        })
    
    def delete(self, request:Request, id:int)->Response:
        int,_ = Building.objects.get(id=id).delete()

        return self.toApiResponse({
            "message" : "Deleted Successfully!"
        })
    
class GetBuildingByIdView(APIView):

    def get(self, request:Request, id:int)->Response:
        building = Building.objects.get(id=id)

        return Response(data={
            "building" : BuildingSerializer(building).data
        })

        
