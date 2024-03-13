from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _sql_constraints = [
        ('check_name','UNIQUE(name)','The same Tag names are not allowed twice.'),
    ]

    name = fields.Char(required=True)