# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import unittest

from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite


class AnalyticAccountChartTemplateTestCase(ModuleTestCase):
    'Test AnalyticAccountChartTemplate module'
    module = 'analytic_account_chart_template'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            AnalyticAccountChartTemplateTestCase))
    return suite
