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
                # print(x.split(',', 1)[1])
                comment = str(dmi) + ": " + x.split(',', 1)[1]
                rpistr = x.split(",", 1)[1]
                # if(rpistr.split()[0][0:4] == '"RP-' and rpistr.split()[0][-1:-4] == '+00' and rpistr.split()[1] == "DMI"):
                #     print("FOUND IT yay")
                if(rpistr.split()[0][0:4] == '"RP-' and rpistr.split()[0][-3:] == '+00' and rpistr.split()[1] == "DMI"):
                    # print(rpistr.split()[2][:-1])
                    dmi_val = round(convert_chainage(int(rpistr.split()[2][:-1])))
                    rp_val = rpistr.split()[0][1:]
                    # print(rp_val)
                comments.append(comment)
            elif(tmp[0][0:2] == "76" and x.split(',', 1)[1] != '""\n'):
                try:
                    dmi = round(convert_chainage(int(tmp[1])))
                except:
                    raise Exception("Error when Extracting DMI...")
                comment = str(dmi) + ": " + x.split(',', 1)[1]
                comments.append(comment)
    # print(comments)
    return comments, dmi_val, rp_val
    # print(comments)
    # print(dmi_val)

# get_comments("D:/shrey/Documents/INDOT_Project/Underseal_new/US-30 RP-142+-93 to RP-142+62 (concrete 2)/US-30 LL-205 ramp too/US-30 EB RP-142+-93 to RP-142+62.F25")