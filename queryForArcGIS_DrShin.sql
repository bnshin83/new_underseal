Select stda.stda_longlist.longlist_id, stda.stda_calculations.point, stda.stda_longlist_info.request_no, null as "Test Description", stda.stda_Deflections.chainage, stda.stda_longlist.direction, null as "Lane_Position_Research", null as "Lane_Position_DTIMS", stda.stda_deflections.gpsx, stda.stda_deflections.gpsy, null as "Reciever Type", stda.stda_misc.D0_criteria, stda.stda_misc.subgrade_criteria, 
stda.stda_calculations.deflection_0, stda.stda_calculations.deflection_8, stda.stda_calculations.insitucbr, stda.stda_calculations.structural_number,  stda.stda_calculations.insitumr, 
stda.stda_calculations.indot_esals, stda.stda_calculations.k_value, null as "LTE", stda.stda_calculations.elmod_1, stda.stda_calculations.elmod_2, stda.stda_calculations.elmod_3, stda.stda_calculations.elmod_4,
stda.stda_deflections.deflection_1, stda.stda_deflections.deflection_2, stda.stda_deflections.deflection_3, stda.stda_deflections.deflection_4, stda.stda_deflections.deflection_5, stda.stda_deflections.deflection_6, stda.stda_deflections.deflection_7, stda.stda_deflections.deflection_8, stda.stda_deflections.deflection_9, stda.stda_deflections.air_temp, stda.stda_deflections.surface_temp 
FROM stda.stda_Deflections INNER JOIN stda.stda_calculations ON stda.stda_Deflections.longlist_id = stda.stda_calculations.longlist_id AND stda.stda_Deflections.point = stda.stda_calculations.point AND stda.stda_Deflections.drop_no = stda.stda_calculations.drop_no
INNER JOIN stda.stda_misc ON stda.stda_misc.longlist_id = stda.stda_calculations.longlist_id
INNER JOIN stda.stda_longlist ON stda.stda_misc.longlist_id = stda.stda_longlist.longlist_id
INNER JOIN stda.stda_longlist_info ON stda.stda_longlist.longlist_no = stda.stda_longlist_info.longlist_no AND stda.stda_longlist.year = stda.stda_longlist_info.year ORDER BY stda.stda_longlist.longlist_id, stda.stda_calculations.point ASC;


select null as "TS Request", stda.stda_longlist.begin_latitude, stda.stda_longlist.begin_longitude, stda.stda_longlist.end_latitude, stda.stda_longlist.end_longitude, stda.stda_longlist_info.request_no, stda.stda_longlist.direction,
null as "Document Name", null as "Test Description"
FROM stda.stda_longlist INNER JOIN stda.stda_longlist_info ON stda.stda_longlist.longlist_no = stda.stda_longlist_info.longlist_no AND stda.stda_longlist.year = stda.stda_longlist_info.year;