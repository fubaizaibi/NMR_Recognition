# -*- coding: utf-8 -*-
"""
理论谱图预测模块。

基于化学结构类别的启发式理论谱峰库模拟理论 1H NMR 谱。
生产系统中可替换为 GNN 或 Transformer 前向预测模型。
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from NMR.models import Peak


class HeuristicSpectrumPredictor:
    """
    理论谱图预测器。

    当前实现基于化学结构类别的启发式理论谱峰库。生产系统中可替换为
    GNN 或 Transformer 前向预测模型。

    复杂度:
        对于 m 个模板峰，时间复杂度为 O(m)，空间复杂度为 O(m)。
    """

    _STRUCTURE_TEMPLATES: Dict[str, List[Tuple[float, float, str]]] = {
        "ethanol": [
            (1.18, 3.0, "甲基三重峰"),
            (3.65, 2.0, "连氧亚甲基四重峰"),
            (2.10, 1.0, "羟基活泼氢宽峰"),
        ],
        "acetone": [
            (2.16, 6.0, "羰基邻位甲基单峰"),
        ],
        "toluene": [
            (2.34, 3.0, "苄位甲基单峰"),
            (7.18, 5.0, "单取代苯环芳香氢多重峰"),
        ],
        "ethyl_acetate": [
            (1.26, 3.0, "乙基甲基三重峰"),
            (2.05, 3.0, "乙酰甲基单峰"),
            (4.12, 2.0, "连氧亚甲基四重峰"),
        ],
        "benzaldehyde": [
            (7.45, 3.0, "芳香环氢多重峰"),
            (7.85, 2.0, "醛基邻位芳香氢信号"),
            (9.98, 1.0, "醛基氢单峰"),
        ],
        "phenol": [
            (6.85, 2.0, "芳香环邻位氢信号"),
            (7.15, 3.0, "芳香环间对位氢信号"),
            (5.20, 1.0, "酚羟基活泼氢宽峰"),
        ],
    }

    def predict(self, structure_key: str) -> List[Peak]:
        """
        根据结构模板预测理论 1H 谱峰。

        Args:
            structure_key: 内置结构模板键。

        Returns:
            List[Peak]: 理论谱峰列表。

        Raises:
            ValueError: 当结构键不存在时抛出。
        """
        if structure_key not in self._STRUCTURE_TEMPLATES:
            raise ValueError(f"未知结构模板: {structure_key}")

        peaks = []
        for shift, area, assignment in self._STRUCTURE_TEMPLATES[structure_key]:
            peaks.append(
                Peak(
                    shift=shift,
                    intensity=area,
                    area=area,
                    width=0.05,
                    assignment=assignment,
                    confidence=0.95,
                )
            )
        return peaks
