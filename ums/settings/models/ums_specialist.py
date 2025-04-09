# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, models, fields


class Specialist(models.Model):
    _name = "ums.specialist"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Specialist"

    name = fields.Char(string="Name", required=True)
    english_name = fields.Char(string="English Name", required=False)
    code = fields.Char(string="Code", required=False)
    department_id = fields.Many2one('ums.department', 'Department')
    college_id = fields.Many2one('ums.college', string="College", required=True)
    is_department = fields.Boolean(string="Is Department ?", store=True,)

    @api.onchange('college_id')
    def onchange_is_department(self):
        for rec in self:
            if rec.college_id.department == True:
                rec.is_department = True
            else:
                rec.is_department = False
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}
