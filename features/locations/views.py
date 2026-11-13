from rest_framework.views import APIView, Request, Response
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
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
        uploaded_photos = request.FILES.getlist("photos") or request.FILES.getlist(
            "photo"
        )
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
        locations = Location.objects.select_related("department").prefetch_related("photos").filter(dept_filter, is_deleted=False)
        
        res = LocationSerializer(locations, many=True)
        print("this is Location data : ", res.data)
        return Response({"locations": res.data})

    def put(self, request: Request, id: int) -> Response:
        print("route entered!")
        location = Location.objects.select_related("department").get(id=id, is_deleted=False)
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

        location = Location.objects.get(id=id, is_deleted=False)
        location.is_deleted = True
        location.deleted_time = timezone.now()
        location.save(update_fields=["is_deleted", "deleted_time"])

        log_action(
            user=request.user,
            action="DELETE",
            model_name="locations",
            object_id=location.id,
            description=f"Moved {location.location_name} to recycle bin",
        )

        return Response({"message": f"{location.location_name} has been deleted!"})


class GetLocationByIdView(APIView):

    def get(self, request: Request, id: int) -> Response:

        location = Location.objects.select_related("department").prefetch_related("photos").get(id=id, is_deleted=False)

        return Response({"location": LocationSerializer(location).data})


class GetLocationByColumnView(APIView):

    def get(self, request: Request) -> Response:

        serializer = LocationSearchSerializer(data=request.query_params)

        serializer.is_valid(raise_exception=True)

        filters = setLocationFilters(serializer.validated_data)
        dept_filter = get_location_department_filter(request)

        locations = (
            Location.objects.select_related("department")
            .prefetch_related("photos")
            .filter(dept_filter, is_deleted=False)
            .filter(filters)
        )

        return Response({"locations": LocationSerializer(locations, many=True).data})


class GetLocationOptionsView(APIView):
    def get(self, request: Request) -> Response:
        dept_filter = get_location_department_filter(request)
        qs = Location.objects.filter(dept_filter, is_deleted=False)
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


import html
import io
import os
import fitz
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


def get_pdf_font_archive_and_css() -> tuple[fitz.Archive, str]:
    archive = fitz.Archive()
    font_dirs = [
        "C:/Windows/Fonts",
        "/usr/share/fonts",
        "/usr/local/share/fonts",
    ]
    for d in font_dirs:
        if os.path.isdir(d):
            try:
                archive.add(d)
            except Exception:
                pass

    regular_candidates = [
        ("C:/Windows/Fonts/Pyidaungsu-2.5.3_Regular.ttf", "Pyidaungsu-2.5.3_Regular.ttf"),
        ("C:/Windows/Fonts/mmrtext.ttf", "mmrtext.ttf"),
        ("/usr/share/fonts/truetype/padauk/Padauk-Regular.ttf", "Padauk-Regular.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf", "NotoSansMyanmar-Regular.ttf"),
    ]
    bold_candidates = [
        ("C:/Windows/Fonts/Pyidaungsu-2.5.3_Bold.ttf", "Pyidaungsu-2.5.3_Bold.ttf"),
        ("C:/Windows/Fonts/mmrtextb.ttf", "mmrtextb.ttf"),
        ("/usr/share/fonts/truetype/padauk/Padauk-Bold.ttf", "Padauk-Bold.ttf"),
        ("/usr/share/fonts/truetype/noto/NotoSansMyanmar-Bold.ttf", "NotoSansMyanmar-Bold.ttf"),
    ]

    reg_font = None
    for full_path, fname in regular_candidates:
        if os.path.exists(full_path):
            reg_font = fname
            break

    bold_font = None
    for full_path, fname in bold_candidates:
        if os.path.exists(full_path):
            bold_font = fname
            break

    if reg_font and not bold_font:
        bold_font = reg_font

    font_face_css = ""
    if reg_font:
        font_face_css = f"""
        @font-face {{
            font-family: 'MyanmarFont';
            src: url('{reg_font}');
            font-weight: normal;
        }}
        @font-face {{
            font-family: 'MyanmarFont';
            src: url('{bold_font}');
            font-weight: bold;
        }}
        """

    return archive, font_face_css


@method_decorator(never_cache, name="dispatch")
class ExportLocationPdfView(APIView):
    def get(self, request: Request) -> HttpResponse:
        dept_filter = get_location_department_filter(request)
        locations = (
            Location.objects.filter(dept_filter, is_deleted=False)
            .select_related("department")
            .order_by("-date", "-id")
        )

        search = request.query_params.get("search", "").strip()
        if search:
            locations = locations.filter(
                Q(location_name__icontains=search)
                | Q(department__department_name__icontains=search)
                | Q(photo__icontains=search)
            )

        archive, font_face_css = get_pdf_font_archive_and_css()

        css = f"""
        {font_face_css}
        body {{
            font-family: 'MyanmarFont', sans-serif;
            margin: 0;
            padding: 0;
            color: #1e293b;
        }}
        .header {{
            text-align: center;
            margin-bottom: 15pt;
        }}
        .title {{
            font-size: 16pt;
            font-weight: bold;
            color: #1a4a98;
            margin: 0 0 4pt 0;
        }}
        .subtitle {{
            font-size: 10pt;
            color: #64748b;
            margin: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background-color: #1a4a98;
            color: #ffffff;
            font-weight: bold;
            font-size: 10pt;
            padding: 6pt 6pt;
            border: 0.5pt solid #e2e8f0;
            text-align: center;
        }}
        td {{
            font-size: 9pt;
            padding: 6pt 6pt;
            border: 0.5pt solid #e2e8f0;
            color: #1e293b;
        }}
        tr.even td {{
            background-color: #f8fafc;
        }}
        tr.odd td {{
            background-color: #ffffff;
        }}
        .center {{
            text-align: center;
        }}
        .left {{
            text-align: left;
        }}
        """

        location_list = list(locations)
        tr_list = []

        for idx, loc in enumerate(location_list, start=1):
            file_name = loc.location_name or "Unknown"

            file_type = "image"
            if loc.photo and hasattr(loc.photo, "name") and loc.photo.name:
                parts = loc.photo.name.split(".")
                if len(parts) > 1:
                    file_type = parts[-1].lower()

            dept_name = loc.department.department_name if loc.department else "—"
            uploaded_date = str(loc.date) if loc.date else "—"
            row_cls = "odd" if idx % 2 == 1 else "even"

            tr_list.append(
                f"""
                <tr class="{row_cls}">
                    <td class="center" width="40">{idx}</td>
                    <td class="left" width="260">{html.escape(str(file_name))}</td>
                    <td class="center" width="90">{html.escape(str(file_type))}</td>
                    <td class="left" width="250">{html.escape(str(dept_name))}</td>
                    <td class="center" width="100">{html.escape(str(uploaded_date))}</td>
                </tr>
                """
            )

        if not tr_list:
            tr_list.append(
                """
                <tr class="odd">
                    <td class="center" colspan="5">No locations found.</td>
                </tr>
                """
            )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body>
            <div class="header">
                <div class="title">Myanma Oil and Gas Enterprise (MOGE)</div>
                <div class="subtitle">Locations Report ({len(location_list)} items)</div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th width="40">SL</th>
                        <th width="260">File Name</th>
                        <th width="90">File Type</th>
                        <th width="250">Department</th>
                        <th width="100">Uploaded Date</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(tr_list)}
                </tbody>
            </table>
        </body>
        </html>
        """

        buffer = io.BytesIO()
        mediabox = fitz.paper_rect("a4-l")
        where = mediabox + (30, 30, -30, -30)

        story = fitz.Story(html=html_content, user_css=css, archive=archive)
        writer = fitz.DocumentWriter(buffer)

        more = True
        while more:
            device = writer.begin_page(mediabox)
            more, _ = story.place(where)
            story.draw(device)
            writer.end_page()

        writer.close()
        pdf_value = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_value, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="locations.pdf"'
        response = HttpResponse(pdf_value, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="locations.pdf"'
        return response


@method_decorator(never_cache, name="dispatch")
class LocationListView(APIView):
    """
    GET location/list/?limit=10&offset=0&search=&folder=&snapshot_id=
    Database-level pagination & folder stats for Locations.
    """

    def get(self, request: Request) -> Response:
        from django.db.models import Count
        from features.shared.helpers.helper import paginate_queryset, _to_int

        dept_filter = get_location_department_filter(request)
        params = request.query_params

        base_qs = Location.objects.select_related("department").prefetch_related("photos").filter(dept_filter, is_deleted=False)

        try:
            adv_filters = setLocationFilters(params)
            base_qs = base_qs.filter(adv_filters)
        except Exception:
            pass

        raw_snapshot = _to_int(params.get("snapshot_id"), 0)
        if raw_snapshot > 0:
            base_qs = base_qs.filter(id__lte=raw_snapshot)

        # Compute folder stats over the base queryset
        folder_counts: dict[str, int] = {}
        for row in base_qs.values("location_type").annotate(count=Count("id")):
            fname = (row["location_type"] or "").strip() or "Untitled"
            folder_counts[fname] = folder_counts.get(fname, 0) + row["count"]

        folders_list = [
            {"name": k, "count": folder_counts[k]}
            for k in sorted(folder_counts.keys())
        ]
        stats = {
            "total": sum(folder_counts.values()),
            "folders": folders_list,
        }

        qs = base_qs

        # Optional folder filter (when inside a folder)
        folder = (params.get("folder") or "").strip()
        if folder:
            if folder == "Untitled":
                qs = qs.filter(Q(location_type__isnull=True) | Q(location_type=""))
            else:
                qs = qs.filter(location_type=folder)

        # Text search filter
        search = (params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(location_name__icontains=search)
                | Q(location_id__icontains=search)
                | Q(city__icontains=search)
                | Q(state_division__icontains=search)
                | Q(location_type__icontains=search)
                | Q(description__icontains=search)
                | Q(department__department_name__icontains=search)
            )

        qs = qs.order_by("-date", "-id")
        page_locs, pagination = paginate_queryset(qs, Location, params)

        return Response(
            {
                "locations": LocationSerializer(page_locs, many=True).data,
                "pagination": pagination,
                "stats": stats,
            }
        )


# <!--==============================
#   RECYCLED LOCATIONS VIEWS
# ================================-->
class RecycledLocationView(APIView):
    def get(self, request: Request) -> Response:
        dept_filter = get_location_department_filter(request)
        recycled_locations = (
            Location.objects.select_related("department")
            .prefetch_related("photos")
            .filter(dept_filter, is_deleted=True)
            .order_by("-deleted_time", "-id")
        )
        return Response(
            {"locations": LocationSerializer(recycled_locations, many=True).data}
        )

    def patch(self, request: Request, id: int) -> Response:
        dept_filter = get_location_department_filter(request)
        try:
            location = (
                Location.objects.select_related("department")
                .prefetch_related("photos")
                .filter(dept_filter)
                .get(id=id, is_deleted=True)
            )
        except Location.DoesNotExist:
            return Response(
                {"message": "Location not found in recycle bin."},
                status=status.HTTP_404_NOT_FOUND,
            )

        location.is_deleted = False
        location.deleted_time = None
        location.save(update_fields=["is_deleted", "deleted_time"])

        log_action(
            user=request.user,
            action="RESTORE",
            model_name="recycled locations",
            object_id=location.id,
            description=f"Restored {location.location_name}",
        )

        return Response(
            {
                "location": LocationSerializer(location).data,
                "message": f"{location.location_name} has been restored!",
            }
        )

    def delete(self, request: Request, id: int) -> Response:
        dept_filter = get_location_department_filter(request)
        try:
            location = Location.objects.filter(dept_filter).get(id=id, is_deleted=True)
        except Location.DoesNotExist:
            return Response(
                {"message": "Location not found in recycle bin."},
                status=status.HTTP_404_NOT_FOUND,
            )

        loc_name = location.location_name
        loc_id = location.id
        num, _ = location.delete()

        if num < 0:
            return Response({"message": f"Failed to delete {loc_name}"})

        log_action(
            user=request.user,
            action="DELETE",
            model_name="recycled locations",
            object_id=loc_id,
            description=f"Permanently deleted {loc_name}",
        )

        return Response({"message": f"{loc_name} has been permanently deleted!"})


@method_decorator(never_cache, name="dispatch")
class RecycledLocationListView(APIView):
    """
    GET location/recycle/list/?limit=10&offset=0&search=&snapshot_id=
    Database-level pagination & stats for Recycled Locations.
    """

    def get(self, request: Request) -> Response:
        from features.shared.helpers.helper import paginate_queryset, _to_int

        dept_filter = get_location_department_filter(request)
        params = request.query_params

        base_qs = (
            Location.objects.select_related("department")
            .prefetch_related("photos")
            .filter(dept_filter, is_deleted=True)
        )

        raw_snapshot = _to_int(params.get("snapshot_id"), 0)
        if raw_snapshot > 0:
            base_qs = base_qs.filter(id__lte=raw_snapshot)

        stats = {
            "total": base_qs.count(),
        }

        qs = base_qs
        search = (params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(location_name__icontains=search)
                | Q(location_id__icontains=search)
                | Q(city__icontains=search)
                | Q(state_division__icontains=search)
                | Q(location_type__icontains=search)
                | Q(description__icontains=search)
                | Q(department__department_name__icontains=search)
            )

        qs = qs.order_by("-deleted_time", "-id")
        page_locs, pagination = paginate_queryset(qs, Location, params)

        return Response(
            {
                "locations": LocationSerializer(page_locs, many=True).data,
                "pagination": pagination,
                "stats": stats,
            }
        )


class LocationAuditActionView(APIView):
    """
    POST location/view/<id>/ or location/download/<id>/
    Records VIEW or DOWNLOAD audit log entries for a location.
    """

    action_type = "VIEW"

    def post(self, request: Request, id: int, action: str | None = None) -> Response:
        act = (action or self.action_type or "VIEW").upper()
        if act not in ("VIEW", "DOWNLOAD"):
            act = "VIEW"

        dept_filter = get_location_department_filter(request)
        try:
            location = Location.objects.filter(dept_filter).get(id=id)
        except Location.DoesNotExist:
            return Response(
                {"message": "Location not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        verb = "Viewed" if act == "VIEW" else "Downloaded"
        log_action(
            user=request.user,
            action=act,
            model_name="locations",
            object_id=location.id,
            description=f"{verb} {location.location_name}",
        )

        return Response({"message": f"{verb} action logged."})

