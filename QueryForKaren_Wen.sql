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
    ROUND(c.insitucbr, 2)                               AS "IN_SITU_CBR",
    ROUND(c.structural_number, 2)                       AS "IN_SITU_STRUCTURE_NUMBER",
    ROUND(c.insitumr)                                   AS "RESILIENT_MODULUS_CORRECTED",
    ROUND(c.indot_esals)                                AS "REMAINING_ESALS",
    ROUND(c.k_value)                                    AS "K_VALUE",
    ROUND(c.e1_layer1_ksi * 1000)                       AS "E1_Layer1 (psi)",
    ROUND(c.e2_layer2_ksi * 1000)                       AS "E2_Layer2 (psi)",
    ROUND(c.e3_layer3_ksi * 1000)                       AS "E3_Layer3 (psi)",
    ROUND(c.e4_layer4_ksi * 1000)                       AS "E4_Layer4 (psi)",
    ROUND(d.deflection_1, 2)                            AS "D1(mil)",
    ROUND(d.deflection_2, 2)                            AS "D2(mil)",
    ROUND(d.deflection_3, 2)                            AS "D3(mil)",
    ROUND(d.deflection_4, 2)                            AS "D4(mil)",
    ROUND(d.deflection_5, 2)                            AS "D5(mil)",
    ROUND(d.deflection_6, 2)                            AS "D6(mil)",
    ROUND(d.deflection_7, 2)                            AS "D7(mil)",
    ROUND(d.deflection_8, 2)                            AS "D8(mil)",
    ROUND(d.deflection_9, 2)                            AS "D9(mil)",
    d.surface_temp                                      AS "Surface Temperature(F)",
    d.air_temp                                          AS "Air Temperature(F)",
    ROUND(me.thickness_1, 2)                            AS "Thickness_Layer1 (in)",
    ROUND(me.thickness_2, 2)                            AS "Thickness_Layer2 (in)",
    ROUND(me.thickness_3, 2)                            AS "Thickness_Layer3 (in)",
    ROUND(me.thickness_4, 2)                            AS "Thickness_Layer4 (in)",
    l.f25_info                                          AS "Filename"
FROM
    stda.stda_moduli_estimated me
    INNER JOIN stda.stda_deflections d ON d.longlist_id = me.longlist_id
                                      AND d.point = me.point
                                      AND d.drop_no = me.drop_no
    INNER JOIN stda.stda_calculations c ON d.longlist_id = c.longlist_id
                                      AND d.point = c.point
                                      AND d.drop_no = c.drop_no
    INNER JOIN stda.stda_misc m ON m.longlist_id = c.longlist_id
    INNER JOIN stda.stda_longlist l ON m.longlist_id = l.longlist_id
    INNER JOIN stda.stda_longlist_info li ON l.longlist_no = li.longlist_no
                                         AND l.year = li.year
WHERE
    li.request_no IN ('D2004070001', 'D2104060001', 'D2208110001')
