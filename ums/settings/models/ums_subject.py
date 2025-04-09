from odoo import models, fields, api, _
from datetime import datetime
from dateutil import relativedelta

class Subject(models.Model):

    _name = "ums.subject"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Subjects"

    name = fields.Char('Name', required=True, help='Subject name')
    english_name = fields.Char('English Name', required=False, help='Subject name')
    weight = fields.Float(string="Weight", tracking=True, required=False)
    hours = fields.Float(string="Hours", tracking=True, required=False)
    lab = fields.Boolean(string="Lab", tracking=True)
    college_id = fields.Many2one('ums.college', required=True,string="College Name")
    
    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}