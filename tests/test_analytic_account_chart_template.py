# This file is part of analytic_account_chart_template.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AnalyticAccountChartTemplateTestCase(ModuleTestCase):
    'Test AnalyticAccountChartTemplate module'
    module = 'analytic_account_chart_template'

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AnalyticAccountChartTemplateTestCase))
    return suite
