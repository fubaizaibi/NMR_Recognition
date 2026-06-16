# -*- coding: utf-8 -*-
"""
多模态结构推测引擎模块。

通过观测谱峰与理论谱峰的启发式相似度完成逆向结构推测。
生产环境中可替换为多模态 GNN、Transformer 和谱图-结构双向映射模型。
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from NMR.config import DEFAULT_MAX_CANDIDATES
from NMR.database import StructureDatabase
from NMR.models import MolecularCandidate, ParsedSpectrum, Peak
from NMR.prediction import HeuristicSpectrumPredictor


class StructureInferenceEngine:
    """
    多模态结构推测引擎。

    当前原型通过"观测谱峰"与"理论谱峰"的启发式相似度完成逆向结构推测。
    生产环境中可替换为多模态 GNN、Transformer 和谱图-结构双向映射模型。

    复杂度:
        若候选结构数量为 c，观测峰数量为 n，理论峰数量为 m，
        则时间复杂度约为 O(c * n * m)，空间复杂度为 O(c + n + m)。
    """

    def __init__(
        self,
        database: Optional[StructureDatabase] = None,
        predictor: Optional[HeuristicSpectrumPredictor] = None,
    ) -> None:
        """
        初始化结构推测引擎。

        Args:
            database: 结构知识库。
            predictor: 理论谱图预测器。
        """
        self.database = database or StructureDatabase()
        self.predictor = predictor or HeuristicSpectrumPredictor()

    def infer(
        self,
        parsed_spectrum: ParsedSpectrum,
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
    ) -> List[MolecularCandidate]:
        """
        根据解析谱峰推测结构候选。

        Args:
            parsed_spectrum: 谱图解析结果。
            max_candidates: 最大候选数量。

        Returns:
            List[MolecularCandidate]: 按评分降序排列的结构候选列表。

        Raises:
            ValueError: 当输入解析结果或参数非法时抛出。
        """
        if parsed_spectrum is None:
            raise ValueError("谱图解析结果不能为空。")
        if max_candidates <= 0:
            raise ValueError("最大候选数量必须大于 0。")

        candidates: List[MolecularCandidate] = []

        for record in self.database.list_records():
            predicted_peaks = self.predictor.predict(record["key"])
            score, evidence = self._score_candidate(parsed_spectrum.peaks, predicted_peaks)
            candidates.append(
                MolecularCandidate(
                    name=record["name"],
                    smiles=record["smiles"],
                    formula=record["formula"],
                    score=round(score, 4),
                    evidence=evidence,
                    predicted_peaks=predicted_peaks,
                )
            )

        candidates.sort(key=lambda item: item.score, reverse=True)
        return candidates[:max_candidates]

    def _score_candidate(
        self,
        observed_peaks: Sequence[Peak],
        predicted_peaks: Sequence[Peak],
    ) -> Tuple[float, List[str]]:
        """
        计算候选结构与观测谱峰的匹配评分。

        Args:
            observed_peaks: 观测谱峰。
            predicted_peaks: 理论谱峰。

        Returns:
            Tuple[float, List[str]]: 评分与证据列表。
        """
        if not observed_peaks or not predicted_peaks:
            return 0.0, ["观测峰或理论峰为空，无法可靠匹配。"]

        evidence: List[str] = []
        matched_scores: List[float] = []

        for predicted_peak in predicted_peaks:
            nearest_peak = min(
                observed_peaks,
                key=lambda observed_peak: abs(observed_peak.shift - predicted_peak.shift),
            )
            shift_error = abs(nearest_peak.shift - predicted_peak.shift)

            if shift_error <= 0.12:
                local_score = 1.0
                evidence.append(
                    f"理论峰 {predicted_peak.shift:.2f} ppm 与观测峰 "
                    f"{nearest_peak.shift:.2f} ppm 高度匹配，误差 {shift_error:.2f} ppm。"
                )
            elif shift_error <= 0.35:
                local_score = 0.65
                evidence.append(
                    f"理论峰 {predicted_peak.shift:.2f} ppm 与观测峰 "
                    f"{nearest_peak.shift:.2f} ppm 中等匹配，误差 {shift_error:.2f} ppm。"
                )
            elif shift_error <= 0.70:
                local_score = 0.3
                evidence.append(
                    f"理论峰 {predicted_peak.shift:.2f} ppm 附近存在弱相关观测信号，"
                    f"误差 {shift_error:.2f} ppm。"
                )
            else:
                local_score = 0.0
                evidence.append(
                    f"理论峰 {predicted_peak.shift:.2f} ppm 未找到可靠观测匹配。"
                )

            matched_scores.append(local_score)

        coverage_score = sum(matched_scores) / len(predicted_peaks)
        observed_penalty = max(0.0, (len(observed_peaks) - len(predicted_peaks)) * 0.025)
        final_score = max(0.0, min(1.0, coverage_score - observed_penalty))

        return final_score, evidence
