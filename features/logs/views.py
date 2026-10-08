import io
import os
import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q
from rest_framework.views import APIView, Request, Response
from features.logs.models import AuditLog
from features.logs.serializers import LogSerializer

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


class LogView(APIView):

    def get(self, request: Request) -> Response:

        logs = AuditLog.objects.select_related("user").all().order_by("-created_at")

        return Response({"logs": LogSerializer(logs, many=True).data})


class ExportLogPdfView(APIView):
    def get(self, request: Request) -> HttpResponse:
        logs = AuditLog.objects.select_related("user").all().order_by("-created_at")

        date_param = request.query_params.get("date", "").strip()
        if date_param == "today":
            logs = logs.filter(created_at__date=timezone.now().date())
        elif date_param == "7days":
            past = timezone.now() - datetime.timedelta(days=7)
            logs = logs.filter(created_at__gte=past)
        elif date_param == "30days":
            past = timezone.now() - datetime.timedelta(days=30)
            logs = logs.filter(created_at__gte=past)

        action_param = request.query_params.get("action", "").strip()
        if action_param and action_param.lower() != "all":
            logs = logs.filter(action__iexact=action_param)

        role_param = request.query_params.get("role", "").strip()
        if role_param and role_param.lower() != "all":
            logs = logs.filter(user__role__iexact=role_param)

        search_param = request.query_params.get("search", "").strip()
        if search_param:
            logs = logs.filter(
                Q(description__icontains=search_param)
                | Q(model_name__icontains=search_param)
                | Q(user__username__icontains=search_param)
                | Q(action__icontains=search_param)
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
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=1,
        )
        td_style = ParagraphStyle(
            "TDStyle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=8.5,
            leading=11,
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
        now_str = timezone.now().strftime("%Y-%m-%d %H:%M")
        elements.append(
            Paragraph(
                f"System Audit Logs Report ({logs.count()} entries • Generated {now_str})",
                sub_style,
            )
        )
        elements.append(Spacer(1, 15))

        headers = ["ID", "User", "Role", "Event", "Resource", "Description", "Date & Time"]
        table_data = [[Paragraph(h, th_style) for h in headers]]

        for log in logs:
            username = log.user.username if log.user else "Unknown"
            role = log.user.role if log.user and log.user.role else "N/A"
            action = log.action or "UNKNOWN"
            resource = log.model_name or "System"
            desc = log.description or ""
            date_time = log.created_at.strftime("%Y-%m-%d %H:%M") if log.created_at else "—"

            action_upper = action.upper()
            action_color = (
                "#059669"
                if action_upper == "CREATE"
                else "#b45309"
                if action_upper == "UPDATE"
                else "#dc2626"
                if action_upper == "DELETE"
                else "#475569"
            )
            event_p = Paragraph(f"<font color='{action_color}'><b>{action_upper}</b></font>", td_center)

            row = [
                Paragraph(str(log.id), td_center),
                Paragraph(username, td_style),
                Paragraph(role, td_center),
                event_p,
                Paragraph(resource, td_style),
                Paragraph(desc, td_style),
                Paragraph(date_time, td_center),
            ]
            table_data.append(row)

        col_widths = [35, 75, 65, 60, 75, 330, 140]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4a98")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
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
        response["Content-Disposition"] = 'attachment; filename="system_logs.pdf"'
        return response
