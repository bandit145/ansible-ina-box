import smtplib
import email

def Email():

	def __init__(self, smtp_server, auth_required, smtp_port, ssl, from_addr):
		self.from_addr = from_addr
		if ssl:
			self.smtp_con = smtplib.SMTP_SSL(smtp_server, smtp_port)
		else:
			self.smtp_con = smtplib.SMTP(smtp_server, smtp_port)

		if auth_required:
			self.smtp_con.login(kwargs['user'], kwargs['password'])

	def send_email(self, message, subject, to_addr ):
		message = email.MIMEMultipart()
		message['To'] = to_addr
		message['From'] = self.from_addr
		message['Subject'] = subject
		message.attach(email.MIMEText(message))
		message.subject(subject)
		self.smtp_con.sendmail(self.from_addr, self.to_addr, message.as_string())

	def send_playbook_completed(self, to_addr, playbook_results, playbook):
		if playbook_results['overall_result'] == 'success':
			subject = '{playbook} success'.format(playbook=playbook)
			message = 'Playbook {playbook} has completed successfully'.format(playbook=playbook)
		else:
			subject = '{playbook} failed'.format(playbook=playbook)
			for play in playbook_results['plays'].keys():
				for task in playbook_results['plays'][play].keys():
					task_info = playbook_results['plays'][play][task]
					stderr = task_info['stderr']
					targets = task_info['target']
			message = '''Playbook {playbook} failed on hosts {hosts} 
			with error:\n {error}'''.format(playbook=playbook, hosts='\n'.join(targets), error=stderr)
		self.send_email(message, subject, to_addr)
