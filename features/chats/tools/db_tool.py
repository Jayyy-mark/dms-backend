from langchain_core.tools import tool
from django.db.models import Q
from urllib.parse import unquote
from features.staffs.models import Staff
from features.departments.models import Department
from features.ranks.models import Rank
from features.roles.models import Role
from features.stypes.models import Stype
from features.documents.models import Document as DBDocument
from features.buildings.models import Building
from features.rooms.models import Room
from authentication.models import MogUser
from features.logs.models import AuditLog


@tool
def query_database_tool(query: str) -> str:
    """
    Search the system database for information regarding Staff, Departments, Ranks, Roles, Buildings, Rooms, Document Records, Users (authentication_moguser), and Audit Logs.
    Use this tool whenever the user asks about staff members, staff count, departments, ranks, roles, users, user accounts, user logs, audit logs, recent actions, login history, or database metadata.
    """
    query_lower = query.lower().strip()
    results = []

    # 1. Staff Search
    staff_qs = Staff.objects.all().select_related("department", "role", "rank", "stype")

    # Check if query is looking for staff count or list
    if any(
        k in query_lower
        for k in [
            "how many staff",
            "staff count",
            "total staff",
            "list staff",
            "all staff",
        ]
    ):
        total_staff = staff_qs.count()
        results.append(f"Total Staff Count: {total_staff}")
        staff_samples = staff_qs[:15]
        results.append("Staff List Summary:")
        for s in staff_samples:
            dept_name = s.department.department_name if s.department else "N/A"
            role_name = s.role.role_name if s.role else "N/A"
            rank_name = s.rank.rank_name if s.rank else "N/A"
            results.append(
                f"- ID: {s.staff_id} | Name: {s.staff_name} | Dept: {dept_name} | Role: {role_name} | Rank: {rank_name} | Email: {s.staff_email} | Phone: {s.staff_ph_number} | Gender: {s.staff_gender}"
            )
    else:
        # Search by specific keyword/name in staff — but skip if query is clearly about logs/actions/users
        is_log_query = any(
            k in query_lower
            for k in ["log", "logs", "audit", "action", "actions", "activity", "activities", "last action", "latest action"]
        )
        if not is_log_query:
            staff_stop_words = {
                "the", "is", "are", "was", "were", "it", "its", "on", "in", "a", "an",
                "of", "to", "for", "and", "or", "not", "this", "that", "what", "how",
                "who", "which", "when", "where", "why", "do", "did", "does", "can",
                "has", "have", "had", "get", "me", "my", "our", "with", "from",
                "about", "many", "much", "please", "tell", "find", "search", "show",
                "system", "mean", "there", "here", "been",
            }
            terms = [t for t in query_lower.split() if len(t) > 1 and t not in staff_stop_words]
            staff_filter = Q()
            for term in terms:
                staff_filter |= (
                    Q(staff_name__icontains=term)
                    | Q(staff_id__icontains=term)
                    | Q(staff_email__icontains=term)
                    | Q(staff_ph_number__icontains=term)
                    | Q(department__department_name__icontains=term)
                    | Q(role__role_name__icontains=term)
                    | Q(rank__rank_name__icontains=term)
                )
            if staff_filter:
                matched_staff = staff_qs.filter(staff_filter).distinct()[:10]
                if matched_staff.exists():
                    results.append(f"Matched Staff Members ({matched_staff.count()} found):")
                    for s in matched_staff:
                        dept_name = s.department.department_name if s.department else "N/A"
                        role_name = s.role.role_name if s.role else "N/A"
                        rank_name = s.rank.rank_name if s.rank else "N/A"
                        results.append(
                            f"- Staff ID: {s.staff_id} | Name: {s.staff_name} | Department: {dept_name} | Role: {role_name} | Rank: {rank_name} | Email: {s.staff_email} | Phone: {s.staff_ph_number} | Address: {s.staff_address}"
                        )

    # 2. Department Search
    depts = Department.objects.all()
    if any(k in query_lower for k in ["department", "dept"]):
        results.append("\nDepartments in Database:")
        for d in depts:
            staff_count = d.staffs.count()
            results.append(
                f"- {d.department_name} (Code: {d.department_id}) - Staff Count: {staff_count}"
            )

    # 3. Document Records in DB — skip for clearly log/audit queries
    is_log_or_audit_query = any(
        k in query_lower
        for k in ["log", "logs", "audit", "audit log", "action", "actions", "activity", "last action", "latest action"]
    )
    if not is_log_or_audit_query:
        doc_qs = DBDocument.objects.filter(is_archived=False, is_recycled=False)
        doc_stop_words = {
            "the", "is", "are", "was", "were", "its", "on", "in", "of", "to",
            "for", "and", "or", "not", "this", "that", "what", "how", "who",
            "which", "when", "where", "why", "can", "has", "have", "had", "get",
            "with", "from", "about", "many", "much", "please", "tell", "find",
            "search", "show", "system", "mean", "there", "here", "been",
        }
        terms = [t for t in query_lower.split() if len(t) > 2 and t not in doc_stop_words]
        doc_filter = Q()
        for term in terms:
            doc_filter |= (
                Q(document_name__icontains=term)
                | Q(document_id__icontains=term)
                | Q(description__icontains=term)
            )

        if doc_filter:
            matched_docs = doc_qs.filter(doc_filter).distinct()[:10]
            if matched_docs.exists():
                results.append("\nMatched Document Metadata in Database:")
                for doc in matched_docs:
                    staff_name = doc.staff.staff_name if doc.staff else "N/A"
                    # Decode the URL-encoded file path for clean display
                    if doc.document:
                        decoded_url = unquote(doc.document.url)
                        file_display = doc.document_name or decoded_url
                    else:
                        decoded_url = "N/A"
                        file_display = "N/A"
                    results.append(
                        f"- Document ID: {doc.document_id} | Name: {doc.document_name} | Staff: {staff_name} | File: {file_display} | Description: {doc.description or 'N/A'}"
                    )

    # 4. User (MogUser / authentication_moguser) Search
    if any(
        k in query_lower
        for k in [
            "how many user",
            "user count",
            "total user",
            "list user",
            "all user",
            "authentication_moguser",
            "moguser",
        ]
    ):
        user_qs = MogUser.objects.all().select_related("staff")
        total_users = user_qs.count()
        results.append(f"\nTotal User Accounts: {total_users}")
        user_samples = user_qs[:20]
        results.append("User Accounts List:")
        for u in user_samples:
            staff_name = u.staff.staff_name if u.staff else "N/A"
            results.append(
                f"- User ID: {u.user_id} | Username: {u.username} | Email: {u.email} | Role: {u.role} | Staff: {staff_name} | Active: {u.is_active} | Joined: {u.date_joined}"
            )
    else:
        # Search users by keyword — but skip if query is clearly about logs/audit
        is_log_query = any(
            k in query_lower
            for k in ["log", "logs", "audit", "audit log", "user log", "action", "actions", "activity", "last action"]
        )
        if not is_log_query and any(
            k in query_lower
            for k in ["user", "account", "login user", "registered"]
        ):
            user_qs = MogUser.objects.all().select_related("staff")
            user_stop_words = {
                "user", "users", "account", "accounts", "registered", "the", "is",
                "are", "a", "an", "of", "to", "for", "and", "or", "not", "this",
                "that", "what", "how", "who", "which", "when", "where", "why",
                "on", "in", "it", "its", "do", "did", "does", "can", "has",
                "have", "had", "get", "me", "my", "our", "with", "from", "about",
                "many", "much", "please", "tell", "find", "search", "show",
                "system", "mean", "there", "here", "been",
            }
            terms = [t for t in query_lower.split() if len(t) > 1 and t not in user_stop_words]
            user_filter = Q()
            for term in terms:
                user_filter |= (
                    Q(username__icontains=term)
                    | Q(email__icontains=term)
                    | Q(user_id__icontains=term)
                    | Q(role__icontains=term)
                    | Q(staff__staff_name__icontains=term)
                )
            if user_filter:
                matched_users = user_qs.filter(user_filter).distinct()[:10]
                if matched_users.exists():
                    results.append(f"\nMatched User Accounts ({matched_users.count()} found):")
                    for u in matched_users:
                        staff_name = u.staff.staff_name if u.staff else "N/A"
                        results.append(
                            f"- User ID: {u.user_id} | Username: {u.username} | Email: {u.email} | Role: {u.role} | Staff: {staff_name} | Active: {u.is_active} | Joined: {u.date_joined}"
                        )

    # 5. Audit Log Search
    if any(
        k in query_lower
        for k in [
            "log",
            "logs",
            "audit",
            "audit log",
            "action",
            "actions",
            "latest action",
            "last action",
            "recent action",
            "who performed",
            "who did",
            "login history",
            "user log",
            "activity",
            "activities",
        ]
    ):
        log_qs = AuditLog.objects.all().select_related("user").order_by("-created_at")

        # Check for action type filter
        action_types = ["CREATE", "UPDATE", "DELETE", "LOGIN", "ARCHIVE", "RESTORE", "OTHER"]
        action_filter = None
        for action_type in action_types:
            if action_type.lower() in query_lower:
                action_filter = action_type
                break

        if action_filter:
            log_qs = log_qs.filter(action=action_filter)

        # Filter by specific model/user name ONLY if meaningful terms remain
        # Comprehensive stop words to avoid false-positive filtering
        stop_words = {
            "log", "logs", "audit", "action", "actions", "the", "for", "what",
            "latest", "last", "recent", "who", "performed", "check", "table",
            "user", "users", "show", "list", "all", "history", "activity",
            "activities", "this", "that", "system", "on", "in", "is", "are",
            "was", "were", "it", "its", "do", "did", "does", "can", "could",
            "would", "should", "will", "how", "many", "much", "get", "give",
            "me", "my", "our", "mean", "about", "from", "with", "has", "have",
            "had", "been", "there", "here", "which", "when", "where", "why",
            "please", "tell", "find", "search", "look", "see", "view",
            "record", "records", "data", "info", "information", "database",
            "and", "or", "not", "no", "yes", "any", "some",
        }
        model_terms = [
            t for t in query_lower.split()
            if len(t) > 2 and t not in stop_words
        ]
        if model_terms:
            model_filter = Q()
            for term in model_terms:
                model_filter |= (
                    Q(model_name__icontains=term)
                    | Q(description__icontains=term)
                    | Q(user__username__icontains=term)
                    | Q(user__email__icontains=term)
                )
            filtered_qs = log_qs.filter(model_filter)
            # Only apply filter if it actually returns results;
            # otherwise fall back to unfiltered (latest) logs
            if filtered_qs.exists():
                log_qs = filtered_qs

        total_logs = log_qs.count()
        log_samples = log_qs[:15]
        if total_logs > 0:
            results.append(f"\nAudit Logs ({total_logs} total matching records, showing latest {min(total_logs, 15)}):")
            for log in log_samples:
                user_display = log.user.username if log.user else "System"
                user_email = log.user.email if log.user else "N/A"
                results.append(
                    f"- [{log.created_at.strftime('%Y-%m-%d %H:%M:%S')}] User: {user_display} ({user_email}) | Action: {log.action} | Model: {log.model_name} | Object ID: {log.object_id or 'N/A'} | Description: {log.description or 'N/A'}"
                )
        else:
            results.append("\nNo audit log records found in the system.")

    if not results:
        return f"No database records found matching query: '{query}'. You can try searching by staff name, department name, user account, audit log, or document title."

    return "\n".join(results)


def get_related_documents(query: str) -> list:
    """
    Search for documents related to the query and return structured metadata
    for rendering as clickable source document links in the frontend.
    """
    query_lower = query.lower().strip()
    terms = [t for t in query_lower.split() if len(t) > 2]

    doc_qs = DBDocument.objects.filter(is_archived=False, is_recycled=False)
    doc_filter = Q()
    for term in terms:
        doc_filter |= (
            Q(document_name__icontains=term)
            | Q(document_id__icontains=term)
            | Q(description__icontains=term)
            | Q(staff__staff_name__icontains=term)
        )

    matched_docs = doc_qs.filter(doc_filter).distinct()[:10]
    source_docs = []
    seen = set()

    for doc in matched_docs:
        file_url = doc.document.url if doc.document else ""
        file_name = doc.document_name or (unquote(file_url) if file_url else "Unknown")

        if file_name in seen:
            continue
        seen.add(file_name)

        staff_name = doc.staff.staff_name if doc.staff else "N/A"
        snippet = (
            doc.description or f"Document ID: {doc.document_id} | Staff: {staff_name}"
        )

        source_docs.append(
            {
                "file_name": file_name,
                "file_url": file_url,
                "page": 1,
                "snippet": snippet,
            }
        )

    return source_docs
