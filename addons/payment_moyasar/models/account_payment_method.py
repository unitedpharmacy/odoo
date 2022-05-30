# -*- coding: utf-8 -*-
# Copyright 2022 Just Try

from odoo import api, models


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['moyasar'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res
