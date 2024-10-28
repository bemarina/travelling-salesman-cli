#! /usr/bin/env python

import geopy
import geopy.location
import geopy.distance
import pandas as pd

from viz.plot_path import driver

import click


def build_dictionary(cities_names):
    # cities=["Boston","Amherst","New York","San Francisco"]
    city_dict = {}
    # loop through the cities list and get the latitudes and longitudes
    for city in cities_names:
        geolocator = geopy.geocoders.Nominatim(user_agent="myApp")
        location = geolocator.geocode(city)
        lat = location.latitude
        long = location.longitude
        city_dict[city] = (lat, long)
    return city_dict


def HKAlgorithm(matrix):
    import math

    distances = matrix
    n = len(distances)  # Number of cities
    dp = [[math.inf] * n for _ in range(1 << n)]
    parent = [[None] * n for _ in range(1 << n)]

    # Base case: starting from city 0
    dp[1][0] = 0

    # Fill DP table
    for mask in range(1 << n):
        for last in range(n):
            if not (mask & (1 << last)):
                continue
            for nexti in range(n):
                if mask & (1 << nexti):
                    continue
                new_mask = mask | (1 << nexti)
                new_dist = dp[mask][last] + distances[last][nexti]
                if new_dist < dp[new_mask][nexti]:
                    dp[new_mask][nexti] = new_dist
                    parent[new_mask][nexti] = last

    # Find the optimal tour and minimum cost
    min_cost = math.inf
    end_city = None
    full_mask = (1 << n) - 1

    for last in range(1, n):
        cost = dp[full_mask][last] + distances[last][0]
        if cost < min_cost:
            min_cost = cost
            end_city = last

    # Reconstruct the optimal tour
    tour = []
    mask = full_mask
    last = end_city
    while mask:
        tour.append(last)
        new_last = parent[mask][last]
        mask ^= 1 << last
        last = new_last
    tour = tour[::-1]
    tour.append(0)  # Add the starting city at the end to complete the loop
    # Print the optimal tour and minimum cost
    print("\nOptimal Tour:", tour)
    print("Minimum Cost:", min_cost)
    return (tour, min_cost)


def build_matrix(city_dict, cities):
    num_cities = len(city_dict)
    mat = [[0] * num_cities for _ in range(num_cities)]
    for i in range(num_cities):
        for j in range(num_cities):
            if i == j:
                mat[i][j] = -1
            # calculated already
            elif mat[i][j] > 0:
                continue
            else:
                # getting the cities names
                city1 = cities[i]
                city2 = cities[j]
                mat[i][j] = round(
                    geopy.distance.distance(city_dict[city1], city_dict[city2]).miles
                )
                mat[j][i] = mat[i][j]
    return mat


def printMat(matrix):
    rows = len(matrix)
    for i in range(rows):
        print(matrix[i])
    return


# convert tour into a dataframe with columns
# visit_order | city_name | latitude | longitude
def build_df_viz(dict_cities, tour_names):
    lst = []
    for i in range(len(tour_names)):
        city = tour_names[i]
        print(city)
        latitude = (dict_cities[city])[0]
        longitude = (dict_cities[city])[1]
        row = [city, latitude, longitude]
        lst.append(row)

    df = pd.DataFrame(lst, columns=["site", "latitude", "longitude"])
    return df


def main(cities_list, image):
    # cities_list = ["Boston", "Amherst", "New York", "San Francisco"]
    d = build_dictionary(cities_list)
    tsp_mat = build_matrix(d, cities_list)
    min_tour, minCost = HKAlgorithm(tsp_mat)
    tourNames = []
    for item in min_tour:
        tourNames.append(cities_list[item])
    print(f"Path of cities: {tourNames}")
    print(f"Distance traveled: {minCost} miles")
    if image != False:
        df_viz = build_df_viz(d, tourNames)
        driver(df_viz)


def build_list_from_cli(*args):
    """Build a list of cities from input"""
    return list(args)


# create click group
@click.group()
def cli():
    """This is a command-line tool that calculates the shortest path between 2-10 cities in the USA.
    This tool can also create an image that shows the calculated path.

      A flag can be added to avoid saving the path into an image. This image is saved by default or when the flag is True.

    Examples:
    ./calculate_route.py tsp_path citiescli "Boston" "San Francisco" "Austin"
    ./calculate_route.py tsp_path citiescli "Boston" "San Francisco" "Austin" --image False
    ./calculate_route.py tsp_path citiescli "Boston" "San Francisco" "Austin" --image True

    """


# create a click command that takes a variable number of arguments of cities passed in and an optional
# flag that specifies whether an image should be built/saved or not
@cli.command("tsp_path")
@click.argument("citiescli", nargs=-1)
@click.option("--image", is_flag=False, flag_value=True, default=True)
def tsp_path_cli(citiescli, image):
    # create a list of cities
    cities_cli_list = build_list_from_cli(*citiescli)
    main(cities_cli_list[1:], image)


if __name__ == "__main__":
    cli()
