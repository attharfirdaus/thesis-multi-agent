#!/usr/bin/env bash
# Create the local roles and databases. Run once per machine, as a superuser.
#
#   thesis_migrator — owns the schema, runs migrations
#   thesis_app      — what the API connects as; NOT the owner, so row-level security applies
#
# Two roles on purpose: RLS is bypassed by the table owner unless FORCE ROW LEVEL SECURITY is
# set (we set it), and a superuser bypasses it unconditionally (hence a plain, non-superuser
# runtime role).
set -euo pipefail

PG=${PG:-$(command -v psql || echo /opt/homebrew/opt/postgresql@18/bin/psql)}
DEV_DB=${DEV_DB:-thesis_dev}
TEST_DB=${TEST_DB:-thesis_test}
MIGRATOR_PW=${MIGRATOR_PW:-migrator_local_pw}
APP_PW=${APP_PW:-app_local_pw}

echo "Using $PG"
"$PG" -d postgres <<SQL
do \$\$
begin
  if not exists (select 1 from pg_roles where rolname = 'thesis_migrator') then
    create role thesis_migrator login password '${MIGRATOR_PW}';
  end if;
  if not exists (select 1 from pg_roles where rolname = 'thesis_app') then
    create role thesis_app login password '${APP_PW}';
  end if;
end \$\$;
SQL

for db in "$DEV_DB" "$TEST_DB"; do
  if ! "$PG" -d postgres -tAc "select 1 from pg_database where datname = '$db'" | grep -q 1; then
    createdb_owner=thesis_migrator
    "$PG" -d postgres -c "create database $db owner $createdb_owner"
  fi
  "$PG" -d "$db" -c "grant connect on database $db to thesis_app"
  "$PG" -d "$db" -c "grant usage, create on schema public to thesis_migrator"
done

echo
echo "DATABASE_URL=postgresql://thesis_app:${APP_PW}@localhost:5432/${DEV_DB}"
echo "MIGRATION_DATABASE_URL=postgresql://thesis_migrator:${MIGRATOR_PW}@localhost:5432/${DEV_DB}"
