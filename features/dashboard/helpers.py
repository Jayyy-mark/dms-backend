from django.utils import timezone
from features.staffs.models import Staff
from features.departments.models import Department
from features.documents.models import Document
from features.categories.models import Category
from features.dtypes.models import Dtype
from features.buildings.models import Building
from authentication.models import MogUser


def getStaffCount(department_id=None):
    if department_id is not None:
        return Staff.objects.filter(department_id=department_id).count()
    return Staff.objects.count()


def getDepartmentCount():
    return Department.objects.count()


def getDocumentCount(department_id=None):
    if department_id is not None:
        return Document.objects.filter(staff__department_id=department_id).count()
    return Document.objects.count()


def getUserCount():
    return MogUser.objects.filter(is_active=True).count()


def getCategoryCount():
    return Category.objects.count()


def getBuildingCount():
    return Building.objects.count()


def getPermanentDocumentCount(department_id=None):
    """Count documents with dtype_name 'Permanent' (case-insensitive)."""
    permanent_dtypes = Dtype.objects.filter(dtype_name__icontains="permanent")
    qs = Document.objects.filter(dtype__in=permanent_dtypes, is_archived=False, is_recycled=False)
    if department_id is not None:
        qs = qs.filter(staff__department_id=department_id)
    return qs.count()


def getTemporaryDocumentCount(department_id=None):
    """Count documents with dtype_name 'Temporary' (case-insensitive)."""
    temporary_dtypes = Dtype.objects.filter(dtype_name__icontains="temporary")
    qs = Document.objects.filter(dtype__in=temporary_dtypes, is_archived=False, is_recycled=False)
    if department_id is not None:
        qs = qs.filter(staff__department_id=department_id)
    return qs.count()


def getRecentUploadsCount(department_id=None):
    """Count documents uploaded today."""
    today = timezone.now().date()
    qs = Document.objects.filter(created_at__date=today)
    if department_id is not None:
        qs = qs.filter(staff__department_id=department_id)
    return qs.count()


def getExpiredArchivesCount(department_id=None):
    """Count documents that are expired (expired_at <= today) and not recycled."""
    today = timezone.now().date()
    qs = Document.objects.filter(expired_at__lte=today, is_recycled=False)
    if department_id is not None:
        qs = qs.filter(staff__department_id=department_id)
    return qs.count()


def getDocumentTrafficSummary(department_id=None):
    """Calculate departmental document upload rates and file type breakdown across periods."""
    from datetime import timedelta

    today = timezone.now().date()
    base_qs = Document.objects.filter(is_recycled=False)
    if department_id is not None:
        base_qs = base_qs.filter(staff__department_id=department_id)

    periods = {
        "daily": base_qs.filter(created_at__date=today),
        "weekly": base_qs.filter(created_at__gte=timezone.now() - timedelta(days=7)),
        "monthly": base_qs.filter(created_at__gte=timezone.now() - timedelta(days=30)),
    }

    colors = [
        "bg-indigo-500",
        "bg-teal-500",
        "bg-amber-400",
        "bg-rose-400",
        "bg-cyan-500",
        "bg-purple-500",
        "bg-emerald-500",
        "bg-blue-500",
        "bg-orange-500",
    ]

    all_departments = list(Department.objects.all())

    result = {}
    for p_name, qs in periods.items():
        # Department traffic
        dept_counts = {dept.department_name: 0 for dept in all_departments}
        for doc in qs.select_related("staff__department"):
            if doc.staff and doc.staff.department:
                dname = doc.staff.department.department_name
                dept_counts[dname] = dept_counts.get(dname, 0) + 1

        # Sort by uploads descending
        sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)
        max_val = max([v for _, v in sorted_depts]) if sorted_depts and max([v for _, v in sorted_depts]) > 0 else 1

        dept_list = []
        for idx, (name, val) in enumerate(sorted_depts[:7]):
            pct = round((val / max_val) * 100) if val > 0 else 0
            dept_list.append({
                "name": name,
                "value": val,
                "percent": pct,
                "color": colors[idx % len(colors)],
            })

        # File types breakdown
        type_counts = {"PDF": 0, "DOCX": 0, "XLSX": 0, "Images": 0}
        for doc in qs:
            fname = doc.document.name.lower() if doc.document else ""
            ext = fname.split(".")[-1] if "." in fname else ""
            if ext == "pdf":
                type_counts["PDF"] += 1
            elif ext in ["docx", "doc"]:
                type_counts["DOCX"] += 1
            elif ext in ["xlsx", "xls", "csv"]:
                type_counts["XLSX"] += 1
            elif ext in ["png", "jpg", "jpeg", "gif", "webp", "svg"]:
                type_counts["Images"] += 1

        total_files = sum(type_counts.values())
        file_list = [
            {
                "type": "PDF",
                "count": type_counts["PDF"],
                "percent": round((type_counts["PDF"] / total_files) * 100) if total_files > 0 else 0,
                "color": "bg-red-400",
            },
            {
                "type": "DOCX",
                "count": type_counts["DOCX"],
                "percent": round((type_counts["DOCX"] / total_files) * 100) if total_files > 0 else 0,
                "color": "bg-blue-400",
            },
            {
                "type": "XLSX",
                "count": type_counts["XLSX"],
                "percent": round((type_counts["XLSX"] / total_files) * 100) if total_files > 0 else 0,
                "color": "bg-emerald-400",
            },
            {
                "type": "Images",
                "count": type_counts["Images"],
                "percent": round((type_counts["Images"] / total_files) * 100) if total_files > 0 else 0,
                "color": "bg-purple-400",
            },
        ]

        result[p_name] = {
            "departments": dept_list,
            "fileTypes": file_list,
        }

    return result


def getStaffPerformanceSummary(department_id=None):
    """Calculate staff distribution per department and top document uploaders per period."""
    from datetime import timedelta

    today = timezone.now().date()
    base_qs = Document.objects.filter(is_recycled=False)
    if department_id is not None:
        base_qs = base_qs.filter(staff__department_id=department_id)

    periods = {
        "daily": base_qs.filter(created_at__date=today),
        "weekly": base_qs.filter(created_at__gte=timezone.now() - timedelta(days=7)),
        "monthly": base_qs.filter(created_at__gte=timezone.now() - timedelta(days=30)),
    }

    avatar_colors = [
        "bg-blue-100 text-[#997524]",
        "bg-teal-100 text-teal-600",
        "bg-indigo-100 text-indigo-600",
        "bg-amber-100 text-amber-600",
        "bg-rose-100 text-rose-600",
        "bg-purple-100 text-purple-600",
        "bg-cyan-100 text-cyan-600",
        "bg-emerald-100 text-emerald-600",
    ]

    uploads_by_period = {}
    for p_name, qs in periods.items():
        staff_counts = {}
        for doc in qs.select_related("staff__department"):
            if doc.staff:
                s_id = doc.staff.id
                if s_id not in staff_counts:
                    staff_counts[s_id] = {
                        "id": s_id,
                        "name": doc.staff.staff_name,
                        "dept": doc.staff.department.department_name if doc.staff.department else "-",
                        "uploads": 0,
                    }
                staff_counts[s_id]["uploads"] += 1

        sorted_staff = sorted(staff_counts.values(), key=lambda x: x["uploads"], reverse=True)
        for idx, s in enumerate(sorted_staff):
            s["avatar"] = avatar_colors[idx % len(avatar_colors)]
        uploads_by_period[p_name] = sorted_staff

    dept_stats = {}
    departments_list = []
    for d in Department.objects.all():
        count = Staff.objects.filter(department=d).count()
        dept_stats[d.department_name] = count
        departments_list.append(d.department_name)

    total_staff = Staff.objects.count() if department_id is None else Staff.objects.filter(department_id=department_id).count()
    active_users = MogUser.objects.filter(is_active=True).count()

    return {
        "total_staff": total_staff,
        "active_users": active_users,
        "departments": departments_list,
        "department_counts": dept_stats,
        "uploads": uploads_by_period,
    }


def getCategoryDocumentSummary(department_id=None, department_name=None):
    """Calculate hierarchical category document tree and aggregated document counts per period."""
    from datetime import timedelta

    today = timezone.now().date()
    base_qs = Document.objects.filter(is_recycled=False)

    if department_id is not None:
        base_qs = base_qs.filter(staff__department_id=department_id)
    elif department_name and department_name != "အားလုံး":
        base_qs = base_qs.filter(staff__department__department_name=department_name)

    periods = {
        "daily": base_qs.filter(created_at__date=today),
        "weekly": base_qs.filter(created_at__gte=timezone.now() - timedelta(days=7)),
        "monthly": base_qs.filter(created_at__gte=timezone.now() - timedelta(days=30)),
    }

    all_cats = list(Category.objects.all())
    cat_by_id = {c.id: c for c in all_cats}

    children_map = {}
    for c in all_cats:
        children_map.setdefault(c.parent_id, []).append(c.id)

    def get_all_descendant_ids(cat_id):
        descendants = [cat_id]
        for child_id in children_map.get(cat_id, []):
            descendants.extend(get_all_descendant_ids(child_id))
        return descendants

    def build_tree_node(c, level=1):
        child_nodes = [build_tree_node(cat_by_id[cid], level + 1) for cid in children_map.get(c.id, [])]
        return {
            "id": str(c.id),
            "category_id": c.category_id,
            "name": c.category_name,
            "level": level,
            "parent_id": str(c.parent_id) if c.parent_id is not None else None,
            "children": child_nodes,
        }

    root_tree = [build_tree_node(c, 1) for c in all_cats if c.parent_id is None]

    counts_by_period = {}
    for p_name, qs in periods.items():
        doc_cat_counts = {}
        for d in qs.values("category_id"):
            cid = d["category_id"]
            if cid:
                doc_cat_counts[cid] = doc_cat_counts.get(cid, 0) + 1

        cat_total_counts = {}
        for c in all_cats:
            desc_ids = get_all_descendant_ids(c.id)
            total = sum(doc_cat_counts.get(did, 0) for did in desc_ids)
            cat_total_counts[str(c.id)] = total

        counts_by_period[p_name] = cat_total_counts

    departments_list = list(Department.objects.values_list("department_name", flat=True))

    return {
        "tree": root_tree,
        "counts": counts_by_period,
        "departments": departments_list,
    }


def globalSystemSearch(query: str, user, limit: int = 5):
    """
    Fast, permission- and department-scoped global search across core MOGE models.
    Uses values/select_related + strict LIMIT slicing + short-lived cache for low latency.
    """
    import unicodedata
    from django.db.models import Q
    from django.core.cache import cache
    from features.locations.models import Location
    from features.rooms.models import Room
    from common.security.authorization.roles import Roles

    clean_q = unicodedata.normalize("NFKC", (query or "").strip())
    if not clean_q:
        return {
            "query": "",
            "total": 0,
            "results": {
                "documents": [],
                "locations": [],
                "staffs": [],
                "departments": [],
                "categories": [],
                "facilities": [],
                "users": [],
            },
        }

    safe_limit = max(1, min(int(limit or 5), 10))
    user_role = getattr(user, "role", "") or ""
    is_privileged = user_role in Roles.PRIVILEGED

    department_id = None
    if not is_privileged:
        staff_obj = getattr(user, "staff", None)
        if staff_obj is not None:
            department_id = staff_obj.department_id

    cache_key = f"global_search:{getattr(user, 'id', 0)}:{user_role}:{department_id}:{clean_q.lower()}:{safe_limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 1. Documents
    doc_qs = Document.objects.select_related("category", "staff__department", "dtype").filter(
        Q(document_name__icontains=clean_q)
        | Q(document_id__icontains=clean_q)
        | Q(description__icontains=clean_q)
        | Q(category__category_name__icontains=clean_q)
        | Q(staff__staff_name__icontains=clean_q)
    )
    if department_id is not None:
        doc_qs = doc_qs.filter(staff__department_id=department_id)

    documents = []
    for d in doc_qs.order_by("-updated_at")[:safe_limit]:
        if d.is_recycled:
            status = "recycled"
            target_url = "/documents/recycles/"
        elif d.is_archived:
            status = "archived"
            target_url = "/documents/archives/"
        else:
            status = "active"
            target_url = f"/documents/edit/{d.id}"

        subtitle_parts = []
        if d.category:
            subtitle_parts.append(d.category.category_name)
        if d.staff and d.staff.department:
            subtitle_parts.append(d.staff.department.department_name)
        elif d.staff:
            subtitle_parts.append(d.staff.staff_name)

        documents.append({
            "id": d.id,
            "code": d.document_id,
            "title": d.document_name,
            "subtitle": " • ".join(subtitle_parts) if subtitle_parts else (d.description or "Document"),
            "status": status,
            "file_url": d.document.url if d.document else None,
            "url": target_url,
            "type": "document",
        })

    # 2. Locations / Activity Records
    loc_qs = Location.objects.select_related("department").filter(
        Q(location_name__icontains=clean_q)
        | Q(location_id__icontains=clean_q)
        | Q(city__icontains=clean_q)
        | Q(state_division__icontains=clean_q)
        | Q(location_type__icontains=clean_q)
        | Q(description__icontains=clean_q)
        | Q(department__department_name__icontains=clean_q)
    )
    if department_id is not None:
        loc_qs = loc_qs.filter(department_id=department_id)

    locations = []
    for loc in loc_qs.order_by("-id")[:safe_limit]:
        sub = [p for p in [loc.city, loc.state_division, loc.department.department_name if loc.department else None] if p]
        locations.append({
            "id": loc.id,
            "code": loc.location_id,
            "title": loc.location_name,
            "subtitle": " • ".join(sub) if sub else (loc.location_type or "Activity Location"),
            "url": f"/locations/edit/{loc.id}",
            "type": "location",
        })

    # 3. Staffs
    staff_qs = Staff.objects.select_related("department", "rank", "role").filter(
        Q(staff_name__icontains=clean_q)
        | Q(staff_id__icontains=clean_q)
        | Q(staff_email__icontains=clean_q)
        | Q(staff_ph_number__icontains=clean_q)
        | Q(department__department_name__icontains=clean_q)
        | Q(rank__rank_name__icontains=clean_q)
    )
    if department_id is not None:
        staff_qs = staff_qs.filter(department_id=department_id)

    staffs = []
    for s in staff_qs.order_by("-id")[:safe_limit]:
        sub = [p for p in [s.rank.rank_name if s.rank else None, s.department.department_name if s.department else None, s.staff_email] if p]
        staffs.append({
            "id": s.id,
            "code": s.staff_id,
            "title": s.staff_name,
            "subtitle": " • ".join(sub) if sub else "Staff Member",
            "url": f"/staff/edit/{s.id}",
            "type": "staff",
        })

    # 4. Departments
    dept_qs = Department.objects.select_related("room__building").filter(
        Q(department_name__icontains=clean_q)
        | Q(department_id__icontains=clean_q)
        | Q(room__room_name__icontains=clean_q)
    )
    departments = []
    for dept in dept_qs.order_by("department_name")[:safe_limit]:
        room_info = None
        if dept.room:
            room_info = f"{dept.room.room_name}" + (f" ({dept.room.building.building_name})" if dept.room.building else "")
        departments.append({
            "id": dept.id,
            "code": dept.department_id,
            "title": dept.department_name,
            "subtitle": room_info or "Department",
            "url": f"/departments/edit/{dept.id}",
            "type": "department",
        })

    # 5. Categories
    cat_qs = Category.objects.select_related("parent").filter(
        Q(category_name__icontains=clean_q) | Q(category_id__icontains=clean_q)
    )
    categories = []
    for cat in cat_qs.order_by("category_name")[:safe_limit]:
        categories.append({
            "id": cat.id,
            "code": cat.category_id,
            "title": cat.category_name,
            "subtitle": f"Parent: {cat.parent.category_name}" if cat.parent else "Root Category",
            "url": f"/categories/edit/{cat.id}",
            "type": "category",
        })

    # 6. Facilities (Buildings & Rooms)
    facilities = []
    for b in Building.objects.filter(Q(building_name__icontains=clean_q) | Q(building_id__icontains=clean_q))[:3]:
        facilities.append({
            "id": b.id,
            "code": b.building_id,
            "title": b.building_name,
            "subtitle": "Building",
            "url": f"/buildings/edit/{b.id}",
            "type": "building",
        })
    for r in Room.objects.select_related("building").filter(
        Q(room_name__icontains=clean_q) | Q(room_id__icontains=clean_q)
    )[:3]:
        facilities.append({
            "id": r.id,
            "code": r.room_id,
            "title": r.room_name,
            "subtitle": f"Room • {r.building.building_name}" if r.building else "Room",
            "url": f"/rooms/edit/{r.id}",
            "type": "room",
        })

    # 7. Users (Privileged / Admin roles)
    users = []
    if is_privileged:
        user_qs = MogUser.objects.select_related("staff").filter(
            Q(username__icontains=clean_q)
            | Q(email__icontains=clean_q)
            | Q(user_id__icontains=clean_q)
            | Q(role__icontains=clean_q)
        )
        for u in user_qs.order_by("-id")[:safe_limit]:
            users.append({
                "id": u.id,
                "code": u.user_id,
                "title": u.username,
                "subtitle": f"{u.email} • {u.role}",
                "url": f"/users/edit/{u.id}",
                "type": "user",
            })

    total = (
        len(documents)
        + len(locations)
        + len(staffs)
        + len(departments)
        + len(categories)
        + len(facilities)
        + len(users)
    )

    payload = {
        "query": clean_q,
        "total": total,
        "results": {
            "documents": documents,
            "locations": locations,
            "staffs": staffs,
            "departments": departments,
            "categories": categories,
            "facilities": facilities,
            "users": users,
        },
    }
    cache.set(cache_key, payload, timeout=15)
    return payload
