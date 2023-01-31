# PyPDF
A tool for handling PDF files:

* Script dedects QR codes in top right corner (region of interest) of an DIN A4 pdf document
* It then finds empty pages and eleminates them
* It combines alle pages between next QR code found to a single document
* It then converts pdf to an archive pdf pdf/a-1 and pdf/b-1 (done overy spring boot micro service -not part of this script)
* After manual quality check it can automatically move the document to the correct destination path

Examplex config.
Please note that all paths must end with slashes.

# Installation guide
1. Install python version 3.9.2 or higher.

2. Clone this git repository.

~~~
git clone https://github.com/samatthias/PyPDF.git
~~~

3. Create config folder directly in the root directory and a config.json file in this directory. The structure of the json config must mucht the one below.

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


4. Create virtual python environment.
4.1. Install virtual environment
~~~
pip install virtualenv
~~~
4.2 Create a virtual environment within the root directory
~~~
python -m venv venv
~~~
4.3 Activate virtual environment
~~~
venv/Scripts/activate.{bat,ps1) for windows
venv/Scripts/activate.sh for linux
~~~

5. Install requirements.txt
~~~
pip install -r requirements.txt
~~~

