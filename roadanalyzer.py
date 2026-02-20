import xlrd
import excel

def set_vars(testDesc, pavtype):
    initservability = None
    termservability = None
    if pavtype == "concrete":
        initservability = 4.5
    else:
        initservability = 4.2
    if (testDesc == 's'):
        termservability = 2
    else:
        termservability = 2.5
    std = None
    if pavtype.lower() == "concrete":
        std = 0.35
    else:
        std = 0.45
    ## Setting IRI to a fixed value right now because I think pavcond is always set to Fair
    if(pavtype == "asphalt"):
        iri = 120
    elif pavtype == "concrete":
        iri = 140
    else:
        iri = 130
    return initservability, termservability, std, iri  

def calc_esal(ll_obj):
    try:
        trucks = int(ll_obj["traffic"])
    except (ValueError, TypeError):
        trucks = 1
    tf = 0.38
    r = 0.014
    Y = 18
    L = 1
    D = 0.5
    G = 1.13
    esal = trucks*tf*G*D*L*Y*365
    return esal

    

