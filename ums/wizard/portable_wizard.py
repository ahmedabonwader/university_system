from odoo import fields, api, models, _

#must be delete
class CertitifactWizard(models.TransientModel):
    _name = 'ceritifcat.wizard'
    fff = fields.Boolean()


class PortableWizard(models.TransientModel):
    _name = 'portable.wizard'
    _description = "Select student had portable subject"

    def default_get(self, fields):
        res = super(PortableWizard, self).default_get(fields)

        if self.env.context.get('active_id'):
            res['evaluation_id'] = self.env.context.get('active_id')
        return res

    student_ids = fields.Many2many('ums.portable')
    evaluation_id = fields.Many2one('ums.exam.evaluation', 'Evaluation')
    class_id = fields.Many2one(related='evaluation_id.class_id', string='Class', required=True)
    college_id = fields.Many2one(related='evaluation_id.college_id', string="College", required=True)
    specialist_id = fields.Many2one(related='evaluation_id.specialist_id', string="Specialist", required=True)
    program_id = fields.Many2one(related='evaluation_id.program_id', string='Program')
    department = fields.Many2one(related='evaluation_id.department_id', string='Department')
    level_id = fields.Many2one(related='evaluation_id.level_id', string='Level')
    semester = fields.Many2one(related='evaluation_id.semester_id', string='Semester')
    subject_id = fields.Many2one(related='evaluation_id.subject_id', string='Subject', required=True)
    student_status = fields.Many2one('ums.student.status', 'Student Status')
    result_test = fields.Boolean(related='evaluation_id.result_test', string="Test")

    @api.onchange("evaluation_id")
    def change_portable_domain(self):
        for rec in self:
            portable_data = self.env["ums.portable"].search([
                ('college_id', '=', rec.college_id.id),
                ('department', '=', rec.department.id),
                ('program_id', '=', rec.program_id.id),
                ('level_id', '=', rec.level_id.id),
                ('specialist_id', '=', rec.specialist_id.id),
            ])
            portable_ids = []
            for record in portable_data:
                if record.firest_semstar == rec.semester:
                    for sub_line in record.portable_ids:
                        if sub_line.subject_id == rec.subject_id:
                            portable_ids.append(record.id)
                elif record.second_semstar == rec.semester:
                    for sub_line in record.portable_second_ids:
                        if sub_line.subject_id == rec.subject_id:
                            portable_ids.append(record.id)
            return {'domain': {'student_ids': [('id', 'in', portable_ids)]}}

    def validate(self):
        for portabale_student in self.student_ids:
            evaluation_line_obj = self.env['exam.evaluation.line']
            if self.evaluation_id.semester_id == portabale_student.firest_semstar:
                for l in portabale_student.portable_ids:
                    if l.subject_id.id == self.evaluation_id.subject_id.id:
                        student_vals_first = {
                            'sub_id': l.sub_first_regional_id.id,
                            'student_id': portabale_student.name.id,
                            'student_name': portabale_student.name.name,
                            'student_status': self.student_status.id,
                            'evaluation_id': self.evaluation_id.id,
                            'class_id': portabale_student.class_id.id,
                        }
                        evaluation_line_obj.create(student_vals_first)
            elif self.evaluation_id.semester_id == portabale_student.second_semstar:
                for t in portabale_student.portable_second_ids:
                    if t.subject_id.id == self.evaluation_id.subject_id.id:
                        student_vals_second = {
                            'sub_id': t.sub_second_regional_id.id,
                            'student_id': portabale_student.name.id,
                            'student_name': portabale_student.name.name,
                            'student_status': self.student_status.id,
                            'evaluation_id': self.evaluation_id.id,
                            'class_id': portabale_student.class_id.id,
                        }
                        evaluation_line_obj.create(student_vals_second)
        # self.evaluation_id.result_test = self.result_test
