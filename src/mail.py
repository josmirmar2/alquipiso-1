import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib

load_dotenv()

def sendEmail(email_reciver, body) :
    email_sender = "alquipisopgpi@gmail.com"
    password = os.getenv("MAILPASSWORD")
    
    subject = "Reserva correctamente efectuada"
    
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_reciver
    em["Subject"] = subject
    em.set_content(body)
    
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL("smtp.gmail.com",465,context= context) as smtp:
        smtp.login(email_sender, password)
        smtp.sendmail(email_sender, email_reciver,em.as_string());
        
if __name__ == "__main__":
    reciver = "pablo07113@gmail.com"
    body = "prueba del correo enviado con python desde la app de alquipiso"
    
    sendEmail(reciver, body)
    
    