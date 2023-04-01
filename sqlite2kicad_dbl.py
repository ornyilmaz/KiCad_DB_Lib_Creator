'''

ORHAN YILMAZ
ORELTEK ELEKTRONİK VE YAZILIM TEKNOLOJİLERİ SAN. TİC. LTD. ŞTİ.

'''

import sqlite3
import pandas as pd
import json

'''
Referances
-----------

1. https://docs.kicad.org/master/en/eeschema/eeschema_advanced.html
2. https://docs.kicad.org/doxygen/database__lib__settings_8cpp_source.html
3. http://www.ch-werner.de/sqliteodbc/

'''

KICAD_DB_NAME            = "ORELTEK KiCAD DATABASE LIBRARY"
KICAD_DB_DESCRIPTION     = "ORELTEK Elektronik Komponentleri Kutuphanesi"
KICAD_DB_SRC_DSN_NAME    = "KICAD_DB"
KICAD_DB_SRC_USERNAME    = ""
KICAD_DB_SRC_PASSWORD    = ""
KICAD_DBL_OUTPUT_PATH    = "./"


# KiCad Ref Template
template_file = open('template.kicad_dbl', 'r')
template_json = json.loads(template_file.read())

# Set initial definitions
template_json["name"]                   = KICAD_DB_NAME
template_json["description"]            = KICAD_DB_DESCRIPTION
template_json["source"]["dsn"]          = KICAD_DB_SRC_DSN_NAME
template_json["source"]["username"]     = KICAD_DB_SRC_USERNAME
template_json["source"]["password"]     = KICAD_DB_SRC_PASSWORD

output_dbl_file = open('ORELTEK_LibDB.kicad_dbl','w')

# Veritabanına bağlan
conn = sqlite3.connect('LibDB.db')

# Tüm tabloları oku
table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].tolist()

template_json["libraries"] = [] # initial clear


# Her tabloyu JSON dosyası olarak kaydet
for table_name in table_names:
    # Verileri oku
    df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    
    # JSON dosyasına dönüştür ve kaydet
    json_table = json.loads(df.to_json(orient="records"))
    sample_dev_lib = {
            "name": "Resistors",
            "table": "Resistors",
            "key": "Part ID",
            "symbols": "Symbols",
            "footprints": "Footprints",
            "fields": [
                {
                    "column": "MPN",
                    "name": "MPN",
                    "visible_on_add": "false",
                    "visible_in_chooser": "true",
                    "show_name": "true",
                    "inherit_properties": "true"
                },
                {
                    "column": "Value",
                    "name": "Value",
                    "visible_on_add": "true",
                    "visible_in_chooser": "true",
                    "show_name": "false"
                }
            ],
            "properties": {
                "description": "Description",
                "footprint_filters": "Footprint Filters",
                "keywords": "Keywords",
                "exclude_from_bom": "No BOM",
                "exclude_from_board": "Schematic Only"
            }
        }
    # Component parametrelerini güncelle
    sample_dev_lib["name"]          = table_name
    sample_dev_lib["table"]         = table_name
    sample_dev_lib["key"]           = "Part Number"
    sample_dev_lib["symbols"]       = "KICAD_SCHLIB"
    sample_dev_lib["footprints"]    = "KICAD_MODLIB"
    sample_dev_lib["fields"]        = [] #clear first

    dummy_field = {"column":"Value","name":"Value","visible_on_add":"false","visible_in_chooser":"true","show_name":"true","inherit_properties":"true"}
    sample_dev_lib["fields"].append(dummy_field)

    dummy_field = {"column":"Manufacturer","name":"Manufacturer","visible_on_add":"false","visible_in_chooser":"true","show_name":"true","inherit_properties":"true"}
    sample_dev_lib["fields"].append(dummy_field)


    for attr in json_table[0]:
        if attr not in {"Part Number","KICAD_SCHLIB","KICAD_MODLIB","Value","Manufacturer","Description","index"} :
            dummy_field = {"column":f'{attr}',"name":f'{attr}',"visible_on_add":"false","visible_in_chooser":"true","show_name":"true","inherit_properties":"true"}
            sample_dev_lib["fields"].append(dummy_field)

    sample_dev_lib["properties"]["description"] = "Description"
    sample_dev_lib["properties"]["footprint_filters"] = "Footprint Filters" #default bırakıldı
    sample_dev_lib["properties"]["keywords"] = "Value" 
    sample_dev_lib["properties"]["exclude_from_bom"] = "No BOM" #default bırakıldı
    sample_dev_lib["properties"]["exclude_from_board"] = "Schematic Only" #default bırakıldı

    # print(sample_dev_lib["name"])
    # oluşturulan device şablonu kütüphane başlığına ekleyelim.
 
    template_json["libraries"].append(sample_dev_lib) 
    # print(template_json["libraries"])

    # Veritabanı kontrolü ve gerekli ise düzenlemesini yapalım #

    # DB işaretçisi tanımla
    cursor = conn.cursor()

    # Sembol Sutunu ekle
    if "KICAD_SCHLIB" not in json_table[0]:

        cursor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN KICAD_SCHLIB TEXT;')

        # Sembol Sutunu uygun şekilde eşle
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:R_Small_US" where "Library Ref" = "Resistor";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:C_Small" where "Library Ref" = "Capacitor";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:C_Polarized_Small_US" where "Library Ref" = "ELEC_Capacitor";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:L" where "Library Ref" = "Inductance";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:L_Ferrite_Small" where "Library Ref" = "Feridbeed";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:D" where "Library Ref" = "STD_Diode";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:D_Schottky" where "Library Ref" = "Schottky_Diode";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:LED" where "Library Ref" = "LED";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "ORL-Diodes:TVS_Unidirection" where "Library Ref" = "TVS_Diode";')
        cursor.execute(f'update "{table_name}" set KICAD_SCHLIB = "Device:D_Zener" where "Library Ref" = "Zener_Diode";')
        #Others
        cursor.execute(f'''update "{table_name}" set KICAD_SCHLIB = "ORL_{table_name}:" || "Library Ref"
            where "Library Ref" not in  ("Resistor" ,"Capacitor", "ELEC_Capacitor", "Inductance", "Feridbeed", "STD_Diode", "Schottky_Diode", "LED", "TVS_Diode", "Zener_Diode");''')
        
    # Footprint Sutunu ekle
    if "KICAD_MODLIB" not in json_table[0]:  
        cursor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN KICAD_MODLIB TEXT;')
    
    # Footprint Sutunu uygun şekilde eşle
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Resistor_SMD:R_0805_2012Metric" where "Footprint Ref" = "RES0805";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Resistor_SMD:R_0603_1608Metric" where "Footprint Ref" = "RES0603";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:C_0805_2012Metric" where "Footprint Ref" = "CAP0805";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:C_0603_1608Metric" where "Footprint Ref" = "CAP0603";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:CP_Elec_4x5.8" where "Footprint Ref" = "CAPE_B";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:CP_Elec_5x5.8" where "Footprint Ref" = "CAPE_C";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:C_Elec_6.3x5.8" where "Footprint Ref" = "CAPE_D";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:C_Elec_6.3x7.7" where "Footprint Ref" = "CAPE_D8";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:C_Elec_8x6.2" where "Footprint Ref" = "CAPE_E";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:C_Elec_8x6.2" where "Footprint Ref" = "CAPE_F";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Capacitor_SMD:C_Elec_8x10.2" where "Footprint Ref" = "CAPE_G";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Inductor_SMD:L_0805_2012Metric" where "Footprint Ref" = "FB0805";')
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "Inductor_SMD:L_1206_3216Metric" where "Footprint Ref" = "FB1206";')
        
        #Others
        cursor.execute(f'update "{table_name}" set KICAD_MODLIB = "ORL_{table_name}:" || "Footprint Ref" where "KICAD_MODLIB" IS NULL;')

        #Database yaz
        conn.commit()

    # print(table_name)
    # print(json_table[0])
    # print(json_table[0]["Categories"])
#file write
output_dbl_file.write(json.dumps(template_json,indent=3))

conn.close()
template_file.close()
output_dbl_file.close()
