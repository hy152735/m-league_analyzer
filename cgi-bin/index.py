#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# python -m http.server --cgiで起動後、
# http://localhost:8000/にアクセスする。終了はctrl + Pause
from jinja2 import Environment, FileSystemLoader

import os
import sys

TMP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(TMP_DIR)
import analysis


def application(environ, start_response):
    """
    html作成クラス
    Parameters
    ----------
    environ
    start_response

    Returns
    -------

    """
    jinja2_env = Environment(loader=FileSystemLoader(os.path.join(TMP_DIR, '../', 'template'), encoding='utf8'))
    start_response('200 OK', [('Content-Type', 'text/html')])
    method = environ.get('REQUEST_METHOD')

    if method == 'POST':
        # 開始ボタン押下後
        # 2019レギュラーシーズン
        # hashimoto = analysis.MyTeam('hsmt', ['小林剛', '園田賢', '瑞原明奈', '白鳥翔'])
        # rachi = analysis.MyTeam('東豚', ['鈴木たろう', '魚谷侑未', '松本吉弘', '日向藍子'])
        # umeda = analysis.MyTeam('UMD', ['佐々木寿人', '茅森早香', '多井隆晴', '内川幸太郎'])
        # sasamura = analysis.MyTeam('パンダ', ['朝倉康心', '勝又健志', '和久津晶', '瀬戸熊直樹'])
        # yosei = analysis.MyTeam('妖精', ['滝沢和典', '近藤誠一', '高宮まり', '藤崎智'])

        # 2019セミファイナル
        # hashimoto = analysis.MyTeam('hsmt', ['小林剛', '瑞原明奈', '白鳥翔'])
        # rachi = analysis.MyTeam('東豚', ['魚谷侑未', '松本吉弘', '日向藍子'])
        # umeda = analysis.MyTeam('UMD', ['佐々木寿人', '茅森早香', '多井隆晴'])
        # sasamura = analysis.MyTeam('パンダ', ['朝倉康心', '和久津晶', '瀬戸熊直樹'])
        # yosei = analysis.MyTeam('妖精', ['近藤誠一', '高宮まり', '藤崎智'])

        # 2020レギュラーシーズン
        #hashimoto = analysis.MyTeam('hsmt', ['小林剛', '黒沢咲', '堀慎吾', '勝又健志'])
        #rachi = analysis.MyTeam('東豚', ['魚谷侑未', '松本吉弘', '鈴木たろう', '藤崎智'])
        #umeda = analysis.MyTeam('UMD', ['佐々木寿人', '園田賢', '朝倉康心', '瑞原明奈'])
        #sasamura = analysis.MyTeam('パンダ', ['多井隆晴', '茅森早香', '瀬戸熊直樹', '村上淳'])
        #yosei = analysis.MyTeam('妖精', ['近藤誠一', '滝沢和典', '高宮まり', '白鳥翔'])

        # # 2021 レギュラーシーズン
        # hashimoto = analysis.MyTeam('hsmt', ['小林剛', '黒沢咲', '堀慎吾', '勝又健志'])
        # rachi = analysis.MyTeam('東豚', ['魚谷侑未', '松本吉弘', '本田朋広', '二階堂亜樹'])
        # umeda = analysis.MyTeam('UMD', ['佐々木寿人', '松ヶ瀬隆弥', '鈴木たろう', '岡田紗佳'])
        # sasamura = analysis.MyTeam('パンダ', ['多井隆晴', '茅森早香', '瀬戸熊直樹', '村上淳'])
        # yosei = analysis.MyTeam('妖精', ['近藤誠一', '滝沢和典', '日向藍子', '園田賢'])

        # 2022 レギュラーシーズン
        # hashimoto = analysis.MyTeam('hsmt', ['小林剛', '堀慎吾', '勝又健志', '丸山奏子'])
        # rachi = analysis.MyTeam('東豚', ['魚谷侑未', '松本吉弘', '仲林圭', '滝沢和典'])
        # umeda = analysis.MyTeam('UMD', ['佐々木寿人', '松ヶ瀬隆弥', '鈴木たろう', '伊達朱里紗'])
        # sasamura = analysis.MyTeam('パンダ', ['多井隆晴', '黒沢咲', '村上淳', '内川幸太郎'])

        # 2023 レギュラーシーズン
        # hashimoto = analysis.MyTeam('hsmt', ['佐々木寿人', '多井隆晴', '仲林圭', '鈴木優', '浅見真紀'])
        # rachi = analysis.MyTeam('東豚', ['猿川真寿', '松ヶ瀬隆弥', '松本吉弘', '渡辺太', '魚谷侑未'])
        # umeda = analysis.MyTeam('UMD', ['伊達朱里紗', '小林剛', '堀慎吾', '鈴木大介', '白鳥翔'])
        # sasamura = analysis.MyTeam('パンダ', ['園田賢', '勝又健志', '内川幸太郎', '瑞原明奈','黒沢咲'])
        # daisu = analysis.MyTeam('ダイス', ['菅原千瑛', '岡田紗佳', '中田花奈', '鈴木たろう', '高宮まり'])

        # 2024 レギュラーシーズン
        hashimoto = analysis.MyTeam('hsmt', ['仲林圭', '竹内元太', '浅井堂岐', '浅見真紀'])
        rachi = analysis.MyTeam('東豚', ['松本吉弘', '佐々木寿人', '松ヶ瀬隆弥', '日向藍子'])
        umeda = analysis.MyTeam('UMD', ['堀慎吾', '伊達朱里紗', '多井隆晴', '鈴木優'])
        daisu1 = analysis.MyTeam('ダイス１', ['二階堂瑠美', '鈴木大介', '菅原千瑛', '中田花奈'])
        daisu2 = analysis.MyTeam('ダイス２', ['内川幸太郎', '高宮まり', '本田朋広', '白鳥翔'])

        #team_list = [hashimoto, rachi, umeda, sasamura, yosei]
        #team_list = [hashimoto, rachi, umeda, sasamura]
        #team_list = [hashimoto, rachi, umeda, sasamura, daisu]
        team_list = [hashimoto, rachi, umeda, daisu1, daisu2]

        dal = analysis.DataAnalysis()
        dal.make_team_score(team_list)
        # スコア順に並び変え
        team_list = sorted(team_list, key=lambda t: t.total_score, reverse=True)

        template = jinja2_env.get_template('m_score.html')
        html = template.render(team_list=team_list, team_score_map=dal.team_score_map, team_rank_map=dal.team_rank_map, team_maxmin_map=dal.team_maxmin_map)
    else:
        # 初期画面
        template = jinja2_env.get_template('index.html')
        html = template.render()

    return [html.encode('utf-8')]


if __name__ == '__main__':
    from wsgiref.handlers import CGIHandler

    CGIHandler().run(application)
