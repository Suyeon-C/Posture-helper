import cv2
import tensorflow
from PIL import Image, ImageOps
import numpy as np
import beepy
import kakao_utils

# 내장 카메라 사용 :0
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


def beepsound():
    beepy.beep(sound=6)

# 카카오톡 메세지에 담을 내용 
def send_music_link():
    KAKAO_TOKEN_FILENAME = "kakao_message/kakao_token.json"
    KAKAO_APP_KEY = "rest api 적기"
    tokens = kakao_utils.update_tokens(KAKAO_APP_KEY, KAKAO_TOKEN_FILENAME)

    template = {
        "object_type": "text",
        "text": "자세가 틀렸어요! 아래 영상을 보고 다시 해보세요",
        "link": {
            "web_url": "https://www.youtube.com/watch?v=IfJcq4LDXKE",
            "mobile_web_url": "https://www.youtube.com/watch?v=IfJcq4LDXKE"
        },
        "button_title": "바른 자세 확인하기"
    }

    res = kakao_utils.send_message(KAKAO_TOKEN_FILENAME, template)
    if res.json().get('result_code') == 0:
        print('메시지를 성공적으로 보냈습니다.')
    else:
        print('메시지를 보내지 못했습니다. 오류메시지 : ', res.json())


# 이미지 전처리 함수
def preprocessing(frame):
    size = (224,224)
    frame_resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    frame_normalized = (frame_resized.astype(np.float32) / 127.0) - 1
    frame_reshaped = frame_normalized.reshape((1, 224, 224, 3))

    return frame_reshaped


# Load the model
model = tensorflow.keras.models.load_model('keras_model.h5')

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1.
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Replace this with the path to your image
image = Image.open('kakao_message/wrong.jpg')

#resize the image to a 224x224 with the same strategy as in TM2:
#resizing the image to be at least 224x224 and then cropping from the center
size = (224, 224)
image = ImageOps.fit(image, size, Image.ANTIALIAS)

#turn the image into a numpy array
image_array = np.asarray(image)

# display the resized image
image.show()

# Normalize the image
normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

# Load the image into the array
data[0] = normalized_image_array

# run the inference
prediction = model.predict(data)
print(prediction)

model_filename = 'keras_model.h5'
model = tensorflow.keras.models.load_model(model_filename)

cnt = 1  
while True:
    ret, frame = capture.read()
    if ret == True:
        print("보고있습니다")

    frame_fliped = cv2.flip(frame,1) 
    cv2.imshow("VideoFrame", frame_fliped)

    if cv2.waitKey(200) > 0:
        break

    # 데이터 전처리
    preprocessed = preprocessing(frame_fliped)
    prediction = model.predict(preprocessed)
        
    if prediction[0,0] < prediction[0,1]:
        print('잘못된 자세')
        cnt += 1

        # 잘못된 자세로 1분간 운동 시, 알람소리 & 카카오톡 보내기
        if cnt % 30 == 0:
            cnt = 1
            print('잘못된 자세 입니다')
            beepsound()
            send_music_link()
            break # 1번만 알람이 오면 프로그램을 정지시킴(반복을 원한다면, 주석으로 막기)
    else:
        print('좋은 자세 입니다.')
        cnt = 1

capture.release()
cv2.destroyAllWindows