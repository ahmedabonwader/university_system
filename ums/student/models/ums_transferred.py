import datetime
from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from dateutil import relativedelta
from datetime import date

class TransferredStudent(models.Model):
    _name = 'ums.transferred'
    _description = "Ums Transferred"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _rec_name = "student"
    
    student = fields.Many2one('ums.student', string="Student Name")
    college_id = fields.Many2one("ums.college", string="College")
    department = fields.Many2one("ums.department", string="Department")
    program = fields.Many2one('ums.program', 'Program')
    specialist_id = fields.Many2one('ums.specialist', string="Specialist")
    transfer_lins_ids = fields.One2many('ums.transfer.line', 'transfer_id', string="Transferred Line")
    ref = fields.Char(string='Reference', tracking=True)
    
    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('ums.transferred')
        return super(TransferredStudent, self).create(vals)

    def write(self, vals):
        if not self.ref:
            vals['ref'] = self.env['ir.sequence'].next_by_code('ums.transferred')
        return super(TransferredStudent, self).write(vals)
    
    
class TransferLine(models.Model):
    _name = "ums.transfer.line"
    _description = "Transfer Line"
    
    transfer_id = fields.Many2one('ums.transferred')
    semester_id = fields.Many2one('ums.semester', string="Semester")
    subject = fields.Many2many('ums.subject', string="Subject")
    level = fields.Many2one("ums.level", string="Level")
