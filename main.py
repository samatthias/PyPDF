import os, json, sys, math, fnmatch, requests
import cv2
import numpy as np
import shutil
import argparse
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter
from os import listdir
from os.path import isfile, join
from os.path import exists
from PIL import Image
from page import Page
from document import Document
from mapping import Mapping


#Runner

class Runner:



  def __init__(self):
    workDirectory = os.getcwd()
    try:
      with open(os.path.join(workDirectory,"config","config.json")) as cm:
        self.configMicroservice = json.load(cm)
    except OSError as error:
      print(error)
      print("Failed to load config from json file. Provide the respective config.json file within the subfolder /config.")
      sys.exit()

    
    if not os.path.exists(self.configMicroservice["inputDirectory"]):
      os.makedirs(self.configMicroservice["inputDirectory"])

    if not os.path.exists(self.configMicroservice["workDirectory"]):
      os.makedirs(self.configMicroservice["workDirectory"])
    
    if not os.path.exists(self.configMicroservice["outputDirectory"]):
      os.makedirs(self.configMicroservice["outputDirectory"])


  def createDocumentList(self, documentList):
    print(self.configMicroservice["inputDirectory"])

    # list only files in input directory
    pdfDocuments = [f for f in listdir(self.configMicroservice["inputDirectory"]) if isfile(join(self.configMicroservice["inputDirectory"], f))]


    for fileName in pdfDocuments:
      document = Document()
      document.setFileName(fileName)

      documentList.append(document)
    
    return documentList



    

  def convertPDFtoImage(self, documentList):

    

    for document in documentList:
      
      
      i = 0

      orginalFilePath = self.configMicroservice["inputDirectory"]+document.getFileName()
      print(orginalFilePath)

      reader = PdfReader(orginalFilePath)
      for page in reader.pages:
        for image in page.images:

          print("image")

          page = Page()

          
          pageImageFileName = document.getFileName()[0:-4]
          pageImageFileName += "__"+str(i)+"__"
          pageImageFileName += image.name

          print(pageImageFileName)

          pageImagePath = self.configMicroservice["workDirectory"] + pageImageFileName

          #page.setPageImagePath(pageImagePath)

          #indexSuffix = pageImageFileNamefind('.')
          #imagFileName = ipageImageFileName[[0:indexSuffix]
          #page.setFileNameWithExtension(pageImageFileName)
          #page.setFileName(imagFileName)

          page.setImageFileName(pageImageFileName)

          with open(pageImagePath, "wb") as fp:
            fp.write(image.data)


          document.addPage(page)

          i += 1

    return documentList


  def findEmptyPages(self, documentList):

    for document in documentList:
       for page in document.getPages():
          pageImagePath = self.configMicroservice["workDirectory"] + page.getImageFileName()
          image = Image.open(pageImagePath)
          width, height = image.size


          area = (30, 30, width-30, height-30)
  
          cropedImage = image.crop(area)

          pageImageFileName = page.getImageFileName()[0:-4]
          #print(pageImageFileName)
          fileExtension = page.getImageFileName()[-4:]
          #print(fileExtension)
          #print(fileExtension)
          pageImageCroppedFileName = pageImageFileName + "__crop-gray__" + fileExtension
          pageImageCroppedPath = self.configMicroservice["workDirectory"] +  pageImageCroppedFileName


          page.setPageImageRoiFileName(pageImageCroppedFileName)
          #print(pageImageCroppedPath)
  
          cropedImage.save(pageImageCroppedPath)
          width, height = cropedImage.size
          totalImagePixel = width * height
          print(totalImagePixel)

          cv2GrayImage = cv2.imread(pageImageCroppedPath, cv2.IMREAD_GRAYSCALE)
          (thresh, cv2BinaryImage) = cv2.threshold(cv2GrayImage, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
          
          pageImageBinaryFileName = pageImageFileName + "__binary__" + fileExtension
          pageImageBinaryPath = self.configMicroservice["workDirectory"] +  pageImageBinaryFileName
          #print(pageImageBinaryPath)

          totalWhitePixel = np.sum(cv2BinaryImage == 255)
          totalBlackPixel = np.sum(cv2BinaryImage == 0)
          print('Number of white pixels:', str(totalWhitePixel))
          print('Number of black pixels:', str(totalBlackPixel))
          
          percentageWhitePixel = (totalWhitePixel / totalImagePixel) * 100
          print ("percentage white pixels" + str(percentageWhitePixel))
          percentageCompare = float(self.configMicroservice["thresholdEmptyPage"])

          if percentageWhitePixel >= percentageCompare:
            print("page is empty!")
            page.setPageIsEmpty(True)
          else:
            print("page is not empty")
            page.setPageIsEmpty(False)

          
          #cv2.imwrite(pageImageBinaryPath, cv2BinaryImage)


    



      

  def extractRoiImage(self, documentList):

    for document in documentList:
      i = 0
      for page in document.getPages():        
  
            pageImagePath = self.configMicroservice["workDirectory"] +  page.getImageFileName()
      
            image = Image.open(pageImagePath)
            width, height = image.size
  
            cropWidth = math.floor(width/3)
            cropHeight = math.floor(height/6)
  
            area = (width-cropWidth, 0, width, cropHeight)
  
            cropedImage = image.crop(area)
  
            pageImageFileName = page.getImageFileName()[0:-4]
            fileExtension = page.getImageFileName()[-4:]
            print(fileExtension)

            pageImageRoiGrayFileName = pageImageFileName + "__roi-gray__" + fileExtension
            pageImageRoiGrayPath = self.configMicroservice["workDirectory"] + "\\" + pageImageRoiGrayFileName

            cropedImage.save(pageImageRoiGrayPath)

            cv2GrayImage = cv2.imread(pageImageRoiGrayPath, cv2.IMREAD_GRAYSCALE)
            (thresh, cv2BinaryImage) = cv2.threshold(cv2GrayImage, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            pageImageBinaryFileName = pageImageFileName + "__roi-binary__" + fileExtension
            pageImageBinaryPath = self.configMicroservice["workDirectory"] +  pageImageBinaryFileName

            cv2.imwrite(pageImageBinaryPath,cv2BinaryImage)
            

            page.setPageImageRoiFileName(pageImageBinaryFileName)
            #print(pageImageRoiFileName)
  
            
  
            #print(math.floor(width/3))
            #print(math.floor(height/6))
            #print(width)
            #print(height)

            i += 1
  
    return documentList
  
  
  def extractQrCode(self, documentList):
  
    for document in documentList:
      for page in document.getPages():

        imageRoiPath = self.configMicroservice["workDirectory"] + "\\" + page.getPageImageRoiFileName()
		
        print("Image Roi Path " + imageRoiPath)
  
        imageRoi= cv2.imread(imageRoiPath)
        qrDecoder = cv2.QRCodeDetector()
          
        ## Detect and decode the qrcode
        data,bbox,rectifiedImage = qrDecoder.detectAndDecode(imageRoi)

        if len(data)>0:
          print("Qr code found on image - " + imageRoiPath)
          print("Data found and read - " + data)
		 
		  
          #print("Decoded Data : {}".format(data))
          page.setQrCodeData(data)
          #print(page.getQrCodeData())
        else:
          print("QR Code not detected")
          page.setQrCodeData("")

    return documentList

        

      
  def mergePdfFiles(self, documentList):

    outputDocumentList = []
    documentIndex = 0

    lastQRCodeDocIndex = 0
    lastQRCodePageIndex = 0 
    

    for document in documentList:
      
        pageIndex = 0

        for page in document.getPages():

          inputFilePath = self.configMicroservice["inputDirectory"] + document.getFileName()
          outputTmpFilePath = self.configMicroservice["workDirectory"] + self.configMicroservice["tmpPDFFilename"] 
          
          print("-----------------------------------")
          print("Document Index: " + str(documentIndex))
          print("Document Count pages: " + str(document.getCountPages()))
          print("Page Index: " + str(pageIndex))
          print("QR code data: " + page.getQrCodeData())
          


          
          if page.getQrCodeData() != "":
            print("page has qr code - create new document")

           # check if there is a tmp file and then movit 

            if exists(outputTmpFilePath):
              
              # get the last qr code data from the last doc and page
              print("Last Document Index: " + str(lastQRCodeDocIndex))
              print("Last QR Code Index: " + str(lastQRCodePageIndex))
              lastQRCode = documentList[lastQRCodeDocIndex].getPages()[lastQRCodePageIndex].getQrCodeData()
              print("Last QR Code data: " + lastQRCode)
              

              outputFileName = str(len(outputDocumentList)) + "__" + lastQRCode + ".pdf"
              outputFilePath = self.configMicroservice["workDirectory"] + outputFileName

              print("output file path: " + outputFilePath)
           
              shutil.copy(outputTmpFilePath, outputFilePath)        
              outputDocumentList.append(outputFileName)
              os.remove(outputTmpFilePath)

            lastQRCodeDocIndex = documentIndex
            lastQRCodePageIndex = pageIndex              

            # just copy pdf file to ouptput directory in new tmp.pdf file
            if (pageIndex == 0 and document.getCountPages() == 1):
              print("hopla")
              shutil.copy(inputFilePath, outputTmpFilePath)
              
  
            # extract from page to new tmp.pdf file
            #else:
            #  merger = PdfWriter()
            #  outputDocument = open(inputFilePath, "rb")
            #  merger.append(fileobj=outputDocument, pages=(pageIndex-1, pageIndex))
            #  output = open(outputTmpFilePath, "wb")
            #  merger.write(output)
            #  # Close File Descriptors
            #  outputDocument.close()
            #  merger.close()
            #  output.close() 
               
          print("Page empty? " + str(page.getPageIsEmpty()))
          if page.getQrCodeData() == "" and not page.getPageIsEmpty():
             self.helpMerge(inputFilePath, outputTmpFilePath, pageIndex)

          pageIndex = pageIndex + 1
        
        documentIndex = documentIndex + 1
    

    

    #get last qr code document and page
    print(lastQRCodeDocIndex)
    print(lastQRCodePageIndex)
    lastQRCode = documentList[lastQRCodeDocIndex].getPages()[lastQRCodePageIndex].getQrCodeData()

    print("last round")
    outputFileName = str(len(outputDocumentList)) + "__" + lastQRCode + ".pdf"
    outputFilePath = self.configMicroservice["workDirectory"] 
    outputFilePath += outputFileName
    print(outputFilePath)

    shutil.copy(outputTmpFilePath, outputFilePath)        
    outputDocumentList.append(outputFileName)
    os.remove(outputTmpFilePath)

    return outputDocumentList
         


  def helpMerge(self,inputFilePath,outputTmpFilePath,pageIndex):
    print("page has no qr - so merging is needed")

    merger = PdfWriter()

    outputDocument1 = open(outputTmpFilePath, "rb")
    outputDocument2 = open(inputFilePath, "rb")

    merger.append(fileobj=outputDocument1)
    merger.append(fileobj=outputDocument2, pages=(pageIndex-1, pageIndex))

    tmpFile = self.configMicroservice["outputDirectory"] + "tmp.pdf.tmp"
    output = open(tmpFile, "wb")
    merger.write(output)

    # Close File Descriptors
    outputDocument1.close()
    outputDocument2.close()
    merger.close()
    output.close() 

    os.remove(outputTmpFilePath)
    os.rename(tmpFile, outputTmpFilePath)
    
  
  
  def cleanup(self):
    # Cleanup working directory
    shutil.rmtree(self.configMicroservice["workDirectory"])
    os.makedirs(self.configMicroservice["workDirectory"])

    # Cleanup output directory
    shutil.rmtree(self.configMicroservice["outputDirectory"])
    os.makedirs(self.configMicroservice["outputDirectory"])
  
  

  def convertPdfToArchivePdf(self,outputDocumentList,sourceDirectory):
    for outputDocument in outputDocumentList:
      inputPdfFilePath = sourceDirectory + outputDocument
      inputPdfFile = open(inputPdfFilePath, "rb")

      url = self.configMicroservice["pdfa_convert_url"]
      #headers = {'Content-Type':'multipart/form-data'}



      response = requests.post(url, files = {"file": inputPdfFile})

      outputPdfFilePath = self.configMicroservice["outputDirectory"] + outputDocument
      file = open(outputPdfFilePath, "wb")
      file.write(response.content)
      file.close()


  

  def cmdLineInput(self, outputDocumentList):

    for outputDocument in outputDocumentList:
      print(outputDocument)
      userInput = input("I want to move file: " + outputDocument + " - ok?: ")
      print("You entered: " + userInput)
      if userInput == "y":
        self.movePDFFile(outputDocument)
      else:
        print("Tb implemented!")
        pass




  def countFilesInDir(self, path):
    if not os.path.exists(path):
      os.makedirs(path)
    #return len([name for name in os.listdir(path) if os.path.isfile(name)])
    return len(fnmatch.filter(os.listdir(path), '*.pdf'))
  

  
  def movePDFFile(self, outputDocument):

    indexSeparator = outputDocument.find("_")+2
    mappingName = outputDocument[indexSeparator:indexSeparator+2]
    print("Mapyping name:" + mappingName)
    print(self.configMicroservice["mappings"][mappingName]["destinationDirectory"])
    
    #for attrs in self.configMicroservice["mappings"]:

    if mappingName == "RF" or mappingName == "RP":
        #map = Mapping()sq>a
        #map.setDefaultYear(attrs["name"])


        indexStartSeparator = outputDocument.find("-")
        indexEndSeparator = outputDocument.find(".")

        directoryMonth = outputDocument[indexStartSeparator+1:indexEndSeparator] + "\\"
        print(directoryMonth)

        destinationDirectory = self.configMicroservice["mappings"][mappingName]["destinationDirectory"] + directoryMonth 
        print(destinationDirectory)
        sourceFilePath= self.configMicroservice["outputDirectory"] + outputDocument 
        destFileName = str(self.countFilesInDir(destinationDirectory )) + "__a-1.pdf"
        
        destFilePath = destinationDirectory + destFileName

        print(sourceFilePath)
        print(destFilePath)
  

        shutil.copy(sourceFilePath, destFilePath)
        os.remove(sourceFilePath)

      
    elif mappingName == "AD":

        destinationDirectory = self.configMicroservice["mappings"][mappingName]["destinationDirectory"]
        destFileName = str(self.countFilesInDir(destinationDirectory )) + "__a-1.pdf"
        destFilePath = destinationDirectory + destFileName

        sourceFilePath= self.configMicroservice["outputDirectory"] + outputDocument
        
        shutil.copy(sourceFilePath, destFilePath)
        os.remove(sourceFilePath)
    else:
        print('No mapping found!')
        mappingName = ""

		
  def readCmdParam(self):
  #https://docs.python.org/3/library/argparse.html#choices
  #https://chris48s.github.io/blogmarks/python/2020/12/07/stdin-or-file.html
    parser = argparse.ArgumentParser(
        description='A pdf tool to combine, convert and pdf documents with the help of qr codes'
    )

#    parser.add_argument(
#        'file',
#        nargs='?',
#        help='Input file, if empty stdin is used',
#        type=argparse.FileType('r'),
#        default=sys.stdin,
#    )

    parser.add_argument('-m', '--mode',
		default='qr',
        choices=['qr', 'pdfa'],
		help='Runs PyPDF and find and separate pages with qr codes {qr} or simple convert pdf document found in input folder {pdfa}') 
					
    args = parser.parse_args()

    print(args.mode)
    return args
   
	  
	
   
#    if args.file.isatty():
#        parser.print_help()
#        return 0

		
 #   sys.stdout.write(args.file.read())
 #   return 0
  

    


runner = Runner()

args = runner.readCmdParam()

documentList = []
runner.createDocumentList(documentList)

if args.mode == 'qr':
  runner.convertPDFtoImage(documentList)
  runner.findEmptyPages(documentList)
  runner.extractRoiImage(documentList)
  runner.extractQrCode(documentList)
  outputDocumentList = runner.mergePdfFiles(documentList)
  runner.convertPdfToArchivePdf(outputDocumentList, runner.configMicroservice["workDirectory"] )
  runner.cmdLineInput(outputDocumentList)
  runner.cleanup()
  
if args.mode == "pdfa":
  outputDocumentList = []
  for document in documentList:
    outputFilePath =  document.getFileName()
    outputDocumentList.append(outputFilePath)
    print(outputFilePath)
  runner.convertPdfToArchivePdf(outputDocumentList,runner.configMicroservice["inputDirectory"])

