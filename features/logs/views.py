import html
import io
import os
import fitz
from django.utils import timezone
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.views import APIView, Request, Response
from features.logs.serializers import LogSerializer
from features.logs.helpers import get_filtered_logs, paginate_logs, build_log_stats
from features.locations.views import get_pdf_font_archive_and_css


# <!--==============================
#   LOGS VIEWS
# ================================-->
@method_decorator(never_cache, name="dispatch")
class LogView(APIView):
    """
    GET log/all/ -> every log (optionally filtered by date/action/role/search).
    Kept for backward compatibility (dashboard widget, client-side exports).
    """

    def get(self, request: Request) -> Response:

        logs = get_filtered_logs(request.query_params)

        return Response({"logs": LogSerializer(logs, many=True).data})


@method_decorator(never_cache, name="dispatch")
class LogListView(APIView):
    """
    GET log/list/?limit=50&offset=0&date=&action=&role=&search=&snapshot_id=&tz=
    Server-side pagination: only `limit` rows are read from the database
    (SQL LIMIT / OFFSET) together with the total count of matching rows.
    """

    def get(self, request: Request) -> Response:

        logs = get_filtered_logs(request.query_params)
        page_logs, pagination = paginate_logs(logs, request.query_params)

        return Response(
            {
                "logs": LogSerializer(page_logs, many=True).data,
                "pagination": pagination,
            }
        )


@method_decorator(never_cache, name="dispatch")
class LogStatsView(APIView):
    """
    GET log/stats/?tz= -> aggregated counts for the Logs dashboard header.
    """

    def get(self, request: Request) -> Response:

        return Response({"stats": build_log_stats(request.query_params)})


@method_decorator(never_cache, name="dispatch")
class ExportLogPdfView(APIView):
    def get(self, request: Request) -> HttpResponse:
        logs = list(get_filtered_logs(request.query_params))
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
            font-size: 9pt;
            padding: 5pt 5pt;
            border: 0.5pt solid #e2e8f0;
            text-align: center;
        }}
        td {{
            font-size: 8.5pt;
            padding: 5pt 5pt;
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

        now_str = timezone.now().strftime("%Y-%m-%d %H:%M")
        tr_list = []

        for idx, log in enumerate(logs, start=1):
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
            row_cls = "odd" if idx % 2 == 1 else "even"

            tr_list.append(
                f"""
                <tr class="{row_cls}">
                    <td class="center" width="35">{log.id}</td>
                    <td class="left" width="75">{html.escape(str(username))}</td>
                    <td class="center" width="65">{html.escape(str(role))}</td>
                    <td class="center" width="60"><span style="color: {action_color}; font-weight: bold;">{html.escape(str(action_upper))}</span></td>
                    <td class="left" width="75">{html.escape(str(resource))}</td>
                    <td class="left" width="330">{html.escape(str(desc))}</td>
                    <td class="center" width="140">{html.escape(str(date_time))}</td>
                </tr>
                """
            )

        if not tr_list:
            tr_list.append(
                """
                <tr class="odd">
                    <td class="center" colspan="7">No audit logs found.</td>
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
                <div class="subtitle">System Audit Logs Report ({len(logs)} entries • Generated {now_str})</div>
            </div>
            <table>
                <thead>
                    <tr>
                        <th width="35">ID</th>
                        <th width="75">User</th>
                        <th width="65">Role</th>
                        <th width="60">Event</th>
                        <th width="75">Resource</th>
                        <th width="330">Description</th>
                        <th width="140">Date &amp; Time</th>
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
        response["Content-Disposition"] = 'attachment; filename="system_logs.pdf"'
        return response
