# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError
import babel, calendar
#import datetime


class vertiple_employee(models.Model):
	#_name = 'vertiple_employee.vertiple_employee'
	_inherit = 'hr.employee'

	employee_id = fields.Char(string='Employee ID', readonly=True)
	first_name = fields.Char("First Name")
	last_name = fields.Char("Last Name")
	fathers_name = fields.Char("Father's Name")
	mothers_name = fields.Char("Mother's Name")
	spouse_name = fields.Char('Spouse Name')
	blood_group = fields.Many2one('vertiple_employee.blood_group', string='Blood Group')
	contact_number = fields.Char('Contact Number')
	emergency_contact = fields.Char('Emergency Contact')
	birthday_as_per_cert = fields.Date('Date of Birth (as per certificate)')
	# Fields for Actions on Employee Page
	manager_status = fields.Char('Manager Status', readonly=True)
	manager_feedback = fields.Selection([
        ('good', 'GOOD'),
        ('avg','AVERAGE'),
        ('poor','POOR'),
        ], string='Feedback', default=False)
	hr_status = fields.Char('HR Status', readonly=True)
	hr_feedback = fields.Selection([
         ('good', 'GOOD'),
        ('avg','AVERAGE'),
        ('poor','POOR'),
        ], string='Feedback', default=False)
	probation_date_end = fields.Date('Probation Date End')
	state = fields.Selection([
        ('probation', 'PROBATION'),
        ('manager_review','MANAGER REVIEW'),
        ('hr_review','HR REVIEW'),
        ('confirmed', 'CONFIRMED'),
        ('notice', 'NOTICE / RESIGN'),
        ('exit','EXIT'),
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='probation',)
	check_field = fields.Boolean(string="Check", compute='get_user')
	working_address = fields.Char('Working Address', compute='get_working',readonly=True)
	pf_acc_number = fields.Char('PF Account Number')
	emp_id = fields.Char('Employee ID')

	@api.one
	def get_working(self):
		self.working_address = str(self.address_id.name)+",\n"+str(self.address_id.street)+","+str(self.address_id.city)+",\n"+str(self.address_id.zip)+","+str(self.address_id.state_id.name)+",\n"+str(self.address_id.country_id.name)

	@api.one
	@api.depends('check_field')
	def get_user(self):
		if self.user_id.id == self._uid:
			self.check_field = True
		else:
			self.check_field = False
	@api.multi
	def status_approve_manager(self):
		"""Manager's Employee Approval Status"""
		self.write({'manager_status':'Approved'})
		return self.write({'state': 'hr_review'})
	@api.multi
	def status_refuse_manager(self):
		print "!!!!!!!!!!!!!!!!!!!!!@@@@@@@@@@@@@@@@############$$$$$$$$4"
		"""Manager's Employee Refusal Status"""
		self.write({'manager_status':'Refused'})
		return self.write({'state': 'hr_review'})
	@api.multi
	def status_approve_hr(self):
		"""HR's Employee Approval Status"""
		self.write({'hr_status': 'Approved'})
		return self.write({'state': 'confirmed'})
	@api.multi
	def status_refuse_hr(self):
		"""HR's Employee Refusal Status"""
		self.write({'hr_status': 'Refused'})
		return self.write({'state': 'notice'})

	@api.multi
	def manager_approve(self):
		"""Set's the manager's status to Approve & sends email notificaiton"""
		self.status_approve_manager()
		template = self.env.ref('email_status_to_hr_template.email_status_to_hr')
		self.env['mail.template'].browse(template.id).send_mail(self.id)

	@api.multi
	def manager_refuse(self):
		"""Set's the manager's status to Refuse & sends email notificaiton"""
		self.status_refuse_manager()
		template = self.env.ref('email_status_to_hr_template.email_status_to_hr')
		self.env['mail.template'].browse(template.id).send_mail(self.id)
	
	@api.multi
	def hr_approve(self):
		"""Set's the hr's status to Approve & sends email notificaiton"""
		self.write({'hr_status': 'Approved'})
		return self.write({'state': 'confirmed'})
	@api.multi
	def hr_refuse(self):
		print '!@!@!@!@!@!@!@!@!@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@!@!@!@!'
		"""Set's the hr's status to Refuse & sends email notificaiton"""
		if not self.state == 'notice':
			self.write({'hr_status': 'Refused'})
			return self.write({'state': 'notice'})
		else:
			raise ValidationError("Your are already in  %s" % self.state)
	# Workflow Setting Methods
	@api.multi
	def set_to_probation(self):
		self.write({'state': 'probation'})

	@api.multi
	def set_to_manager_review(self):
		self.write({'state': 'manager_review'})

	@api.multi
	def action_hr_review(self):
		self.write({'state': 'hr_review'})

	@api.multi
	def set_to_confirm(self):
		return self.write({'state': 'confirmed'})

	@api.multi
	def set_to_notice(self):
		self.write({'state': 'notice'})
	@api.multi
	def set_to_exit(self):
		self.write({'state': 'exit'})

	@api.multi
	def emp_resign(self):
		"""Send's email and changes state to notice"""
		if not self.state == 'notice':
			self.sudo().set_to_notice()
		else:
			raise ValidationError("Your are already in  %s" % self.state)

class BloodGroup(models.Model):
	_name = 'vertiple_employee.blood_group'
	name = fields.Char(string="Blood Group", required=True,) 

class NoticeConfig(models.Model):
	# _name = 'vertiple_employee.notice_config'
	_inherit = 'hr.contract'
	notice_days = fields.Integer("Notice Days")

	# @api.onchange('config_date')
	# def act_notice_config(self):
	# 	print self.request_resign.date,"#$#$#$$$$#"

class RequestResign(models.Model):
	_name = 'vertiple_employee.request_resign'
	_inherit = "mail.thread"
	
	name = fields.Char('Employee',readonly=True)
	request_resign = fields.Many2one('vertiple_employee.notice_config')
	remarks = fields.Text("Remarks")
	notice_date = fields.Date("Date")
	get_date = fields.Date(compute='_get_date')
	request_on = fields.Date("Requsted On")
	notice_upto = fields.Date("Notice Upto")
	request_id = fields.Char("Request ID")
	emp_id = fields.Many2one("hr.employee",readonly=True,string="Employee Name")
	email = fields.Char('Email')
	manager_email = fields.Char('manager Email')
	cont = fields.Many2one("hr.contract")
	general_notice = fields.Date("Actual Notice",readonly=True)

	@api.depends('notice_date')
	@api.one
	def _get_date(self):
		obj = self.env['hr.contract'].search([('employee_id.user_id', '=', self.env.uid)])
		print obj.name
		for i in obj:
			print "***",i.name
			temp =  i.notice_days
		self.notice_date=datetime.now()+timedelta(days=temp)
		#t= datetime.strptime(self.notice_date,"%Y-%m-%d")
		self.general_notice = datetime.now()+timedelta(days=temp)
		#print self.general_notice
		# self.actual_notice=datetime.now()+timedelta(days=temp)
		#return t
		
	def _validate_date(self,notice_date):
		day= datetime.strptime(str(notice_date), '%Y-%m-%d')
		if day < datetime.now():
			return True
		else:
			return False

	@api.model
	def create(self,vals):
		print vals['notice_date']
		print self._validate_date(vals['notice_date'])
		if self._validate_date(vals['notice_date'])== True:
			raise ValidationError("please select valid date ")
		else:
			print datetime.today()
			print self.emp_id
			vals['request_on']=datetime.today()
			vals['request_id'] = self.env['ir.sequence'].next_by_code('request.code')
			resource = self.env['resource.resource'].search([('user_id','=',self.env.user.id)])
			emp = self.env['hr.employee'].search([('resource_id','=',resource.id)])
			vals['name'] = emp.name
			vals['emp_id'] = emp.id
			vals['email'] = emp.work_email
			vals['manager_email'] = emp.parent_id.work_email

			obj = self.env['hr.contract'].search([('employee_id.user_id', '=', self.env.uid)])
			for i in obj:
				temp = i.notice_days
				print temp,"***Temp"
			k = datetime.now()+timedelta(days=temp)
			print k,"K***"
			vals['general_notice']= k
			# print "*********",self._get_date()
			# k = datetime.strptime(str(self._get_date()),"%Y-%m-%d")
			# print type(k)
			# vals['general_notice'] = k
			new = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
			for i in new:
				i.emp_resign()
				# template = self.env.ref('vertiple_employee.resign_notification_email_template')
				# self.env['mail.template'].browse(template.id).sudo().send_mail(self.id)
			return super(RequestResign, self).create(vals)
		

# class RequestResign(models.Model):
# 	_name = 'vertiple_employee.request_resign'
# 	_inherit = "hr.employee"
	

# 	employee = fields.Char('Employee',readonly=True)	
# 	request_resign = fields.Many2one('vertiple_employee.notice_config')
# 	remarks = fields.Text("remarks")
# 	date = fields.Date("Date")
# 	get_date = fields.Date(compute='_get_date')
# 	request_on = fields.Date("Requsted On")
# 	notice_upto = fields.Date("Notice Upto")
# 	request_id = fields.Char("Request ID")
# 	emp_id = fields.Many2one("hr.employee",readonly=True,string="Employee Name")


# 	@api.depends('date')
# 	def _get_date(self):	
# 		obj = self.env['vertiple_employee.notice_config'].search([])
# 		for i in obj:
# 			temp =  i.config_date
# 		print temp
# 		self.date=datetime.now()+timedelta(days=temp)
# 		print type(self.date)


# 	@api.model
#  	def create(self,vals):
#  		print self.name

#  		return super(RequestResign, self).create(vals)

	
	
	
	
	

	
	


	




