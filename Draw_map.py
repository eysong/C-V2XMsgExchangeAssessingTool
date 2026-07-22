import os
import webbrowser
import folium
import csv
from pathlib import Path

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "coords.csv"

coordinates = []

with open(csv_path, mode = "r") as file:
    csv_reader = csv.reader(file, skipinitialspace = True)
    for row in csv_reader:
        if not row:
            continue

        lat = float(row[0])
        long = float(row[1])
        status = row[2].strip().lower() == "true"
        coordinates.append(([lat, long], status))

# Ensure we actually found coordinates in the file
if not coordinates:
    raise ValueError("Error: No valid SAE J2735 coordinates were found in your PDML file!")

# Create map centered around the starting location
map_center = coordinates[0][0]
m = folium.Map(location=map_center, zoom_start=15)

# # Trace the path
# folium.PolyLine(
#     locations=coordinates,
#     color="blue",
#     weight=5,
#     opacity=0.8,
#     tooltip="Car Path"
# ).add_to(m)

#Start marker
folium.Marker(
    location=coordinates[0][0],
    popup="Start",
    icon=folium.Icon(color="green", icon="play")
).add_to(m)

#End marker
folium.Marker(
    location=coordinates[-1][0],
    popup="End",
    icon=folium.Icon(color="red", icon="stop")
).add_to(m)

#Traverses thru the coordinates 2D list to obtain individual pairs of lat and long
#Plots those coordinates on the map
for coordinate in coordinates:
    if coordinate[1] == True:
        color='green',  # Outline color
    else:
        color = 'red'
    folium.CircleMarker(
    location=coordinate[0],
    radius=3,  # Size of the dot in pixels
    fill=True,
    color=color,
    fill_color=color,  # Fill color
    fill_opacity=1
).add_to(m)

#Save the map to an HTML file to view it in a browser
m.save(r"C:\Users\sns123\Documents\My Code\V2X Message Exchanging Process Analyzer Tool\C-V2XMsgExchangeAssessingTool\car_trajectory.html")