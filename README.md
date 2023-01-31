# PyPDF
A tool for handling PDF files:

* Script dedects QR codes in top right corner (region of interest) of an DIN A4 page document
* It then finds empty pages and eleminates them
* It combines alle pages between next QR code found to a single document
* It then converts pdf to an archive pdf pdf/a-1 and pdf/b-1 (done overy spring boot micro service -not part of this script)
* After manual quality check it can automatically move the document to the correct destination path

Examplex config.
Please note that all paths must end with slashes.
~~~
{
    "configVersion": "1",
    "pdfa_convert_url": "<url>",
    "rootDirectory":"<rootpath>\\",
    "inputDirectory":"<rootpath>\\<inputDirectory>\\",
    "workDirectory":"<rootpath>\\<workDirectory>\\",
    "outputDirectory":"<rootpath>\\<outputkDirectory>\\",
    "tmpPDFFilename":"tmp.pdf",
    "roiHeightDivider":"6",
    "roiWidthDivider":"3",
    "thresholdEmptyPage":"99.98",
    "mappings" : [
        {
            "name":"<name1>",
            "destinationDirectory":"<destPath>\\"
        },
        {
            "name":"<name2>",
            "destinationDirectory":"<destPath>\\"
        }
    ]

 }

 ~~~