import pytest
from pytest_django.asserts import assertContains

from django.urls import reverse
from .factories import CheeseFactory, UserFactory, cheese
from ..models import Cheese
from ..views import (CheeseListView, CheeseDetailView, CheeseUpdateView)

@pytest.fixture
def user():
    return UserFactory()

pytestmark = pytest.mark.django_db

def test_good_cheese_list_view_expanded(rf):
    # Determine the URL
    url = reverse("cheeses:list")
    # rf is pytest shortcut to django.test.RequestFactory
    # We generate a request as if from a user accessing the cheese list view
    request = rf.get(url)
    # Call as_view() to make a callable object
    # callable_obj is analogous to a function-based view
    callable_obj = CheeseListView.as_view()
    #Pass in the request into the callable_onj to get an HTTP Response served up by Django
    response = callable_obj(request)
    # Test that the HTTP Response has 'Cheese List' in the HTML
    # and has a 200 response code.
    assertContains(response, 'Cheese List')

def test_good_cheese_list_view(rf):
    # Get the request
    request = rf.get(reverse("cheeses:list"))
    # Use the request to get the response
    response = CheeseListView.as_view()(request)
    # Test that the response is valid
    assertContains(response, 'Cheese List')

def test_good_cheese_detail_view(rf, cheese):
    #Make a request for our new cheese
    url = reverse("cheeses:detail", kwargs={'slug': cheese.slug})
    request = rf.get(url)

    #User the request to get the response
    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    # Test that the response is valid
    assertContains(response, cheese.name)

def test_good_cheese_create_view(client, user):
    # Make the client authenticate
    client.force_login(user)
    # Specify the URL of the view
    url = reverse("cheeses:add")
    # Use the client to make the request
    response = client.get(url)
    # Test that the response is valid
    assert response.status_code == 200

def test_cheese_list_contains_2_chesses(rf):
    # Let's create a couple of cheeses
    cheese1 = CheeseFactory()
    cheese2 = CheeseFactory()
    # Create a request and then a response
    # for a list of cheeses
    request = rf.get(reverse('cheeses:list'))
    response = CheeseListView.as_view()(request)
    # Assert that the response contains both cheese nmames
    # in the templates.
    assertContains(response, cheese1.name)
    assertContains(response, cheese2.name)

def test_detail_contains_cheese_data(rf):
    cheese = CheeseFactory()
    # Make a request for our new cheese
    url = reverse("cheeses:detail", kwargs={'slug': cheese.slug})
    request = rf.get(url)
    # Use the request to get the response
    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    # Let's test our Cheesy Details!
    assertContains(response, cheese.name)
    assertContains(response, cheese.get_firmness_display())
    assertContains(response, cheese.country_of_origin.name)

def test_cheese_create_form_valid(client, user):
    # Authenticate the user
    client.force_login(user)
    # Submit the cheese add form
    form_data = {
        "name": "Paski Sir",
        "description": "A salty hard cheese",
        "firmness": Cheese.Firmness.HARD,
    }
    url = reverse("cheeses:add")
    response = client.post(url, form_data)

    # Get the cheese based on the name
    cheese = Cheese.objects.get(name="Paski Sir")

    # Test that the cheese matches our form
    assert cheese.description == "A salty hard cheese"
    assert cheese.firmness == Cheese.Firmness.HARD
    assert cheese.creator == user

def test_cheese_create_correct_title(client, user):
    """ Page title for CheeseCreateView should be Add Cheese. """
    # Authenticate the user
    client.force_login(user)
    # Call the cheese add view
    response = client.get(reverse("cheeses:add"))
    # Confirm that 'Add Cheese' is in the render HTML
    assertContains(response, "Add Cheese")


def test_cheese_update_correct_title(client, user, cheese):
    """ Page title for CheeseUpdateView should be Add Cheese. """
    # Authenticate the user
    client.force_login(user)
    # Get the URL
    url = reverse("cheeses:update", kwargs={"slug": cheese.slug})
    # Call the cheese add view
    response = client.get(url)
    # Confirm that 'Update Cheese' is in the render HTML
    assertContains(response, "Update Cheese")

def test_cheese_update(client, user, cheese):
    """  POST request to CheeseUpdateView updates a cheese and redirects. """
    # Authenticate user
    client.force_login(user)
    # Make a data request
    form_data = {
        "name": cheese.name,
        "description": "Something new",
        "firmness": cheese.firmness,
    }

    url = reverse("cheeses:update", kwargs={"slug": cheese.slug})
    response = client.post(url, form_data)

    # Check that the cheese has been changed
    cheese.refresh_from_db()
    assert cheese.description == form_data["description"]