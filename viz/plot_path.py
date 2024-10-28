from geopy.distance import geodesic
import pandas as pd
import folium
from typing import Tuple
import io
from PIL import Image

_Location = Tuple[float, float]


def ellipsoidal_distance(point1: _Location, point2: _Location) -> float:
    """Calculate ellipsoidal distance (in meters) between point1 and
    point2 where each point is represented as a tuple (lat, lon)"""
    return geodesic(point1, point2).meters


def _make_route_segments_df(df_route: pd.DataFrame) -> pd.DataFrame:
    """Given a dataframe whose rows are ordered stops in a route,
    and where the index has integers representing the visit order of those
    stops, return a dataframe having new columns with the information of
    each stop's next site"""
    df_route_segments = df_route.join(
        df_route.shift(-1), rsuffix="_next"  # map each stop to its next
    ).dropna()
    df_route_segments["distance_seg"] = df_route_segments.apply(
        lambda stop: ellipsoidal_distance(
            (stop.latitude, stop.longitude), (stop.latitude_next, stop.longitude_next)
        ),
        axis=1,
    )
    return df_route_segments


def plot_route_on_map(df_route: pd.DataFrame) -> folium.Map:
    """Takes a dataframe of a route and displays it on a map, adding
    a marker for each stop and a line for each pair of consecutive
    stops"""
    df_route_segments = _make_route_segments_df(df_route)

    # create empty map
    map_route = folium.Map(location=[30, -102], zoom_start=4)

    for stop in df_route_segments.itertuples():
        initial_stop = stop.Index == 0
        # marker for current stop
        icon = folium.Icon(
            icon="home" if initial_stop else "info-sign",
            color="cadetblue" if initial_stop else "red",
        )
        marker = folium.Marker(
            location=(stop.latitude, stop.longitude),
            icon=icon,
            tooltip=f"<b>Name</b>: {stop.site} <br>"
            + f"<b>Stop number</b>: {stop.Index} <br>",
        )
        # line for the route segment connecting current to next stop
        line = folium.PolyLine(
            locations=[
                (stop.latitude, stop.longitude),
                (stop.latitude_next, stop.longitude_next),
            ],
            # add to each line its start, end, and distance
            tooltip=f"<b>From</b>: {stop.site} <br>"
            + f"<b>To</b>: {stop.site_next} <br>"
            + f"<b>Distance</b>: {stop.distance_seg:.0f} m",
        )
        # add elements to the map
        marker.add_to(map_route)
        line.add_to(map_route)

        # check if first site's name and location coincide with last's?
        first_stop = df_route.iloc[0][["site", "latitude", "longitude"]]
        last_stop = df_route.iloc[-1][["site", "latitude", "longitude"]]
        is_closed_tour = (first_stop == last_stop).all()

    # When for loop ends, the marker for the last stop is missing
    # (**unless the route is closed**). If the route is not closed,
    # we add it now using the "next" columns of the last row
    if not is_closed_tour:
        folium.Marker(
            location=(last_stop.latitude_next, last_stop.longitude_next),
            tooltip=f"<b>Name</b>: {last_stop.site_next} <br>"
            + f"<b>Stop number</b>: {last_stop.Index + 1} <br>",
            icon=folium.Icon(icon="info-sign", color="red"),
        ).add_to(map_route)

    return map_route


def build_map(df_path):
    map_usa = folium.Map(location=[30, -102], zoom_start=3)
    # Add markers to each site, including the name of the site in the tooltip
    for site in df_path.itertuples():
        marker = folium.Marker(
            location=(site.latitude, site.longitude), tooltip=site.site
        )
        marker.add_to(map_usa)

    # Create another dataframe that shows the order (index number) in which the cities are visited
    df_route = df_path.copy()
    df_route.index.name = "visit_order"

    # Add lines connecting consecutive segments
    # df_route_segments = df_route.join(
    #    df_route.shift(-1), rsuffix="_next"  # map each stop to its next stop
    # ).dropna()  # last stop has no "next one", so drop it
    df_route_closed = pd.concat([df_route, df_route.head(1)], ignore_index=True)
    df_route_closed.index.name = df_route.index.name

    myMap = plot_route_on_map(df_route_closed)
    return myMap


def save_img(map_path):
    img_data = map_path._to_png(5)
    img = Image.open(io.BytesIO(img_data))
    img.save("tsp-path-image.png")
    return


# this has to take as input the map and whether or not a viz is desired
# pylint: disable = no-value-for-parameter
def driver(df_path):
    # df_path = pd.DataFrame(
    # [
    #     ["Boston", 42.355433, -71.060511],
    #     ["New York", 40.712728, -74.006015],
    #     ["San Francisco", 37.779259, -122.419329],
    #     ["Amherst", 42.373195, -72.519876],
    #     ["Boston", 42.355433, -71.06051],
    # ],
    # columns=pd.Index(["site", "latitude", "longitude"], name="USA"),
    # )
    tsp_map = build_map(df_path)
    save_img(tsp_map)


if __name__ == "__main__":
    driver()
