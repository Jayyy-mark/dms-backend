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


import io
import os
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def get_pdf_fonts():
    font_name = "Helvetica"
    bold_font_name = "Helvetica-Bold"

    candidates = [
        ("Pyidaungsu", "C:/Windows/Fonts/Pyidaungsu-2.5.3_Regular.ttf"),
        ("Pyidaungsu-Bold", "C:/Windows/Fonts/Pyidaungsu-2.5.3_Bold.ttf"),
        ("MyanmarText", "C:/Windows/Fonts/mmrtext.ttf"),
        ("MyanmarText-Bold", "C:/Windows/Fonts/mmrtextb.ttf"),
    ]
    for name, path in candidates:
        if os.path.exists(path) and name not in pdfmetrics.getRegisteredFontNames():
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception:
                pass

    if "Pyidaungsu" in pdfmetrics.getRegisteredFontNames():
        font_name = "Pyidaungsu"
        bold_font_name = (
            "Pyidaungsu-Bold"
            if "Pyidaungsu-Bold" in pdfmetrics.getRegisteredFontNames()
            else "Pyidaungsu"
        )
    elif "MyanmarText" in pdfmetrics.getRegisteredFontNames():
        font_name = "MyanmarText"
        bold_font_name = (
            "MyanmarText-Bold"
            if "MyanmarText-Bold" in pdfmetrics.getRegisteredFontNames()
            else "MyanmarText"
        )

    return font_name, bold_font_name


class ExportLocationPdfView(APIView):
    def get(self, request: Request) -> HttpResponse:
        dept_filter = get_location_department_filter(request)
        locations = (
            Location.objects.filter(dept_filter)
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

        font_name, bold_font_name = get_pdf_fonts()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Normal"],
            fontName=bold_font_name,
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1a4a98"),
            alignment=1,
        )
        sub_style = ParagraphStyle(
            "SubStyle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            alignment=1,
        )
        th_style = ParagraphStyle(
            "THStyle",
            parent=styles["Normal"],
            fontName=bold_font_name,
            fontSize=10,
            leading=12,
            textColor=colors.white,
            alignment=1,
        )
        td_style = ParagraphStyle(
            "TDStyle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1e293b"),
        )
        td_center = ParagraphStyle(
            "TDCenter",
            parent=td_style,
            alignment=1,
        )

        elements = []
        elements.append(Paragraph("Myanma Oil and Gas Enterprise (MOGE)", title_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"Locations Report ({locations.count()} items)", sub_style))
        elements.append(Spacer(1, 15))

        # Leaving action column on generate
        headers = ["SL", "File Name", "File Type", "Department", "Uploaded Date"]
        table_data = [[Paragraph(h, th_style) for h in headers]]

        for idx, loc in enumerate(locations, start=1):
            file_name = loc.location_name or "Unknown"

            file_type = "image"
            if loc.photo and hasattr(loc.photo, "name") and loc.photo.name:
                parts = loc.photo.name.split(".")
                if len(parts) > 1:
                    file_type = parts[-1].lower()

            dept_name = loc.department.department_name if loc.department else "—"
            uploaded_date = str(loc.date) if loc.date else "—"

            row = [
                Paragraph(str(idx), td_center),
                Paragraph(file_name, td_style),
                Paragraph(file_type, td_center),
                Paragraph(dept_name, td_style),
                Paragraph(uploaded_date, td_center),
            ]
            table_data.append(row)

        col_widths = [40, 260, 90, 250, 100]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4a98")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8fafc")],
                    ),
                ]
            )
        )

        elements.append(t)
        doc.build(elements)

        pdf_value = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf_value, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="locations.pdf"'
        return response
