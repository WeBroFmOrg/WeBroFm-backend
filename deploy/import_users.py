import re, json
from datetime import datetime
from accounts.models import CustomUser

with open("/tmp/users.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

insert_match = re.search(
    r"INSERT INTO `users`\s*\((.*?)\)\s*VALUES\s*(.*?);",
    sql, re.DOTALL | re.IGNORECASE
)

if not insert_match:
    print("No INSERT found")
    exit()

headers = [h.strip().strip("`") for h in insert_match.group(1).split(",")]
values_block = insert_match.group(2)

# Parse VALUES rows
rows = re.findall(r"\((.*?)\)\s*,?\s*(?=\(|;)", values_block, re.DOTALL)
print(f"Found {len(rows)} user rows in SQL")

added = 0
skipped = 0
errors = 0

for row_str in rows:
    # Split by commas not inside quotes
    fields = []
    current = ""
    in_quote = False
    in_squote = False
    for ch in row_str:
        if ch == "'" and not in_quote:
            in_squote = not in_squote
            current += ch
        elif ch == '"' and not in_squote:
            in_quote = not in_quote
            current += ch
        elif ch == "," and not in_quote and not in_squote:
            fields.append(current.strip())
            current = ""
        else:
            current += ch
    fields.append(current.strip())

    if len(fields) != len(headers):
        errors += 1
        continue

    record = {}
    for i, h in enumerate(headers):
        val = fields[i].strip()
        if val == "NULL" or val == "":
            record[h] = None
        else:
            record[h] = val.strip("'\"")

    phone = record.get("phone")
    if not phone:
        skipped += 1
        continue

    # Check if user exists
    if CustomUser.objects.filter(phone_number=phone).exists():
        skipped += 1
        continue

    # Map fields
    full_name = record.get("name") or ""
    email = record.get("email") or None
    dob = None
    if record.get("dob"):
        try:
            dob = datetime.strptime(record["dob"], "%Y-%m-%d").date()
        except:
            pass

    is_active = record.get("status") in ("1", 1)
    if record.get("deleted_at"):
        is_active = False

    date_joined = None
    if record.get("created_at"):
        try:
            date_joined = datetime.strptime(record["created_at"], "%Y-%m-%d %H:%M:%S")
        except:
            pass

    try:
        user = CustomUser(
            phone_number=phone,
            full_name=full_name,
            email=email,
            is_active=is_active,
            date_of_birth=dob,
        )
        if date_joined:
            user.date_joined = date_joined
        user.set_unusable_password()
        user.save()
        added += 1
        if added <= 5 or added % 10 == 0:
            print(f"  + {phone} ({full_name or 'no name'})")
    except Exception as e:
        errors += 1
        print(f"  ! {phone}: {e}")

print(f"\nDone: {added} added, {skipped} skipped (exists/invalid), {errors} errors")
