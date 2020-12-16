import pytest
from ..functions.search import search
from ..functions.channels import channels_create
from .helpers import create_mock_user, clear_dbs, generate_messages


@pytest.fixture(autouse=True)
def run_before_tests():
    clear_dbs()
    yield


reg_data = {"query_str": "anyquery"}

################################################################################
#   search - Given a query string, return a collection of messages that        #
#            match the query                                                   #
################################################################################


def test_search_empty_strings():
    user = create_mock_user()
    query_str = ""
    results = search(user["token"], query_str)
    assert len(results["messages"]) == 0


def test_search_no_match():
    user = create_mock_user()
    channel_id = channels_create(user["token"], "anyname", is_public=False)
    generate_messages(user["token"], channel_id, 50)
    results = search(user["token"], "queerry")
    assert len(results["messages"]) == 0


def test_search_no_channels():
    user = create_mock_user()
    results = search(user["token"], "any")
    assert len(results["messages"]) == 0


def test_search_valid():
    user = create_mock_user()
    channel_id = channels_create(user["token"], "anyname", is_public=False)
    msgs = generate_messages(user["token"], channel_id, 50)
    query = msgs[0]
    results = search(user["token"], query)
    assert len(results["messages"]) == 1
