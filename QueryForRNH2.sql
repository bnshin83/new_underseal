SELECT 
    CAST(ROWNUM AS VARCHAR(10))                   AS "UNIQID",
    sdo_geometry(
        2001, 4326, sdo_point_type(
            stda.stda_deflections.gpsy, stda.stda_deflections.gpsx, NULL
        ), NULL, NULL
    )                                             AS "GEOMETRY",    
    stda.stda_longlist_info.request_no as "Request ID",
    stda.stda_longlist.f25_info as "Test Description",
    stda.stda_longlist.pavtype as "Pavement Type",
    stda.stda_Deflections.chainage_ft as "Test DMI",
    stda.stda_longlist_info.traffic_ctrl as "Test Date",
    CASE 
        WHEN stda.stda_longlist.direction LIKE '%EB%' THEN 'Inc' 
        WHEN stda.stda_longlist.direction LIKE '%NB%' THEN 'Inc' 
        ELSE 'Dec' 
    END As "Travel Direction",
    null as "Lane_Position_Research",
    null as "Lane_Position_DTIMS",
    stda.stda_deflections.gpsx as "Latitude(decimal degrees)",
    stda.stda_deflections.gpsy as "Longitude(decimal degrees)",
    null as "Receiver Type",
    null as "LTE",
    round(stda.stda_misc.d0_criteria, 2) AS "SURFACE_DEFLECTION_CRITERIA",
    round(stda.stda_misc.subgrade_criteria, 2) AS "SUBGRADE_DEFLECTION_CRITERIA",
    round(stda.stda_calculations.deflection_0, 2) AS "SURFACE_DEFLECTION",
    round(stda.stda_calculations.deflection_8, 2) AS "SUBGRADE_DEFLECTION",
    round(stda.stda_calculations.insitucbr, 2) AS "IN_SITU_CBR",
    round(stda.stda_calculations.structural_number, 2) AS "IN_SITU_STRUCTURE_NUMBER",
    round(stda.stda_calculations.insitumr) AS "RESILIENT_MODULUS_CORRECTED",
    round(stda.stda_calculations.indot_esals) AS "REMAINING_ESALS",
    round(stda.stda_calculations.k_value)  AS "K_VALUE (pci)",
    round(stda.stda_calculations.e1_layer1_ksi * 1000) AS "E1_Layer1 (psi)",
    round(stda.stda_calculations.e2_layer2_ksi * 1000) AS "E2_Layer2 (psi)",
    round(stda.stda_calculations.e3_layer3_ksi * 1000) AS "E3_Layer3 (psi)",
    round(stda.stda_calculations.e4_layer4_ksi * 1000) AS "E4_Layer4 (psi)",
    round(stda.stda_deflections.deflection_1, 2) AS "D1(uncorrected)",
    round(stda.stda_deflections.deflection_2, 2) AS "D2(uncorrected)",
    round(stda.stda_deflections.deflection_3, 2) AS "D3(uncorrected)",
    round(stda.stda_deflections.deflection_4, 2) AS "D4(uncorrected)",
    round(stda.stda_deflections.deflection_5, 2) AS "D5(uncorrected)",
    round(stda.stda_deflections.deflection_6, 2) AS "D6(uncorrected)",
    round(stda.stda_deflections.deflection_7, 2) AS "D7(uncorrected)",
    round(stda.stda_deflections.deflection_8, 2) AS "D8(uncorrected)",
    round(stda.stda_deflections.deflection_9, 2) AS "D9(uncorrected)",
    stda.stda_deflections.surface_temp as "Surface Temperature(F)",
    stda.stda_deflections.air_temp as "Air Temperature(F)"
FROM 
    stda.stda_Deflections 
INNER JOIN stda.stda_calculations ON stda.stda_Deflections.longlist_id = stda.stda_calculations.longlist_id 
                    AND stda.stda_Deflections.point = stda.stda_calculations.point 
                    AND stda.stda_Deflections.drop_no = stda.stda_calculations.drop_no
INNER JOIN stda.stda_misc ON stda.stda_misc.longlist_id = stda.stda_calculations.longlist_id
INNER JOIN stda.stda_longlist ON stda.stda_misc.longlist_id = stda.stda_longlist.longlist_id
INNER JOIN stda.stda_longlist_info ON stda.stda_longlist.longlist_no = stda.stda_longlist_info.longlist_no 
                      AND stda.stda_longlist.year = stda.stda_longlist_info.year




SELECT 
    CAST(ROWNUM AS VARCHAR(10))                   AS "UNIQID",
    null as "TS Request",
    stda_longlist.begin_latitude as "Beginning_lat",
    stda_longlist.begin_longitude as "Beginning_lon",
    stda_longlist.end_latitude as "Ending_lat",
    stda_longlist.end_longitude as "Ending_lon",
    stda_longlist_info.request_no as "Request ID",
    CASE 
        WHEN stda_longlist.direction LIKE '%EB%' THEN 'Inc' 
        WHEN stda_longlist.direction LIKE '%NB%' THEN 'Inc' 
        ELSE 'Dec' 
    END As "Direction",
    null as "Document Name",
    stda_longlist.f25_info as "Test Description"
FROM 
    stda_longlist 
INNER JOIN 
    stda_longlist_info ON stda_longlist.longlist_no = stda_longlist_info.longlist_no 
                      AND stda_longlist.year = stda_longlist_info.year


