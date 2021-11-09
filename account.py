# This file is part of analytic_account_chart_template. The COPYRIGHT file
# at the top level of this repository contains the full copyright notices
# and license terms.


from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta


class Account(metaclass=PoolMeta):
    __name__ = 'analytic_account.account'
    template = fields.Many2One('analytic_account.template', 'Template')


class AccountTemplate(ModelSQL, ModelView):
    'Analytic Account Template'
    __name__ = 'analytic_account.template'
    name = fields.Char('Name', size=None, required=True, select=True)
    code = fields.Char('Code', size=None, select=True)
    type = fields.Selection([
        ('root', 'Root'),
        ('view', 'View'),
        ('normal', 'Normal'),
        ('distribution', 'Distribution'),
        ], 'Type', required=True)
    root = fields.Many2One('analytic_account.template', 'Root', select=True)
    parent = fields.Many2One('analytic_account.template', 'Parent',
        select=True)
    childs = fields.One2Many('analytic_account.template', 'parent',
        'Children')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('opened', 'Opened'),
        ('closed', 'Closed'),
        ], 'State', required=True)
    display_balance = fields.Selection([
        ('debit-credit', 'Debit - Credit'),
        ('credit-debit', 'Credit - Debit'),
        ], 'Display Balance', required=True)
    mandatory = fields.Boolean('Mandatory', states={
            'invisible': Eval('type') != 'root',
            },
        depends=['type'],
        help="Make this account mandatory when filling documents")

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order.insert(0, ('code', 'ASC'))
        cls._order.insert(1, ('name', 'ASC'))

    @staticmethod
    def default_type():
        return 'normal'

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_display_balance():
        return 'credit-debit'

    @staticmethod
    def default_mandatory():
        return False

    def get_rec_name(self, name):
        if self.code:
            return self.code + ' - ' + self.name
        else:
            return self.name

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            ('code',) + tuple(clause[1:]),
            (cls._rec_name,) + tuple(clause[1:]),
            ]

    def _get_account_value(self, account=None):
        '''
        Set the values for account creation.
        '''
        res = {}
        if not account or account.name != self.name:
            res['name'] = self.name
        if not account or account.code != self.code:
            res['code'] = self.code
        if not account or account.type != self.type:
            res['type'] = self.type
        if not account or account.state != self.state:
            res['state'] = self.state
        if not account or account.mandatory != self.mandatory:
            res['mandatory'] = self.mandatory
        if not account or account.template != self:
            res['template'] = self.id
        return res

    def create_account(self, company_id, template2account=None):
        '''
        Create recursively accounts based on template.
        template2account is a dictionary with template id as key and account id
        as value, used to convert template id into account. The dictionary is
        filled with new accounts
        '''
        pool = Pool()
        Account = pool.get('analytic_account.account')
        assert self.parent is None

        if template2account is None:
            template2account = {}

        def create(templates):
            values = []
            created = []
            for template in templates:
                if template.id not in template2account:
                    vals = template._get_account_value()
                    vals['company'] = company_id
                    if template.root:
                        vals['root'] = template2account[template.parent.id]
                    else:
                        vals['root'] = None
                    if template.parent:
                        vals['parent'] = template2account[template.parent.id]
                    else:
                        vals['parent'] = None
                    values.append(vals)
                    created.append(template)

            accounts = Account.create(values)
            for template, account in zip(created, accounts):
                template2account[template.id] = account.id

        childs = [self]
        while childs:
            create(childs)
            childs = sum((c.childs for c in childs), ())


class CreateChartStart(ModelView):
    'Create Chart'
    __name__ = 'analytic_account.create_chart.start'


class CreateChartAccount(ModelView):
    'Create Chart'
    __name__ = 'analytic_account.create_chart.account'
    company = fields.Many2One('company.company', 'Company', required=True)
    account_template = fields.Many2One('analytic_account.template',
            'Account Template', required=True, domain=[('parent', '=', None)])

    @staticmethod
    def default_company():
        return Transaction().context.get('company')


class CreateChart(Wizard):
    'Create Chart'
    __name__ = 'analytic_account.create_chart'
    start = StateView('analytic_account.create_chart.start',
        'analytic_account_chart_template.create_chart_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'account', 'tryton-ok', default=True),
            ])
    account = StateView('analytic_account.create_chart.account',
        'analytic_account_chart_template.create_chart_account_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create', 'create_account', 'tryton-ok', default=True),
            ])
    create_account = StateTransition()

    def transition_create_account(self):
        Config = Pool().get('ir.configuration')

        with Transaction().set_context(language=Config.get_language(),
                company=self.account.company.id):
            account_template = self.account.account_template
            company = self.account.company

            # Create accounts
            template2account = {}
            account_template.create_account(
                company.id,
                template2account=template2account)
        return 'end'
