# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from datetime import datetime
from odoo.exceptions import ValidationError


class Registration(models.Model):
    _name = "ums.registration"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "registration students"
    _order = "registration_date desc"

    name = fields.Char(string="Name", readonly=True, default='New')
    student = fields.Many2one('ums.student', 'Student', required=True, tracking=True)
    registration_date = fields.Date(string="Registration Data", default=datetime.now(), required=True, tracking=True)

    college_id = fields.Many2one("ums.college", string="College", required=False)
    class_id = fields.Many2one("ums.class", string='Class', readonly=True)

    academic_year = fields.Many2one("ums.academic.year", string='Academic Year', readonly=True)
    program_id = fields.Many2one("ums.program", string='Program', readonly=True)

    department_id = fields.Many2one('ums.department', string='Department', readonly=True)
    specialist_id = fields.Many2one('ums.specialist', string="Specialist", readonly=True)

    level_id = fields.Many2one("ums.level", string='Level', readonly=True)
    semester_id = fields.Many2one('ums.semester', string="Semester", readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('cancel', 'Canceled')],
        default='draft', string="State")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ums.registration.seq')
        return super(Registration, self).create(vals)

    @api.onchange('student')
    def onchange_student_info(self):
        for rec in self:
            if rec.student:
                if not rec.student.class_id:
                    raise ValidationError(_("student haven't class select class for a student on his profile"))

                elif not rec.student.program:
                    raise ValidationError(_("student haven't program select program for a student on his profile"))
                else:
                    rec.college_id = rec.student.college_id.id
                    rec.class_id = rec.student.class_id.id
                    rec.academic_year = rec.class_id.academic_year

                    rec.program_id = rec.student.program.id

                    rec.department_id = rec.student.department.id
                    rec.specialist_id = rec.student.specialist_id.id

                    rec.level_id = rec.student.level.id
                    rec.semester_id = rec.student.semester_id.id

    def action_confirm(self):
        for rec in self:
            rec.student.registration_status = 'registered'
            rec.state = 'confirm'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
