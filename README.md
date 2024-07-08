# digital-asset-catalog
licensed under terms of MIT License -- Copyright (c) 2024 i4 Ops, inc. and hubbert Smith  

Manage digital assets simply and consistently. As shown in CISA 800-53 framework

pip install -r requirements.txt  

dbcreate.py creates empty database  
create tables --- tableasset-0.py, tableasset-event.py tablepolicy-0.py, tablepolicy-event.py  
get-structure.py creates i4catalog-struct.txt, shows database structure

report-all.py sends all tables to i4catalog_data_report.md  

yamlasset-0.yaml to add data. then run yamlasset-0.py to update database  
yamlasset-event.yaml to add data. then run yamlasset-event.py to update database  
yamlpolicy-0.yaml to add data. then run yamlpolicy-0y.py to update database  
yamlpolicy-event.yaml to add data. then run yamlpolicy-eventy.py to update database  

use dbdisplay-edit.py to display tables, add-row, edit-row, delete-row  

