from odbAccess import openOdb
from abaqusConstants import INTEGRATION_POINT
import os


# ============================================================
# USER SETTINGS
# ============================================================

odb_path = r"Path of the .odb File"

step_name = "Step-1"

# -1 = last frame
frame_number = -1


# ============================================================
# OPEN ODB
# ============================================================

print("")
print("Opening ODB...")
print(odb_path)

odb = openOdb(path=odb_path)

step = odb.steps[step_name]

if frame_number == -1:
    frame = step.frames[-1]
    actual_frame_number = len(step.frames) - 1
else:
    frame = step.frames[frame_number]
    actual_frame_number = frame_number


# ============================================================
# GET STRESS
# ============================================================

stress = frame.fieldOutputs["S"]

stress_ip = stress.getSubset(position=INTEGRATION_POINT)


# ============================================================
# FIND MAXIMUM MISES
# ============================================================

max_mises = -1.0
max_value = None

for value in stress_ip.values:

    if value.mises > max_mises:

        max_mises = value.mises
        max_value = value


if max_value is None:

    print("ERROR: No integration-point stress values found.")

    odb.close()

    raise SystemExit


# ============================================================
# MAXIMUM STRESS LOCATION
# ============================================================

instance = max_value.instance

element_label = max_value.elementLabel

integration_point = max_value.integrationPoint


# ============================================================
# FIND ELEMENT
# ============================================================

element = None

for elem in instance.elements:

    if elem.label == element_label:

        element = elem
        break


if element is None:

    print("ERROR: Could not find element.")

    odb.close()

    raise SystemExit


# ============================================================
# ELEMENT INFORMATION
# ============================================================

print("")
print("============================================================")
print("MAXIMUM MISES STRESS")
print("============================================================")

print("ODB:              %s" % os.path.basename(odb_path))
print("Step:             %s" % step_name)
print("Frame:            %d" % actual_frame_number)

print("------------------------------------------------------------")

print("Instance:         %s" % instance.name)
print("Element:          %d" % element_label)
print("Element Type:     %s" % element.type)
print("Integration Pt:   %d" % integration_point)

print("------------------------------------------------------------")

print("Mises:            %.6f" % max_mises)

print("============================================================")
print("ELEMENT CONNECTIVITY")
print("============================================================")

print("Node labels:")

for node_label in element.connectivity:

    print("  %d" % node_label)


# ============================================================
# GET NODE COORDINATES
# ============================================================

print("")
print("============================================================")
print("ELEMENT NODE COORDINATES")
print("============================================================")

node_coordinates = {}

for node_label in element.connectivity:

    node = instance.nodes[node_label - 1]

    node_coordinates[node_label] = node.coordinates

    print(
        "Node %-8d : X = %12.6f   Y = %12.6f   Z = %12.6f"
        % (
            node_label,
            node.coordinates[0],
            node.coordinates[1],
            node.coordinates[2]
        )
    )


# ============================================================
# CALCULATE APPROXIMATE ELEMENT CENTER
# ============================================================

x = 0.0
y = 0.0
z = 0.0

number_of_nodes = len(element.connectivity)

for node_label in element.connectivity:

    coordinates = node_coordinates[node_label]

    x += coordinates[0]
    y += coordinates[1]
    z += coordinates[2]


x /= number_of_nodes
y /= number_of_nodes
z /= number_of_nodes


# ============================================================
# RESULT
# ============================================================

print("")
print("============================================================")
print("APPROXIMATE ELEMENT CENTER")
print("============================================================")

print("X:                %.9f" % x)
print("Y:                %.9f" % y)
print("Z:                %.9f" % z)

print("============================================================")
print("")
print("NOTE:")
print("The coordinates above are the ELEMENT CENTER,")
print("not necessarily the exact integration-point location.")
print("============================================================")

odb.close()

print("")
print("ODB closed.")
print("")



# abaqus python "Path of this Python File"  
# run the line above in powershell. the ressults will be shown in powershell. enjoy! S.S.