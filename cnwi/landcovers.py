from __future__ import annotations

import enum

from abc import ABC
from dataclasses import dataclass
from typing import Type

import pandas as pd


@dataclass(frozen=True)
class _LandCovers:
    pass


@dataclass(frozen=True)  # this will always be the same
class LandCovers(_LandCovers):
    WETLAND: str = '008000'
    NON_WETLAND: str = 'FF0000'
    WATER: str = '0000FF'


@dataclass(frozen=True)
class SubLandCovers(_LandCovers):  # this needs to variable
    BOG = 'A52A2A'
    FEN = 'FFF600'
    FOREST = 'FF0000'
    MARSH = '8FBC8F'
    SHALLOW_WATER = '7CFC00'
    SWAMP = '008000'
    UPLAND = 'FF0001'
    WATER = '0000FF'


class CMAP(pd.DataFrame):

    def __init__(self, in_labels: list[str], land_cover: Type[_LandCovers]) -> None:
        labels, value, r, g, b = [], [], [], [], []

        for idx, label in enumerate(in_labels, start=1):
            hex = getattr(land_cover, label.upper())
            rgb: tuple[int] = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            r.append(rgb[0])
            g.append(rgb[1])
            b.append(rgb[2])
            value.append(idx), labels.append(label)

        data = {"value": value, "red": r, "green": g, "blue": b}
        super().__init__(pd.DataFrame(data=data, index=labels))

    def to_clr(self, filename: str):
        self.to_csv(
            path_or_buf=filename,
            sep=" ",
            header=False,
            index=False
        )


def palette(lcobj: Type[_LandCovers], labels: list[str] = None) -> list[str]:
    hexs = [getattr(lcobj, label.upper(), None) for label in labels]

    pallette = [
        f'#{hex}' for hex in hexs if hex is not None
    ]
    return pallette
