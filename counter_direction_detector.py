# -*- coding: utf-8 -*-
"""counter_direction_detector.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZNyaVEM7w5iyrG3pY_kZMHgqyQ3P23HT
"""

!pip install yolov5

print(tf.__version__)

!python --version

import tensorflow as tf
print(tf.__version__)

import yolov5
import cv2
import os
from google.colab.patches import cv2_imshow
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np

# load pretrained model
model = yolov5.load('yolov5s.pt')

# parámetros del modelo
model.conf = 0.25  # NMS confidence threshold
model.iou = 0.45  # NMS IoU threshold
model.agnostic = False  # NMS class-agnostic
model.multi_label = False  # NMS multiple labels per box
model.max_det = 100  # maximum number of detections per image

try:
  model_class = load_model("keras_model.h5", compile=False)
except IOError:
  print('error en la carga del modelo h5')
finally:
  print(' ... carga modelo ok!')

try:
  class_names = open("labels.txt", "r").readlines()
except IOError:
  print('error en la carga del fichero con etiquetas')
finally:
  print(' ... carga etiquetas ok!')

pictures = []

for filename in os.listdir("/content"):
    if filename.endswith(".jpg"):
        #print(filename)
        pictures.append('/content/'+filename)

def do_isolate_car(one_image):
  img = one_image
  raw_img = cv2.imread(img)
  cv2_imshow(raw_img)

  # inferencia
  results = model(img)
  results = model(img, size=1280)
  results = model(img, augment=True)

  # resultados
  predictions = results.pred[0]
  boxes = predictions[:, :4] # x1, y1, x2, y2
  scores = predictions[:, 4]
  categories = predictions[:, 5]
  #results.show()

  # salvar imagen resultado
  results.save(save_dir='results/')

  df = results.pandas().xyxy[0]
  df_only_cars = df[((df['name']=='car') | (df['name'] == 'truck')) & (df['confidence'] > 0.5)]

  # TODO determinar la ventana mas grande

  x_width_ant = 0
  index = 0
  for i in range (df_only_cars.shape[1]):
    x_width = int(df_only_cars.iloc[i]['xmax'] - df_only_cars.iloc[i]['xmin'])
    if x_width > x_width_ant:
      x_width_ant = x_width
      index = i


  if df_only_cars.shape[0] > 0:
    # si se ha detectado algún coche capturamos el de mayor confidence
    #print(df_only_cars.iloc[0])
    x0 = int(df_only_cars.iloc[index]['xmin'])
    y0 = int(df_only_cars.iloc[index]['ymin'])
    x1 = int(df_only_cars.iloc[index]['xmax'])
    y1 = int(df_only_cars.iloc[index]['ymax'])
    image = cv2.imread(img)
    cropped_image = image[y0:y1, x0:x1]
    dim = (223, 223)
    resized = cv2.resize(cropped_image, dim, interpolation = cv2.INTER_AREA)
    #cv2_imshow(resized)
    cv2.imwrite('results/'+ one_image[one_image[1:].find('/')+2:], resized)
  else:
    print('no cars found')

  return 'results/'+ one_image[one_image[1:].find('/')+2:]

#for some_pic in pictures:
 # do_inference(some_pic)

#import shutil
#shutil.make_archive('train_cars', 'zip', '/content/results')

def do_inference(image_file):

  try:
    image = Image.open(image_file).convert("RGB")
  except IOError:
    print ('error en la carga de la imagen')
    error = -1
    actual = ''
    predicted = ''
  finally:

    # ajustamos el tamaño de la imagen al formato requerido
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.LANCZOS)

    # mapa de bits a array numpy
    image_array = np.asarray(image)

    # normalizamos los valores de color (0..255) a -1..1
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # trasladamos la imagen al vector de datos con la estructura de la entrada a la red neuronal
    data[0] = normalized_image_array

    # aplicamos inferencia a los datos obtenidos
    prediction = model_class.predict(data)

    # tomamos la etiqueta correspondiente al valor con mayor probabilidad en la clasificación
    index = np.argmax(prediction)
    display(image)

    # capturamos el resultado etiquetado en los datos
    if index == 0:
      return 'front'
    elif index == 1:
      return 'back'
    else:
      return 'none'

    return(index)

do_inference(do_isolate_car(pictures[46]))



print(pictures[40])

#cv2.destroyAllWindows()