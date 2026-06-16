# -*- coding: utf-8 -*-
"""
系统应用服务层 — NMR 谱图智能鉴定系统门面类。

整合谱图解析、结构推测与专家报告生成，模拟从"谱图上传"
到"结构生成、报告导出"的完整闭环。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from NMR.config import DEFAULT_MAX_CANDIDATES, DEFAULT_OUTPUT_REPORT_PATH
from NMR.inference import StructureInferenceEngine
from NMR.io import JsonReportWriter, SpectrumInputLoader
from NMR.logging_config import LOGGER
from NMR.models import AnalysisReport, Spectrum
from NMR.processing import SpectrumProcessor
from NMR.reasoning import ExpertReasoningEngine


class NmrAiIdentificationSystem:
    """
    AI 驱动的 NMR 谱图智能鉴定系统门面类。

    该类整合谱图解析、结构推测与专家报告生成，模拟从"谱图上传"
    到"结构生成、报告导出"的完整闭环。
    """

    def __init__(
        self,
        processor: Optional[SpectrumProcessor] = None,
        inference_engine: Optional[StructureInferenceEngine] = None,
        reasoning_engine: Optional[ExpertReasoningEngine] = None,
    ) -> None:
        """
        初始化系统服务。

        Args:
            processor: 谱图处理器。
            inference_engine: 结构推测引擎。
            reasoning_engine: 专家推理引擎。
        """
        self.processor = processor or SpectrumProcessor()
        self.inference_engine = inference_engine or StructureInferenceEngine()
        self.reasoning_engine = reasoning_engine or ExpertReasoningEngine()

    def analyze_spectrum(
        self,
        spectrum: Spectrum,
        max_candidates: int = DEFAULT_MAX_CANDIDATES,
    ) -> AnalysisReport:
        """
        分析谱图并生成结构鉴定报告。

        Args:
            spectrum: 输入谱图。
            max_candidates: 最大结构候选数量。

        Returns:
            AnalysisReport: 鉴定报告。

        Raises:
            ValueError: 当输入谱图非法时抛出。
        """
        if spectrum is None:
            raise ValueError("输入谱图不能为空。")

        parsed_spectrum = self.processor.parse(spectrum)
        candidates = self.inference_engine.infer(
            parsed_spectrum,
            max_candidates=max_candidates,
        )
        report = self.reasoning_engine.generate_report(parsed_spectrum, candidates)

        LOGGER.info(
            "结构鉴定完成: 报告编号=%s, 最佳候选=%s",
            report.report_id,
            report.candidates[0].name if report.candidates else "无",
        )

        return report

    def analyze_file(
        self,
        file_path: str | Path,
        output_path: str | Path = DEFAULT_OUTPUT_REPORT_PATH,
    ) -> AnalysisReport:
        """
        从文件读取谱图、执行分析并导出报告。

        Args:
            file_path: 输入谱图文件路径。
            output_path: 输出报告文件路径。

        Returns:
            AnalysisReport: 鉴定报告。

        Raises:
            FileNotFoundError: 当输入文件不存在时抛出。
            ValueError: 当文件内容非法时抛出。
            OSError: 当报告写入失败时抛出。
        """
        spectrum = SpectrumInputLoader.load_from_file(file_path)
        report = self.analyze_spectrum(spectrum)
        JsonReportWriter.write(report, output_path)
        return report
