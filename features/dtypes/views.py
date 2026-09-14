from rest_framework.views import APIView, Request, Response,status
from features.dtypes.models import Dtype
from features.dtypes.serializers import DtypeSerializer
from features.shared.helpers.helper import generateId

class DtypeView(APIView):

    def toApiResponse(self,data)->Response:
        return Response(data=data, status=status.HTTP_200_OK)
    
    def get(self, request: Request)->Response:
        
        dtypes = Dtype.objects.all()
        return self.toApiResponse({
            "dtypes" : DtypeSerializer(dtypes, many=True).data
        })
    
    def post(self, request:Request)->Response:
        serializer = DtypeSerializer(data=request.data)
        serializer.initial_data["dtype_id"] = generateId(Dtype, "dtype_id", "DTYPE")
        serializer.is_valid(raise_exception=True)
        dtype = serializer.save()
        res = DtypeSerializer(dtype).data
        return self.toApiResponse({
            "dtype" : res,
            "message" : f"Created Successfully!"
        })
    
    def put(self, request:Request, id:int)->Response:
        dtype = Dtype.objects.get(id=id)
        serializer = DtypeSerializer(instance=dtype, data=request.data)
        serializer.is_valid(raise_exception=True)
        dtype = serializer.save()
        res = DtypeSerializer(dtype).data
        print("this is Dtype update data : ", res)
        return self.toApiResponse({
            "dtype" : res,
            "message" : f"{res['dtype_name']} has been updated successfully!"
        })
    
    def delete(self, request:Request, id:int)->Response:
        int,_ = Dtype.objects.get(id=id).delete()

        return self.toApiResponse({
            "message" : "Deleted Successfully!"
        })
    
class GetDtypeByIdView(APIView):

    def get(self, request:Request, id:int)->Response:
        dtype = Dtype.objects.get(id=id)

        return Response(data={
            "dtype" : DtypeSerializer(dtype).data
        })

        
