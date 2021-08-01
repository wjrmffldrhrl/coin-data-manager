from typing import List

import requests

from coin.candle.Candle import Candle
from coin.candle.upbit.UpbitDayCandle import UpbitDayCandle
from coin.candle.upbit.UpbitMinuteCandle import UpbitMinuteCandle
from coin.candle.upbit.UpbitMonthCandle import UpbitMonthCandle
from coin.candle.upbit.UpbitWeekCandle import UpbitWeekCandle
from coin.tick.Tick import Tick
from coin.tick.Ticker import Ticker
from coin.tick.UpbitTick import UpbitTick


class UpbitQuotationApiCaller:
    def __init__(self):
        self.server_url = "https://api.upbit.com/v1"

    def request(self, url: str, params: dict, method="GET"):
        url = self.server_url + url
        headers = {"Accept": "application/json"}

        return requests.request(method, url, params=params, headers=headers).json()

    def get_market_codes(self):
        """
        Get all market codes on Upbit
        :return: market code list
                market	업비트에서 제공중인 시장 정보
                korean_name	거래 대상 암호화폐 한글명
                english_name	거래 대상 암호화폐 영문명
                market_warning	유의 종목 여부
                                - NONE (해당 사항 없음)
                                - CAUTION(투자유의)
        """
        url = "/market/all"
        query = {"isDetails": "true"}
        return self.request(url, query)

    def get_candles(self, market: str, count: int, unit: str, to=None) -> List[Candle]:
        """
        :param market: Market code ex) KRW-BTC
        :param count: Quantity you want to receive
        :param unit: Candle unit
                ex) - minutes /1, /3, /5, /10, /15, /30, /60, /240
                    - days
                    - weeks
                    - months
        :param to: Last candle time like yyyy-MM-dd'T'HH:mm:ss'Z' or yyyy-MM-dd HH:mm:ss
        :return: candles json data
        """
        if count > 200:
            raise Exception(f"Count can't exceed 200 : {200}")

        url = "/candles/" + unit
        query = {"market": market, "count": count}

        if to is not None:
            query["to"] = to

        candle_type = self.get_candle_type(unit)

        response = self.request(url, query)
        candles = [candle_type.from_response(candle_info) for candle_info in response]

        return candles

    def get_ticks(self, market, count) -> List[Tick]:
        """
        Get ticks
        :param market: market code
        :param count: required amount
        :return: Tick list
        """
        url = "/trades/ticks"
        query = {"market": market, "count": count}

        response = self.request(url, query)
        ticks = [UpbitTick.from_response(market, tick) for tick in response]

        return ticks

    def get_tickers(self, markets) -> List[Ticker]:
        """
        Get tickers
        :param markets: Target markets list
        :return: Ticker list
        """
        url = "/ticker"
        query_string = {"markets": ",".join(markets)}

        response = self.request(url=url, params=query_string)

        tickers = [Ticker.from_response(ticker) for ticker in response]

        return tickers

    @staticmethod
    def get_candle_type(unit):
        if "minutes" in unit:
            candle_type = UpbitMinuteCandle
        elif "days" in unit:
            candle_type = UpbitDayCandle
        elif "weeks" in unit:
            candle_type = UpbitWeekCandle
        elif "month" in unit:
            candle_type = UpbitMonthCandle
        else:
            raise TypeError(f"Can't use {unit}")
        return candle_type
