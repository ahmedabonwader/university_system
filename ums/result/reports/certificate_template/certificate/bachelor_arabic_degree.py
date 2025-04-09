from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class BachelorArabicDegree(models.AbstractModel):
    _name = 'report.ums.print_bachelor_arabic_degree'

    @api.model
    def _get_report_values(self, docids, data=None):
        student = data['form']['student']
        details = data['form']['details']
        docs = []
        
        student_obj = self.env['ums.student'].search([("id","=",student)])
        docs.append({
            'student': student_obj,
            'ac_name': self.env['ir.config_parameter'].get_param('ums.ac_name')
        })
        print (docs)
        return {
            'docs_data': docs,
        }