from rest_framework.response import Response
from rest_framework import status
from features.logs.models import AuditLog


def removeNoneValue(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None}


def toApiResponse(data=None, message="") -> Response:
    return Response({"data": data, "message": message}, status=status.HTTP_201_CREATED)


def generateId(model, field, prefix) -> str:
    last_id = model.objects.order_by(f"-{field}").values_list(field, flat=True).first()
    if last_id:
        number = int(last_id.split("-")[1]) + 1
        return f"{prefix}-{number:03d}"
    else:
        number = 1
    return f"{prefix}-{number:03d}"


def log_action(user, action, model_name, object_id=None, description=""):
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
    )


DEFAULT_PAGE_LIMIT = 10
MAX_PAGE_LIMIT = 500


def _to_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def paginate_queryset(queryset, model_class, params):
    """
    Database-level offset pagination (SQL LIMIT / OFFSET) with snapshot_id anchor.
    Matches the exact pagination response contract used by features.logs.
    """
    from django.db.models import Max

    limit = max(1, min(_to_int(params.get("limit"), DEFAULT_PAGE_LIMIT), MAX_PAGE_LIMIT))
    offset = max(0, _to_int(params.get("offset"), 0))

    raw_snapshot = _to_int(params.get("snapshot_id"), 0)
    snapshot_id = raw_snapshot if raw_snapshot > 0 else (
        model_class.objects.aggregate(max_id=Max("id"))["max_id"] or 0
    )

    if snapshot_id > 0:
        queryset = queryset.filter(id__lte=snapshot_id)

    total = queryset.count()
    page_items = queryset[offset : offset + limit]

    total_pages = max(1, -(-total // limit))
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

    return page_items, pagination
