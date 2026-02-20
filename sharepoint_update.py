import cx_Oracle


# Database connection string
# dsn_tns = cx_Oracle.makedsn('YOUR_ORACLE_HOST', 'PORT', service_name='YOUR_SERVICE_NAME')
# conn = cx_Oracle.connect(user='YOUR_USERNAME', password='YOUR_PASSWORD', dsn=dsn_tns)



cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
con = cx_Oracle.connect(user='stda', password = 'drwsspadts1031$', dsn="dotorad007vl.state.in.us:1621/INDOT3DEV")



cursor = con.cursor()

sql_query = """
SELECT stda_LONGLIST_INFO.REQUEST_NO
FROM stda_LONGLIST_INFO
JOIN stda_LONGLIST
ON stda_LONGLIST_INFO.LONGLIST_NO = stda_LONGLIST.LONGLIST_NO AND stda_LONGLIST_INFO.YEAR = stda_LONGLIST.YEAR
"""

cursor.execute(sql_query)

# Fetch the result
result = cursor.fetchall()

from shareplum import Site
from shareplum import Office365

# Connect to SharePoint using Office365 auth
authcookie = Office365('https://ingov.sharepoint.com/sites/INDOTSpecializedTesting', username='bshin@indot.in.gov', password='91*gksk*91!!').GetCookies()
site = Site('https://ingov.sharepoint.com/sites/INDOTSpecializedTesting', authcookie=authcookie)

# Access the list
sp_list = site.List('FWD Test Request Overview')

for row in result:
    request_no = 'D2204070112'
    
    # Query to find the matching item in SharePoint list
    query = {
        'Where': [('Eq', 'REQUEST NUMBER', request_no)]
    }
    matched_items = sp_list.GetListItems(query=query)

    # Assuming only one item matched, update the desired field
    if matched_items:
        item = matched_items[0]
        sp_list.UpdateListItems(data=[{'ID': item['ID'], 'Status': 'analysis complete'}])

# Don't forget to close the Oracle cursor and connection
cursor.close()
con.close()