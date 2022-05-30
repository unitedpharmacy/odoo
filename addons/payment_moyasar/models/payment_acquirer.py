# Copyright 2022 Just Try.

import logging
import uuid

import requests
from werkzeug.urls import url_join, url_encode

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.payment_moyasar.const import MOYASAR_PAGE_URL
from odoo.addons.payment_moyasar.controllers.main import MoyasarController

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('moyasar', "Moyasar")], ondelete={'moyasar': 'set default'})

    def _moyasar_get_api_url(self):
        """ Return the API URL according to the acquirer state.

        Note: self.ensure_one()

        :return: The API URL
        :rtype: str
        """
        self.ensure_one()

        return MOYASAR_PAGE_URL

    def _moyasar_make_request(self, endpoint, payload=None, method='POST', offline=False):
        """ Make a request to Moyasar API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request
        :param dict payload: The payload of the request
        :param str method: The HTTP method of the request
        :param bool offline: Whether the operation of the transaction being processed is 'offline'
        :return The JSON-formatted content of the response
        :rtype: dict
        :raise: ValidationError if an HTTP error occurs
        """
        self.ensure_one()

        url = MOYASAR_PAGE_URL
        headers = {}
        try:
            response = requests.request(method, url, data=payload, headers=headers, timeout=60)
            # Moyasar can send 4XX errors for payment failures (not only for badly-formed requests).
            # Check if an error code is present in the response content and raise only if not.
            # See https://moyasar.com/docs/error-codes.
            # If the request originates from an offline operation, don't raise and return the resp.
            if not response.ok \
                    and not offline \
                    and 400 <= response.status_code < 500 \
                    and response.json().get('error'):  # The 'code' entry is sometimes missing
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    _logger.exception("invalid API request at %s with data %s", url, payload)
                    error_msg = response.json().get('error', {}).get('message', '')
                    raise ValidationError(
                        "Moyasar: " + _(
                            "The communication with the API failed.\n"
                            "Moyasar gave us the following info about the problem:\n'%s'", error_msg
                        )
                    )
        except requests.exceptions.ConnectionError:
            _logger.exception("unable to reach endpoint at %s", url)
            raise ValidationError("Moyasar: " + _("Could not establish the connection to the API."))
        return response.json()


    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'moyasar':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_moyasar.payment_method_moyasar').id

 