SELECT
    CAST(ROWNUM AS VARCHAR(10))                   AS "UNIQID",
    sdo_geometry(
        2001, 4326, sdo_point_type(
            stda.stda_deflections.gpsy, stda.stda_deflections.gpsx, NULL
        ), NULL, NULL
    )                                             AS "GEOMETRY",
    stda.stda_calculations.point                       AS "POINT",
    stda.stda_longlist_info.request_no                 AS "REQUEST_ID",
	stda.stda_longlist_info.district                 AS "DISTRICT",
	stda.stda_longlist_info.route                 AS "ROUTE",
	stda.stda_longlist_info.rp_from                AS "FROM_RP",
	stda.stda_longlist_info.rp_to                 AS "TO_RP",
    stda.stda_deflections.chainage_ft                     AS "CHAINAGE",
    stda.stda_longlist_info.traffic_ctrl               AS "TEST_DATE",
    stda.stda_longlist.direction                       AS "TRAVEL_DIRECTION",
	stda.stda_longlist.pavtype                       AS "PAVE_TYPE",
	stda.stda_longlist.lane_info                       AS "LANE_TYPE",
    stda.stda_deflections.gpsx                         AS "LATITUDE",
    stda.stda_deflections.gpsy                         AS "LONGITUDE",
    round(
        stda.stda_misc.d0_criteria, 2
    )                                             AS "SURFACE_DEFLECTION_CRITERIA",
    round(
        stda.stda_misc.subgrade_criteria, 2
    )                                             AS "SUBGRADE_DEFLECTION_CRITERIA",
    round(
        stda.stda_calculations.deflection_0, 2
    )                                             AS "SURFACE_DEFLECTION",
    round(
        stda.stda_calculations.deflection_8, 2
    )                                             AS "SUBGRADE_DEFLECTION",
    round(
        stda.stda_calculations.insitucbr, 2
    )                                             AS "IN_SITU_CBR",
    round(
        stda.stda_calculations.structural_number, 2
    )                                             AS "IN_SITU_STRUCTURE_NUMBER",
    round(
        stda.stda_calculations.insitumr
    )                                             AS "RESILIENT_MODULUS_CORRECTED",
    round(
        stda.stda_calculations.indot_esals
    )                                             AS "REMAINING_ESALS",
    round(
        stda.stda_calculations.k_value
    )                                             AS "K_VALUE",
    round(stda.stda_calculations.e1_layer1_ksi * 1000) AS "E1_Layer1 (psi)",
    round(stda.stda_calculations.e2_layer2_ksi * 1000) AS "E2_Layer2 (psi)",
    round(stda.stda_calculations.e3_layer3_ksi * 1000) AS "E3_Layer3 (psi)",
    round(stda.stda_calculations.e4_layer4_ksi * 1000) AS "E4_Layer4 (psi)",
    round(
        stda.stda_deflections.deflection_1, 2
    )                                             AS "D1(uncorrected)",
    round(
        stda.stda_deflections.deflection_2, 2
    )                                             AS "D2(uncorrected)",
    round(
        stda.stda_deflections.deflection_3, 2
    )                                             AS "D3(uncorrected)",
    round(
        stda.stda_deflections.deflection_4, 2
    )                                             AS "D4(uncorrected)",
    round(
        stda.stda_deflections.deflection_5, 2
    )                                             AS "D5(uncorrected)",
    round(
        stda.stda_deflections.deflection_6, 2
    )                                             AS "D6(uncorrected)",
    round(
        stda.stda_deflections.deflection_7, 2
    )                                             AS "D7(uncorrected)",
    round(
        stda.stda_deflections.deflection_8, 2
    )                                             AS "D8(uncorrected)",
    round(
        stda.stda_deflections.deflection_9, 2
    )                                             AS "D9(uncorrected)",
    stda.stda_deflections.surface_temp                 AS "Surface Temperature(F)",
    stda.stda_deflections.air_temp                     AS "Air Temperature(F)",
    round(
        stda.stda_moduli_estimated.thickness_1, 2
    )                                             AS "Thickness_Layer1 (in)",
    round(
        stda.stda_moduli_estimated.thickness_2, 2
    )                                             AS "Thickness_Layer2 (in)",
    round(
        stda.stda_moduli_estimated.thickness_3, 2
    )                                             AS "Thickness_Layer3 (in)",
    round(
        stda.stda_moduli_estimated.thickness_4, 2
    )                                             AS "Thickness_Layer4 (in)"
FROM
    stda.stda_moduli_estimated
    INNER JOIN stda.stda_deflections ON stda.stda_deflections.longlist_id = stda.stda_moduli_estimated.longlist_id
                                   AND stda.stda_deflections.point = stda.stda_moduli_estimated.point
                                   AND stda.stda_deflections.drop_no = stda.stda_moduli_estimated.drop_no
INNER JOIN stda.stda_calculations ON stda.stda_deflections.longlist_id = stda.stda_calculations.longlist_id
                                AND stda.stda_deflections.point = stda.stda_calculations.point
                                    AND stda.stda_deflections.drop_no = stda.stda_calculations.drop_no
INNER JOIN stda.stda_misc ON stda.stda_misc.longlist_id = stda.stda_calculations.longlist_id
INNER JOIN stda.stda_longlist ON stda.stda_misc.longlist_id = stda.stda_longlist.longlist_id
INNER JOIN stda.stda_longlist_info ON stda.stda_longlist.longlist_no = stda.stda_longlist_info.longlist_no
                                 AND stda.stda_longlist.year = stda.stda_longlist_info.year