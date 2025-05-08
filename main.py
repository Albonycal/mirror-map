import requests
import dash
from dash import html, dcc
import dash_leaflet as dl
from dash.dependencies import Output, Input
# Define mirror nodes with their locations
nodes = {
    "https://mirror.bom.albony.in/stats": {"location": "Mumbai", "lat": 19.4, "lon": 72.8777},
    "https://mirror.bom2.albony.in/stats": {"location": "Mumbai-2 (EIX)", "lat": 19.0760, "lon": 72.8777},
    "https://mirror.del.albony.in/stats": {"location": "Delhi (EIX)", "lat": 28.7041, "lon": 77.1025},
    "https://mirror.del2.albony.in/stats": {"location": "Delhi (Cityline)", "lat": 28.9, "lon": 77.3},
    "https://mirror.hyd.albony.in/stats": {"location": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    "https://mirror.ajl.albony.in/stats": {"location": "Aizawl", "lat": 23.7271, "lon": 92.7176},
    "https://mirror.maa.albony.in/stats": {"location": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "https://mirror.nag.albony.in/stats": {"location": "Nagpur", "lat": 21.1458, "lon": 79.0882},
}

# Define custom marker colors (green for online, red for offline)
marker_icons = {
    "green": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
    "red": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
}

# Function to fetch and parse data usage
def fetch_data(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.text.split("\n")

        total_usage, daily_usage = "N/A", "N/A"

        # Extract total usage
        for line in data:
            if "total:" in line:
                parts = line.split("total:")
                if len(parts) > 1:
                    total_usage = parts[1].strip()
                break

        # Extract daily usage
        for i, line in enumerate(data):
            if "daily" in line.lower():
                for j in range(i, len(data)):
                    if "today" in data[j].lower():
                        parts = data[j].split("|")
                        if len(parts) > 2:
                            daily_usage = parts[-2].strip()
                        break
                break

        print(f"Fetched from {url}: Total={total_usage}, Daily={daily_usage}")  # Debugging log
        return total_usage, daily_usage

    except (requests.RequestException, IndexError) as e:
        print(f"Error fetching data from {url}: {e}")  # Debugging log
        return None, None

# Dash App Setup
#app = dash.Dash(__name__)
app = dash.Dash(__name__, url_base_pathname='/map/')

server = app.server
app.layout = html.Div([
    html.H1("Albony Mirror Network Status", style={"textAlign": "center", "color": "#333"}),
    html.P("Live data usage and availability status of Albony mirror nodes across India.", 
           style={"textAlign": "center", "color": "#555"}),
    
    dl.Map(center=[20.5937, 78.9629], zoom=5, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="layer")
    ], style={'width': '100%', 'height': '75vh', "borderRadius": "10px", "boxShadow": "0px 4px 10px rgba(0,0,0,0.1)"}),

    dcc.Interval(id='interval-component', interval=60000, n_intervals=0)  # Refresh every minute
], style={"maxWidth": "800px", "margin": "auto", "padding": "20px", "fontFamily": "Arial, sans-serif"})

# Update markers dynamically
@app.callback(Output("layer", "children"), [Input('interval-component', 'n_intervals')])
def update_markers(n):
    markers = []
    for url, info in nodes.items():
        total_usage, daily_usage = fetch_data(url)

        if total_usage is None:
            status, color = "Offline", "red"
            total_usage, daily_usage = "N/A", "N/A"
        else:
            status, color = "Online", "green"

        try:
            icon_dict = {"iconUrl": marker_icons[color], "iconSize": [25, 41], "iconAnchor": [12, 41]}

            marker = dl.Marker(
                position=[info['lat'], info['lon']],
                icon=icon_dict, 
                children=[
                    dl.Tooltip(info['location']),
                dl.Popup(html.Div([
    html.H4(info['location'], style={"margin-bottom": "5px"}),
    html.P(f"Status: {status}", style={"color": "green" if status == "Online" else "red"}),
    html.P(f"Total Usage: {total_usage}"),
    html.P(f"Current Usage: {daily_usage}")
], style={"font-size": "14px", "font-family": "Arial"}))

                    ]
            )
            markers.append(marker)
        except Exception as e:
            print(f"Error creating marker for {info['location']}: {e}")  # Debugging log

    if not markers:
        print("No valid markers, adding fallback marker.")  # Debugging log
        markers.append(dl.Marker(position=[20.5937, 78.9629], children=[dl.Tooltip("No Data Available")]))

    return markers

# Run the server
if __name__ == '__main__':
    app.run_server(debug=False)
