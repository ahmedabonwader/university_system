from odoo import models, fields, api, _
from datetime import date
from odoo.osv import expression

#import hijri_converter


class Student(models.Model):
    _name = 'ums.student'
    _description = "Students records"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    def _get_default_college(self):
        users = self.env.user
        if len(users.collage_ids) == 1:
            return users.collage_ids[0]
        elif len(users.collage_ids) > 1:
            return self.env['ums.college'].search([('id', 'in', [item.id for item in users.collage_ids])])
        return False

    def _get_user_college(self):
        user = self.env.user
        college_ids = user.collage_ids.ids
        return [('id', 'in', college_ids)]

    name = fields.Char("Student Name", tracking=True)
    english_name = fields.Char("Student Name", tracking=True)
    student_number = fields.Char("Student Number", tracking=True)
    age = fields.Integer(string="Age", compute="_compute_age")
    booking_date = fields.Date(string="Booking Date", default=fields.Date.context_today)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", tracking=True)
    date_of_birth = fields.Date(string="Date_Of_Birth", tracking=True)
    blood_group = fields.Selection([('a+', 'A+'),
                                    ('a-', 'A-'),
                                    ('b+', 'B+'),
                                    ('o+', 'O+'),
                                    ('o-', 'O-'),
                                    ('ab-', 'AB-'),
                                    ('ab+', 'AB+')],
                                   string='Blood Group', tracking=True)
    nationality_id = fields.Many2one('ums.nationality', string='Nationality', ondelete='restrict', tracking=True)
    mother_name = fields.Char(string="Mother Name", tracking=True)
    first_name = fields.Char(string='First Name', tracking=True)
    first_english_name = fields.Char(string='First English Name', tracking=True)
    middle_name = fields.Char(string='Middle Name', tracking=True)
    middle_english_name = fields.Char(string='Middle English Name', tracking=True)
    sur_name = fields.Char(string='Surname', tracking=True)
    sur_english_name = fields.Char(string='English Surname', tracking=True)
    last_name = fields.Char(string='Last Name', tracking=True)
    last_english_name = fields.Char(string='Last English Name', tracking=True)
    image = fields.Binary(string="Image", attachment=True)
    ref = fields.Char(string='Reference', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    mobile = fields.Char(string="Mobile")
    admission_date = fields.Datetime(string="Admission Date", default=fields.Datetime.now, required=True)
    college_id = fields.Many2one("ums.college", domain=_get_user_college, string="College",
                                 default=_get_default_college)
    department = fields.Many2one("ums.department", domain="[('college_id','=',college_id)]", string="Department")
    program = fields.Many2one('ums.program', domain="[('college','=',college_id)]", string='Program')
    specialist_id = fields.Many2one('ums.specialist', domain="[('college_id','=',college_id)]", string="Specialist")
    class_id = fields.Many2one('ums.class', domain="[('college_id','=',college_id)]", string="Class")
    level = fields.Many2one("ums.level", domain="[('college_id','=',college_id)]", string="Level")
    academic_year = fields.Many2one(related='class_id.academic_year', string="Academic Year")
    semester_id = fields.Many2one('ums.semester', domain="[('college_id','=',college_id)]", string="Semester")
    final_result = fields.Float(string="Final Result")
    final_result_letter = fields.Many2one('ums.letter.degree', domain="[('college_id','=',college_id)]",
                                          string="Final Result Letter")
    grade_date = fields.Date(string="Grade Date")
    student_status = fields.Many2one('ums.student.status', 'Student Status')
    hijri_grade_date = fields.Char(string="Grade Date (Hijri)", compute='_compute_hijri_grade_date', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('study', 'On Study'),
        ('graduation', 'Graduation'),
        ('freezing_year', 'Freezing Year'),
        ('quitted', 'Quitted'),
        ('fired', 'Fired'),
        ('old', 'Old'), ], string="Status", default='draft')
    registration_status = fields.Selection([
        ('registered', 'Registered'),
        ('unregistered', 'Un registered')], string="registration Status", default='unregistered')

    # student_type = fields.Selection([
    study_status = fields.Selection([
        ('regular', 'Regular Student'),
        ('repeat', 'Repeat'),
        ('external_1', 'EX 1'),
        ('external_2', 'EX 2'),
        ('external_3', 'EX 3')], string="Study Status", )

    result_count = fields.Integer(string="Result Count", compute='_compute_result_count', tracking=True)
    user = fields.Many2one('res.users', string="User", tracking=True, default=lambda self: self.env.user.id)
    std_note_ids = fields.One2many('student.note.line', 'student_id', string="Note Lines")
    transferred = fields.Boolean(string="Transferred")
    is_final_result_letter = fields.Boolean(string="Is Final Result Letter ?", store=True)
    is_department = fields.Boolean(string="Is Department ?", store=True)
    is_specialist = fields.Boolean(string="Is Specialist ?", store=True)

    @api.onchange('transferred', 'study_status')
    def onchange_student_status(self):
        for rec in self:
            if rec.transferred:
                rec.student_status = self.env['ums.student.status'].search([('code', '=', '4')], limit=1)
            elif rec.study_status == 'external_1':
                rec.student_status = self.env['ums.student.status'].search([('code', '=', '1')], limit=1)
            elif rec.study_status == 'external_2':
                rec.student_status = self.env['ums.student.status'].search([('code', '=', '2')], limit=1)
            elif rec.study_status == 'external_3':
                rec.student_status = self.env['ums.student.status'].search([('code', '=', '3')], limit=1)
            elif rec.study_status == 'regular' or rec.study_status == 'repeat':
                rec.student_status = ' '

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

    @api.depends('grade_date')
    def _compute_hijri_grade_date(self):
        for record in self:
            if record.grade_date:
                hijri_date = hijri_converter.Gregorian(record.grade_date.year, record.grade_date.month,
                                                       record.grade_date.day).to_hijri()
                record.hijri_grade_date = f"{hijri_date.day}/{hijri_date.month_name('ar')}/{hijri_date.year}"
            else:
                record.hijri_grade_date = False

    @api.onchange('college_id')
    def onchange_is_final_result_letter(self):
        for rec in self:
            if rec.college_id.is_final_result_letter == True:
                rec.is_final_result_letter = True
            else:
                rec.is_final_result_letter = False

    def name_get(self):
        return [(student.id, '[%s] %s' % (student.student_number, student.name)) for student in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('student_number', '=ilike', name), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def _compute_result_count(self):
        for rec in self:
            result_count = self.env['ums.result.history'].search_count([('name', '=', rec.id)])
            rec.result_count = result_count

    # This Function of Smart Button Result Count
    def action_result(self):
        for rec in self:
            domain = [('name', '=', rec.id)]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Result History',
                'res_model': 'ums.result.history',
                'domain': domain,
                'view_mode': 'tree,form',
                'target': 'current',

            }

    def action_confirm(self):
        for rec in self:
            if rec.transferred:
                action = self.env.ref('ums.transferred_wizard_action').read()[0]
                return action
            else:

                rec.state = 'study'

    def action_back(self):
        for rec in self:
            rec.state = 'draft'

    # @api.onchange('grade_date')
    # def onchange_college_id(self):
    #     for rec in self:
    #         rec.hijri_grade_date = Gregorian(rec.grade_date.year, rec.grade_date.month, rec.grade_date.day).to_hijri()

    @api.onchange('department', 'college_id')
    def onchange_specialist_id(self):
        for rec in self:
            if rec.department:
                return {'domain': {'specialist_id': [('department_id', '=', rec.department.id)]}}
            else:
                return {'domain': {'specialist_id': [('college_id', '=', rec.college_id.id)]}}

    @api.onchange('college_id')
    def onchange_college_id_program(self):
        for rec in self:
            return {'domain': {'program': [('college', '=', rec.college_id.id)]}}

    @api.onchange('program', 'level', 'semester_id', 'college_id')
    def onchange_college_id_class_id(self):
        for rec in self:
            return {'domain': {'class_id': [('program_id', '=', rec.program.id), ('level', '=', rec.level.id),
                                            ('college_id', '=', rec.college_id.id),
                                            ('semester_id', '=', rec.semester_id.id)]}}

    @api.onchange('first_name', 'middle_name', 'sur_name', 'last_name')
    def _onchange_fullname(self):
        self.name = "{} {} {} {}".format(
            self.first_name or '',
            self.middle_name or '',
            self.sur_name or '',
            self.last_name or ''
        ).strip()

    @api.onchange('first_english_name', 'middle_english_name', 'sur_english_name', 'last_english_name')
    def _onchange_name(self):
        self.english_name = "{} {} {} {}".format(
            self.first_english_name or '',
            self.middle_english_name or '',
            self.sur_english_name or '',
            self.last_english_name or ''
        ).strip()

    @api.depends("date_of_birth")
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 1

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('ums.student')
        return super(Student, self).create(vals)

    def write(self, vals):
        if not self.ref:
            vals['ref'] = self.env['ir.sequence'].next_by_code('ums.student')
        return super(Student, self).write(vals)

    @api.onchange('college_id')
    def onchange_department(self):
        for rec in self:
            return {'domain': {'department': [('college_id', '=', rec.college_id.id)]}}

    @api.onchange('college_id')
    def onchange_collage(self):
        if self.env.user.collage_ids and self.college_id.id not in self.env.user.collage_ids.ids:
            domain = []
            user = self.env.user.collage_ids
            for item in user:
                domain.append(item.id)
            return {'domain': {'college_id': [('id', 'in', domain)]}}

    @api.onchange('program')
    def onchange_level(self):
        if self.program:
            domain = []
            program = self.program.level_line
            for items in program:
                domain.append(items.level.id)
            return {'domain': {'level': [('id', 'in', domain)]}}

    @api.onchange('level')
    def onchange_semester_id(self):
        if self.level:
            vals = []
            domain = []
            program = self.program.level_line
            for items in program:
                vals.append(items.level.id)
                if self.level.id == items.level.id:
                    for rec in items.semester_line:
                        for t in rec.semester_id:
                            domain.append(t.id)
            return {'domain': {'semester_id': [('id', 'in', domain)]}}
