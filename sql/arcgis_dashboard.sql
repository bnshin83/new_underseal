-- ============================================================
-- ArcGIS FWD Dashboard — Oracle Query Layers
-- ============================================================
-- Server: dotorad002vl.state.in.us:1621/INDOT3DEV
-- Schema: stda
-- Last updated: 2026-02-20
--
-- The ArcGIS Pro dashboard uses two query layers:
--   1. FWD_Dashboard_numeric — point geometry layer (per-drop results)
--   2. image_layer — query table, no geometry (image paths)
--
-- Both layers connect via the INDOT3DEV Oracle instance.
-- ============================================================


-- ============================================================
-- LAYER 1: FWD_Dashboard_numeric (point geometry)
-- ============================================================
-- This layer generates one map point per (longlist_id, point, drop_no)
-- using GPS coordinates from stda_deflections.
--
-- GEOMETRY: sdo_geometry(2001, 4326, sdo_point_type(gpsy, gpsx, NULL))
--   Note: gpsy = longitude, gpsx = latitude (naming is swapped in the table)
--
-- JOIN CHAIN (all INNER JOINs — every link must match or the row disappears):
--   stda_moduli_estimated
--     -> stda_deflections      (on longlist_id, point, drop_no)
--     -> stda_calculations     (on longlist_id, point, drop_no)
--     -> stda_misc             (on longlist_id)
--     -> stda_longlist         (on longlist_id)
--     -> stda_longlist_info    (on longlist_no AND year)   <-- CRITICAL JOIN
--
-- If ANY table is missing data for a request, the request won't appear.
-- The longlist <-> longlist_info join on (longlist_no, year) is the most
-- fragile because year is stored as VARCHAR in both tables and must match
-- exactly (e.g., '2025' must equal '2025', not '25').

SELECT
    stda.stda_longlist_info.request_no          AS "Request ID",
    stda.stda_longlist.f25_info                 AS "Test Description",
    stda.stda_longlist.pavtype                  AS "Pavement Type",
    stda.stda_longlist.lane_info                AS "Lane Type",
    stda.stda_deflections.chainage_ft           AS "Test DMI (feet)",
    stda.stda_longlist_info.traffic_ctrl        AS "Test Date",
    CASE
        WHEN stda.stda_longlist.direction LIKE '%EB%' THEN 'Inc'
        WHEN stda.stda_longlist.direction LIKE '%NB%' THEN 'Inc'
        ELSE 'Dec'
    END                                         AS "Travel Direction",
    NULL                                        AS "Lane_Position_Research",
    NULL                                        AS "Lane_Position_DTIMS",
    stda.stda_deflections.gpsx                  AS "Latitude(decimal degrees)",
    stda.stda_deflections.gpsy                  AS "Longitude(decimal degrees)",
    NULL                                        AS "Reciever Type",
    ROUND(stda.stda_misc.d0_criteria, 2)        AS "Surface Deflection Criteria",
    ROUND(stda.stda_misc.subgrade_criteria, 2)  AS "Subgrade Deflection Criteria",
    ROUND(stda.stda_calculations.deflection_0, 2)       AS "Surface Deflection",
    ROUND(stda.stda_calculations.deflection_8, 2)       AS "Subgrade Deflection",
    ROUND(stda.stda_calculations.insitucbr, 2)          AS "In-Situ CBR",
    ROUND(stda.stda_calculations.structural_number, 2)  AS "In-Situ Structure Number",
    ROUND(stda.stda_calculations.insitumr)              AS "Resilient Modulus(corrected, psi)",
    ROUND(stda.stda_calculations.indot_esals)           AS "Remaining ESALs",
    ROUND(stda.stda_calculations.k_value)               AS "K Value",
    NULL                                                AS "LTE",
    ROUND(stda.stda_calculations.e1_layer1_ksi * 1000)  AS "E1_Layer1 (psi)",
    ROUND(stda.stda_calculations.e2_layer2_ksi * 1000)  AS "E2_Layer2 (psi)",
    ROUND(stda.stda_calculations.e3_layer3_ksi * 1000)  AS "E3_Layer3 (psi)",
    ROUND(stda.stda_calculations.e4_layer4_ksi * 1000)  AS "E4_Layer4 (psi)",
    ROUND(stda.stda_deflections.deflection_1, 2)        AS "D1(uncorrected)",
    ROUND(stda.stda_deflections.deflection_2, 2)        AS "D2(uncorrected)",
    ROUND(stda.stda_deflections.deflection_3, 2)        AS "D3(uncorrected)",
    ROUND(stda.stda_deflections.deflection_4, 2)        AS "D4(uncorrected)",
    ROUND(stda.stda_deflections.deflection_5, 2)        AS "D5(uncorrected)",
    ROUND(stda.stda_deflections.deflection_6, 2)        AS "D6(uncorrected)",
    ROUND(stda.stda_deflections.deflection_7, 2)        AS "D7(uncorrected)",
    ROUND(stda.stda_deflections.deflection_8, 2)        AS "D8(uncorrected)",
    ROUND(stda.stda_deflections.deflection_9, 2)        AS "D9(uncorrected)",
    stda.stda_deflections.surface_temp                  AS "Surface Temperature(F)",
    stda.stda_deflections.air_temp                      AS "Air Temperature(F)",
    ROUND(stda.stda_moduli_estimated.thickness_1, 2)    AS "Thickness_Layer1 (in)",
    ROUND(stda.stda_moduli_estimated.thickness_2, 2)    AS "Thickness_Layer2 (in)",
    ROUND(stda.stda_moduli_estimated.thickness_3, 2)    AS "Thickness_Layer3 (in)",
    ROUND(stda.stda_moduli_estimated.thickness_4, 2)    AS "Thickness_Layer4 (in)"
FROM stda.stda_moduli_estimated
INNER JOIN stda.stda_deflections
    ON stda.stda_deflections.longlist_id = stda.stda_moduli_estimated.longlist_id
    AND stda.stda_deflections.point = stda.stda_moduli_estimated.point
    AND stda.stda_deflections.drop_no = stda.stda_moduli_estimated.drop_no
INNER JOIN stda.stda_calculations
    ON stda.stda_deflections.longlist_id = stda.stda_calculations.longlist_id
    AND stda.stda_deflections.point = stda.stda_calculations.point
    AND stda.stda_deflections.drop_no = stda.stda_calculations.drop_no
INNER JOIN stda.stda_misc
    ON stda.stda_misc.longlist_id = stda.stda_calculations.longlist_id
INNER JOIN stda.stda_longlist
    ON stda.stda_misc.longlist_id = stda.stda_longlist.longlist_id
INNER JOIN stda.stda_longlist_info
    ON stda.stda_longlist.longlist_no = stda.stda_longlist_info.longlist_no
    AND stda.stda_longlist.year = stda.stda_longlist_info.year
ORDER BY stda.stda_longlist.longlist_id, stda.stda_calculations.point ASC;


-- ============================================================
-- LAYER 2: image_layer (query table, no geometry)
-- ============================================================
-- Simple query on stda_img. Used for popup image display.
-- No JOINs — if images exist in stda_img, they should appear.

SELECT
    longlist_id,
    request_no,
    direction,
    chainage_ft,
    img_path,
    lane_type
FROM stda.stda_img;


-- ============================================================
-- SUPPLEMENTARY: Route line layer (begin/end GPS)
-- ============================================================
-- Used for route-level overview (line segments, not per-drop points).

SELECT
    NULL                                        AS "TS Request",
    stda.stda_longlist.begin_latitude           AS "Beginning_lat",
    stda.stda_longlist.begin_longitude          AS "Beginning_lon",
    stda.stda_longlist.end_latitude             AS "Ending_lat",
    stda.stda_longlist.end_longitude            AS "Ending_lon",
    stda.stda_longlist_info.request_no          AS "Request ID",
    CASE
        WHEN stda.stda_longlist.direction LIKE '%EB%' THEN 'Inc'
        WHEN stda.stda_longlist.direction LIKE '%NB%' THEN 'Inc'
        ELSE 'Dec'
    END                                         AS "Direction",
    NULL                                        AS "Document Name",
    stda.stda_longlist.f25_info                 AS "Test Description"
FROM stda.stda_longlist
INNER JOIN stda.stda_longlist_info
    ON stda.stda_longlist.longlist_no = stda.stda_longlist_info.longlist_no
    AND stda.stda_longlist.year = stda.stda_longlist_info.year;


-- ============================================================
-- DIAGNOSTIC: Check a specific LL number across both tables
-- ============================================================
-- Replace :ll_no with the actual number (e.g., 9384)
-- Run this in SQL Developer to manually check the join.

-- SELECT l.longlist_id, l.longlist_no, l.year AS l_year,
--        i.longlist_info_id, i.longlist_no AS i_ll_no, i.year AS i_year,
--        i.request_no,
--        DUMP(l.year) AS l_year_dump, DUMP(i.year) AS i_year_dump
-- FROM stda_longlist l, stda_longlist_info i
-- WHERE l.longlist_no = :ll_no
--   AND i.longlist_no = :ll_no;
