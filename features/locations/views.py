from rest_framework.views import APIView, Request, Response
from django.db.models import Q
from features.locations.serializers import (
    LocationSearchSerializer,
    LocationSerializer,
    LocationUpdateSerializer,
)
from features.locations.models import Location
from features.shared.helpers.helper import toApiResponse, log_action
from features.locations.helpers import setLocationFilters
from features.shared.helpers.helper import generateId
from common.security.authorization.roles import Roles


def get_location_department_filter(request) -> Q:
    """
    Returns a Q filter scoping locations to the requesting user's department.
    Admins/super admins get an empty Q() (no restriction).
    For others: filter by department_id = user.staff.department_id.
    If the user has no linked staff/department, returns a safe empty-result filter.
    """
    if request.user.role in Roles.PRIVILEGED:
        return Q()

    staff = getattr(request.user, "staff", None)
    if staff is None or staff.department_id is None:
        return Q(pk__in=[])

    return Q(department_id=staff.department_id)


# <!--==============================
#   LOCATIONS VIEWS
# ================================-->
from features.locations.models import Location, LocationPhoto

class LocationView(APIView):

    def post(self, request: Request) -> Response:
        print("route entered")
        serializer = LocationSerializer(data=request.data)
        serializer.initial_data["location_id"] = generateId(
            Location, "location_id", "LOC"
        )
        print("this is document data ", serializer.initial_data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print("this is error e: ", e)
            raise (e)

        location = serializer.save()

        # Handle multiple photos save
        uploaded_photos = request.FILES.getlist("photos") or request.FILES.getlist("photo")
        for file in uploaded_photos:
            LocationPhoto.objects.create(location=location, photo=file)
            if not location.photo:
                location.photo = file
                location.save()

        if location:
            log_action(
                user=request.user,
                action="CREATE",
                model_name="locations",
                object_id=location.id,
                description=f"Upload {location.location_name}",
            )

        return toApiResponse(
            data=LocationSerializer(location).data,
            message=f"{location.location_name} has been created!",
        )

    def get(self, request: Request) -> Response:

        dept_filter = get_location_department_filter(request)
        locations = Location.objects.filter(dept_filter)
        res = LocationSerializer(locations, many=True)

        return Response({"locations": res.data})

    def put(self, request: Request, id: int) -> Response:
        print("route entered!")
        location = Location.objects.get(id=id)
        serializer = LocationUpdateSerializer(instance=location, data=request.data)
        serializer.is_valid(raise_exception=True)

        location = serializer.save()

        if location:
            log_action(
                user=request.user,
                action="UPDATE",
                model_name="locations",
                object_id=location.id,
                description=f"Updated {location.location_name}",
            )

        return Response(
            {
                "location": LocationSerializer(location).data,
                "message": f"{location.location_name} has been updated!",
            }
        )

    def delete(self, request: Request, id: int) -> Response:

        location = Location.objects.get(id=id)

        num, _ = location.delete()

        if num < 0:
            return Response({"message": f"Failed to delete {location.location_name}"})

        log_action(
            user=request.user,
            action="DELETE",
            model_name="locations",
            object_id=location.id,
            description=f"Deleted {location.location_name}",
        )

        return Response({"message": f"{location.location_name} has been deleted!"})


class GetLocationByIdView(APIView):

    def get(self, request: Request, id: int) -> Response:

        location = Location.objects.get(id=id)

        return Response({"location": LocationSerializer(location).data})


class GetLocationByColumnView(APIView):

    def get(self, request: Request) -> Response:

        serializer = LocationSearchSerializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)

        filters = setLocationFilters(serializer.validated_data)
        dept_filter = get_location_department_filter(request)

        locations = Location.objects.filter(dept_filter).filter(filters)

        return Response({"locations": LocationSerializer(locations, many=True).data})


class GetLocationOptionsView(APIView):
    def get(self, request: Request) -> Response:
        dept_filter = get_location_department_filter(request)
        qs = Location.objects.filter(dept_filter)
        return Response(
            {
                "location_types": list(
                    qs.exclude(location_type__isnull=True)
                    .exclude(location_type="")
                    .values_list("location_type", flat=True)
                    .distinct()
                ),
                "location_names": list(
                    qs.exclude(location_name__isnull=True)
                    .exclude(location_name="")
                    .values_list("location_name", flat=True)
                    .distinct()
                ),
                "cities": list(
                    qs.exclude(city__isnull=True)
                    .exclude(city="")
                    .values_list("city", flat=True)
                    .distinct()
                ),
                "longitudes": list(
                    qs.exclude(longitude__isnull=True)
                    .values_list("longitude", flat=True)
                    .distinct()
                ),
                "latitudes": list(
                    qs.exclude(latitude__isnull=True)
                    .values_list("latitude", flat=True)
                    .distinct()
                ),
                "coordinates": list(
                    qs.exclude(latitude__isnull=True)
                    .exclude(longitude__isnull=True)
                    .values("latitude", "longitude")
                    .distinct()
                ),
            }
        )
