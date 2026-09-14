from rest_framework import views
from features.categories.serializers import CategorySerializer
from features.categories.helpers import toApiResponse
from features.categories.models import Category
from features.shared.helpers.helper import generateId

class CategoryView(views.APIView):

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.initial_data["category_id"] = generateId(Category, "category_id", "C")
        print("this is data : ", serializer.initial_data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        res=CategorySerializer(category).data
        print("this is created data : ",res)
        return toApiResponse({
            "category":res, 
            "message":"Created Successfully",
        })
    
    def get(self, request):
        categories = Category.objects.select_related("parent").all()

        return toApiResponse({"categories" : CategorySerializer(categories, many=True).data})
    
    def put(self, request, id):
        print("this is update data:", request.data)
        category = Category.objects.get(id=id)
        serializer = CategorySerializer(instance=category, data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return toApiResponse({
            "category" :CategorySerializer(category).data, 
            "message" : "Updated Successfully!",
        })
    
    def delete(self, request, id):
        category = Category.objects.get(id=id)
        num,_ = category.delete()


        if num<0:
            return toApiResponse({"message":"Falied to Delete"})

        return toApiResponse({"message":"Deleted Successfully!"})
    
class GetCategoryByIdView(views.APIView):

    def get(self, request, id:int):
        category = Category.objects.get(id=id)

        return toApiResponse({
            "category" : CategorySerializer(category).data
        })


        