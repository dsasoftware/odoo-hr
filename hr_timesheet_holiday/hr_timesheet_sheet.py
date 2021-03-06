# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution, third party addon
# Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'
    
    #~ timesheet_id = fields.Many2one('hr_timesheet_sheet.sheet', 'Timesheet')
    date_start = fields.Datetime('Start Date')
    date_stop = fields.Datetime('Stop Date')
    time_factor = fields.Float('Time Factor', default = 1.0)
    break_time = fields.Integer('Break Time (minutes)', default = 60, help="The total amount of minutes that were spent on breaks.")
    
    @api.one
    @api.onchange('date_start', 'date_stop', 'time_factor', 'break_time')
    def onchange_start_stop_date(self):
        if self.date_start:
            if self.date_start[-2:] != '00':
                self.date_start = self.date_start[:-2] + '00'
            if not self.date_stop:
                self.date_stop = fields.Datetime.to_string(fields.Datetime.from_string(self.date_start) + timedelta(hours = 9))
        if self.date_stop:
            if self.date_stop[-2:] != '00':
                self.date_stop = self.date_stop[:-2] + '00'
        if self.date_start and self.date_stop:
            self.number_of_days_temp = ((fields.Datetime.from_string(self.date_stop) - fields.Datetime.from_string(self.date_start)).total_seconds() / 60 - self.break_time) / 60 * self.time_factor / (self.employee_id.get_working_hours_per_day() or 8) #Assume 8 h working day if not specified.

class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"
    
    #~ holiday_ids = fields.One2many('hr.holidays', 'timesheet_id', 'Holidays')
    remove_holiday_ids = fields.Many2many('hr.holidays', string='Spent Holidays', compute = '_get_holiday_ids', inverse = '_set_holiday_ids')
    add_holiday_ids = fields.Many2many('hr.holidays', string='Earned Holidays', compute = '_get_holiday_ids', inverse = '_set_holiday_ids')
    
    @api.one
    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        if self.employee_id and self.date_from and self.date_to:
            self.remove_holiday_ids = self.env['hr.holidays'].search([
                ('employee_id', '=', self.employee_id.id),
                ('date_from', '>=', self.date_from),
                ('date_from', '<=', self.date_to),
                ('type', '=', 'remove'),
                #~ ('timesheet_id', '=', False),
            ])
            self.add_holiday_ids = self.env['hr.holidays'].search([
                ('employee_id', '=', self.employee_id.id),
                ('date_start', '>=', self.date_from),
                ('date_start', '<=', self.date_to),
                ('type', '=', 'add'),
                #~ ('timesheet_id', '=', False),
            ])
    
    @api.one
    def _get_holiday_ids(self):
        self._onchange_dates()
        #~ self.remove_holiday_ids = self.holiday_ids.filtered(lambda r: r.type == 'remove')
        #~ self.add_holiday_ids = self.holiday_ids.filtered(lambda r: r.type == 'add')
    
    @api.one
    def _set_holiday_ids(self):
        pass
        #~ self.holiday_ids = self.remove_holiday_ids | self.add_holiday_ids
