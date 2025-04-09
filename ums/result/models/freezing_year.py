from odoo import models, fields, api
import requests
import datetime


class FreezingYear(models.Model):
    _name = 'ums.freezing.year'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Freezing Year"
    _order = 'id desc'

    name = fields.Many2one('ums.student', 'Student Name', tracking=True)
    reason = fields.Text('Reason')
    date = fields.Date(string="Date", default=fields.Date.context_today, tracking=True)

    def action_confirm(self):
        for rec in self:
            if rec.name:
                rec.name.state = 'freezing_year'
