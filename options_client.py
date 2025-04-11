#!/usr/bin/env python3
"""
gRPC client for option pricing service using the Black-Scholes model.
"""

import argparse
import grpc
import logging

# Import the generated protobuf code
import black_scholes_pb2
import black_scholes_pb2_grpc


def run_client(server_address, stock_price, strike_price, risk_free_rate,
               dividend_rate, volatility, time_to_maturity, option_type_str):
    """
    Connect to gRPC server and request option pricing calculations.
    """
    # Convert option type string to enum value
    if option_type_str.upper() == "CALL":
        option_type = black_scholes_pb2.CALL
    elif option_type_str.upper() == "PUT":
        option_type = black_scholes_pb2.PUT
    else:
        raise ValueError(f"Invalid option type: {option_type_str}. Must be 'CALL' or 'PUT'.")

    # Create a gRPC channel
    with grpc.insecure_channel(server_address) as channel:
        # Create a stub (client)
        stub = black_scholes_pb2_grpc.OptionPricingServiceStub(channel)

        # Create request message
        parameters = black_scholes_pb2_grpc.BlackScholesParameters(
            stock_price=stock_price,
            strike_price=strike_price,
            risk_free_rate=risk_free_rate,
            dividend_rate=dividend_rate,
            volatility=volatility,
            time_to_maturity=time_to_maturity,
            option_type=option_type
        )

        request = black_scholes_pb2.OptionPricingRequest(parameters=parameters)

        # Make the call
        try:
            response = stub.CalculateOptionPrice(request)

            # Display the response
            print("\n=== Option Pricing Results ===")
            print(f"Option Type: {'CALL' if response.option_type == black_scholes_pb2.CALL else 'PUT'}")
            print(f"Option Price: ${response.option_price:.4f}")
            print(f"Delta: {response.delta:.6f}")
            print(f"Gamma: {response.gamma:.6f}")
            print(f"Vega: {response.vega:.6f}")
            print("============================\n")

            return response

        except grpc.RpcError as e:
            logging.error(f"RPC failed: {e.code()}: {e.details()}")
            return None


def main():
    """Parse command line arguments and call client function."""
    parser = argparse.ArgumentParser(description="Options Pricing gRPC Client")

    parser.add_argument("--server", default="localhost:50051",
                        help="Server address in format host:port")
    parser.add_argument("--stock-price", type=float, required=True,
                        help="Current stock price")
    parser.add_argument("--strike-price", type=float, required=True,
                        help="Strike price")
    parser.add_argument("--risk-free-rate", type=float, default=0.05,
                        help="Risk-free interest rate (decimal, e.g., 0.05 for 5%%)")
    parser.add_argument("--dividend-rate", type=float, default=0.0,
                        help="Continuous dividend rate (decimal, e.g., 0.02 for 2%%)")
    parser.add_argument("--volatility", type=float, required=True,
                        help="Volatility of the underlying asset (decimal)")
    parser.add_argument("--time-to-maturity", type=float, required=True,
                        help="Time to maturity in years")
    parser.add_argument("--option-type", choices=["CALL", "PUT"], default="CALL",
                        help="Type of option (CALL or PUT)")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Call the client function
    run_client(
        args.server,
        args.stock_price,
        args.strike_price,
        args.risk_free_rate,
        args.dividend_rate,
        args.volatility,
        args.time_to_maturity,
        args.option_type
    )


if __name__ == "__main__":
    main()
