import os
import random
from datetime import timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.utils import timezone
from django.db import transaction

from features.buildings.models import Building
from features.rooms.models import Room
from features.departments.models import Department
from features.roles.models import Role
from features.ranks.models import Rank
from features.stypes.models import Stype
from features.dtypes.models import Dtype
from features.categories.models import Category
from features.staffs.models import Staff
from features.documents.models import Document
from features.locations.models import Location, LocationPhoto


def pick_split_datetime(index: int, total: int = 1000):
    """
    Distribute timestamps across:
      - ~15% Today (0 days ago)
      - ~25% This Week (1 to 6 days ago)
      - ~30% This Month (8 to 28 days ago)
      - ~30% Past Months (35 to 240 days ago)
    """
    now = timezone.now()
    ratio = (index % total) / float(total)
    if ratio < 0.15:
        hours_ago = random.randint(0, max(1, now.hour))
        mins_ago = random.randint(1, 55)
        return now - timedelta(hours=hours_ago, minutes=mins_ago)
    elif ratio < 0.40:
        days_ago = random.randint(1, 6)
        return now - timedelta(days=days_ago, hours=random.randint(1, 20), minutes=random.randint(0, 59))
    elif ratio < 0.70:
        days_ago = random.randint(8, 28)
        return now - timedelta(days=days_ago, hours=random.randint(1, 20), minutes=random.randint(0, 59))
    else:
        days_ago = random.randint(35, 240)
        return now - timedelta(days=days_ago, hours=random.randint(1, 20), minutes=random.randint(0, 59))


def main():
    random.seed(20261102)

    all_buildings = list(Building.objects.all())
    all_rooms = list(Room.objects.all())
    all_depts = list(Department.objects.all())
    all_roles = list(Role.objects.all())
    all_ranks = list(Rank.objects.all())
    all_stypes = list(Stype.objects.all())
    all_cats = list(Category.objects.all())

    perm_dtype = Dtype.objects.filter(dtype_name__icontains="permanent").first()
    temp_dtype = Dtype.objects.filter(dtype_name__icontains="temporary").first()

    # ── 1. Add 1,000 More Staffs ──
    existing_staff_ids = set(Staff.objects.values_list("staff_id", flat=True))
    existing_staff_names = set(Staff.objects.values_list("staff_name", flat=True))
    existing_staff_emails = set(Staff.objects.values_list("staff_email", flat=True))
    existing_staff_phones = set(Staff.objects.values_list("staff_ph_number", flat=True))

    prefixes_m = ["ဦး", "U "]
    prefixes_f = ["ဒေါ်", "Daw "]
    first_parts = [
        "အောင်", "ကျော်", "မင်း", "ဇော်", "ထွန်း", "သိန်း", "ဝင်း", "မြင့်", "စိုး", "သန်း",
        "ခင်", "မေ", "စု", "နှင်း", "ဖြူ", "သီတာ", "နန္ဒာ", "ယု", "ဝတ်ရည်", "အေး",
    ]
    second_parts = [
        "ဇော်", "ဦး", "ထက်", "လင်း", "ကို", "မောင်", "နိုင်", "သူ", "ထွဋ်", "လွင်",
        "မာ", "ဝင်း", "သိမ့်", "ချို", "နွယ်", "စံ", "မြတ်", "ကျော်", "အောင်", "ဖြိုး",
    ]
    cities = [
        "Naypyitaw", "Yangon", "Mandalay", "Magway",
        "Chauk", "Yenangyaung", "Kyaukphyu", "Pyay",
        "Minbu", "Nyaungdon", "Maubin", "Pathein",
    ]

    staff_objs = []
    seq = 1000
    while len(staff_objs) < 1000:
        seq += 1
        s_code = f"STF-{seq:04d}"
        if s_code in existing_staff_ids:
            continue
        is_male = (seq % 2 == 0)
        prefix = prefixes_m[seq % 2] if is_male else prefixes_f[seq % 2]
        p1 = first_parts[seq % len(first_parts)]
        p2 = second_parts[(seq * 3) % len(second_parts)]
        p3 = second_parts[(seq * 7 + 5) % len(second_parts)]
        s_name = f"{prefix}{p1}{p2}{p3} #{seq}"
        s_email = f"moge.staff.{seq}@moge.gov.mm"
        s_phone = f"0979{seq:07d}"

        if s_name in existing_staff_names or s_email in existing_staff_emails or s_phone in existing_staff_phones:
            continue

        dt = pick_split_datetime(len(staff_objs), 1000)
        staff_objs.append(
            Staff(
                staff_id=s_code,
                staff_name=s_name[:90],
                staff_email=s_email,
                staff_address=cities[seq % len(cities)],
                staff_ph_number=s_phone,
                staff_gender="Male" if is_male else "Female",
                department=all_depts[seq % len(all_depts)],
                role=all_roles[seq % len(all_roles)],
                rank=all_ranks[seq % len(all_ranks)],
                stype=all_stypes[seq % len(all_stypes)],
                created_at=dt,
                updated_at=dt,
            )
        )
        existing_staff_ids.add(s_code)
        existing_staff_names.add(s_name)
        existing_staff_emails.add(s_email)
        existing_staff_phones.add(s_phone)

    Staff.objects.bulk_create(staff_objs, batch_size=250)
    all_staffs = list(Staff.objects.select_related("department").all())
    print(f"[OK] Added +1,000 Staffs -> Total Staffs: {len(all_staffs)}")

    # ── 2. Helper to Bulk-Add +1,000 Documents per Group with Split Timeframes ──
    sample_files = []
    for idx in range(1, 37):
        if idx % 3 == 1:
            sample_files.append(f"documents/moge_report_{idx:03d}.pdf")
        elif idx % 3 == 2:
            sample_files.append(f"documents/moge_directive_{idx:03d}.docx")
        else:
            sample_files.append(f"documents/moge_statistics_{idx:03d}.xlsx")

    doc_topics = [
        ("ကမ်းလွန်ရေနံတူးဖော်ရေး အစီရင်ခံစာ", "Offshore Drilling Progress Report"),
        ("သဘာဝဓာတ်ငွေ့ ပိုက်လိုင်း စစ်ဆေးရေးမှတ်တမ်း", "Gas Pipeline Integrity Inspection"),
        ("ချောက်ရေနံမြေ နေ့စဉ်ထုတ်လုပ်မှု စာရင်းချုပ်", "Chauk Oilfield Daily Production Summary"),
        ("ရေနံချောင်း တွင်းအမှတ် ၄၂ ပြုပြင်ထိန်းသိမ်းမှု", "Yenangyaung Well Maintenance Log"),
        ("ပစ္စည်းဝယ်ယူရေး တင်ဒါစိစစ်ရေး အစီရင်ခံစာ", "Procurement Tender Evaluation Report"),
        ("ဘူမိဗေဒ တိုင်းတာရေး သုတေသနစာတမ်း", "Geological & Seismic Survey Analysis"),
        ("ဘေးအန္တရာယ်ကင်းရှင်းရေး လစဉ်စစ်ဆေးချက်", "Monthly HSE Compliance Audit"),
        ("ဘဏ္ဍာရေးနှစ် ရသုံးမှန်းခြေငွေစာရင်းချုပ်", "Annual Budget & Expenditure Statement"),
        ("ဝန်ထမ်းအင်အားနှင့် ရာထူးတိုးမြှင့်ရေး မှတ်တမ်း", "HR Staffing & Promotion Order"),
        ("ဦးဆောင်ညွှန်ကြားရေးမှူးရုံး အထူးညွှန်ကြားလွှာ", "Managing Director Executive Directive"),
        ("ကျောက်ဖြူ သဘာဝဓာတ်ငွေ့စခန်း ပို့လွှတ်မှုမှတ်တမ်း", "Kyaukphyu Terminal Gas Dispatch Record"),
        ("မန်းရေနံမြေ စက်ယန္တရား စစ်ဆေးရေးစာရင်း", "Mann Field Heavy Equipment Inventory"),
    ]

    existing_doc_ids = set(Document.objects.values_list("document_id", flat=True))

    # Build 40 distinct timestamp buckets across Today, This Week, This Month, and Past Months
    bucket_timestamps = [pick_split_datetime(b * 25, 1000) for b in range(40)]

    def bulk_add_1000_docs(is_archived: bool, is_recycled: bool, prefix: str, start_seq: int):
        new_docs = []
        codes_by_bucket = {b: [] for b in range(40)}
        seq_num = start_seq

        while len(new_docs) < 1000:
            seq_num += 1
            d_code = f"{prefix}-{seq_num:04d}"
            if d_code in existing_doc_ids:
                continue

            idx = len(new_docs)
            bucket_idx = idx % 40
            dt = bucket_timestamps[bucket_idx]

            mm_title, en_title = doc_topics[seq_num % len(doc_topics)]
            stf = all_staffs[seq_num % len(all_staffs)]
            cat = all_cats[seq_num % len(all_cats)]
            is_temp = (seq_num % 3 == 0)
            dtype_obj = temp_dtype if is_temp else perm_dtype
            file_rel = sample_files[seq_num % len(sample_files)]
            exp_date = (dt + timedelta(days=random.choice([30, 60, 90, 180]))).date() if is_temp else None

            new_docs.append(
                Document(
                    document_id=d_code,
                    document_name=f"{mm_title} ({d_code})"[:200],
                    document=file_rel,
                    description=f"{en_title} - Official MOGE Archive Record ({d_code})"[:200],
                    staff=stf,
                    category=cat,
                    dtype=dtype_obj,
                    is_archived=is_archived,
                    archived_at=dt if is_archived else None,
                    is_recycled=is_recycled,
                    recycled_at=dt if is_recycled else None,
                    expired_at=exp_date,
                )
            )
            existing_doc_ids.add(d_code)
            codes_by_bucket[bucket_idx].append(d_code)

        Document.objects.bulk_create(new_docs, batch_size=250)

        # Apply split created_at & updated_at timestamps per bucket
        with transaction.atomic():
            for b_idx, code_list in codes_by_bucket.items():
                if code_list:
                    b_dt = bucket_timestamps[b_idx]
                    Document.objects.filter(document_id__in=code_list).update(
                        created_at=b_dt, updated_at=b_dt
                    )

    bulk_add_1000_docs(False, False, "DOC", 1000)
    print(f"[OK] Added +1,000 Active Documents -> Total Active: {Document.objects.filter(is_archived=False, is_recycled=False).count()}")

    bulk_add_1000_docs(True, False, "ARC", 3000)
    print(f"[OK] Added +1,000 Archived Documents -> Total Archived: {Document.objects.filter(is_archived=True, is_recycled=False).count()}")

    bulk_add_1000_docs(False, True, "REC", 5000)
    print(f"[OK] Added +1,000 Recycled Documents -> Total Recycled: {Document.objects.filter(is_recycled=True).count()}")

    # ── 3. Add +1,000 Activity Locations & Photos ──
    sample_photos = [
        (f"locations/field_activity_{i:02d}.png", f"locations/photos/field_activity_{i:02d}.png")
        for i in range(1, 13)
    ]
    location_sites = [
        ("ချောက် ရေနံမြေ တွင်းစစ်ဆေးခြင်း", "Field Inspection", "Chauk", "Magway", 20.8992, 94.8178),
        ("ရေနံချောင်း ပိုက်လိုင်းပြုပြင်ခြင်း", "Pipeline Maintenance", "Yenangyaung", "Magway", 20.4647, 94.8712),
        ("မန်း ရေနံမြေ တူးဖော်ရေးလုပ်ငန်း", "Drilling Operation", "Minbu", "Magway", 20.1789, 94.8752),
        ("ကျောက်ဖြူ ဓာတ်ငွေ့ပိုက်လိုင်းစခန်း", "Gas Terminal Audit", "Kyaukphyu", "Rakhine", 19.4264, 93.5519),
        ("ညောင်တုန်း ဓာတ်ငွေ့စက်ရုံ စစ်ဆေးရေး", "Plant Inspection", "Nyaungdon", "Ayeyarwady", 17.0442, 95.6386),
        ("မအူပင် ရေနံမြေ တိုင်းတာရေး", "Seismic Survey", "Maubin", "Ayeyarwady", 16.7314, 95.6544),
        ("ရန်ကုန် ကမ်းလွန်ထောက်ပံ့ရေးစခန်း", "Offshore Logistics", "Yangon", "Yangon", 16.7794, 96.1650),
        ("နေပြည်တော် ရုံးချုပ် စစ်ဆေးရေး", "Executive Review", "Naypyitaw", "Naypyitaw", 19.7633, 96.0785),
        ("ပြည် ရေနံမြေ HSE စစ်ဆေးမှု", "HSE Field Audit", "Pyay", "Bago", 18.8246, 95.2222),
        ("မန္တလေး ပိုက်လိုင်းထိန်းသိမ်းရေးစခန်း", "Pipeline Control", "Mandalay", "Mandalay", 21.9588, 96.0891),
    ]

    existing_loc_ids = set(Location.objects.values_list("location_id", flat=True))
    new_locs = []
    loc_seq = 1000

    while len(new_locs) < 1000:
        loc_seq += 1
        l_code = f"LOC-{loc_seq:04d}"
        if l_code in existing_loc_ids:
            continue

        site_title, l_type, city, region, base_lat, base_lng = location_sites[loc_seq % len(location_sites)]
        dt = bucket_timestamps[len(new_locs) % 40]
        main_photo, _ = sample_photos[loc_seq % len(sample_photos)]
        dept = all_depts[loc_seq % len(all_depts)]

        lat = round(base_lat + random.uniform(-0.06, 0.06), 6)
        lng = round(base_lng + random.uniform(-0.06, 0.06), 6)

        new_locs.append(
            Location(
                location_id=l_code,
                location_name=f"{site_title} ({l_code})"[:200],
                location_type=l_type,
                photo=main_photo,
                latitude=lat,
                longitude=lng,
                description=f"{dept.department_name} - Field inspection at {city}, {region}",
                city=city[:45],
                state_division=region[:45],
                date=dt.date(),
                department=dept,
            )
        )
        existing_loc_ids.add(l_code)

    Location.objects.bulk_create(new_locs, batch_size=250)
    print(f"[OK] Added +1,000 Locations -> Total Locations: {Location.objects.count()}")
    print("=== +1,000 PER MODULE BULK SEEDING COMPLETED ===")


if __name__ == "__main__":
    main()
