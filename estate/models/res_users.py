from odoo import fields, models

class ResUsers(models.Model):
    _name = "res.users.module"
    _inhrit = "res.users"

    property_id = fields.One2many("estate.property", "user_id", string="Properties", domain = [('state','in', ['n','or'])])