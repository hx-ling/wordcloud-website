import base64
import jieba
from flask import Flask, render_template, request, jsonify
from imageio import imread
from wordcloud import WordCloud
import os
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


# 接收txt文件
@app.route('/upload/file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        try:
            file = request.files['file']
            content = file.read().decode("utf-8")
            return jsonify({'data': content}), 200
        except:
            return jsonify({'code': -1, 'msg': '文件上传失败!'}), 500
        finally:
            pass


# jieba分词
@app.route('/cut/jieba', methods=['POST'])
def cut_jieba():
    if request.method == 'POST':
        try:
            content = request.json.get('content', None)
            segment = jieba.lcut(content)
            return jsonify({'data': segment}), 200
        except:
            return jsonify({'code': -1, 'msg': 'Jieba分词失败!'}), 500
        finally:
            pass


# 去停用词
@app.route('/remove/stopwords', methods=['POST'])
def remove_stopwords():
    if request.method == 'POST':
        try:
            segment = request.json.get('segment', None)
            new_segment = [x for x in segment if x not in ['\n', ' ']]
            with open("stopwords.txt", 'r', encoding='gbk') as f:
                stopwords = f.readlines()
                stopwords = [x.strip() for x in stopwords]
            words = [x for x in new_segment if x not in stopwords]
            return jsonify({'data': words}), 200
        except:
            return jsonify({'code': -1, 'msg': '去停用词失败!'}), 500
        finally:
            pass

# 生成词云图
@app.route('/genetate/cloud', methods=['POST'])
def generate_cloud():
    if request.method == 'POST':
        try:
            words = request.json.get('words', None)
            mask = imread(r'mask.jpg')  # 设置词云背景图
            wordcloud = WordCloud(font_path="simhei.ttf",  # 设置字体可以显示中文
                                  background_color="white",
                                  mask=mask,
                                  scale=2,  # 缩放比例，清晰度
                                  # width=20, height=20  # 设置图片默认的大小,若有背景图片则依照背景图片大小,
                                  )
            wc = wordcloud.generate(words)
            wc.to_file("wordcloud.jpg")
            with open("wordcloud.jpg", 'rb') as f:
                image = f.read()
            image_base64 = str(base64.b64encode(image), encoding='utf-8')
            return jsonify({'data': image_base64}), 200
        except:
            return jsonify({'code': -1, 'msg': '生成词云图失败!'}), 500
        finally:
            pass

# 下载词云图
@app.route("/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = os.getcwd()  # 假设在当前目录
    return send_from_directory(directory, filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
