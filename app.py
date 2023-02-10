from flask import Flask, render_template, request, jsonify
from jinja2 import Environment, FileSystemLoader
import json

app = Flask(__name__)

# ランキング表示ページ
@app.route("/ranking-view")
def ranking_view():
    with open("./parameter.json", "r") as f:
        dict = json.load(f)
    return render_template("ranking-view.html", score=dict["score"])

# ランキング編集ページ
@app.route("/ranking-edit")
def ranking_edit():
    return render_template("ranking-edit.html")

# 漢字オセロページ
@app.route("/othello")
def othello():
    # CSSファイルの生成
    env = Environment(loader=FileSystemLoader("./static/", encoding="utf8"))
    tmpl = env.get_template("othello.j2")
    css = tmpl.render()
    with open("./static/othello.css", "w") as f:
        f.write(str(css))
    # HTML埋め込み用のパラメータの読み込み
    with open("./parameter.json", "r") as f:
        dict = json.load(f)
    # HTMLのレンダリング
    return render_template("othello.html", othello_board=dict["othello_board"], score_board=dict["score_board"])

# オセロにおいて取得可能な駒を検索
def search_pieces(id, goal, step, othello_board, friend_color):
    pieces = []
    enemy_color = "blue" if friend_color == "red" else "red"
    if goal != None:
        k = 0
        for now_id in range(id, goal, step):
            if k == 0:
                pieces.append(now_id)
            elif othello_board[now_id-1]["status"] == enemy_color:
                pieces.append(now_id)
            elif othello_board[now_id-1]["status"] == friend_color:
                return pieces
            else:
                break
            k += 1
    else:
        g = 37 if step > 0 else 0
        k = 0
        for now_id in range(id, g, step):
            if k == 0:
                pieces.append(now_id)
            else:
                if othello_board[now_id-1]["status"] == enemy_color:
                    pieces.append(now_id)
                elif othello_board[now_id-1]["status"] == friend_color:
                    return pieces
                else:
                    break
                if now_id in [1, 2, 3, 4, 5, 6, 7, 12, 13, 18, 19, 24, 25, 30, 31, 32, 33, 34, 35, 36]:
                    break
            k += 1
    return []


# 漢字オセロ処理
# 金色の駒はそれを開封するときに、白色の駒はその駒の漢字を正答したときにクリックすること
# オセロ処理をして更新されたparameter.jsonを返す
@app.route("/_othello-processing")
def othello_processing():
    # 駒のステータスと両チームの得点を取得
    with open("./parameter.json", "r") as f:
        dict = json.load(f)
    othello_board = dict["othello_board"]
    score_board = dict["score_board"]
    # 選んだ駒の番号と色をJSON経由で取得
    id = int(request.args.get("id", 0, type=str)[2:])
    classes = request.args.get("class", 0, type=str).split(" ")
    # 今の手番の色を判定（赤が先攻、青が後攻）
    friend_color = "red" if (score_board[0]["score"] + score_board[1]["score"]) % 2 == 0 else "blue"
    # 金色の駒を選んだ場合
    if "gold" in classes:
        # 開封して駒を白にする
        othello_board[id-1]["status"] = "white"
    # 白色の駒を選んだ場合
    elif "white" in classes:
        # 取れる駒の検索
        # 上方向
        up = search_pieces(id, 0, -6, othello_board, friend_color)
        # 下方向
        bottom = search_pieces(id, 37, 6, othello_board, friend_color)
        # 左方向
        left = search_pieces(id, 6*((id-1)//6), -1, othello_board, friend_color)
        # 右方向
        right = search_pieces(id, 6*((id-1)//6+1)+1, 1, othello_board, friend_color)
        # 斜め左上方向
        upper_left = search_pieces(id, None, -7, othello_board, friend_color)
        # 斜め右上方向
        upper_right = search_pieces(id, None, -5, othello_board, friend_color)
        # 斜め左下方向
        lower_left = search_pieces(id, None, 5, othello_board, friend_color)
        # 斜め右下方向
        lower_right = search_pieces(id, None, 7, othello_board, friend_color)
        # 検索結果をまとめる
        change_pieces = list(set(up + bottom + left + right + upper_left + upper_right + lower_left + lower_right))
        # 取れた駒を自分の色にする
        if len(change_pieces) != 1:
            for change_id in change_pieces:
                othello_board[change_id-1]["status"] = friend_color
    # 得点の更新
    score = {"red": 0, "blue": 0}
    for piece in othello_board:
        if piece["status"] == "red":
            score["red"] += 1
        elif piece["status"] == "blue":
            score["blue"] += 1
    score_board[0]["score"] = score["red"]
    score_board[1]["score"] = score["blue"]
    # JSONファイルにオセロ操作済みの駒のステータスと両チームの得点を書き出す
    with open("./parameter.json", "w") as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)
    return jsonify(dict)

# ランキング処理
@app.route("/_ranking-processing")
def ranking_processing():
    player = request.args.get("player", "ゲスト", type=str)
    print("hello")
    with open("./parameter.json", "r") as f:
        dict = json.load(f)
    score = dict["score"]
    is_done = False
    k = -1
    for p in score:
        k += 1
        name = p["name"]
        if name == player:
            score[k]["points"] += 1
            is_done = True
            break
    if not is_done:
        score.append({"name": player, "points": 1})
    dict["score"] = sorted(score, key=lambda x:x["points"], reverse=True)
    with open("./parameter.json", "w") as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)
    return jsonify(dict)

@app.route("/_update-ranking")
def update_ranking():
    with open("./parameter.json", "r") as f:
        dict = json.load(f)
    print("hello2")
    return jsonify(dict)