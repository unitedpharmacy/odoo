# Copyright 2022 Just Try

{
    'name': 'Moyasar Payment Acquirer',
    'version': '1.0',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Payment Acquirer: Moyasar Implementation',
    'description': """Moyasar Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_moyasar_template.xml',
        'data/payment_acquirer_data.xml',
    ],
    'application': True,
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_moyasar/static/src/js/payment_form.js',
        ],
    },
    'license': 'LGPL-3',
}
