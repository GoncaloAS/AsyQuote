"""Client creation: the NIF rules and the delete guard."""
import json

import pytest
from django.urls import reverse

from asyquote.clients.models import Client
from asyquote.projects.tests.factories import make_user, simple_quote

pytestmark = pytest.mark.django_db

FORM = {
    "name": "Construções Teste, Lda.",
    "email": "geral@teste.example",
    "phone": "912000000",
    "address": "Rua de Teste 1, Porto",
    "nif": "500000000",
}


def post_client(client, **overrides):
    response = client.post(reverse("create_client"), {**FORM, **overrides})
    return response, json.loads(response.content)


class TestNifValidation:
    def test_a_well_formed_nif_is_accepted(self, client):
        client.force_login(make_user())
        _, body = post_client(client)
        assert "success" in body
        assert Client.objects.filter(nif="500000000").exists()

    def test_too_few_digits_is_refused(self, client):
        client.force_login(make_user())
        _, body = post_client(client, nif="12345")
        assert body["error"] == "O NIF deve ter exatamente 9 dígitos."
        assert not Client.objects.exists()

    def test_too_many_digits_is_refused_by_the_field_itself(self, client):
        """max_length=9 on the model fires before the view's own check, so this
        one comes back as a field error rather than the custom message."""
        client.force_login(make_user())
        _, body = post_client(client, nif="1234567890")
        assert "nif" in body["error"]
        assert not Client.objects.exists()

    def test_letters_are_rejected(self, client):
        client.force_login(make_user())
        _, body = post_client(client, nif="50000000A")
        assert body["error"] == "O NIF só deve conter dígitos."
        assert not Client.objects.exists()

    def test_the_same_nif_twice_is_refused(self, client):
        client.force_login(make_user())
        post_client(client)
        _, body = post_client(client, name="Outro nome")
        assert "já existe" in body["error"]
        assert Client.objects.filter(nif="500000000").count() == 1

    def test_two_users_may_each_have_the_same_nif(self, client):
        """The uniqueness is per owner, not global."""
        first = make_user("first")
        client.force_login(first)
        post_client(client)

        client.force_login(make_user("second"))
        _, body = post_client(client)

        assert "success" in body
        assert Client.objects.filter(nif="500000000").count() == 2

    def test_a_client_belongs_to_whoever_created_it(self, client):
        user = make_user()
        client.force_login(user)
        post_client(client)
        assert Client.objects.get(nif="500000000").user == user


class TestDeleteGuard:
    def test_a_client_with_quotes_cannot_be_deleted(self, client):
        user = make_user()
        project, _, _ = simple_quote(user)
        client.force_login(user)

        client.post(reverse("delete_client", kwargs={"client_id": project.client.pk}))

        assert Client.objects.filter(pk=project.client.pk).exists()

    def test_a_client_without_quotes_can(self, client):
        user = make_user()
        client.force_login(user)
        post_client(client)
        target = Client.objects.get(nif="500000000")

        client.post(reverse("delete_client", kwargs={"client_id": target.pk}))

        assert not Client.objects.filter(pk=target.pk).exists()
