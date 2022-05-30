# Copyright 2022 Just Try.

import hashlib
import hmac
import json
import logging
import pprint
import moyasar
from datetime import datetime

from odoo import _, http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.payment_moyasar.const import CALLBACK_URL, API_KEY, PUBLISHABLE_API_KEY, AUTHORIZATION

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class MoyasarWebsiteController(WebsiteSale):
    @http.route([
        '/moyasar/'],
        type='http', auth='public', website=True, sitemap=False, csrf=False)
    def moyasar_page(self, **post):
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False
        render_values['reference'] = order.transaction_ids[0].reference
        render_values['PUBLISHABLE_API_KEY'] = PUBLISHABLE_API_KEY
        render_values['CALLBACK_URL'] = CALLBACK_URL
        render_values['AUTHORIZATION'] = AUTHORIZATION
        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')
        
        partner = request.env['res.users'].browse(request.env.uid).partner_id
        cards = request.env['payment.card'].search([('partner_id', '=', partner.id)])
        render_values['cards']=cards
        
        return request.render("payment_moyasar.moyasar_payment_form", render_values)

class MoyasarController(http.Controller):

    @http.route([
        '/payment/moyasar/result/'],
        type='http', auth='public', methods=['GET','POST'], csrf=False)
    def moyasar_result(self, **data):
        _logger.info("beginning DPN with post data:\n%s", pprint.pformat(data))
        
        moyasar.api_key = API_KEY

        response = moyasar.Payment.fetch(data.get('id'))
        data['reference'] = response.description
        if not data:  # The customer has cancelled the payment
            pass  # Redirect them to the status page to browse the draft transaction
        else:
            try:
                notification_data = data #self._validate_pdt_data_authenticity(**data)
            except ValidationError:
                _logger.exception("could not verify the origin of the PDT; discarding it")
            else:
                request.env['payment.transaction'].sudo()._handle_feedback_data(
                    'moyasar', notification_data
                )

        return request.redirect('/payment/status')
    
    @http.route([
        '/payment/moyasar/save/'],
        type='http', auth='public', methods=['POST'], csrf=False)
    def moyasar_save(self, **data):
        partner = request.env['res.users'].browse(request.env.uid).partner_id
        values = {'name':data.get('name'), 'number':data.get('number'), 'year':data.get('year'), 'month':data.get('month'), 'partner_id':partner.id}
        request.env['payment.card'].create(values)
        return
        
    @http.route([
        '/payment/moyasar/delete/'],
        type='http', auth='public', methods=['POST'], csrf=False)
    def moyasar_delete(self, **data):
        request.env['payment.card'].search([('id', '=', data.get('id'))]).unlink()
        return