import re
def convert_chainage(a):
    return a*3.28084

def get_comments(f25_path):
    comments = []
    dmi_val = None
    rp_val = None
    with open(f25_path, "r") as f:
        dmi = 0
        for x in f:
            tmp = x.split(',')
            comment = ""
            if(tmp[0] == "7901" and x.split(',', 1)[1] != '""\n'):
                comment = str(dmi) + ": " + x.split(',', 1)[1]
                rpistr = x.split(",", 1)[1]
                if(rpistr.split()[0][0:4] == '"RP-' and rpistr.split()[0][-3:] == '+00' and rpistr.split()[1] == "DMI"):
                    dmi_val = round(convert_chainage(float(rpistr.split()[2][:-1])))
                    rp_val = rpistr.split()[0][1:]
                comments.append(comment)
            elif(tmp[0][0:2] == "76" and x.split(',', 1)[1] != '""\n'):
                try:
                    dmi = round(convert_chainage(float(tmp[1])))
                except Exception:
                    raise Exception("Error when Extracting DMI...")
                comment = str(dmi) + ": " + x.split(',', 1)[1]
                comments.append(comment)
    return comments, dmi_val, rp_val