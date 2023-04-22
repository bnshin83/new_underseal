Select stda.stda_longlist_info.request_no, stda.stda_Deflections.chainage, stda.stda_longlist.direction, stda.stda_deflections.gpsx, stda.stda_deflections.gpsy, stda.stda_misc.D0_criteria, stda.stda_misc.subgrade_criteria, 
stda.stda_calculations.deflection_0, stda.stda_calculations.deflection_8, stda.stda_calculations.structural_number, stda.stda_calculations.insitucbr, stda.stda_calculations.insitumr, 
stda.stda_calculations.indot_esals, stda.stda_calculations.k_value, stda.stda_calculations.elmod_1, stda.stda_calculations.elmod_2, stda.stda_calculations.elmod_3, stda.stda_calculations.elmod_4,
stda.stda_deflections.deflection_1, stda.stda_deflections.deflection_2, stda.stda_deflections.deflection_3, stda.stda_deflections.deflection_4, stda.stda_deflections.deflection_5, stda.stda_deflections.deflection_6, stda.stda_deflections.deflection_7, stda.stda_deflections.deflection_8, stda.stda_deflections.deflection_9, stda.stda_deflections.air_temp, stda.stda_deflections.surface_temp 
from stda.stda_deflections inner join
stda.stda_longlist ON stda.stda_deflections.longlist_id = stda.stda_longlist.longlist_id 
inner join
stda.stda_misc ON stda.stda_misc.longlist_id = stda.stda_longlist.longlist_id
inner join
stda.stda_calculations ON stda.stda_calculations.longlist_id = stda.stda_longlist.longlist_id
inner join
stda.stda_longlist_info ON stda.stda_longlist.longlist_no = stda.stda_longlist_info.longlist_no AND stda.stda_longlist.year = stda.stda_longlist_info.year;
