from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _sql_constraints = [
        ('check_name', 'UNIQUE(name)', 'This property name can not be used. It is already taken.'),
    ]

    name = fields.Char(required=True)