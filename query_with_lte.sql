SELECT
    CAST(ROWNUM AS VARCHAR(10))                         AS "UNIQID",
    sdo_geometry(2001, 4326, sdo_point_type(d.gpsy, d.gpsx, NULL), NULL, NULL) AS "GEOMETRY",
    c.point                                             AS "POINT",
    li.request_no                                       AS "REQUEST_ID",
    li.district                                         AS "DISTRICT",
    li.route                                            AS "ROUTE",
    li.rp_from                                          AS "FROM_RP",
    li.rp_to                                            AS "TO_RP",
    d.chainage_ft                                       AS "CHAINAGE",
    li.traffic_ctrl                                     AS "TEST_DATE",
    l.direction                                         AS "TRAVEL_DIRECTION",
    l.pavtype                                           AS "PAVE_TYPE",
    l.lane_info                                         AS "LANE_TYPE",
    d.gpsx                                              AS "LATITUDE",
    d.gpsy                                              AS "LONGITUDE",
    ROUND(m.d0_criteria, 2)                             AS "SURFACE_DEFLECTION_CRITERIA",
    ROUND(m.subgrade_criteria, 2)                       AS "SUBGRADE_DEFLECTION_CRITERIA",
    ROUND(c.deflection_0, 2)                            AS "SURFACE_DEFLECTION",
    ROUND(c.deflection_8, 2)                            AS "SUBGRADE_DEFLECTION",
    CASE
      WHEN d.deflection_3 / d.deflection_1 >1 THEN ROUND(1.00, 2)
      ELSE ROUND(d.deflection_3 / d.deflection_1, 2)
    END AS LTE,
    l.longlist_id                                       AS "LONGLIST_ID",
    d.surface_temp                                      AS "Surface Temperature(F)",
    d.air_temp                                          AS "Air Temperature(F)",
    l.f25_info                                          AS "Filename"
FROM
    stda_moduli_estimated me
    INNER JOIN stda_deflections d ON d.longlist_id = me.longlist_id
                                      AND d.point = me.point
                                      AND d.drop_no = me.drop_no
    INNER JOIN stda_calculations c ON d.longlist_id = c.longlist_id
                                      AND d.point = c.point
                                      AND d.drop_no = c.drop_no
    INNER JOIN stda_misc m ON m.longlist_id = c.longlist_id
    INNER JOIN stda_longlist l ON m.longlist_id = l.longlist_id
    INNER JOIN stda_longlist_info li ON l.longlist_no = li.longlist_no
                                         AND l.year = li.year
WHERE
    li.request_no IN ('D2510220001')