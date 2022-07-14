import cv2
import numpy as np
import tensorflow as tf
from pyzbar import pyzbar
# from pyzbar.pyzbar import decode
# import glob
# from PIL import Image

# model_path = 'qrmodel.tflite'

# # Load the labels into a list
# classes = ['QR_CODE']

# Define a list of colors for visualization
# COLORS = np.random.randint(0, 255, size=(len(classes), 3), dtype=np.uint8)

def preprocess_image(image_path, input_size):
  """Preprocess the input image to feed to the TFLite model"""
  img = tf.io.read_file(image_path)
  img = tf.io.decode_image(img, channels=3)
  img = tf.image.convert_image_dtype(img, tf.uint8)
  original_image = img
  resized_img = tf.image.resize(img, input_size)
  resized_img = resized_img[tf.newaxis, :]
  resized_img = tf.cast(resized_img, dtype=tf.uint8)
  return resized_img, original_image

def detect_objects(interpreter, image, threshold):
  """Returns a list of detection results, each a dictionary of object info."""

  signature_fn = interpreter.get_signature_runner()

  # Feed the input image to the model
  output = signature_fn(images=image)

  # Get all outputs from the model
  count = int(np.squeeze(output['output_0']))
  scores = np.squeeze(output['output_1'])
  # classes = np.squeeze(output['output_2'])
  boxes = np.squeeze(output['output_3'])
  results = []
  for i in range(count):
    if scores[i] >= threshold:
      result = {
        'bounding_box': boxes[i],
        # 'class_id': classes[i],
        'score': scores[i]
      }
      results.append(result)
  return results

def run_odt_and_draw_results(image_path, interpreter, threshold=0.5):
  """Run object detection on the input image and draw the detection results"""
  # Load the input shape required by the model
  _, input_height, input_width, _ = interpreter.get_input_details()[0]['shape']

  # Load the input image and preprocess it
  preprocessed_image, original_image = preprocess_image(
      image_path,
      (input_height, input_width)
    )

  # Run object detection on the input image
  results = detect_objects(interpreter, preprocessed_image, threshold=threshold)

  # Plot the detection results on the input image
  original_image_np = original_image.numpy().astype(np.uint8)
  for obj in results:
    # Convert the object bounding box from relative coordinates to absolute
    # coordinates based on the original image resolution
    ymin, xmin, ymax, xmax = obj['bounding_box']
    xmin = int(xmin * original_image_np.shape[1])
    xmax = int(xmax * original_image_np.shape[1])
    ymin = int(ymin * original_image_np.shape[0])
    ymax = int(ymax * original_image_np.shape[0])

    # Find the class index of the current object
    # class_id = int(obj['class_id'])

    # Draw the bounding box and label on the image
    # color = [int(c) for c in COLORS[class_id]]
    # boundb = cv2.rectangle(original_image_np, (xmin, ymin), (xmax, ymax), color, 2)
    boundb = cv2.rectangle(original_image_np, (xmin, ymin), (xmax, ymax), (0,255,102), 2)
    
    crop = boundb[ymin:ymax, xmin:xmax]
    
    con = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    gaussian_blur = cv2.GaussianBlur(con, (7,7), 2)
    sharpened1 = cv2.addWeighted(con, 1.5, gaussian_blur, -0.5, 0)

    cv2.imwrite("cropQR/"+'crop.jpg', sharpened1)
    # cv2.imwrite("cropQR/"+'crop.jpg', crop)
    
    # read the QRCODE image
    # qrc = cv2.imread(crop)
    
    # initialize the cv2 QRCode detector
    # detector = cv2.QRCodeDetector()
    # # detect and decode
    # data, vertices_array, binary_qrcode = detector.detectAndDecode(qrc)
    # data, vertices_array, binary_qrcode = detector.detectAndDecode(crop)
    
    # # if there is a QR code
    # # print the data
    # if vertices_array is not None:
    #     print("QRCode data:")
    #     print(data)
    # else:
    #     print("There was some error")
    
    # barcodes = pyzbar.decode(crop)
    
    for barcode in pyzbar.decode(sharpened1):
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        print("Decoded_Data_:", barcodeData, '\n', barcodeType)
          
  # Return the final image
  original_uint8 = original_image_np.astype(np.uint8)
  return original_uint8

# DETECTION_THRESHOLD = 0.5

# i=glob.glob('Crop/*.jpg')
# TEMP_FILE = i[-1]
# TEMP_FILE = glob.glob('Crop/*.jpg')

# TEMP_FILE = 'Crop/crop_1657707298127.jpg'

# Load the TFLite model
# interpreter = tf.lite.Interpreter(model_path=model_path)
# interpreter.allocate_tensors()

# Run inference and draw detection result on the local copy of the original file
# detection_result_image = run_odt_and_draw_results(
#     TEMP_FILE,
#     interpreter,
#     threshold=DETECTION_THRESHOLD
# )

# # Show the detection result
# image  = Image.fromarray(detection_result_image)
# image.show()