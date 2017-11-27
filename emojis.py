class Emojis:
  
  EMOJI = {"EMJ_MUSCLE":u'\U0001f4aa',
          "EMJ_CLAP":u'\U0001f44f'}
  
  def get(self,id):
    return self.EMOJI[id]
  
  def parse(self,text):
    start = text.find("EMJ_")
    if(start==-1):
      return text
    end = text[start:].find(" ")
    if(end==-1):
      end=len(text)
    else:
      end+=start
    text= text[:start]+self.get(text[start:end])+text[end:]
    return text
  
emojis = Emojis()

"""TESTING
print emojis.parse("Hi EMJ_MUSCLE")
print emojis.parse("Hi EMJ_MUSCLE hru ?")
print emojis.parse("EMJ_MUSCLE bro")
print emojis.parse("EMJ_MUSCLE")
"""