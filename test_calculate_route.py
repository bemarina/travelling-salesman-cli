from pytest import fixture
from calculate_route import *


@fixture
# hardcode a list of cities
def cities():
    cities_list = ["Boston", "Amherst", "New York", "San Francisco"]
    return cities_list


@fixture
def cities_dictionary(cities):
    cities_d = build_dictionary(cities)
    #     cities_mat_fix = build_matrix(cities_d, cities)
    return cities_d


def test_build_dictionary(cities):
    d = build_dictionary(cities)
    assert len(d) == 4


# testing the matrix is built correctly
def test_build_matrix(cities):
    cities_d = build_dictionary(cities)
    cities_matrix = build_matrix(cities_d, cities)
    assert (len(cities_matrix[0])) == 4





# TO DO: Add tests to test the cli
