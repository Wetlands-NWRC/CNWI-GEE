import os

from pipelines import colors

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def main():

    colors.Colors.mkcmap(
        filename="../results/phase03/cmap.clr",
        labels=['Bog', 'Fen', 'Marsh', 'Swamp', 'Upland', 'Water']
    )

    return None


if __name__ == "__main__":
    os.chdir(CURRENT_DIR)
    main()
