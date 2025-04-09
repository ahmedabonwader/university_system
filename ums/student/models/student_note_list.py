from odoo import models, fields, api, _


class StudentNote(models.Model):
    _name = 'student.note.line'
    _description = "Student Note Line"

    student_id = fields.Many2one('ums.student', 'Student')
    college_id = fields.Many2one(related='student_id.college_id', string="College")
    note_id = fields.Many2one('ums.result', 'Result#', required=True)
    key = fields.Char("Key")
    note_select = fields.Many2one('ums.note.list', '#', required=True)
    note = fields.Char('Note')
    note_details = fields.Char('Note Details', required=True)
    note_en_details = fields.Char('Note English Details', required=True)
    # note_second_id = fields.Many2one('ums.result.second')
    # note_first_id = fields.Many2one('ums.result.first')

    @api.onchange('note_select')
    def change_note(self):
        for rec in self:
            rec.note = rec.note_select.note
            rec.note_details = rec.note_select.note_details
            rec.note_en_details = rec.note_select.note_en_details
            
    @api.onchange('college_id')
    def onchange_college_id_note_id(self):
        for rec in self:
            return {'domain': {'note_id': [('college', '=', rec.college_id.id)]}}