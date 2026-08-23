from tinvest_devkit.client import TInvestReadClient
from tinvest_devkit.config import load_settings


def main() -> None:
    settings = load_settings()
    client = TInvestReadClient(settings)

    accounts = client.get_accounts()

    for account in accounts:
        print(
            account.account_id,
            account.name,
            account.status,
        )


if __name__ == "__main__":
    main()
