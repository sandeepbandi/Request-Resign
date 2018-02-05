# -*- coding: utf-8 -*-
from odoo import http

# class VertipleEmployee(http.Controller):
#     @http.route('/vertiple_employee/vertiple_employee/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vertiple_employee/vertiple_employee/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vertiple_employee.listing', {
#             'root': '/vertiple_employee/vertiple_employee',
#             'objects': http.request.env['vertiple_employee.vertiple_employee'].search([]),
#         })

#     @http.route('/vertiple_employee/vertiple_employee/objects/<model("vertiple_employee.vertiple_employee"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vertiple_employee.object', {
#             'object': obj
#         })