# Import the generated protobuf code
import os
import sys
import asyncio
import black_scholes_pb2
import black_scholes_pb2_grpc
import functools
import grpc
import logging
import logging.handlers
import queue
import numpy as np
import pandas as pd


# Async logging setup
log_queue = queue.Queue()
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
log_queue_listener = logging.handlers.QueueListener(log_queue, stream_handler)
log_queue_handler = logging.handlers.QueueHandler(log_queue)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_queue_handler)


def log_queue_async_decorator(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        log_queue_listener.start()
        try:
            await func(*args, **kwargs)
        finally:
            log_queue_listener.stop()

    return wrapper


# Setting this up this way to avoid leaking infra details
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")


async def pricing_request(
    stock_price,
    strike_price,
    risk_free_rate,
    dividend_rate,
    volatility,
    time_to_maturity,
    option_type,
):
    with grpc.insecure_channel(SERVER_ADDRESS) as channel:
        stub = black_scholes_pb2_grpc.OptionPricingServiceStub(channel)
        parameters = black_scholes_pb2.BlackScholesParameters(
            stock_price=stock_price,
            strike_price=strike_price,
            risk_free_rate=risk_free_rate,
            dividend_rate=dividend_rate,
            volatility=volatility,
            time_to_maturity=time_to_maturity,
            option_type=option_type,
        )
        request = black_scholes_pb2.OptionPricingRequest(parameters=parameters)
        try:
            response = stub.CalculateOptionPrice(request)
            logger.info(
                f"""Option Pricing Results 
                Option Type: {'CALL' if response.option_type == black_scholes_pb2.CALL else 'PUT'} 
                Option Price: ${response.option_price:.4f} 
                Delta: {response.delta:.6f} 
                Gamma: {response.gamma:.6f} 
                Vega: {response.vega:.6f}"""
            )
            return response
        except grpc.RpcError as e:
            logger.error(f"RPC failed: {e.code()}: {e.details()}")
        return None


@log_queue_async_decorator
async def main():
    stock_price = 100
    strike_prices = range(1, 201)  # strikes ranging from 1 to
    risk_free_rate = 0.05
    volatility = 0.10
    dividend_rate = 0.0
    times_to_maturity_years = np.arange(
        0.25, 3.01, 0.25
    )  # 3 month increments as 0.25 year fractions

    call_inputs = []
    for expiration in times_to_maturity_years:
        for strike in strike_prices:
            call_inputs.append(
                (
                    stock_price,
                    strike,
                    risk_free_rate,
                    dividend_rate,
                    volatility,
                    expiration,
                    "CALL",
                )
            )

    put_inputs = []
    for expiration in times_to_maturity_years:
        for strike in strike_prices:
            put_inputs.append(
                (
                    stock_price,
                    strike,
                    risk_free_rate,
                    dividend_rate,
                    volatility,
                    expiration,
                    "PUT",
                )
            )

    joint_inputs = call_inputs + put_inputs
    tasks = [pricing_request(*inputs) for inputs in joint_inputs]
    responses = await asyncio.gather(*tasks)

    result_dict = {"type": [], "price": [], "delta": [], "gamma": [], "vega": []}
    for response in responses:
        result_dict["type"].append(
            "CALL" if response.option_type == black_scholes_pb2.CALL else "PUT"
        )
        result_dict["price"].append(response.option_price)
        result_dict["delta"].append(response.delta)
        result_dict["gamma"].append(response.gamma)
        result_dict["vega"].append(response.vega)

    df = pd.DataFrame(result_dict)
    print(df)


if __name__ == "__main__":
    asyncio.run(main())
