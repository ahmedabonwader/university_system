from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class BachelorEnglishDegree(models.AbstractModel):
    _name = 'report.ums.print_bachelor_english_degree'

    @api.model
    def _get_report_values(self, docids, data=None):
        student = data['form']['student']
        details = data['form']['details']
        docs = []

        student_obj = self.env['ums.student'].search([("id","=",student)])
        docs.append({
            'student': student_obj,
            'final_result_letter': student_obj.final_result_letter.english_name,
            'ac_name': self.env['ir.config_parameter'].get_param('ums.ac_name_en')
        })
        print (docs)
        return {
            'docs_data': docs,
        }