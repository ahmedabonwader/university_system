from odoo import models, fields, api, _


class Division(models.Model):
    _name = "ums.division"
    _description = "Subject result division (A, B, C)"

    name = fields.Char('Name', required=True, help='Division of the standard')
    english_name = fields.Char('English Name', required=True, help='Division of the standard')
    maximum_marks = fields.Integer("Maximum marks", required=True, help='Maximum marks of the subject can get')
    minimum_marks = fields.Integer("Minimum marks", required=True, help='''Required minimum
                                                     marks of the subject''')
    college_id = fields.Many2one('ums.college', required=True, string="College Name")
    is_fail = fields.Boolean(string="Is Fail")

    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}