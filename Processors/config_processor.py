import pandas as pd
import datetime
from ifctester import ids
import xml.etree.ElementTree as ET
import os

def pattern(value):
    result = None if value == '' else value
    try:
        if ',' in value:
            enums = [j.strip() for j in value.split(',')]
            if isinstance(enums[0], str):
                base = "string"
            elif isinstance(enums[0], int):
                base = "integer"
            elif isinstance(enums[0], bool):
                base = "boolean"
            else:
                base = "decimal"
            
            result = ids.Restriction(base=base, options={'enumeration' : enums})
        if value[:1] == '/' and value[-1:] == '/':
            value = value[1:-1]
            if 'clusive=' in value:
                l = value.split(',')                
                options = {}
                for it in l:
                    key=it.split('=')[0].strip()
                    val=int(it.split('=')[1].strip())
                    options[key]=val
                result = ids.Restriction(base="integer", options=options)
            elif  'ength=' in value:
                l = value.split(',')
                options = {}
                for it in l:
                    key=it.split('=')[0].strip().strip()
                    val=int(it.split('=')[1].strip())
                    options[key]=val
                result = ids.Restriction(base="string", options=options)
            else:
                result = ids.Restriction(base="string", options={'pattern' : value})  
        #print(result) 
        return result
    
    except:
        return None

def load_config_excel(config_path):

    out_value = ""
    counter_value = 0
    counter_requirement = 0

    if(config_path):
            
        df_metadata = pd.read_excel(config_path, dtype=str, skiprows=2, sheet_name="METADATA").fillna('')
        df_specifications = pd.read_excel(config_path, dtype=str, skiprows=2, sheet_name="SPECIFICATIONS")
        df_applicability  = pd.read_excel(config_path, dtype=str, skiprows=2, sheet_name="APPLICABILITY")
        df_requirements   = pd.read_excel(config_path, dtype=str, skiprows=2, sheet_name="REQUIREMENTS")

        if df_specifications  is not None and df_metadata is not None:

            try:
            
                ifc_version = df_metadata.loc[0,"IFC Version"]

                my_ids = ids.Ids(title=df_metadata.loc[0,"Title"],
                                copyright=df_metadata.loc[0,"Copyright"],
                                version=df_metadata.loc[0,"Version"],
                                author=df_metadata.loc[0,"Author"],
                                description=df_metadata.loc[0,"Decription"],
                                date=df_metadata.loc[0,"Date"],
                                purpose=df_metadata.loc[0,"Purpose"],
                                milestone=df_metadata.loc[0,"Milestone"]
                )

                for index, spec in df_specifications.iterrows():
                    my_spec = ids.Specification(
                        name=spec.iloc[0],
                        description=spec.iloc[1],
                        #minOccurs=0 if spec.iloc[2].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                        #maxOccurs='unbounded' if spec.iloc[2].upper() in ['REQUIRED', 'OPTIONAL'] else 0,
                        ifcVersion=ifc_version
                    )


                    df_app_spec = df_applicability.query(f"specification == '{spec.iloc[0]}'").fillna('')
                    df_req_spec = df_requirements.query(f"specification == '{spec.iloc[0]}'").fillna('')

                    print(df_app_spec)
                    print(df_req_spec)

                    # create applicability

                    for index, row in df_app_spec.iterrows():                        
                        # add entity
                        
                        entity = ids.Entity(
                            name=pattern(row['entity name']),
                            predefinedType = pattern(row['predefined type'])
                        ) if row['entity name'] != '' else None
                        
                        #add attribute                        

                        attribute = ids.Attribute(
                            name  = pattern(row['attribute name']),
                            value = pattern(row['attribute value'])
                        ) if row['attribute name'] != '' else None
                        
                        #add property                        

                        property = ids.Property( 
                            uri         = row['URI'] if row['URI'] != '' else None,
                            name        = pattern(row['property name']),
                            value       = pattern(row['property value']),
                            propertySet = pattern(row['property set']),
                            datatype    = row['data type'] if row['data type'] != '' else None
                        ) if row['property name'] != '' else None

                        #add property                        

                        property = ids.Property( 
                            uri         = row['URI'] if row['URI'] != '' else None,
                            name        = pattern(row['property name']),
                            value       = pattern(row['property value']),
                            propertySet = pattern(row['property set']),
                            datatype    = row['data type'] if row['data type'] != '' else None
                        ) if row['property name'] != '' else None

                        # add classification

                        classification = ids.Classification( 
                            uri    = row['URI'] if row['URI'] != '' else None,
                            value  = pattern(row['classification reference']),
                            system = pattern(row['classification system'])
                        ) if row['classification reference'] != '' and row['classification system'] != '' else None
                        
                        # add material

                        material = ids.Material(
                            uri   = row['URI'] if row['URI'] != '' else None,
                            value = pattern(row['material name'])
                        ) if row['material name'] != '' else None

                        # add parts

                        parts = ids.PartOf(
                            entity   =row['part of entity'].upper(),
                            relation =None if row['relation'] == '' else row['relation']
                        ) if row['part of entity'] != '' else None

                        if entity:
                            my_spec.applicability.append(entity)                            
                        if attribute:
                            my_spec.applicability.append(attribute)                            
                        if property:
                            my_spec.applicability.append(property)                            
                        if classification:
                            my_spec.applicability.append(classification)                            
                        if material:
                            my_spec.applicability.append(material)                            
                        if parts:
                            my_spec.applicability.append(parts)                            

                    # create requirements
                    for index, row in df_req_spec.iterrows():
                        row['optionality'] = 'REQUIRED' if row['optionality'] == '' else row['optionality']   
                        # add entity

                        entity = ids.Entity(
                            name           = pattern(row['entity name']),
                            predefinedType = pattern(row['predefined type']),
                        ) if row['entity name'] != '' else None

                        #add attribute                        

                        attribute = ids.Attribute(
                            name        = pattern(row['attribute name']),
                            value       = pattern(row['attribute value'])
                        ) if row['attribute name'] != '' else None

                        #add property                        

                        property = ids.Property(
                            uri         = row['URI'] if row['URI'] != '' else None,
                            name        = pattern(row['property name']),
                            value       = pattern(row['property value']),
                            propertySet = pattern(row['property set']),
                            datatype    = row['data type'] if row['data type'] != '' else None,
                            minOccurs   = 0 if row['optionality'].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                            maxOccurs   = 'unbounded' if row['optionality'].upper() in ['REQUIRED', 'OPTIONAL'] else 0
                        ) if row['property name'] != '' else None

                        # add classification

                        classification = ids.Classification(
                            uri       = row['URI'] if row['URI'] != '' else None,
                            value     = pattern(row['classification reference']),
                            system    = pattern(row['classification system']),
                            minOccurs = 0 if row['optionality'].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                            maxOccurs = 'unbounded' if row['optionality'].upper() in ['REQUIRED', 'OPTIONAL'] else 0
                        ) if row['classification reference'] != '' and row['classification system'] != '' else None
                            
                        # add material

                        material = ids.Material(
                            uri       = row['URI'] if row['URI'] != '' else None,
                            value     = pattern(row['material name']),
                            minOccurs = 0 if row['optionality'].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                            maxOccurs = 'unbounded' if row['optionality'].upper() in ['REQUIRED', 'OPTIONAL'] else 0
                        ) if row['material name'] != '' else None

                        # add parts

                        parts = ids.PartOf(
                            name=row['part of entity'].upper(),
                            relation=None if row['relation'] == '' else row['relation'],
                            minOccurs=0 if row['optionality'].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                            maxOccurs='unbounded' if row['optionality'].upper() in ['REQUIRED', 'OPTIONAL'] else 0
                        ) if row['part of entity'] != '' else None
                            

                        if entity:
                            my_spec.requirements.append(entity)
                            counter_requirement+=1
                        if attribute:
                            my_spec.requirements.append(attribute)
                            counter_requirement+=1
                        if property:
                            my_spec.requirements.append(property)
                            counter_requirement+=1
                        if classification:
                            my_spec.requirements.append(classification)
                            counter_requirement+=1
                        if material:
                            my_spec.requirements.append(material)
                            counter_requirement+=1
                        if parts:
                            my_spec.requirements.append(parts)
                            counter_requirement+=1
                        

                    # Add specification in specifications
                    my_ids.specifications.append(my_spec)
                    counter_value += 1

                #ids_export_data = None
                ids_export_data = my_ids.to_string()



                if ids_export_data is not None:
                    # Parse the XML string
                    root = ET.fromstring(ids_export_data)

                    # Create an ElementTree object
                    tree = ET.ElementTree(root)

                    # Specify the file path with .ids extension
                    file_name = os.path.basename(config_path)
                    export_folder = os.path.dirname(config_path)
                    file_path = os.path.join(r"{}".format(export_folder), "{}.ids".format(file_name.split(".")[0]))

                    # Write the XML data to the file
                    with open(file_path, "wb") as file:
                        tree.write(file, encoding="utf-8", xml_declaration=True)
                        print('File successfully exported')
                        out_value = 'File successfully exported'

                else:
                    print('ERROR : File not created!')
                    out_value = 'ERROR : File not created!'
            except:
                print("Wrong Input Data")
                out_value = "Wrong Input Data"

    return (out_value, counter_value, counter_requirement)