from tinvest_devkit.client import TInvestReadClient
from tinvest_devkit.config import load_settings


def main() -> None:
    settings = load_settings(
        require_account_id=True
    )
    client = TInvestReadClient(settings)

    operations = client.get_all_operations()

    print("Operations:", len(operations))

    for operation in operations[-10:]:
        print(
            operation.timestamp,
            operation.operation_type,
            operation.description,
        )


if __name__ == "__main__":
    main()
