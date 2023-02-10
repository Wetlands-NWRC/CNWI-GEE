import os

import arcpy

cwd = r"C:\Users\ryanh\Work\projects\eerfpl"
print(cwd)
gdb = 'eerfpl.gdb'

# Environment Settings #
arcpy.env.workspace = "CURRENT"
arcpy.env.workspace = os.path.join(cwd, gdb)
arcpy.env.overwriteOutput = True
arcpy.env.outputMFlag = 'Disabled'
arcpy.env.outputZFlag = 'Disabled'

# print(f"{#<'Script Starts'}")
print(f"arcpy.env.workspace: {arcpy.env.workspace}")

TARGET = 'Manual_Mapping_Select_A'
LAND_COVER = 'Class'

# check if in FC is in the right format to split
rows = [row[0] for row in arcpy.da.SearchCursor(TARGET, LAND_COVER)]
land_covers = set(rows)

print(f"\nnRows = {len(rows)}")
print(f'nLand Covers = {len(land_covers)}')

is_dissolved = (len(rows) < len(land_covers))
print(f"\nIs Dissolved: {is_dissolved}")

if not is_dissolved:
    print(f"Dissolving: on {LAND_COVER}")
    out_fc = f'{TARGET}_dis'
    arcpy.Dissolve_management(
        in_features=TARGET,
        out_feature_class=out_fc,
        dissolve_field=[LAND_COVER]
    )
    TARGET = out_fc
    print(f'Target Feature Class: {TARGET}')

print(f"{TARGET} is Dissolved... Proceeding to Point Generation\n")
filenames = []
for land_cover in land_covers:
    ####################################################
    # tool paramaters
    in_layer = TARGET
    selection_ty = 'NEW_SELECTION'
    where = f"{LAND_COVER} = '{land_cover}'"

    print('Executing: Select Layer By Attribute Management')
    # logging
    print(f"In layer = {TARGET}")
    print(f"selection_type = {selection_ty}")
    print(f'where_clause ={where}')

    arcpy.SelectLayerByAttribute_management(
        in_layer_or_view=TARGET,
        selection_type=selection_ty,
        where_clause=where
    )
    print('GP Tool Exits...\n')
    ###################################################
    # tool pramaters
    land_cover = land_cover.replace(" ", "_") if " " in land_cover \
        else land_cover # removes invalid char
    out_name = f'_{land_cover}_ran_pts'
    out_path = arcpy.env.workspace
    bounding_fc = TARGET
    number_of_points = 500
    min_allowed_distance = '60 Meters'

    # logging
    print('Executing: Create Random Points Management')
    print(f"out_name = {out_name}")
    print(f"out_path = {out_path}")
    print(f"constraining_feature_class = {bounding_fc}")
    print(f"number_of_points_or_field = {number_of_points}")
    print(f"minimum_allowed_distance = {min_allowed_distance}")

    arcpy.CreateRandomPoints_management(
        out_name=out_name,
        out_path=out_path,
        constraining_feature_class=TARGET,
        number_of_points_or_field=number_of_points,
        minimum_allowed_distance=min_allowed_distance
    )
    print("GP Tool Exits...\n")
    #################################################
    in_table = out_name
    field_type = 'TEXT'
    express = f'"{land_cover}"'
    expres_ty = "PYTHON3"
    field = 'land_cover'

    # logging
    print('Executing: Calculate Field Management')

    print(f"in_table = {in_table}")
    print(f"field = {field}")
    print(f"field_type = {field_type}")
    print(f"expression = {express}")
    print(f"expression_type = {expres_ty}")

    arcpy.CalculateField_management(
        in_table=out_name,
        field=field,
        field_type=field_type,
        expression=express,
        expression_type=expres_ty
    )
    print("GP Tool Exits...\n")
    ##################################################
    arcpy.SelectLayerByAttribute_management(TARGET, 'CLEAR_SELECTION')
    filenames.append(out_name)
    print(f'END: {land_cover}\n')

######################################################
filenames.sort()
print('Executing: Merge Management')
print(f'inputs: {filenames}')

arcpy.Merge_management(
    inputs=filenames,
    output=os.path.join(cwd, "development", '000-training-data', 
                        'training_data_rcm_cp_williston.gdb',"training_points_500")
)
