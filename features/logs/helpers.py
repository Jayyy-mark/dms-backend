import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.db.models import Count, Max, Q, QuerySet
from django.utils import timezone

from features.logs.models import AuditLog


# <!--==============================
#   PAGINATION CONFIG
# ================================-->
DEFAULT_LIMIT = 10
MAX_LIMIT = 500

# Deterministic ordering: "-id" breaks ties between rows sharing the same
# created_at so that LIMIT/OFFSET never returns duplicated / skipped rows.
LOG_ORDERING = ("-created_at", "-id")


def _to_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_pagination(params) -> tuple[int, int]:
    """
    Reads `limit` & `offset` from query params and clamps them to safe values.
    limit  -> 1..MAX_LIMIT (default DEFAULT_LIMIT)
    offset -> >= 0        (default 0)
    """
    limit = _to_int(params.get("limit"), DEFAULT_LIMIT)
    offset = _to_int(params.get("offset"), 0)

    limit = max(1, min(limit, MAX_LIMIT))
    offset = max(0, offset)

    return limit, offset


def parse_snapshot_id(params) -> int | None:
    snapshot_id = _to_int(params.get("snapshot_id"), 0)
    return snapshot_id if snapshot_id > 0 else None


def get_latest_log_id() -> int:
    return AuditLog.objects.aggregate(max_id=Max("id"))["max_id"] or 0


# <!--==============================
#   FILTER HELPERS
# ================================-->
def get_today_start(tz_name: str | None = None) -> datetime.datetime:
    """
    Returns the aware datetime of "today 00:00" in the client's timezone
    (e.g. "Asia/Yangon"). Falls back to the server timezone when the
    provided timezone is missing or invalid.
    """
    tz = timezone.get_current_timezone()
    if tz_name:
        try:
            tz = ZoneInfo(tz_name)
        except (ZoneInfoNotFoundError, ValueError):
            pass

    local_now = timezone.now().astimezone(tz)
    return local_now.replace(hour=0, minute=0, second=0, microsecond=0)


def apply_log_filters(logs: QuerySet, params) -> QuerySet:
    """
    Applies the same filters used by the frontend LogTable
    (date / action / role / search) on an AuditLog queryset.
    """
    date_param = (params.get("date") or "").strip()
    if date_param == "today":
        today_start = get_today_start(params.get("tz"))
        logs = logs.filter(
            created_at__gte=today_start,
            created_at__lt=today_start + datetime.timedelta(days=1),
        )
    elif date_param == "7days":
        past = timezone.now() - datetime.timedelta(days=7)
        logs = logs.filter(created_at__gte=past)
    elif date_param == "30days":
        past = timezone.now() - datetime.timedelta(days=30)
        logs = logs.filter(created_at__gte=past)

    action_param = (params.get("action") or "").strip()
    if action_param and action_param.lower() != "all":
        logs = logs.filter(action__iexact=action_param)

    role_param = (params.get("role") or "").strip()
    if role_param and role_param.lower() != "all":
        logs = logs.filter(user__role__iexact=role_param)

    search_param = (params.get("search") or "").strip()
    if search_param:
        logs = logs.filter(
            Q(description__icontains=search_param)
            | Q(model_name__icontains=search_param)
            | Q(user__username__icontains=search_param)
            | Q(action__icontains=search_param)
        )

    return logs


def get_filtered_logs(params) -> QuerySet:
    logs = AuditLog.objects.select_related("user").order_by(*LOG_ORDERING)
    return apply_log_filters(logs, params)


# <!--==============================
#   PAGINATION
# ================================-->
def paginate_logs(logs: QuerySet, params) -> tuple[QuerySet, dict]:
    """
    Offset pagination (SQL LIMIT / OFFSET) with a snapshot anchor.

    - First request (no snapshot_id) -> snapshot_id = latest log id.
    - Next requests send snapshot_id back -> only rows with id <= snapshot_id
      are counted / returned, so logs inserted while the user is paging do
      not shift the offsets (no duplicated rows between pages).
    """
    limit, offset = parse_pagination(params)
    snapshot_id = parse_snapshot_id(params) or get_latest_log_id()

    logs = logs.filter(id__lte=snapshot_id)

    total = logs.count()
    page_logs = logs[offset : offset + limit]

    total_pages = max(1, -(-total // limit))  # ceil division
    page = (offset // limit) + 1
    shown_until = min(offset + limit, total)

    pagination = {
        "total": total,
        "limit": limit,
        "offset": offset,
        "page": page,
        "total_pages": total_pages,
        "remaining": max(total - shown_until, 0),
        "remaining_pages": max(total_pages - page, 0),
        "has_next": shown_until < total,
        "has_previous": offset > 0,
        "snapshot_id": snapshot_id,
    }

    return page_logs, pagination


# <!--==============================
#   STATS
# ================================-->
def build_log_stats(params) -> dict:
    """
    Aggregated counts for the Logs dashboard header (computed by the DB,
    so the frontend no longer needs to download every log row).
    """
    logs = AuditLog.objects.all()

    today_start = get_today_start(params.get("tz"))
    today = logs.filter(
        created_at__gte=today_start,
        created_at__lt=today_start + datetime.timedelta(days=1),
    ).count()

    actions: dict[str, int] = {}
    for row in logs.values("action").annotate(count=Count("id")):
        key = (row["action"] or "UNKNOWN").upper()
        actions[key] = actions.get(key, 0) + row["count"]

    roles: dict[str, int] = {}
    for row in logs.values("user__role").annotate(count=Count("id")):
        key = row["user__role"] or "Unknown"
        roles[key] = roles.get(key, 0) + row["count"]

    available_roles = sorted(role for role in roles.keys() if role != "Unknown")

    return {
        "total": logs.count(),
        "today": today,
        "actions": actions,
        "roles": roles,
        "available_roles": available_roles,
    }

