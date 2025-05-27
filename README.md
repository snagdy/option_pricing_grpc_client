# Options Pricing gRPC Client

This project provides two Python clients for a gRPC service that calculates option prices and Greeks using the Black-Scholes model.

It includes:
1.  A simple command-line interface (CLI) client for making individual pricing requests.
2.  An experimental asynchronous client capable of making multiple concurrent requests for a range of parameters.

**Note:** This project contains only the client-side code. It requires a compatible gRPC server implementing the `OptionPricingService` defined in the protobuf definition (which is not included in this repository). It also relies on the generated Python protobuf files (`black_scholes_pb2.py` and `black_scholes_pb2_grpc.py`).

You can find the server-side code [here](https://github.com/snagdy/option-pricing-server).

## Project Structure (excluding hidden dirs)

```bash
.
├── README.md
├── option_pricing_client_async_experiment.py
├── option_pricing_client_cli.py
│   └── finance
│       └── options
└── requirements.txt
```

## Prerequisites

* Python 3.7+
* A running gRPC server that implements the Black-Scholes option pricing service.
* Docker Desktop and a devcontainer capable IDE (recommend VSCode).
* The generated Python protobuf files (`black_scholes_pb2.py` and `black_scholes_pb2_grpc.py`) placed in a location where they can be imported by the client scripts (e.g., in the same directory or a package structure). You can find the .proto spec in [this repo](https://github.com/snagdy/finance_protos) - although if you use a Devcontainer workflow with VSCode, this is all provided via the repo files under `<repo_root>/.devcontainer/`.




## Installation via Venv (not recommended locally)

<details><summary>Expand to see details.</summary>

This is more work, since you will have to use the protoc compiler to compile the .proto files from the relevant repo yourself.

It's highly recommended to use a virtual environment to avoid conflicts with your system's Python packages.

1.  Clone or download the repository.
2.  Navigate to the project directory in your terminal.
3.  Create a virtual environment:

    ```bash
    python -m venv venv
    ```

4.  Activate the virtual environment:

    * **On macOS and Linux:**

        ```bash
        source venv/bin/activate
        ```

    * **On Windows (Command Prompt):**

        ```bash
        venv\Scripts\activate.bat
        ```

    * **On Windows (PowerShell):**

        ```bash
        venv\Scripts\Activate.ps1
        ```

    You should see `(venv)` at the beginning of your terminal prompt, indicating the virtual environment is active.

5.  Install the required dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

    This will install `grpcio`, `grpcio-tools`, `numpy`, `pandas`, and other necessary libraries listed in `requirements.txt` into your virtual environment.

6.  When you are finished working on the project, you can deactivate the virtual environment:

    ```bash
    deactivate
    ```

</details>

## Installation Devcontainer (recommended)

Use your IDE's functionality to make use of the `.devcontainer/devcontainer.json` configuration and launch it.

## Usage

Make sure your virtual environment is activated and you have the generated protobuf files (`black_scholes_pb2.py` and `black_scholes_pb2_grpc.py`) in the same directory as the client scripts or in your Python path.

### Command-Line Interface (CLI) Client

The `option_pricing_client_cli.py` script allows you to calculate the price and Greeks for a single option using command-line arguments.

```bash
python option_pricing_client_cli.py \
    --server <server_address:port> \
    --stock-price <stock_price> \
    --strike-price <strike_price> \
    --volatility <volatility> \
    --time-to-maturity <time_to_maturity_years> \
    [--risk-free-rate <risk_free_rate>] \
    [--dividend-rate <dividend_rate>] \
    [--option-type <CALL|PUT>]
```


### Experimental Async Client Script

This can be launched via the following:

```bash
export SERVER_ADDRESS=<service_ip:port>                 # NOTE: the service_ip can get from Docker Desktop, or host OS - DNS name usage is more advanced.

python option_pricing_client_async_experiment.py
```

## Planned Updates

- Validation script for cross-checking IV produced for a given option premium, against the sigma used to generate that option premium.

- Some numba JIT compilation optimisations where possible.