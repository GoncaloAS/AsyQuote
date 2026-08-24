"""Ownership: knowing another user's quote or client id must not be enough.

Every endpoint here used to look its object up by id or project_key alone, so an
authenticated user could read and edit anyone else's data.
"""
import pytest
from django.urls import reverse

from asyquote.clients.models import Client
from asyquote.projects.models import PricesQuote, Project, SectionQuote

from .factories import make_user, simple_quote

pytestmark = pytest.mark.django_db


@pytest.fixture
def victim():
    user = make_user("victim")
    project, chapter, service = simple_quote(user, quote_number="01")
    return {"user": user, "project": project, "chapter": chapter, "service": service}


@pytest.fixture
def intruder(client):
    user = make_user("intruder")
    client.force_login(user)
    return user


class TestQuoteOwnership:
    def test_cannot_open_the_builder(self, client, victim, intruder):
        url = reverse("edit_project", kwargs={"key": victim["project"].key})
        assert client.get(url).status_code == 404

    def test_cannot_edit_a_field(self, client, victim, intruder):
        line = PricesQuote.objects.filter(project_key=victim["project"].key).first()
        response = client.get(
            reverse("save_quote_data"),
            {
                "action": "description",
                "key": str(victim["project"].key),
                "value": "invadido",
                "section_count": line.section_key,
                "service_count": line.services_key,
                "price_count": line.prices_count,
            },
        )
        assert response.status_code == 404
        line.refresh_from_db()
        assert line.description != "invadido"

    def test_cannot_add_a_row(self, client, victim, intruder):
        before = SectionQuote.objects.filter(project_key=victim["project"].key).count()
        response = client.get(
            reverse("create_fields_quote"),
            {"action": "add-section", "key": str(victim["project"].key),
             "section_count": 1, "service_count": 1, "price_count": 1, "next_id": 2},
        )
        assert response.status_code == 404
        assert SectionQuote.objects.filter(project_key=victim["project"].key).count() == before

    def test_cannot_delete_a_row(self, client, victim, intruder):
        line = PricesQuote.objects.filter(project_key=victim["project"].key).first()
        response = client.get(
            reverse("delete_fields_quote"),
            {"action": "drop-price", "key": str(victim["project"].key),
             "section_count": line.section_key, "service_count": line.services_key,
             "price_count": line.prices_count},
        )
        assert response.status_code == 404
        line.refresh_from_db()
        assert line.visible is True

    def test_cannot_delete_the_quote(self, client, victim, intruder):
        url = reverse("delete_project", kwargs={"key": victim["project"].key})
        assert client.post(url).status_code == 404
        assert Project.objects.filter(pk=victim["project"].pk).exists()

    def test_cannot_rename_the_quote(self, client, victim, intruder):
        url = reverse("update_project", kwargs={"project_id": victim["project"].pk})
        response = client.post(url, {"update_title": "invadido", "update_address": "x", "update_state": "PERDIDO"})
        assert response.status_code == 404
        victim["project"].refresh_from_db()
        assert victim["project"].title != "invadido"

    def test_cannot_search_products_against_it(self, client, victim, intruder):
        response = client.get(reverse("filter_edit_products"), {"key": str(victim["project"].key), "value": "x"})
        assert response.status_code == 404


class TestClientOwnership:
    def test_cannot_edit_someone_elses_client(self, client, victim, intruder):
        target = victim["project"].client
        url = reverse("update_client", kwargs={"client_id": target.pk})
        response = client.post(
            url,
            {"update_name": "invadido", "update_email": "a@b.test", "update_phone": "912000000",
             "update_address": "x", "update_nif": "500000000"},
        )
        assert response.status_code == 404
        target.refresh_from_db()
        assert target.name != "invadido"

    def test_cannot_delete_someone_elses_client(self, client, victim, intruder):
        target = victim["project"].client
        assert client.post(reverse("delete_client", kwargs={"client_id": target.pk})).status_code == 404
        assert Client.objects.filter(pk=target.pk).exists()


class TestAnonymousAccess:
    @pytest.mark.parametrize(
        "name,kwargs",
        [
            ("project_list", {}),
            ("client_list", {}),
            ("products_page", {}),
            ("list_projects_table", {}),
        ],
    )
    def test_pages_require_a_login(self, client, name, kwargs):
        response = client.get(reverse(name, kwargs=kwargs))
        assert response.status_code in (302, 404)
        if response.status_code == 302:
            assert "/login" in response.url or "accounts" in response.url


class TestCatalogueIsSuperuserOnly:
    """The backoffice was hidden in the template but its views accepted anyone."""

    def test_a_normal_user_cannot_create_a_category(self, client):
        from asyquote.products.models import Category

        client.force_login(make_user("normal"))
        response = client.post(reverse("create-category"), {"name_category": "Invadida"})

        assert response.status_code in (302, 403)
        assert not Category.objects.filter(name_category="Invadida").exists()

    def test_a_normal_user_cannot_upload_a_spreadsheet(self, client):
        client.force_login(make_user("normal2"))
        response = client.post(reverse("upload-excel"), {})
        assert response.status_code in (302, 403)
        assert "/login" in response.url if response.status_code == 302 else True
