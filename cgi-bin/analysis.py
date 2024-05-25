#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class MyTeam:
    """
    チーム情報
    """

    def __init__(self, team_name, member):
        self.team_name = team_name
        self.member = member
        self.total_score = 0.0
        self.member_score = {}


class DataAnalysis:
    def __init__(self):
        """
        公式サイトからhtml情報を取得
        """
        #res = requests.get('http://localhost:8000/m_league.html')
        res = requests.get('https://m-league.jp/', verify=False)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        self.soup = BeautifulSoup(res.content, "html.parser")

        self.player_score_map = None
        self.team_score_map = None

    @property
    def make_player_score(self):
        """
        各選手の集計結果を作成する

        Returns
        -------
        player_score_map　:　dict
            ゲームごとの全選手の集計データ（key：game_count、value：（key：player_name、value：score））

        """
        # トータルスコア（key：player_name、value：score）
        sum_score_map = {}

        # 日ごとトータルスコア（key：game_count、value：sum_score_map）
        player_score_map = {}

        games_result = self.soup.find_all(class_="p-gamesResult")
        game_count = 0
        for one_day_result in games_result:
            game_day = one_day_result.find(class_="p-gamesResult__date").text
            if game_day == '/日(曜日)':
                continue

            # # セミファイルナル仕様（3/16以降まで飛ばす）
            # game_only_day = game_day.split('(')[0].split('/')
            # if int(game_only_day[0]) != 3:
            #     continue
            # if int(game_only_day[1]) < 15:
            #     continue

            game_count += 1
            result_column = one_day_result.find_all(class_="p-gamesResult__rank-item")
            for one_result in result_column:
                player_name = one_result.find(class_="p-gamesResult__name").text.strip()
                # row_score 例: ▲53.3pt
                row_score = one_result.find(class_="p-gamesResult__point").text.strip()
                # player_score 例：　-53.3
                player_score = row_score.replace('▲', '-').replace('pt', '')
                # 2022/01/11 チョンボ対応　チョンボの時は65.5(-20)となるので、括弧を外して加算する
                if ('(' in player_score):
                    player_score = player_score.replace('(', '').replace(')', '')
                    # 65.5-20 = 45.5
                    player_score = eval(player_score)

                    # score_map作成 小数点の誤差が発生するため、四捨五入を行う
                sum_score_map[player_name] = round(sum_score_map.get(player_name, 0.0) + float(player_score), 1)

            # game_countごとの結果を保管
            player_score_map[game_count] = sum_score_map.copy()

        self.player_score_map = player_score_map
        return player_score_map

    def make_team_score(self, team_list):
        """

        Parameters
        ----------
        team_list : list
            チームクラスのリスト

        Returns
        -------
        team_score_map : dict
            ゲームごとの全チームの集計データ（key：game_conut、value：(key:team_name ,value:point)）

        """
        if self.player_score_map is None:
            self.make_player_score

        # 全チームのデータ（key：game_conut、value：(key:team_name ,value:point)）
        team_score_map = {0: {}}
        # 初期値0.0の配置
        for team in team_list:
            team_score_map[0][team.team_name] = 0.0

        # game_countごとの集計
        for game_count, sum_score_map in self.player_score_map.items():
            # 初期化
            team_score_map[game_count] = {}
            for team in team_list:
                team.total_score = 0.0

            for score_key in sum_score_map.keys():
                # チームごとの集計
                for team in team_list:
                    for mem in team.member:
                        if mem == score_key:
                            team.total_score = round(team.total_score + sum_score_map[score_key], 1)
                            team.member_score[mem] = sum_score_map[score_key]
                    team_score_map[game_count][team.team_name] = team.total_score
        self.team_score_map = team_score_map
        return team_score_map


if __name__ == '__main__':
    # 2019 予選メンバー
    # hashimoto = MyTeam('hsmt', ['小林剛', '園田賢', '瑞原明奈', '白鳥翔'])
    # rachi = MyTeam('東豚', ['鈴木たろう', '魚谷侑未', '松本吉弘', '日向藍子'])
    # umeda = MyTeam('UMD', ['佐々木寿人', '茅森早香', '多井隆晴', '内川幸太郎'])
    # sasamura = MyTeam('パンダ', ['朝倉康心', '勝又健志', '和久津晶', '瀬戸熊直樹'])
    # yosei = MyTeam('妖精', ['滝沢和典', '近藤誠一', '高宮まり', '藤崎智'])

    # 2019 準決勝メンバー
    #hashimoto = MyTeam('hsmt', ['小林剛', '瑞原明奈', '白鳥翔'])
    #rachi = MyTeam('東豚', ['魚谷侑未', '松本吉弘', '日向藍子'])
    #umeda = MyTeam('UMD', ['佐々木寿人', '茅森早香', '多井隆晴'])
    #sasamura = MyTeam('パンダ', ['朝倉康心', '和久津晶', '瀬戸熊直樹'])
    #yosei = MyTeam('妖精', ['近藤誠一', '高宮まり', '藤崎智'])

    # 2020 予選メンバー
    #hashimoto = MyTeam('hsmt', ['小林剛', '黒沢咲', '堀慎吾', '勝又健志'])
    #rachi = MyTeam('東豚', ['魚谷侑未', '松本吉弘', '鈴木たろう', '藤崎智'])
    #umeda = MyTeam('UMD', ['佐々木寿人', '園田賢', '朝倉康心', '瑞原明奈'])
    #sasamura = MyTeam('パンダ', ['多井隆晴', '茅森早香', '瀬戸熊直樹', '村上淳'])
    #yosei = MyTeam('妖精', ['近藤誠一', '滝沢和典', '高宮まり', '白鳥翔'])

    # # 2021 レギュラーシーズン
    # hashimoto = MyTeam('hsmt', ['小林剛', '黒沢咲', '堀慎吾', '勝又健志'])
    # rachi = MyTeam('東豚', ['魚谷侑未', '松本吉弘', '本田朋広', '二階堂亜樹'])
    # umeda = MyTeam('UMD', ['佐々木寿人', '松ヶ瀬隆弥', '鈴木たろう', '岡田紗佳'])
    # sasamura = MyTeam('パンダ', ['多井隆晴', '茅森早香', '瀬戸熊直樹', '村上淳'])
    # yosei = MyTeam('妖精', ['近藤誠一', '滝沢和典', '日向藍子', '園田賢'])

    # 2022 レギュラーシーズン
    # hashimoto = MyTeam('hsmt', ['小林剛', '堀慎吾', '勝又健志', '丸山奏子'])
    # rachi = MyTeam('東豚', ['魚谷侑未', '松本吉弘', '仲林圭', '滝沢和典'])
    # umeda = MyTeam('UMD', ['佐々木寿人', '松ヶ瀬隆弥', '鈴木たろう', '伊達朱里紗'])
    # sasamura = MyTeam('パンダ', ['多井隆晴', '黒沢咲', '村上淳', '内川幸太郎'])

    # 2023 レギュラーシーズン
    hashimoto = MyTeam('hsmt', ['佐々木寿人', '多井隆晴', '仲林圭', '鈴木優', '浅見真紀'])
    rachi = MyTeam('東豚', ['猿川真寿', '松ヶ瀬隆弥', '松本吉弘', '渡辺太', '魚谷侑未'])
    umeda = MyTeam('UMD', ['伊達朱里紗', '小林剛', '堀慎吾', '鈴木大介', '白鳥翔'])
    sasamura = MyTeam('パンダ', ['園田賢', '勝又健志', '内川幸太郎', '瑞原明奈','黒沢咲'])
    daisu = MyTeam('ダイス', ['菅原千瑛', '岡田紗佳', '中田花奈', '鈴木たろう', '高宮まり'])

    dal = DataAnalysis()
    print(dal.make_team_score([hashimoto, rachi, umeda, sasamura, daisu]))
