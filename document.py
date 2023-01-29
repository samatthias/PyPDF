class Document:
  
  def __init__(self):
    self.listPages = []

  def addPage(self, page):
    self.listPages.append(page)
  
  def getPages(self):
    return self.listPages

  def getCountPages(self):
    return len(self.listPages)
 
  def setFileNameWithExtension(self, fileNameWithExtension):
    self.fileNameWithExtension = fileNameWithExtension

  def getFileNameWithExtension(self):
    return self.fileNameWithExtension
  
  def setFileName(self, fileName):
    self.fileName = fileName

  def getFileName(self):
    return self.fileName