# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import datetime


class Portable(models.Model):
    _name = "ums.portable"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "University Portable"

    name = fields.Many2one('ums.student', 'Student Name')
    exam_name = fields.Char(string="Exam Name")
    class_id = fields.Many2one('ums.class', 'Class', required=True, tracking=True)
    program_id = fields.Many2one(related='result_id.program', string='Program')
    level_id = fields.Many2one(related='result_id.level', string='Level')
    academic_year = fields.Many2one(related='result_id.academic_year', string='Academic Year', required=True,
                                    tracking=True)
    college_id = fields.Many2one('ums.college', string="College", required=True, tracking=True)
    specialist_id = fields.Many2one('ums.specialist', string="Specialist", tracking=True)
    portable_ids = fields.One2many('first.portable.line', 'portable_id', 'Line')
    portable_second_ids = fields.One2many('second.portable.line', 'portable_id', 'Line')
    date = fields.Date(string='Date')
    department = fields.Many2one("ums.department", string="Department")
    firest_semstar = fields.Many2one('ums.semester', 'First Semstar')
    second_semstar = fields.Many2one('ums.semester', 'Second Semstar')
    result_id = fields.Many2one('ums.result', 'Result')
    is_department = fields.Boolean(string="Is Department ?", store=True)
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True)

    @api.onchange('college_id')
    def onchange_is_department(self):
        for rec in self:
            if rec.college_id.department == True:
                rec.is_department = True
            else:
                rec.is_department = False

    @api.onchange('college_id')
    def onchange_is_specialist(self):
        for rec in self:
            if rec.college_id.specialist == True:
                rec.is_specialist = True
            else:
                rec.is_specialist = False

    @api.onchange('college_id')
    def onchange_college_id(self):
        for rec in self:
            return {'domain': {'specialist_id': [('college_id', '=', rec.college_id.id)]}}

    @api.onchange('specialist_id')
    def onchange_specialist_id(self):
        for rec in self:
            return {'domain': {'class_id': [('specialist_id', '=', rec.specialist_id.id)]}}


class FirstPortableLine(models.Model):
    _name = 'first.portable.line'
    _description = 'First Portable Line'

    portable_id = fields.Many2one('ums.portable', 'Portable')
    student_id = fields.Many2one('ums.student', 'Student')
    subject_id = fields.Many2one('ums.subject', 'Subject')
    pass_or_fail = fields.Boolean(string='Pass?', readonly=True)
    mark_scored = fields.Float(string='Mark')
    degree_letter = fields.Many2one("ums.division", string="Degree in letter")
    sub_first_id = fields.Many2one('result.subject.line', string="Supplement ID")
    sub_first_regional_id = fields.Many2one('result.subject.line', string="Regional ID")


class SecondPortableLine(models.Model):
    _name = 'second.portable.line'
    _description = 'Second Portable Line'

    portable_id = fields.Many2one('ums.portable', 'Portable')
    student_id = fields.Many2one('ums.student', 'Student')
    subject_id = fields.Many2one('ums.subject', 'Subject')
    pass_or_fail = fields.Boolean(string='Pass?', readonly=True)
    mark_scored = fields.Float(string='Mark')
    degree_letter = fields.Many2one("ums.division", string="Degree in letter")
    sub_second_id = fields.Many2one('result.subject.line', string="Supplement ID")
    sub_second_regional_id = fields.Many2one('result.subject.line', string="Regional ID")
