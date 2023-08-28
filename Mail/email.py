import smtplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendMail(request,receiver_email,username,pk):
	# Email parameters
	link =request.build_absolute_uri(reverse('set_password', kwargs={'pk':pk}))
	sender_email = 'itstanveer11@gmail.com'
	subject = 'Set Password for Your Account'
	message_template = """
Dear {username},

Please set a password for your account by clicking on the link below:
{link}
	
Thank you,
Your Organization
"""
	
	message = message_template.format(username=username, link=link)
	# Create a multipart message object
	msg = MIMEMultipart()
	msg['From'] = sender_email
	msg['To'] = receiver_email
	msg['Subject'] = subject
	
	# Attach the message to the MIMEMultipart object
	msg.attach(MIMEText(message, 'plain'))
	
	# Send the email
	with smtplib.SMTP('smtp.gmail.com', 587) as server:
	    server.starttls()
	    server.login("<id>", '<password>')
	    server.send_message(msg)