import os
import re 
# import qrdetect
import gspread
import pytesseract
from app import app
import tensorflow as tf
from datetime import datetime
# from pyzbar import pyzbar
# from pyzbar.pyzbar import decode
from flask import request, jsonify
from werkzeug.utils import secure_filename
from oauth2client.service_account import ServiceAccountCredentials
# import base64

model_path = 'qrmodel.tflite'
# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
DETECTION_THRESHOLD = 0.5


scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name("novice-342709-9a8f64515cff.json", scopes)
file = gspread.authorize(credentials) 
sheet = file.open("Student Data").get_worksheet(0)
header = ["Gr. No.", "Full Name", "Mo.No.", "Date of Birth", "Course", "Passing Year"]
# sheet.insert_row(header)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    print("in allowed file''''''''''", filename)
    allowd = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return allowd

@app.route('/input', methods=['GET', 'POST'])

def upload_file():
    file = request.files['file']
    print("file", file)
    if request.method == "GET":
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            resp = jsonify({"Successfully GET file": filename})
            resp.status_code = 200
            return resp
        
    elif request.method == "POST":
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            print("file name =====================", filename)

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            resp = jsonify({"filename": filename, "Status":200})
            print("resp!!!!!!!!!!!!!!!",resp)
            resp.status_code = 200
            imag = 'Crop/'+filename
            
            # qrdetect.run_odt_and_draw_results(imag, interpreter, threshold=DETECTION_THRESHOLD)
        
            #OCR }}}}}}}}}}}}}}}}
            # print("ID_CARD_OCR_:\n",pytesseract.image_to_string(imag, lang='eng'))

            list = []
            p = pytesseract.image_to_string(imag, lang='eng')
            #extracted text without new line }}}}}}}}}}}}}
            p = p.replace("\n", " ")
            print("ID_CARD_OCR_:\n\n", p)
            try:
                # extract Gr.No. }}}}}}}}}}}}}}}}}
                r = re.search(r'\d+', p).group()
                grno = list.append(r)
                
                # Remove all characters before Gr.No. from string
                pattern  = ".*" + r 
                nme = re.sub(pattern, '', p)
                res = nme[0:30]
                nam=re.sub('[a-z]', "", res)
                # print("\nFull Name: ",nam)
                pattern  = ".*" + res 
                # Remove all characters before name from string
                sr = re.sub(pattern, '', nme)
                a = sr.split(",")
                # print("address start,,,,,,,,,,,", a)

                #remove start-end space from str}}}}}}}}}}
                name = list.append(" ".join(nam.split()))

                mono = sr.split(":")[1]
                mb = mono.split("/")[0]
                mbi = mono.split("/")[1]
                mn = re.search(r'\d+', mbi).group()
                # print("Mo.No. :",mb,"/", mn)
                mi = mb+"/"+mn
                mo_no = list.append(" ".join(mi.split()))
                
                match_dt = re.search(r'\d{2}-\d{2}-\d{4}', mbi)
                # feeding format
                dateStr = datetime.strptime(match_dt.group(), '%d-%m-%Y').date()
                dt = dateStr.strftime("%d-%m-%Y")
                dob = list.append(dt)

                crc = ['M.Ed.', 'MEd.', 'M.Ed', 'med', 'mEd', 'm.ed.', 'BCA', 'bca', 'B.Ed.', 'bed', 'BED', 'Bcom', 'BCOM', 'B.COM.', 'B.com', 'B.com.', 'bcom', 'b.com', 'b.com.', 'bba', 'BBA', 'BSC', 'bsc', 'Bsc', 'bSC', 'bsC', 'bSc',
                    'msc-chem', 'MSCchem', 'MSC', 'Msc', 'MSc', 'msc', 'MsC', 'MSCCHEM', 'Msc-chem', 'Msc-Chem',  'msc-it', 'MSCit', 'MSC-it', 'MscIT', 'MSc-IT', 'msc-IT', 'MSC-IT', 'Msc-it', 'MSc-it']

                c = [word for word in crc if word in mbi]
                course = list.append(" ".join(c))
                            
                match_y = re.findall(r'\d{4}-\d{4}', mbi)
                # print("Passing year: ",match_y)
                passy = list.append(" ".join(match_y))
            except:
                pass
            l = len(sheet.col_values(1)) 
            l += 1           
            sheet.update('A'+str(l),[list])
            print("Data::::::::::::::", list)
            
            return resp   
    return 'file'

if __name__=="__main__":
    # context = ('/etc/letsencrypt/live/npr.mylionsgroup.com/cert.pem','/etc/letsencrypt/live/npr.mylionsgroup.com/privkey.pem')
    app.run(host=os.getenv('IP', '0.0.0.0'), 
            port=int(os.getenv('PORT', 8011)))
            # , ssl_context=context)