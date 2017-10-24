# This file is part of the analytic_account_chart_template module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool
from . import account


def register():
    Pool.register(
        account.Account,
        account.AccountTemplate,
        account.CreateChartStart,
        account.CreateChartAccount,
        module='analytic_account_chart_template', type_='model')
    Pool.register(
        account.CreateChart,
        module='analytic_account_chart_template', type_='wizard')
