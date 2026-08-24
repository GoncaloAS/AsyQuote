"""The margin arithmetic: the numbers the whole product exists to produce."""
from decimal import Decimal

import pytest

from asyquote.projects.models import PricesQuote

from .factories import add_chapter, add_line, add_service, make_quote, make_user, simple_quote

pytestmark = pytest.mark.django_db


class TestLineProfit:
    def test_profit_is_charged_minus_cost(self):
        project, chapter, service = simple_quote(make_user())
        line = PricesQuote.objects.get(project_key=project.key, description="Mão de obra")
        assert line.profit_money == Decimal("50.00")

    def test_percentage_is_profit_over_cost(self):
        project, chapter, service = simple_quote(make_user())
        line = PricesQuote.objects.get(project_key=project.key, description="Mão de obra")
        assert float(line.profit_percentage) == pytest.approx(50.0)

    def test_a_loss_is_negative(self):
        user = make_user()
        project = make_quote(user)
        chapter = add_chapter(project, "Cap")
        service = add_service(project, chapter, "Serv")
        line = add_line(project, chapter, service, cost=200, charged=150)
        assert line.profit_money == Decimal("-50.00")
        assert float(line.profit_percentage) == pytest.approx(-25.0)

    def test_zero_cost_keeps_the_whole_amount_as_profit(self):
        user = make_user()
        project = make_quote(user)
        chapter = add_chapter(project, "Cap")
        service = add_service(project, chapter, "Serv")
        line = add_line(project, chapter, service, cost=0, charged=80)
        assert line.profit_money == Decimal("80.00")

    def test_profit_is_not_computed_until_both_sides_are_known(self):
        user = make_user()
        project = make_quote(user)
        chapter = add_chapter(project, "Cap")
        service = add_service(project, chapter, "Serv")
        line = add_line(project, chapter, service, cost=100, charged=None)
        assert line.profit_money is None
        assert line.profit_percentage is None


class TestQuoteTotals:
    def test_totals_sum_every_line(self):
        project, _, _ = simple_quote(make_user())
        assert project.total_cost() == Decimal("200.00")
        assert project.total_charged() == Decimal("400.00")

    def test_margin_is_derived_from_both_totals(self):
        project, _, _ = simple_quote(make_user())
        assert project.profit_percentage() == pytest.approx(100.0)

    def test_an_empty_quote_is_zero_not_an_error(self):
        project = make_quote(make_user())
        assert project.total_cost() == 0
        assert project.total_charged() == 0
        assert project.profit_percentage() == 0

    def test_a_deleted_line_stops_counting(self):
        """Deleting in the builder hides the row; the totals must follow.

        They used to ignore `visible`, so a deleted line kept moving the project
        total while the Excel export, which does filter on it, disagreed.
        """
        project, chapter, service = simple_quote(make_user())
        line = PricesQuote.objects.get(project_key=project.key, description="Material")
        line.visible = False
        line.save()

        assert project.total_cost() == Decimal("100.00")
        assert project.total_charged() == Decimal("150.00")

    def test_client_value_follows_its_quotes(self):
        user = make_user()
        project, _, _ = simple_quote(user)
        assert project.client.total_charged_amount() == Decimal("400.00")
