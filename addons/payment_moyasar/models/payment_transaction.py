# Copyright 2022 Just Try.

import logging
import pprint

from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.payment_moyasar.const import PAYMENT_STATUS_MAPPING, CALLBACK_URL
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_moyasar.controllers.main import MoyasarController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return Moyasar-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'moyasar':
            return res

        partner_first_name, partner_last_name = payment_utils.split_partner_name(self.partner_name)
        
        return {
            'amount': self.amount,
            'currency_code': self.currency_id.name,
        
            'item_number': self.reference,
            'return_url': CALLBACK_URL,
            'api_url': self.acquirer_id._moyasar_get_api_url(),
            'reference': self.reference,
        }

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Moyasar data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'moyasar':
            return tx

        reference = data.get('reference')
        if not reference:
            raise ValidationError("Moyasar: " + _("Received data with missing merchant reference"))

        tx = self.search([('reference', '=', reference), ('provider', '=', 'moyasar')])
        if not tx:
            raise ValidationError(
                "Moyasar: " + _("No transaction found matching reference %s.", reference)
            )
        return tx


    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Moyasar data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_feedback_data(data)
        if self.provider != 'moyasar':
            return

        txn_id = data.get('id')
        if not all((txn_id)):
            raise ValidationError(
                "Moyasar: " + _(
                    "Missing value for txn_id (%(txn_id)s).",
                    txn_id=txn_id
                )
            )
        self.acquirer_reference = txn_id

        payment_status = data.get('status')
        
        if payment_status in PAYMENT_STATUS_MAPPING['pending']:
            self._set_pending(state_message=data.get('pending_reason'))
        elif payment_status in PAYMENT_STATUS_MAPPING['done']:
            self._set_done()
        elif payment_status in PAYMENT_STATUS_MAPPING['cancel']:
            self._set_canceled()
        else:
            _logger.info("received data with invalid payment status: %s", payment_status)
            self._set_error(
                "Moyasar: " + _("Received data with invalid payment status: %s", payment_status)
            )
            
    