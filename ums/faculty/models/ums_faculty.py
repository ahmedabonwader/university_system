# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, models, fields


class Faculty(models.Model):
    _name = "ums.faculty"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Faculties records"

    name = fields.Char(string="Full Name", tracking=True)
    last_name = fields.Char(string='Last Name', tracking=True)

    degree = fields.Char(string="Degree")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string='Gender', required=True,
        tracking=True)
    blood_group = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'), ('o-', 'O-'),
         ('ab-', 'AB-'), ('ab+', 'AB+')],
        string='Blood Group', required=True,
        tracking=True)
    age = fields.Integer(string="Age", compute="_compute_age")
    date_of_birth = fields.Date(string="Date_Of_Birth", required=True, tracking=True)

    image = fields.Binary(string='Image',
                          attachment=True, )
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone", required=True)
    mobile = fields.Char(string="Mobile")
    subject_lines_id = fields.Many2one('ums.subject', 'Subject')

    @api.depends("date_of_birth")
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 1
