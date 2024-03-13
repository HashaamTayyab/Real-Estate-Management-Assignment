from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

from datetime import datetime
from dateutil.relativedelta import relativedelta

class EstateProperties(models.Model):
    _name = "estate.property"
    _description = "Model for Real-Estate Properties"

    # Choices for selection fields:
    garden_orientation_choices = [
        ('n', 'North'),
        ('s', 'South'),
        ('e','East'),
        ('w', 'West')
    ]
    state_choices = [
        ('n','New'),
        ('or', 'Offer Received'),
        ('oa', 'Offer Accepted'),
        ('s', 'Sold'),
        ('cn', 'Canceled')
    ]

    # Helper Functions
    def _default_availability():
        return datetime.now() + relativedelta(months=3)

    # Model Fields
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=_default_availability())
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=garden_orientation_choices)
    state = fields.Selection(selection=state_choices, required=True, copy=False, default="n")

    #Foreign Fields
    property_type_id = fields.Many2one("estate.property.type", string="Propety Type")
    user_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    #Computed Field
    total_area = fields.Integer("Total Area", compute="_compute_total_area")
    best_price = fields.Float("Best Price", compute="_compute_best_price")

    #Computed Fields Methods
    @api.depends('garden_area','living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            if self.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.00

    # OnChange Field Method
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = "n"
            self.garden_area = 10
        else:
            self.garden_orientation = ""
            self.garden_area = 0

    # Button Actions
    def action_sold(self):
        if "cn" in self.mapped("state"):
            raise UserError("Canceled properties cannot be sold.")
        return self.write({"state": "s"})

    def action_cancel(self):
        if "s" in self.mapped("state"):
            raise UserError("Sold properties cannot be canceled.")
        return self.write({"state": "cn"})

    _sql_constraints = [
        ('check_expected_price', 'CHECK (expected_price > 0)', 'The expected price should always be posiive.'),
        ('check_selling_price', 'CHECK (selling_price > 0)', 'The sellings price should always be positive.'),
    ]

    @api.constrains("expected_price", "selling_price")
    def _check_price_difference(self):
        for prop in self:
            if (
                    not float_is_zero(prop.selling_price, precision_rounding=0.01)
                    and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )
