from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/_add_numbers')
def add_numbers():

    # request.args.get(クエリパラメータ、[デフォルト値]、[値の型])
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)

    # jsonify({key:value}): 引数に与えられた辞書形式データをJsonに変換する。
    # またその際にheaderの"content-type"を'application/json'に変換してくれる。
    return jsonify({'result': a+b})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
