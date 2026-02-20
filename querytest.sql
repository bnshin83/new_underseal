SELECT
    CAST(ROWNUM AS VARCHAR(10))                   AS "UNIQID",
    stda_longlist.begin_latitude,
    stda_longlist.begin_longitude,
    stda_longlist_info.request_no,
    stda_longlist.f25_info,
    stda_longlist.pavtype,
    stda_Deflections.chainage_ft,
    stda_longlist_info.traffic_ctrl,
    stda_deflections.gpsx,
    stda_deflections.gpsy,
	stda_misc.d0_criteria,
    stda_misc.subgrade_criteria,
    stda_calculations.deflection_0,
    stda_calculations.deflection_8,
    stda_calculations.insitucbr,
    stda_calculations.structural_number,
    stda_calculations.insitumr,
    stda_calculations.indot_esals,
    stda_calculations.k_value,
    stda_calculations.e1_layer1_ksi,
    stda_calculations.e2_layer2_ksi,
    stda_calculations.e3_layer3_ksi,
    stda_calculations.e4_layer4_ksi,
    stda_deflections.deflection_1,
    stda_deflections.deflection_2,
    stda_deflections.deflection_3,
    stda_deflections.deflection_4,
    stda_deflections.deflection_5,
    stda_deflections.deflection_6,
    stda_deflections.deflection_7,
    stda_deflections.deflection_9
FROM 
    stda_Deflections 
INNER JOIN stda_calculations ON stda_Deflections.longlist_id = stda_calculations.longlist_id 
                    AND stda_Deflections.point = stda_calculations.point 
                    AND stda_Deflections.drop_no = stda_calculations.drop_no
INNER JOIN stda_misc ON stda_misc.longlist_id = stda_calculations.longlist_id
INNER JOIN stda_longlist ON stda_misc.longlist_id = stda_longlist.longlist_id
INNER JOIN stda_longlist_info ON stda_longlist.longlist_no = stda_longlist_info.longlist_no 
                      AND stda_longlist.year = stda_longlist_info.year
                      
SELECT 
    CAST(ROWNUM AS VARCHAR(10))                   AS "UNIQID",
    stda_longlist.begin_latitude,
    stda_longlist.begin_longitude,
    stda_longlist.end_latitude,
    stda_longlist.end_longitude,
    stda_longlist_info.request_no,
    stda_longlist.f25_info
FROM 
    stda_longlist 
INNER JOIN 
    stda_longlist_info ON stda_longlist.longlist_no = stda_longlist_info.longlist_no 
                      AND stda_longlist.year = stda_longlist_info.year