#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import os
import sys
import re

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
        self.soten_score = 0.0

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
        self.player_rank_map = None
        self.player_maxmin_map = None
        self.team_score_map = None
        self.team_rank_map = None
        self.team_maxmin_map = None

    @property
    def make_player_score(self):
        """
        各選手の集計結果を作成する
        """
        # 順位点定義（例：1着だと順位点30＋オカ20が入っているのでその分を引く）
        RANK_DEF = {0:50.0, 1:10.0, 2:-10.0, 3:-30.0}
        # プレイヤーごとの順位データ（key：player_name、value：順位配列[1着回数, 2着回数, 3着回数, 4着回数]）
        player_rank_map = {}
        # トータルスコア（key：player_name、value：score）
        sum_score_map = {}
        # 日ごとトータルスコア（key：game_count、value：sum_score_map）
        player_score_map = {}
        # プレイヤーごとの最高・最低データ（key：player_name、value：配列[max_date, max_tensu, min_date, min_tensu]]）
        player_maxmin_map = {}

        games_result = self.soup.find_all(class_="p-gamesResult")
        game_count = 0
        for one_day_result in games_result:
            game_day = one_day_result.find(class_="p-gamesResult__date").text
            if game_day == '/日(曜日)':
                continue

            # # セミファイナル仕様（3/16以降まで飛ばす）
            # game_only_day = game_day.split('(')[0].split('/')
            # if int(game_only_day[0]) != 3:
            #     continue
            # if int(game_only_day[1]) < 15:
            #     continue

            game_count += 1
            result_column = one_day_result.find_all(class_="p-gamesResult__rank-item")
            for one_result in result_column:
                # 名前取得
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
                player_score = float(player_score)

                # score_map作成 小数点の誤差が発生するため、四捨五入を行う
                sum_score_map[player_name] = round(sum_score_map.get(player_name, 0.0) + player_score, 1)
                      
                # 順位取得&設定
                player_rank = eval(one_result.find(class_=re.compile("^p-gamesResult__rank-badge")).text.strip())
                if not player_name in player_rank_map:
                    player_rank_map[player_name] = [0 ,0, 0, 0]
                player_rank_map[player_name][player_rank - 1] = player_rank_map[player_name][player_rank - 1] + 1

                # 個人ごとの点数最大・最小判定
                player_tensu = int(round((player_score + 30.0 - RANK_DEF[player_rank - 1]) * 1000, 1)) # scoreから点数を復元
                if not player_name in player_maxmin_map:
                    player_maxmin_map[player_name] = [game_day, player_tensu, game_day, player_tensu]
                else:
                    if player_tensu > player_maxmin_map[player_name][1]:
                        player_maxmin_map[player_name][0] = game_day
                        player_maxmin_map[player_name][1] = player_tensu
                    elif player_tensu < player_maxmin_map[player_name][3]:
                        player_maxmin_map[player_name][2] = game_day
                        player_maxmin_map[player_name][3] = player_tensu

            # game_countごとの結果を保管
            player_score_map[game_count] = sum_score_map.copy()

        self.player_score_map = player_score_map
        self.player_rank_map = player_rank_map
        self.player_maxmin_map = player_maxmin_map

    def make_team_score(self, team_list):
        """

        Parameters
        ----------
        team_list : list
            チームクラスのリスト

        """
        if self.player_score_map is None:
            self.make_player_score

        # 素点定義（例：1着だと順位点30,オカ15が入っているのでその分を引く）
        SOTEN_DEF = {0:-45.0, 1:-5.0, 2:15.0, 3:35.0}
        # 全チームの点数データ(key：game_conut、value：(key:team_name ,value:point))
        team_score_map = {0: {}}
        # 全チームの順位データ(key：team_name、value：順位配列[1着回数, 2着回数, 3着回数, 4着回数])
        team_rank_map = {}
        # チームごとの最高・最低データ（key：team_name、value：配列[max_date, member, max_score, min_date, member, min_score]]）
        team_maxmin_map = {}

        for team in team_list:
            # 初期値0.0の配置
            team_score_map[0][team.team_name] = 0.0

            # チームごとの順位集計
            team_rank_map[team.team_name] = [0, 0, 0, 0]
            for mem in team.member:
                # 個人の順位をチームごとの集計に集約
                if mem in self.player_rank_map:
                    team_rank_map[team.team_name] = [x + y for (x, y) in zip(team_rank_map[team.team_name], self.player_rank_map[mem])]
                # チームごとの最高・最低データを設定
                if mem in self.player_maxmin_map:
                    if not team.team_name in team_maxmin_map:
                        team_maxmin_map[team.team_name] = self.player_maxmin_map[mem]
                        team_maxmin_map[team.team_name].insert(1, mem) 
                        team_maxmin_map[team.team_name].insert(4, mem) 
                    else:
                        if self.player_maxmin_map[mem][1] > team_maxmin_map[team.team_name][2]:
                            team_maxmin_map[team.team_name][0] = self.player_maxmin_map[mem][0] #日付
                            team_maxmin_map[team.team_name][1] = mem #メンバー
                            team_maxmin_map[team.team_name][2] = self.player_maxmin_map[mem][1] #スコア
                        if self.player_maxmin_map[mem][3] < team_maxmin_map[team.team_name][5]:
                            team_maxmin_map[team.team_name][3] = self.player_maxmin_map[mem][2]
                            team_maxmin_map[team.team_name][4] = mem
                            team_maxmin_map[team.team_name][5] = self.player_maxmin_map[mem][3]
            
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

        # 素点計算
        for team in team_list:
            team.soten_score = team.total_score
            for index, rank_count in enumerate(team_rank_map[team.team_name]):
                team.soten_score = round(team.soten_score + SOTEN_DEF[index] * rank_count, 1)

        self.team_score_map = team_score_map
        self.team_rank_map = team_rank_map
        self.team_maxmin_map = team_maxmin_map

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
    # hashimoto = MyTeam('hsmt', ['佐々木寿人', '多井隆晴', '仲林圭', '鈴木優', '浅見真紀'])
    # rachi = MyTeam('東豚', ['猿川真寿', '松ヶ瀬隆弥', '松本吉弘', '渡辺太', '魚谷侑未'])
    # umeda = MyTeam('UMD', ['伊達朱里紗', '小林剛', '堀慎吾', '鈴木大介', '白鳥翔'])
    # sasamura = MyTeam('パンダ', ['園田賢', '勝又健志', '内川幸太郎', '瑞原明奈','黒沢咲'])
    # daisu = MyTeam('ダイス', ['菅原千瑛', '岡田紗佳', '中田花奈', '鈴木たろう', '高宮まり'])

    # 2024 レギュラーシーズン
    hashimoto = MyTeam('hsmt', ['仲林圭', '竹内元太', '浅井堂岐', '浅見真紀'])
    rachi = MyTeam('東豚', ['松本吉弘', '佐々木寿人', '松ヶ瀬隆弥', '日向藍子'])
    umeda = MyTeam('UMD', ['堀慎吾', '伊達朱里紗', '多井隆晴', '鈴木優'])
    daisu1 = MyTeam('ダイス１', ['二階堂瑠美', '鈴木大介', '菅原千瑛', '中田花奈'])
    daisu2 = MyTeam('ダイス２', ['内川幸太郎', '高宮まり', '本田朋広', '白鳥翔'])

    dal = DataAnalysis()
    dal.make_team_score([hashimoto, rachi, umeda, daisu1, daisu2])
    #print(dal.player_score_map)
    #print(dal.player_rank_map)
    #print(dal.player_maxmin_map)
    #print(dal.team_score_map)
    print(dal.team_rank_map)
    print(dal.team_maxmin_map)
