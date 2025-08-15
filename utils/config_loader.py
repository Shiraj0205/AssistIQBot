import yaml

def load_config(config_path: str = "config\config.yaml") -> dict:
    """
    Read config.yaml and return configuration as dictionary
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


if __name__ == "__main__":
    config = load_config()
    print(f"App Configuration : {config}")
    