"""Helpers for building a quote in tests."""
from decimal import Decimal

from django.contrib.auth import get_user_model

from asyquote.clients.models import Client
from asyquote.projects.models import PricesQuote, Project, SectionQuote, ServicesQuote


def make_user(username="tester"):
    return get_user_model().objects.create_user(username=username, email=f"{username}@example.test", password="pw")


def make_client(user, name="Cliente Teste", nif="500000000"):
    return Client.objects.create(
        user=user, name=name, email="cliente@example.test", phone="912000000", address="Rua 1", nif=nif
    )


def make_quote(user, quote_number="01", state="EM ESPERA"):
    return Project.objects.create(
        user=user,
        quote_number=quote_number,
        title="Obra de teste",
        address="Rua de teste",
        client=make_client(user, nif=f"5000000{quote_number[-2:]}"),
        state=state,
    )


def add_chapter(project, name, position=1):
    return SectionQuote.objects.create(project_key=project.key, name=name, section_count=position)


def add_service(project, chapter, name, quantity="1 un", position=1):
    return ServicesQuote.objects.create(
        project_key=project.key,
        name=name,
        quantity=quantity,
        section_key=chapter.section_count,
        service_count=position,
    )


def add_line(project, chapter, service, cost, charged, description="Linha", position=1):
    return PricesQuote.objects.create(
        project_key=project.key,
        description=description,
        cost=Decimal(str(cost)) if cost is not None else None,
        charged=Decimal(str(charged)) if charged is not None else None,
        section_key=chapter.section_count,
        services_key=service.service_count,
        prices_count=position,
    )


def simple_quote(user, quote_number="01"):
    """A quote with one chapter, one service and two priced lines."""
    project = make_quote(user, quote_number=quote_number)
    chapter = add_chapter(project, "Demolições")
    service = add_service(project, chapter, "Remoção de pavimento", quantity="10 m2")
    add_line(project, chapter, service, cost=100, charged=150, description="Mão de obra", position=1)
    add_line(project, chapter, service, cost=100, charged=250, description="Material", position=2)
    return project, chapter, service
