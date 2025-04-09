from odoo import fields, api, models, _


class CeritifcatWizard(models.TransientModel):
    _name = 'note.wizard'
    _description = "Add note to student in same semester Result"

    result = fields.Many2one('ums.result', readonly=True)
    semester = fields.Many2one("ums.semester")
    note_select = fields.Many2one('ums.note.list', '#')
    note = fields.Char('Note')
    note_details = fields.Char('Note Details')
    note_en_details = fields.Char('Note English Details')

    @api.onchange('note_select')
    def change_note(self):
        for rec in self:
            rec.note = rec.note_select.note
            rec.note_details = rec.note_select.note_details
            rec.note_en_details = rec.note_select.note_en_details

    def validate(self):
        if self.result.firest_semstar == self.semester:
            for line in self.result.first_semester_result:
                note_vals = {
                    "note_select":self.note_select.id,
                    "note":self.note,
                    "note_details":self.note_details,
                    "note_en_details":self.note_en_details,
                    "note_first_id":line.id,
                }
                self.env["ums.result.note"].create(note_vals)
        elif self.result.second_semstar == self.semester:
            for line in self.result.second_semester_result:
                note_vals = {
                    "note_select":self.note_select.id,
                    "note":self.note,
                    "note_details":self.note_details,
                    "note_en_details":self.note_en_details,
                    "note_second_id":line.id,
                }
                self.env["ums.result.note"].create(note_vals)