from tinvest_devkit.client import TInvestReadClient
from tinvest_devkit.config import load_settings


def main() -> None:
    settings = load_settings(
        require_account_id=True
    )
    client = TInvestReadClient(settings)

    positions = client.get_security_positions()

    for position in positions:
        print(
            position.ticker,
            position.balance,
            position.instrument_uid,
        )


if __name__ == "__main__":
    main()
