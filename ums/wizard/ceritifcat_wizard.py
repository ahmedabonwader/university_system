from odoo import fields, api, models, _


class CeritifcatWizard(models.TransientModel):
    _name = 'ceritifcat.wizard'

    student = fields.Many2one('ums.student',readonly=True)
    language = fields.Selection([("arabic", "Arabic"), ("english", "English")], default="arabic", string="language",
                                required=True)
    details = fields.Boolean(string="Details")
    
    def validate(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'student': self.student.id,
                'details': self.details
            },
        }
        if self.language == "arabic":
            print(self.student.college_id.report_certificate_id)
        elif self.language == "english":
            print(self.student.college_id.en_report_certificate_id)