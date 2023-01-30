import os

import classification

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def main():
    classification.benchmark(
        config="./config.yaml"
    )


if __name__ == "__main__":
    os.chdir(CURRENT_DIR)
    main()
