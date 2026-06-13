"""
WeBroFm Data Migration Command
================================
Migrates old Laravel/MySQL data from a SQL dump into the new Django backend.

Usage:
    python manage.py migrate_old_data --sql-file old_data.sql
    python manage.py migrate_old_data --sql-file old_data.sql --dry-run

Audio files are ALREADY in Cloudflare R2 (webrofm bucket).
The 'audio' column in old DB stores the full R2 URL.
This script extracts the key and maps it to audio_file_key.
"""

import re
import os
import sys
import io
from django.utils.text import slugify
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Migrate old WeBroFm Laravel MySQL data into new Django backend'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sql-file',
            type=str,
            required=True,
            help='Path to the exported MySQL .sql dump file'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and preview data without writing to the database'
        )

    def _write(self, msg, style_func=None):
        """Safe write that handles Unicode on Windows."""
        if style_func:
            msg = style_func(msg)
        try:
            self.stdout.write(msg)
        except UnicodeEncodeError:
            self.stdout.write(msg.encode('ascii', 'replace').decode('ascii'))

    def handle(self, *args, **options):
        sql_file = options['sql_file']
        dry_run = options['dry_run']

        if not os.path.exists(sql_file):
            raise CommandError(f"SQL file not found: {sql_file}")

        self._write(f"\n{'='*60}\n  WeBroFm Old Data Migration\n{'='*60}", self.style.MIGRATE_HEADING)

        if dry_run:
            self._write("  [DRY RUN] No data will be written.\n", self.style.WARNING)

        # Parse SQL dump
        self._write("[*] Reading SQL file...")
        with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()

        genres   = self._parse_table(sql_content, 'genres')
        shows    = self._parse_table(sql_content, 'shows')
        episodes = self._parse_table(sql_content, 'episodes')
        users    = self._parse_table(sql_content, 'users')

        self._write(f"  Genres   : {len(genres)}")
        self._write(f"  Shows    : {len(shows)}")
        self._write(f"  Episodes : {len(episodes)}")
        self._write(f"  Users    : {len(users)}")

        if dry_run:
            self._write("\n--- GENRES ---")
            for g in genres:
                self._write(f"  id={g.get('id')} name={g.get('name')}")
            self._write("\n--- SHOWS (first 10) ---")
            for s in shows[:10]:
                self._write(f"  id={s.get('id')} title={s.get('title')} genre_id={s.get('genre_id')} poster={s.get('poster', '')[:60]}")
            self._write("\n--- EPISODES (first 10) ---")
            for ep in episodes[:10]:
                self._write(f"  id={ep.get('id')} show_id={ep.get('show_id')} title={ep.get('title')} audio={ep.get('audio', '')[:60]}")
            self._write("\n--- USERS (first 5) ---")
            for u in users[:5]:
                self._write(f"  id={u.get('id')} phone={u.get('phone')} name={u.get('name')}")
            self._write("\n[OK] Dry run complete. Run without --dry-run to import.", self.style.SUCCESS)
            return

        # --- Import ---
        from content.models import Show, Episode, Category, Author

        created_categories = 0
        created_shows = 0
        created_episodes = 0

        with transaction.atomic():

            # 1. Default Author
            default_author, _ = Author.objects.get_or_create(
                name="WeBroFm Original",
                defaults={'bio': 'Content migrated from the original WeBroFm platform.'}
            )
            self._write(f"\n[*] Default Author: '{default_author.name}'")

            # 2. Genres -> Categories
            self._write("\n[1/4] Genres -> Categories", self.style.MIGRATE_LABEL)
            genre_map = {}

            for g in genres:
                gname = (g.get('name') or 'Unknown').strip()
                gslug = slugify(gname) or f"genre-{g.get('id', 'x')}"

                base_slug = gslug
                counter = 1
                while Category.objects.filter(slug=gslug).exists():
                    gslug = f"{base_slug}-{counter}"
                    counter += 1

                cat, created = Category.objects.get_or_create(
                    name=gname,
                    defaults={'slug': gslug, 'is_active': True}
                )
                if created:
                    created_categories += 1
                genre_map[str(g['id'])] = cat
                icon = '[+]' if created else '[=]'
                self._write(f"  {icon} {cat.name}")

            # Fallback category
            fallback_cat, _ = Category.objects.get_or_create(
                name='General',
                defaults={'slug': 'general', 'is_active': True}
            )

            # 3. Shows
            self._write("\n[2/4] Importing Shows", self.style.MIGRATE_LABEL)
            show_map = {}

            for s in shows:
                if str(s.get('status', '1')) == '0':
                    continue

                old_id = str(s.get('id', ''))
                title  = (s.get('title') or 'Untitled').strip()
                desc   = (s.get('description') or '').strip()

                category = genre_map.get(str(s.get('genre_id', '')), fallback_cat)

                # Poster: old system stored full R2 URL in poster column
                poster_raw = s.get('poster') or ''
                if poster_raw and not poster_raw.startswith('http'):
                    poster_key = f"migrated/shows/{poster_raw}"
                else:
                    poster_key = poster_raw

                show, created = Show.objects.get_or_create(
                    title=title,
                    defaults={
                        'description': desc,
                        'category': category,
                        'author': default_author,
                        'thumbnail': poster_key,
                        'age_rating': 'U',
                        'is_featured': False,
                        'is_trending': False,
                    }
                )
                show_map[old_id] = show
                if created:
                    created_shows += 1
                icon = '[+]' if created else '[=]'
                self._write(f"  {icon} [{category.name}] {show.title}")

            # 4. Episodes
            self._write("\n[3/4] Importing Episodes", self.style.MIGRATE_LABEL)
            seq_tracker = {}

            for ep in episodes:
                if str(ep.get('is_delete', '0')) == '1':
                    continue
                if str(ep.get('status', '1')) == '0':
                    continue

                show_id_old = str(ep.get('show_id', ''))
                show = show_map.get(show_id_old)
                if not show:
                    self._write(f"  [!] Skipping '{ep.get('title')}' - show_id {show_id_old} not found", self.style.WARNING)
                    continue

                title = (ep.get('title') or 'Untitled Episode').strip()
                desc  = (ep.get('description') or '').strip()

                # Audio: old system stored full R2 URL like https://audio.webrofm.com/filename.mp3
                audio_raw = (ep.get('audio') or '').strip()
                if 'audio.webrofm.com/' in audio_raw:
                    audio_key = audio_raw.split('audio.webrofm.com/')[-1]
                elif audio_raw.startswith('http'):
                    audio_key = audio_raw.split('/')[-1]
                else:
                    audio_key = audio_raw

                # Duration: old stored as float seconds (e.g. 1075.58)
                try:
                    duration_raw = float(ep.get('duration', 0) or 0)
                    duration_seconds = int(duration_raw)
                except (ValueError, TypeError):
                    duration_seconds = 0

                # Auto-assign sequence number per show
                seq = seq_tracker.get(show_id_old, 0) + 1
                seq_tracker[show_id_old] = seq

                episode, created = Episode.objects.get_or_create(
                    show=show,
                    title=title,
                    defaults={
                        'description': desc,
                        'audio_file_key': audio_key,
                        'duration_seconds': duration_seconds,
                        'sequence_number': seq,
                        'hls_playlist_key': '',
                    }
                )
                if created:
                    created_episodes += 1
                icon = '[+]' if created else '[=]'
                audio_short = audio_key[:50] if audio_key else 'NO AUDIO'
                self._write(f"  {icon} Ep{seq:02d} | {show.title} - {title} | {audio_short}")

            # 5. Users
            self._write("\n[4/4] Importing Users (phone accounts)", self.style.MIGRATE_LABEL)
            from accounts.models import CustomUser
            created_users = 0

            for u in users:
                phone = (u.get('phone') or '').strip()
                name  = (u.get('name') or '').strip()
                if not phone:
                    continue

                user, created = CustomUser.objects.get_or_create(
                    phone_number=phone,
                    defaults={
                        'full_name': name,
                        'is_active': True,
                    }
                )
                if created:
                    created_users += 1
                icon = '[+]' if created else '[=]'
                self._write(f"  {icon} {phone} ({name})")

        # Summary
        self._write(f"""
{'='*60}
  Migration Complete!

  Categories created : {created_categories}
  Shows created      : {created_shows}
  Episodes created   : {created_episodes}
  Users created      : {created_users}

  Audio files are in Cloudflare R2 bucket 'webrofm'.
  They stream via https://audio.webrofm.com/<key>
{'='*60}
""", self.style.SUCCESS)

    # -- SQL Parsing Helpers --

    def _parse_table(self, sql, table_name):
        """Extract INSERT rows from a MySQL/phpMyAdmin SQL dump as list of dicts."""
        records = []

        # phpMyAdmin format: INSERT INTO `table` (`col1`, `col2`, ...) VALUES (...), (...);
        insert_re = re.compile(
            rf"INSERT INTO `{table_name}`\s*(\([^)]*\)\s*)?VALUES\s*(.+?);",
            re.DOTALL | re.IGNORECASE
        )

        for ins_match in insert_re.finditer(sql):
            col_block = ins_match.group(1)
            rows_block = ins_match.group(2)

            columns = []
            if col_block:
                columns = re.findall(r'`(\w+)`', col_block)

            if not columns:
                create_re = re.compile(
                    rf"CREATE TABLE `{table_name}`\s*\((.*?)\)\s*ENGINE",
                    re.DOTALL | re.IGNORECASE
                )
                create_match = create_re.search(sql)
                if create_match:
                    for line in create_match.group(1).split('\n'):
                        line = line.strip().rstrip(',')
                        m = re.match(r'^`(\w+)`\s+', line)
                        if m:
                            columns.append(m.group(1))

            if not columns:
                self._write(f"  [!] No columns found for table `{table_name}`", self.style.WARNING)
                continue

            for raw_row in self._extract_row_tuples(rows_block):
                values = self._split_values(raw_row)
                if len(values) == len(columns):
                    records.append({columns[i]: self._clean(values[i])
                                    for i in range(len(columns))})

        return records

    def _extract_row_tuples(self, block):
        """Extract content between matching parens for each row tuple."""
        tuples = []
        i = 0
        while i < len(block):
            if block[i] == '(':
                depth = 1
                start = i + 1
                i += 1
                in_q = False
                q_ch = None
                while i < len(block) and depth > 0:
                    ch = block[i]
                    if ch == '\\' and i + 1 < len(block):
                        i += 2
                        continue
                    if in_q:
                        if ch == q_ch:
                            in_q = False
                    else:
                        if ch in ("'", '"'):
                            in_q = True
                            q_ch = ch
                        elif ch == '(':
                            depth += 1
                        elif ch == ')':
                            depth -= 1
                    i += 1
                if depth == 0:
                    tuples.append(block[start:i - 1])
            else:
                i += 1
        return tuples

    def _split_values(self, s):
        """Split a SQL row value string respecting quotes and escapes."""
        values, cur, in_q, q_ch, esc = [], [], False, None, False
        for ch in s:
            if esc:
                cur.append(ch); esc = False; continue
            if ch == '\\':
                esc = True; cur.append(ch); continue
            if in_q:
                cur.append(ch)
                if ch == q_ch:
                    in_q = False
            else:
                if ch in ("'", '"'):
                    in_q = True; q_ch = ch; cur.append(ch)
                elif ch == ',':
                    values.append(''.join(cur).strip()); cur = []
                else:
                    cur.append(ch)
        if cur:
            values.append(''.join(cur).strip())
        return values

    def _clean(self, val):
        """Strip quotes, handle NULL."""
        if val is None:
            return None
        val = val.strip()
        if val.upper() == 'NULL':
            return None
        if len(val) >= 2 and val[0] in ("'", '"') and val[-1] == val[0]:
            val = val[1:-1]
            val = val.replace("\\'", "'").replace('\\"', '"') \
                     .replace('\\n', '\n').replace('\\r', '\r')
        return val
