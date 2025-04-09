# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import datetime

class RequestCertificate(models.Model):
    _name = 'ums.request.certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Requests for Certificates"
    _rec_name = 'ref'
    _order = "request_date desc"

    student = fields.Many2one("ums.student", string="Student", required=True, tracking=True)
    english_name = fields.Char("English name of student", tracking=True)

    first_english_name = fields.Char(string='First English Name', tracking=True)
    middle_english_name = fields.Char(string='Middle English Name', tracking=True)
    sur_english_name = fields.Char(string='English Surname', tracking=True)
    last_english_name = fields.Char(string='Last English Name', tracking=True)
    college_id = fields.Many2one("ums.college", string="College", readonly=True, tracking=True)
    specialist_id = fields.Many2one("ums.specialist", string="Specialist", readonly=True, tracking=True)

    phone = fields.Char("Phone", default="249", tracking=True)
    phone_2 = fields.Char("Phone 2", default="249", tracking=True)
    language = fields.Selection([("arabic", "Arabic"), ("english", "English")], default="arabic", string="Language",
                                required=True, tracking=True)
    details = fields.Boolean(string="Details", tracking=True)
    ref = fields.Char(string='Reference', tracking=True)
    resend = fields.Boolean("Send twice", tracking=True)
    state = fields.Selection([("draft", "Draft"), ("in_progress", "In Progress"), ("completed", "Completed")],
                             default="draft")

    request_date = fields.Date("Request Date", readonly=True, default=fields.Datetime.now)
    done_date = fields.Date("Complete Date", readonly=True)

    @api.onchange("student")
    def _change_college(self):
        for rec in self:
            rec.college_id = rec.student.college_id
            rec.specialist_id = rec.student.specialist_id

    @api.onchange('first_english_name', 'middle_english_name', 'sur_english_name', 'last_english_name')
    def _onchange_name(self):
        self.english_name = "{} {} {} {}".format(
            self.first_english_name or '',
            self.middle_english_name or '',
            self.sur_english_name or '',
            self.last_english_name or ''
        ).strip()

    def print_action(self):
        for rec in self:
            rec.student.first_english_name = rec.first_english_name
            rec.student.middle_english_name = rec.middle_english_name
            rec.student.sur_english_name = rec.sur_english_name
            rec.student.english_name = rec.english_name

            rec.student.first_english_name = rec.first_english_name
            rec.state = "in_progress"

            data = {
                'ids': self.ids,
                'model': self._name,
                'form': {
                    'student': rec.student.id,
                    'details': rec.details
                },
            }
            if rec.language == "arabic" and not rec.details:
                return rec.student.college_id.certificate_id.report_action(self, data=data)
            elif rec.language == "arabic" and rec.details:
                return rec.student.college_id.report_certificate_id.report_action(self, data=data)

            if rec.language == "english" and not rec.details:
                return  rec.student.college_id.en_certificate_id.report_action(self, data=data)
            elif rec.language == "english" and rec.details:
                return rec.student.college_id.en_report_certificate_id.report_action(self, data=data)

    def set_complete(self):
        if self.phone:
            data = {}
            msg = self.student.name + " " + "الشهادة جاهزة الرجاء الحضور للاستلام"
            params = {'user': 'imam',
                      'pwd': '420864',
                      'smstext': msg,
                      'Sender': 'Elmahdi Un.',
                      'Nums': self.phone,
                      }
            url = 'http://www.airtel.sd/bulksms/webacc.aspx?'

            self.state = "completed"
            self.done_date = datetime.datetime.now()
            try:
                r = requests.get(url=url, params=params)
                data = r.json()
            except Exception as e:
                print((
                          'Cannot contact geolocation servers. Please make sure that your Internet connection is up '
                          'and running (%s).') % e)
            for rec in self:
                return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'تمت العملية بنجاح',
                    'type': 'rainbow_man',
                }
            }

    def resend_sms(self):
        if self.phone_2:
            data = {}
            msg = self.student.name + " " + "الشهادة جاهزة الرجاء الحضور للاستلام"
            params = {'user': 'imam',
                      'pwd': '420864',
                      'smstext': msg,
                      'Sender': 'Elmahdi Un.',
                      'Nums': self.phone_2,
                      }
            url = 'http://www.airtel.sd/bulksms/webacc.aspx?'

            self.resend = True
            try:
                r = requests.get(url=url, params=params)
                data = r.json()
            except Exception as e:
                print((
                          'Cannot contact geolocation servers. Please make sure that your Internet connection is up '
                          'and running (%s).') % e)

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('ums.request.certificate')
        return super(RequestCertificate, self).create(vals)

    def write(self, vals):
        if not self.ref:
            vals['ref'] = self.env['ir.sequence'].next_by_code('ums.request.certificate')
        return super(RequestCertificate, self).write(vals)
