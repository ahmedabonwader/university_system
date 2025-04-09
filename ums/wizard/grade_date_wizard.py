from odoo import fields, api, models


class GradeDateWizard(models.TransientModel):
    _name = 'grade.date.wizard'
    _description = "Add grade date to all graduations student"

    grade_date = fields.Date('Graduation Date')
    hijri_grade_date = fields.Char('Graduation Date in hijri Format')
    result_id = fields.Many2one('ums.result', 'Select Result')

    @api.depends('grade_date')
    def change_hijri_date(self):
        for rec in self:
            rec.hijri_grade_date = str(rec.grade_date)

    def validate(self):
        for rec in self:
            for student_line in rec.result_id.second_semester_result:
                student_line.student.grade_date = rec.grade_date
                student_line.student.grade_date = rec.hijri_grade_date
                student_line.student.state = 'graduation'
