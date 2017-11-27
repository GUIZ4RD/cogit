from settings import *
import traceback

class Alert():
     
  @classmethod
  def send_email(self,user, pwd, recipient, subject, body):
      import smtplib

      gmail_user = user
      gmail_pwd = pwd
      FROM = user
      TO = recipient if type(recipient) is list else [recipient]
      SUBJECT = subject
      TEXT = body

      # Prepare actual message
      message = """From: %s\nTo: %s\nSubject: %s\n\n%s
      """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
      try:
          server = smtplib.SMTP("smtp.gmail.com", 587)
          server.ehlo()
          server.starttls()
          server.login(user, pwd)
          server.sendmail(FROM, TO, message)
          server.close()
          print 'successfully sent the mail'
      except Exception, e:
          print e
          print "failed to send mail"    
          
          
  @classmethod
  def notify(self, user=None, error=None, tb=None,msg=None):
    title = "Alert for Hi Coach on "+PLATFORM
    content = "Alert for Hi Coach on "+PLATFORM
    if(user!=None):
      content+=" for user "
      content+=str(user)+"\n"
    if(msg!=None):
      content+="\nMESSAGE\n"
      content+=msg+"\n"
    if(error!=None):
      content+="\nERROR TYPE\n"
      content+=str(error)+"\n"
    if(tb!=None):
      content+="\nSTACKTRACE\n"
      content+=str(tb)
    self.send_email("gfgullo@gmail.com","gottfriedleibniz4","gfgullo@gmail.com",title,content)
          
          

if __name__ == "__main__":
  try:
    a=1
    b='2'
    print a+b
  except Exception, e:  
    tb = traceback.format_exc()
    print tb
    Alert.notify(user="12345",error=e,tb=tb,msg="Test error")