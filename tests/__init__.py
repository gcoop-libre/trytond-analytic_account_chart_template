# This file is part of analytic_account_chart_template.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

try:
    from trytond.modules.analytic_account.tests.test_analytic_account_chart_template import suite
except ImportError:
    from .test_analytic_account_chart_template import suite

__all__ = ['suite']
