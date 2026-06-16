# -*- coding: utf-8 -*-
"""
专家推理与报告生成模块。

模拟化学波谱专家的解释逻辑，将谱峰区域、结构候选和匹配证据
转换为可读的解析推理报告。
"""

from __future__ import annotations

from typing import List, Sequence

from NMR.config import DEFAULT_TOP_K_REPORT
from NMR.models import AnalysisReport, MolecularCandidate, ParsedSpectrum


class ExpertReasoningEngine:
    """
    专家级推理与报告生成器。

    该类模拟化学波谱专家的解释逻辑，将谱峰区域、结构候选和匹配证据
    转换为可读的解析推理报告。
    """

    def generate_report(
        self,
        parsed_spectrum: ParsedSpectrum,
        candidates: Sequence[MolecularCandidate],
        top_k: int = DEFAULT_TOP_K_REPORT,
    ) -> AnalysisReport:
        """
        生成谱图智能鉴定报告。

        Args:
            parsed_spectrum: 谱图解析结果。
            candidates: 结构候选列表。
            top_k: 报告中展开说明的候选数量。

        Returns:
            AnalysisReport: 智能鉴定报告。

        Raises:
            ValueError: 当输入为空或 top_k 非法时抛出。
        """
        if parsed_spectrum is None:
            raise ValueError("谱图解析结果不能为空。")
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0。")

        selected_candidates = list(candidates[:top_k])
        reasoning = self._build_reasoning(parsed_spectrum, selected_candidates)
        warnings = self._build_warnings(parsed_spectrum, selected_candidates)

        report_id = self._create_report_id(parsed_spectrum)

        return AnalysisReport(
            report_id=report_id,
            spectrum_type=parsed_spectrum.raw_spectrum.spectrum_type.value,
            quality_score=parsed_spectrum.quality_score,
            detected_peaks=list(parsed_spectrum.peaks),
            candidates=selected_candidates,
            reasoning=reasoning,
            warnings=warnings,
        )

    def _build_reasoning(
        self,
        parsed_spectrum: ParsedSpectrum,
        candidates: Sequence[MolecularCandidate],
    ) -> str:
        """
        构建专家推理文本。

        Args:
            parsed_spectrum: 谱图解析结果。
            candidates: 候选结构列表。

        Returns:
            str: 专家推理文本。
        """
        peak_lines = []
        for peak in parsed_spectrum.peaks:
            peak_lines.append(
                f"- {peak.shift:.2f} ppm，积分约 {peak.area:.2f}，"
                f"峰宽 {peak.width:.2f} ppm，初步归属为 {peak.assignment}。"
            )

        candidate_lines = []
        for rank, candidate in enumerate(candidates, start=1):
            candidate_lines.append(
                f"{rank}. {candidate.name}（{candidate.formula}, SMILES={candidate.smiles}）"
                f"匹配评分为 {candidate.score:.2%}。"
            )
            for evidence in candidate.evidence[:4]:
                candidate_lines.append(f"   - {evidence}")

        if not candidate_lines:
            candidate_lines.append("未生成可靠结构候选，建议补充二维谱图或高分辨质谱数据。")

        return (
            "谱图解析推理报告\n"
            "一、谱图质量与峰识别\n"
            f"系统对输入 {parsed_spectrum.raw_spectrum.spectrum_type.value} 谱图完成去噪、"
            f"基线校正与峰识别，质量评分为 {parsed_spectrum.quality_score:.2%}。\n"
            f"共检出 {len(parsed_spectrum.peaks)} 个主要信号：\n"
            + "\n".join(peak_lines)
            + "\n\n二、结构候选与证据匹配\n"
            + "\n".join(candidate_lines)
            + "\n\n三、结论\n"
            "排名第一的候选结构可作为优先验证对象。若候选之间评分接近，"
            "应结合 HSQC、HMBC、COSY、质谱和样品来源信息进行联合确认。"
        )

    def _build_warnings(
        self,
        parsed_spectrum: ParsedSpectrum,
        candidates: Sequence[MolecularCandidate],
    ) -> List[str]:
        """
        构建报告风险提示。

        Args:
            parsed_spectrum: 谱图解析结果。
            candidates: 候选结构列表。

        Returns:
            List[str]: 风险提示列表。
        """
        warnings: List[str] = []

        if parsed_spectrum.quality_score < 0.55:
            warnings.append("谱图质量评分偏低，可能存在噪声、基线漂移或样品浓度不足。")

        if len(parsed_spectrum.peaks) < 2:
            warnings.append("检出峰数量较少，结构推测不确定性较高。")

        if candidates:
            best_score = candidates[0].score
            if best_score < 0.65:
                warnings.append("最高结构匹配评分低于 65%，建议补充二维 NMR 或 MS 数据。")

            if len(candidates) > 1 and abs(candidates[0].score - candidates[1].score) < 0.08:
                warnings.append("前两名候选评分接近，可能存在异构体或混合物干扰。")
        else:
            warnings.append("未获得结构候选。")

        warnings.append("当前结果由原型启发式模型生成，不能替代正式实验鉴定结论。")
        return warnings

    def _create_report_id(self, parsed_spectrum: ParsedSpectrum) -> str:
        """
        创建报告编号。

        Args:
            parsed_spectrum: 谱图解析结果。

        Returns:
            str: 报告编号。
        """
        point_count = len(parsed_spectrum.raw_spectrum.points)
        peak_count = len(parsed_spectrum.peaks)
        quality_part = int(parsed_spectrum.quality_score * 10000)
        return f"NMR-{parsed_spectrum.raw_spectrum.spectrum_type.value}-{point_count}-{peak_count}-{quality_part}"
