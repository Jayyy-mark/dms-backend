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