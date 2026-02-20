-- Query #1
SELECT 
    stda_longlist_info.request_no as "Request ID",
    stda_longlist.f25_info as "Test Description",
    stda_longlist.pavtype as "Pavement Type",
    stda_Deflections.chainage_ft as "Test DMI",
    stda_longlist_info.traffic_ctrl as "Test Date",
    CASE 
        WHEN stda_longlist.direction LIKE '%EB%' THEN 'Inc' 
        WHEN stda_longlist.direction LIKE '%NB%' THEN 'Inc' 
        ELSE 'Dec' 
    END As "Travel Direction",
    null as "Lane_Position_Research",
    null as "Lane_Position_DTIMS",
    stda_deflections.gpsx as "Latitude(decimal degrees)",
    stda_deflections.gpsy as "Longitude(decimal degrees)",
    null as "Receiver Type",
    stda_misc.D0_criteria as "Surface Deflection Criteria",
    stda_misc.subgrade_criteria as "Subgrade Deflection Criteria",
    stda_calculations.deflection_0 as "Surface Deflection",
    stda_calculations.deflection_8 as "Subgrade Deflection",
    stda_calculations.insitucbr as "In-Situ CBR",
    stda_calculations.structural_number as "In-Situ Structure Number",
    stda_calculations.insitumr as "Resilient Modulus(corrected)",
    stda_calculations.indot_esals as "Remaining ESALs",
    stda_calculations.k_value as "K Value",
    null as "LTE",
    stda_calculations.e1_layer1_psi as "E1",
    stda_calculations.e2_layer2_psi as "E2",
    stda_calculations.e3_layer3_psi as "E3",
    stda_calculations.e4_layer4_psi as "E4",
    stda_deflections.deflection_1 as "D1(uncorrected)",
    stda_deflections.deflection_2 as "D2(uncorrected)",
    stda_deflections.deflection_3 as "D3(uncorrected)",
    stda_deflections.deflection_4 as "D4(uncorrected)",
    stda_deflections.deflection_5 as "D5(uncorrected)",
    stda_deflections.deflection_6 as "D6(uncorrected)",
    stda_deflections.deflection_7 as "D7(uncorrected)",
    stda_deflections.deflection_8 as "D8(uncorrected)",
    stda_deflections.deflection_9 as "D9(uncorrected)",
    stda_deflections.surface_temp as "Surface Temperature(F)",
    stda_deflections.air_temp as "Air Temperature(F)" 
FROM 
    stda_Deflections 
INNER JOIN 
    stda_calculations ON stda_Deflections.longlist_id = stda_calculations.longlist_id 
                    AND stda_Deflections.point = stda_calculations.point 
                    AND stda_Deflections.drop_no = stda_calculations.drop_no
INNER JOIN 
    stda_misc ON stda_misc.longlist_id = stda_calculations.longlist_id
INNER JOIN 
    stda_longlist ON stda_misc.longlist_id = stda_longlist.longlist_id
INNER JOIN 
    stda_longlist_info ON stda_longlist.longlist_no = stda_longlist_info.longlist_no 
                      AND stda_longlist.year = stda_longlist_info.year 
ORDER BY 
    stda_longlist.longlist_id, stda_calculations.point ASC;
    
    
-- Query #2
SELECT 
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
                      AND stda_longlist.year = stda_longlist_info.year;

--Select stda_longlist_info.request_no as "Request ID", stda_longlist.f25_info as "Test Description", stda_Deflections.chainage as "Test DMI", stda_longlist_info.traffic_ctrl as "Test Date", 
--CASE WHEN stda_longlist.direction LIKE '%EB%' THEN 'Inc' WHEN stda_longlist.direction LIKE '%NB%' THEN 'Inc' ELSE 'Dec' END As "Travel Direction", null as "Lane_Position_Research", null as "Lane_Position_DTIMS", stda_deflections.gpsx as "Latitude(decimal degrees)", stda_deflections.gpsy as "Longitude(decimal degrees)", null as "Reciever Type", stda_misc.D0_criteria as "Surface Deflection Criteria", stda_misc.subgrade_criteria as "Subgrade Deflection Criteria", 
--stda_calculations.deflection_0 as "Surface Deflection", stda_calculations.deflection_8 as "Subgrade Deflection", stda_calculations.insitucbr as "In-Situ CBR", stda_calculations.structural_number as "In-Situ Structure Number",  stda_calculations.insitumr as "Resilient Modulus(corrected)", 
--stda_calculations.indot_esals as "Remaining ESALs", stda_calculations.k_value as "K Value", null as "LTE", stda_calculations.elmod_1 as "E1", stda_calculations.elmod_2 as "E2", stda_calculations.elmod_3 as "E3", stda_calculations.elmod_4 as "E4",
--stda_deflections.deflection_1 as "D1(uncorrected)", stda_deflections.deflection_2 as "D2(uncorrected)", stda_deflections.deflection_3 as "D3(uncorrected)", stda_deflections.deflection_4 as "D4(uncorrected)", stda_deflections.deflection_5 as "D5(uncorrected)", stda_deflections.deflection_6 as "D6(uncorrected)", stda_deflections.deflection_7 as "D7(uncorrected)", stda_deflections.deflection_8 as "D8(uncorrected)", stda_deflections.deflection_9 as "D9(uncorrected)", stda_deflections.surface_temp as "Surface Temperature(F)", stda_deflections.air_temp as "Air Temperature(F)" 
--FROM stda_Deflections INNER JOIN stda_calculations ON stda_Deflections.longlist_id = stda_calculations.longlist_id AND stda_Deflections.point = stda_calculations.point AND stda_Deflections.drop_no = stda_calculations.drop_no
--INNER JOIN stda_misc ON stda_misc.longlist_id = stda_calculations.longlist_id
--INNER JOIN stda_longlist ON stda_misc.longlist_id = stda_longlist.longlist_id
--INNER JOIN stda_longlist_info ON stda_longlist.longlist_no = stda_longlist_info.longlist_no AND stda_longlist.year = stda_longlist_info.year WHERE stda_longlist_info.request_no='D2204070212' ORDER BY stda_longlist.longlist_id, stda_calculations.point ASC;
--
--
--select null as "TS Request", stda_longlist.begin_latitude as "Beginning_lat", stda_longlist.begin_longitude as "Beginning_lon", stda_longlist.end_latitude as "Ending_lat", stda_longlist.end_longitude as "Ending_lon", stda_longlist_info.request_no as "Request ID", CASE WHEN stda_longlist.direction LIKE '%EB%' THEN 'Inc' WHEN stda_longlist.direction LIKE '%NB%' THEN 'Inc' ELSE 'Dec' END As "Direction",
--null as "Document Name", stda_longlist.f25_info as "Test Description"
--FROM stda_longlist INNER JOIN stda_longlist_info ON stda_longlist.longlist_no = stda_longlist_info.longlist_no AND stda_longlist.year = stda_longlist_info.year;

