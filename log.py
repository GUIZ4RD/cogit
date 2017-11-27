class Log():
  
  @classmethod
  def e(self,tag,msg):
    self.myprint("ERROR",tag,msg)
    
  @classmethod
  def d(self,tag,msg):
    self.myprint("DEBUG",tag,msg)
    
  @classmethod  
  def myprint(self,type,tag,msg):
    print "["+type+"] "+tag+": "+msg
