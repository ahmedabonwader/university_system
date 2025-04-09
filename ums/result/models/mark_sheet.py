# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Marksheet(models.Model):
    _name = 'ums.result.marksheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Students marks in subject result"

    name = fields.Char(string="Result Name")

    college = fields.Many2one("ums.college", string="College")
    department = fields.Many2one("ums.department", string="Department")
    level = fields.Many2one("ums.level", string="Level")
    academic_year = fields.Many2one("ums.academic.year", string="Academic Year")
    program = fields.Selection([("master", "Master"), ("bsc", "Bsc"), ("deploma", "Deploma")], default="bsc",
                               required=True, string="program")

    subject = fields.Many2one("ums.subject", string="Subject")
    pass_mark = fields.Float("Pass Mark")

    confirmed_date = fields.Date(string="Date", required=True)
    state = fields.Selection([("draft", "Draft"), ("confirm", "Confirmed")], default="draft", string="status")

    students_list = fields.One2many("ums.result.studentlist", "sheet_id", string="Students list")

    def set_to_confirm(self):
        self.state = "confirm"

    def set_to_draft(self):
        self.state = "draft"

    @api.onchange('college', 'department', 'level', 'academic_year', 'program')
    def change_student_list(self):
        for rec in self:
            if rec.college and rec.department and rec.level and rec.academic_year and rec.program:

                studentids = self.env['ums.student'].search([('college', '=', rec.college),
                                                             ('department', '=', rec.department),
                                                             ('level', '=', rec.level),
                                                             ('academic_year', '=', rec.academic_year),
                                                             ('program', '=', rec.program)])

                # need work , use delete instant write
                rec.write("students_list", False)

                studentlist_obj = self.env['ums.result.studentlist']

                for student in studentids:
                    vals = {'sheet_id': rec.id,
                            'student': student.id,
                            }
                    studentlist_obj.create(vals)


class StudentsMarks(models.Model):
    _name = 'ums.result.studentlist'
    _description = "student list with marks in a subject"

    sheet_id = fields.Many2one("ums.result.marksheet", string="Result #")

    student = fields.Many2one("ums.student", string="Student")
    degree = fields.Float("Degree")

    degree_letter = fields.Char("Degree in letter")

    note = fields.Char("Note")
