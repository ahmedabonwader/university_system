from odoo import fields, api, models, _


class ResultWizard(models.TransientModel):
    _name = 'result.wizard'

    student_id = fields.Many2one('ums.student', 'Student')
    semester_result = fields.Boolean(string="Semester Result")
    result_id = fields.Many2one('ums.result', 'Select Result')
    first_semester = fields.Many2one(related='result_id.firest_semstar')
    second_semester = fields.Many2one(related='result_id.second_semstar')
    semester_type = fields.Many2one('ums.semester',
                                    domain="[('id', 'in', (second_semester,first_semester))]",
                                    string='Select Semester')
    print_type = fields.Selection([("letter", "Letter"), ("number", "Number")],required=True, default="letter", string="Result Type")

    def print_result(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'result': self.result_id.id,
                'semester': self.semester_type.id,
                'print_type': self.print_type,
            },
        }

        return self.env.ref('ums.action_print_semester_result').report_action(self, data=data)
