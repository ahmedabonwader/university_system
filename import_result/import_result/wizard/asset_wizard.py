from odoo import fields, api, models, _
from odoo.exceptions import UserError

class AssetWizard(models.TransientModel):
    _name = 'asset.wizard'

    auction_id = fields.Many2one("auction.auction",string="auction #")
    asset_ids = fields.Many2many("auction.asset","asset_select_rel","wizard_id","asset_id")
    
    def select_asset(self):
        for record in self:
            for asset_record in record.asset_ids:
                asset_record.auction_id = record.auction_id.id
            # print("hh")