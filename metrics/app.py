from __future__ import print_function
import os
import grpc
import pandas as pd
import json
import sys
from concurrent import futures
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server

from google.protobuf.json_format import MessageToDict, Parse
import insights_pb2_grpc as grpc_service
from insights_pb2_grpc import InfoStub
from insights_pb2 import ComposedMetrics, InfoRequest, MetricsResponse, PortfolioResponse, PricesRequest

from utils.product_metrics import Metrics
from utils.portfolio_metrics import Product, Portfolio
from utils.dashboard import build_dashboard
import logging

logger = logging.getLogger("app")

prices_port = os.environ.get("PRICES_PORT", "8888")
metrics_port = os.environ.get("METRICS_PORT", "9999")


def get_12m(base_date):
    return (datetime.strptime(base_date, "%Y-%m-%d") -
                          relativedelta(months=12)).strftime("%Y-%m-%d")


def get_prices(request):
    try:
        with grpc.insecure_channel(f"prices_service:{prices_port}") as channel:
            stub = InfoStub(channel)
            start_date = get_12m(request.base_date)
            request = InfoRequest(ticker=f"{request.ticker}.SA", start_date=start_date, end_date=request.base_date)
            prices = stub.GetInfo(request)
            return prices
    except Exception as e:
        raise e


def get_multiple_prices(request):
    try:
        with grpc.insecure_channel(f"prices_service:{prices_port}") as channel:
            stub = InfoStub(channel)
            _request = PricesRequest()
            _request.tickers.extend(request["tickers"])
            _request.start_date = request["start_date"]
            _request.end_date = request["end_date"]
            prices = stub.GetPrices(_request).raw
            return prices
    except Exception as e:
        raise e


def response_builder(metrics, name):
    _metrics = MetricsResponse()
    _metrics.name = name
    for k, v in metrics.items():
        metric_value = _metrics.metrics.add()
        metric_value.name = k
        if v:
            metric_value.value = float(v)
        else:
            metric_value.value = 0.0
    return _metrics


def prepare_info(info, index, field, name):
    if info.get(field):
        dividends = pd.DataFrame(info[field]).rename(columns={"value": name})
    else:
        dividends = pd.DataFrame()
        dividends["date"] = index
        dividends[name] = 0.0
    return dividends


def compose_df(data):
    info = MessageToDict(data)
    if not info.get("prices"):
        return pd.DataFrame()
    close = pd.DataFrame(info["prices"]).rename(columns={"value": "close"})
    volumes = prepare_info(info, close["date"], "volumes", "volume")
    dividends = prepare_info(info, close["date"], "dividends", "dividend")
    final_df = close.merge(dividends, "left", on="date").merge(volumes, "left", on="date").set_index("date").fillna(0)
    cols = final_df.columns
    final_df[cols] = final_df[cols].apply(pd.to_numeric, errors='coerce')
    return final_df


def server_setup():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=(PromServerInterceptor(enable_handling_time_histogram=True),))
    grpc_service.add_MetricsServicer_to_server(MetricsServicer(), server)
    server.add_insecure_port(f"metrics_service:{metrics_port}")
    start_http_server(9998)
    try:
        server.start()
        logger.info(f"Server is running on metrics_service:{metrics_port}")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Stopping metrics service")
        server.stop(0)


class MetricsServicer(grpc_service.MetricsServicer):
    def GetMetrics(self, request, context):
        data = get_prices(request)
        if data.ByteSize():
            df = compose_df(data)
            if df.empty:
                return MetricsResponse()
            logger.info(f"Calculating metrics: {request.ticker}")
            metrics = Metrics(request).get_metrics(df)
            return response_builder(metrics, data.name)
        else:
            return MetricsResponse()

    def GetPortfolioMetrics(self, request, context):
        try:
            _request = MessageToDict(request)
            products = _request["products"]
            _ids = [p["id"] for p in products]
            logger.info(f"Calculating metrics for portfolio")
            data = get_multiple_prices({"tickers": _ids, "start_date": _request["startDate"],
                                        "end_date": _request["endDate"]})
            close = pd.DataFrame(json.loads(data)).set_index("date")
            weights = np.array([p["proportion"] for p in products])
            values = np.array([p["amount"] for p in products])
            products = Product(close, values)
            portfolio = Portfolio(close, weights, [sum(values)])
            dash = build_dashboard(products, portfolio, close)
            logger.info(dash["portfolio"]["simple"])
            r = PortfolioResponse()
            return Parse(json.dumps(dash), r)
        except Exception as e:
            raise e


if __name__ == "__main__":
    print(f"Starting metrics server on port {metrics_port}", file=sys.stderr)
    server_setup()