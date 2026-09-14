from django.db.models import Q


def setLocationFilters(data):
    filters = Q()

    if data.get("location_id"):
        filters &= Q(location_id__icontains=data["location_id"])

    if data.get("description"):
        filters &= Q(description__icontains=data["description"])

    if data.get("location_name"):
        filters &= Q(location_name__icontains=data["location_name"])

    if data.get("city"):
        filters &= Q(city__icontains=data["city"])

    if data.get("latitude"):
        filters &= Q(latitude=data["latitude"])

    if data.get("longitude"):
        filters &= Q(longitude=data["longitude"])

    if data.get("location_type"):
        filters &= Q(location_type__icontains=data["location_type"])

    if data.get("department_id"):
        filters &= Q(department_id=data["department_id"])

    if data.get("date"):
        filters &= Q(date__date=data["date"])

    return filters
