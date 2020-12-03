import numpy as np

from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage)
from keras.models import load_model
from keras.preprocessing import image

app = Flask(__name__)

ACCESS_TOKEN = "VAqqFP1U61w3pdHETzfUwYBnbvDp5rclpmunxKzPnEIMZ5PvhvgyvkWrBKHavnuZUKozs96l19GMTKlq6RKqV6K3R5eIB16rUis0AHjj+TShWYY0VGjTFyKyU3fUS7B3vBT7qm67n+mH5iAUAllkTgdB04t89/1O/w1cDnyilFU="
SECRET = "7272c7610b27cc58a09b0edbcf4ae998"

FQDN = "https://toumoriko.herokuapp.com"


line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Requestbody: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return'OK'

#LINEに画像が送られてきた時の発生イベント
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with open("static/"+event.message.id+".jpg", "wb") as f:
        f.write(message_content.content)

        test_url = "./static/"+event.message.id+".jpg"
##########ここからAIモデル＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃＃
        img = image.load_img(test_url, target_size=(150, 150))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0

        model = load_model('absporo.h5')
        result_predict = model.predict(x)
        #res = result_predict[0]

        res = np.array(result_predict)
        if res[0] < 0.5:
            res[0] = 1 - res[0]
            print(res[0])
            okashi = "アポロ"
            per = res[0] * 100
    
        elif res[0]>=0.5:
            okashi = "とうもりこ"
            per = res[0] * 100
        np.set_printoptions(precision=1)
        text = "これは"+ str(per).strip("[]") + "%の確率で" + okashi + "です。"
##############################################################
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
      
if __name__ == "__main__":
    app.run()
