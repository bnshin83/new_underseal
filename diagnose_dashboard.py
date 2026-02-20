"""
ArcGIS Dashboard Diagnostic Script
===================================
Run this on the INDOT work PC to diagnose why certain requests
(e.g., LL 9384+) don't appear in the ArcGIS FWD dashboard.

Usage:
    python diagnose_dashboard.py --dev_env shin --ll_no 9384

Or check multiple LL numbers:
    python diagnose_dashboard.py --dev_env shin --ll_no 9384,9385,9386

The script checks every table in the INNER JOIN chain and reports
where the data breaks.
"""

import argparse
import sys
import os
import db

from log_config import get_logger
logger = get_logger('diagnose_dashboard')


def check_longlist_info(cursor, ll_no):
    """Check stda_longlist_info for this LL number."""
    cursor.execute("""
        SELECT longlist_info_id, longlist_no, year, request_no
        FROM stda_longlist_info
        WHERE longlist_no = :ll_no
        ORDER BY year
    """, {'ll_no': ll_no})
    rows = cursor.fetchall()
    if not rows:
        logger.warning("  stda_longlist_info: NO ROWS for longlist_no=%s", ll_no)
        return []
    for r in rows:
        logger.info("  stda_longlist_info: info_id=%s, longlist_no=%s, year='%s', request_no='%s'",
                     r[0], r[1], r[2], r[3])
    return rows


def check_longlist(cursor, ll_no):
    """Check stda_longlist for this LL number."""
    cursor.execute("""
        SELECT longlist_id, longlist_no, year, direction, lane_info, pavtype,
               begin_latitude, begin_longitude, end_latitude, end_longitude
        FROM stda_longlist
        WHERE longlist_no = :ll_no
        ORDER BY year, longlist_id
    """, {'ll_no': ll_no})
    rows = cursor.fetchall()
    if not rows:
        logger.warning("  stda_longlist: NO ROWS for longlist_no=%s", ll_no)
        return []
    for r in rows:
        logger.info("  stda_longlist: id=%s, longlist_no=%s, year='%s', dir='%s', lane='%s', pav='%s', "
                     "begin_lat=%s, begin_lon=%s, end_lat=%s, end_lon=%s",
                     r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9])
    return rows


def check_join_longlist_to_info(cursor, ll_no):
    """Check if stda_longlist JOIN stda_longlist_info produces rows (the critical join)."""
    cursor.execute("""
        SELECT l.longlist_id, l.longlist_no, l.year,
               i.longlist_info_id, i.longlist_no, i.year,
               i.request_no
        FROM stda_longlist l
        INNER JOIN stda_longlist_info i
            ON l.longlist_no = i.longlist_no AND l.year = i.year
        WHERE l.longlist_no = :ll_no
        ORDER BY l.longlist_id
    """, {'ll_no': ll_no})
    rows = cursor.fetchall()
    if not rows:
        logger.warning("  longlist JOIN longlist_info: NO ROWS — this is likely the problem!")
        return []
    for r in rows:
        logger.info("  JOIN result: l.id=%s, l.ll_no=%s, l.year='%s' | i.id=%s, i.ll_no=%s, i.year='%s', req='%s'",
                     r[0], r[1], r[2], r[3], r[4], r[5], r[6])
    return rows


def check_data_type_mismatch(cursor, ll_no):
    """Check if year/longlist_no have type mismatches between tables."""
    # Check stda_longlist
    cursor.execute("""
        SELECT longlist_no, year, DUMP(longlist_no) as ll_dump, DUMP(year) as year_dump
        FROM stda_longlist
        WHERE longlist_no = :ll_no
        AND ROWNUM <= 3
    """, {'ll_no': ll_no})
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            logger.info("  stda_longlist    : longlist_no=%s, year=%s", r[0], r[1])
            logger.info("    DUMP(longlist_no)=%s", r[2])
            logger.info("    DUMP(year)=%s", r[3])

    # Check stda_longlist_info
    cursor.execute("""
        SELECT longlist_no, year, DUMP(longlist_no) as ll_dump, DUMP(year) as year_dump
        FROM stda_longlist_info
        WHERE longlist_no = :ll_no
        AND ROWNUM <= 3
    """, {'ll_no': ll_no})
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            logger.info("  stda_longlist_info: longlist_no=%s, year=%s", r[0], r[1])
            logger.info("    DUMP(longlist_no)=%s", r[2])
            logger.info("    DUMP(year)=%s", r[3])


def check_per_table_counts(cursor, longlist_ids):
    """Check row counts in each dashboard table for given longlist_ids."""
    tables = [
        'stda_deflections',
        'stda_calculations',
        'stda_moduli_estimated',
        'stda_misc',
        'stda_longlist',
        'stda_img',
    ]
    for lid in longlist_ids:
        logger.info("  Row counts for longlist_id=%s:", lid)
        for table in tables:
            cursor.execute(
                "SELECT COUNT(*) FROM {} WHERE longlist_id = :lid".format(table),
                {'lid': lid}
            )
            count = cursor.fetchone()[0]
            status = "OK" if count > 0 else "MISSING"
            logger.info("    %-30s %5d rows  [%s]", table, count, status)


def check_gps_nulls(cursor, longlist_ids):
    """Check if GPS coordinates are NULL in stda_deflections (would break sdo_geometry)."""
    for lid in longlist_ids:
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN gpsx IS NULL THEN 1 ELSE 0 END) as null_gpsx,
                   SUM(CASE WHEN gpsy IS NULL THEN 1 ELSE 0 END) as null_gpsy,
                   SUM(CASE WHEN gpsx = 0 THEN 1 ELSE 0 END) as zero_gpsx,
                   SUM(CASE WHEN gpsy = 0 THEN 1 ELSE 0 END) as zero_gpsy
            FROM stda_deflections
            WHERE longlist_id = :lid
        """, {'lid': lid})
        r = cursor.fetchone()
        logger.info("  longlist_id=%s GPS check: total=%s, null_gpsx=%s, null_gpsy=%s, zero_gpsx=%s, zero_gpsy=%s",
                     lid, r[0], r[1], r[2], r[3], r[4])
        if r[1] and r[1] > 0:
            logger.warning("    WARNING: %d rows have NULL gpsx — sdo_geometry will fail!", r[1])
        if r[2] and r[2] > 0:
            logger.warning("    WARNING: %d rows have NULL gpsy — sdo_geometry will fail!", r[2])


def check_drop_no_alignment(cursor, longlist_ids):
    """Check if drop_no matches across deflections, calculations, and moduli_estimated."""
    for lid in longlist_ids:
        cursor.execute("""
            SELECT d.point, d.drop_no, c.drop_no as calc_drop, m.drop_no as mod_drop
            FROM stda_deflections d
            LEFT JOIN stda_calculations c
                ON d.longlist_id = c.longlist_id AND d.point = c.point AND d.drop_no = c.drop_no
            LEFT JOIN stda_moduli_estimated m
                ON d.longlist_id = m.longlist_id AND d.point = m.point AND d.drop_no = m.drop_no
            WHERE d.longlist_id = :lid
            AND (c.drop_no IS NULL OR m.drop_no IS NULL)
            AND ROWNUM <= 10
        """, {'lid': lid})
        rows = cursor.fetchall()
        if rows:
            logger.warning("  longlist_id=%s: %d rows have mismatched drop_no (showing first 10):", lid, len(rows))
            for r in rows:
                logger.warning("    point=%s, defl_drop=%s, calc_drop=%s, mod_drop=%s", r[0], r[1], r[2], r[3])
        else:
            logger.info("  longlist_id=%s: drop_no aligned across all 3 tables", lid)


def check_full_dashboard_query(cursor, longlist_ids):
    """Run the actual dashboard INNER JOIN query for specific longlist_ids."""
    for lid in longlist_ids:
        cursor.execute("""
            SELECT COUNT(*)
            FROM stda_moduli_estimated me
            INNER JOIN stda_deflections d
                ON d.longlist_id = me.longlist_id AND d.point = me.point AND d.drop_no = me.drop_no
            INNER JOIN stda_calculations c
                ON d.longlist_id = c.longlist_id AND d.point = c.point AND d.drop_no = c.drop_no
            INNER JOIN stda_misc mi
                ON mi.longlist_id = c.longlist_id
            INNER JOIN stda_longlist l
                ON mi.longlist_id = l.longlist_id
            INNER JOIN stda_longlist_info li
                ON l.longlist_no = li.longlist_no AND l.year = li.year
            WHERE l.longlist_id = :lid
        """, {'lid': lid})
        count = cursor.fetchone()[0]
        if count == 0:
            logger.warning("  Full dashboard query for longlist_id=%s: 0 rows — REQUEST WILL NOT APPEAR!", lid)
        else:
            logger.info("  Full dashboard query for longlist_id=%s: %d rows — OK", lid, count)


def check_working_vs_broken(cursor, working_ll_no, broken_ll_no):
    """Compare a working LL number against the broken one to spot differences."""
    logger.info("=" * 60)
    logger.info("COMPARISON: working LL %s vs broken LL %s", working_ll_no, broken_ll_no)
    logger.info("=" * 60)

    for label, ll_no in [("WORKING", working_ll_no), ("BROKEN", broken_ll_no)]:
        logger.info("--- %s (LL %s) ---", label, ll_no)
        # Check year values in both tables
        cursor.execute("""
            SELECT 'stda_longlist' as src, longlist_no, year, DUMP(year) as ydump
            FROM stda_longlist WHERE longlist_no = :ll_no AND ROWNUM <= 1
            UNION ALL
            SELECT 'stda_longlist_info' as src, longlist_no, year, DUMP(year) as ydump
            FROM stda_longlist_info WHERE longlist_no = :ll_no AND ROWNUM <= 1
        """, {'ll_no': ll_no})
        for r in cursor.fetchall():
            logger.info("  %s: ll_no=%s, year='%s', DUMP(year)=%s", r[0], r[1], r[2], r[3])


def diagnose(con, ll_no, compare_ll_no=None):
    """Run all diagnostic checks for a given LL number."""
    cursor = con.cursor()

    logger.info("=" * 60)
    logger.info("DIAGNOSING LL NUMBER: %s", ll_no)
    logger.info("=" * 60)

    # Step 1: Check stda_longlist_info
    logger.info("\n[1/8] Checking stda_longlist_info...")
    info_rows = check_longlist_info(cursor, ll_no)

    # Step 2: Check stda_longlist
    logger.info("\n[2/8] Checking stda_longlist...")
    ll_rows = check_longlist(cursor, ll_no)

    # Step 3: Check the critical JOIN between longlist and longlist_info
    logger.info("\n[3/8] Checking longlist JOIN longlist_info (the critical join)...")
    join_rows = check_join_longlist_to_info(cursor, ll_no)

    # Step 4: Check data type mismatches
    logger.info("\n[4/8] Checking data types (DUMP) for year and longlist_no...")
    check_data_type_mismatch(cursor, ll_no)

    # Step 5: Get longlist_ids for deeper checks
    longlist_ids = [r[0] for r in ll_rows] if ll_rows else []
    if longlist_ids:
        # Step 6: Per-table row counts
        logger.info("\n[5/8] Checking per-table row counts...")
        check_per_table_counts(cursor, longlist_ids)

        # Step 7: GPS null check
        logger.info("\n[6/8] Checking GPS coordinates for NULLs...")
        check_gps_nulls(cursor, longlist_ids)

        # Step 8: Drop number alignment
        logger.info("\n[7/8] Checking drop_no alignment across tables...")
        check_drop_no_alignment(cursor, longlist_ids)

        # Step 9: Full dashboard query
        logger.info("\n[8/8] Running full dashboard INNER JOIN query...")
        check_full_dashboard_query(cursor, longlist_ids)
    else:
        logger.warning("\n[5-8/8] Skipped — no longlist_ids found in stda_longlist")

    # Optional: compare with a known working LL
    if compare_ll_no is not None:
        check_working_vs_broken(cursor, compare_ll_no, ll_no)

    cursor.close()


def main():
    parser = argparse.ArgumentParser(
        description='Diagnose why FWD requests are missing from ArcGIS dashboard'
    )
    parser.add_argument('--dev_env', type=str, default='shin',
                        choices=['dev_wen', 'shin', 'ecn_wen', 'ecn_shin'])
    parser.add_argument('--ll_no', type=str, required=True,
                        help='LongList number(s) to check, comma-separated. Example: 9384,9385')
    parser.add_argument('--compare_ll_no', type=int, default=None,
                        help='A working LL number to compare against (e.g., 429)')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("ArcGIS Dashboard Diagnostic")
    logger.info("=" * 60)

    con = db.connect(args.dev_env)
    logger.info("Connected to Oracle (%s)", args.dev_env)

    ll_nos = [int(x.strip()) for x in args.ll_no.split(',')]

    for ll_no in ll_nos:
        diagnose(con, ll_no, compare_ll_no=args.compare_ll_no)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("DIAGNOSTIC SUMMARY")
    logger.info("=" * 60)
    logger.info("Checked LL numbers: %s", ll_nos)
    logger.info("Compare LL: %s", args.compare_ll_no)
    logger.info("")
    logger.info("Common causes for missing dashboard data:")
    logger.info("  1. YEAR MISMATCH: stda_longlist.year != stda_longlist_info.year")
    logger.info("     (e.g., '2025' vs '25', or NUMBER vs VARCHAR mismatch)")
    logger.info("  2. LONGLIST_NO TYPE MISMATCH: NUMBER vs VARCHAR comparison failure")
    logger.info("  3. NULL GPS: gpsx/gpsy NULL in stda_deflections breaks sdo_geometry")
    logger.info("  4. DROP_NO MISMATCH: drop_no doesn't align across deflections/calculations/moduli")
    logger.info("  5. MISSING ROWS: one of the 6 tables has no data for this longlist_id")
    logger.info("")
    logger.info("Check run_log.txt for full output.")
    logger.info("Push run_log.txt to GitHub so Claude can analyze the results.")

    con.close()


if __name__ == '__main__':
    main()
