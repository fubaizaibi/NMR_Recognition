# -*- coding: utf-8 -*-
"""
示例数据生成与命令行入口模块。

提供内置示例谱图工厂（基于高斯峰叠加模拟真实 1H NMR 采样点）
以及控制台报告打印和 CLI 入口点。
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import List, Optional

from NMR.config import (
    DEFAULT_OUTPUT_REPORT_PATH,
    DEFAULT_RANDOM_SEED,
    MODULE_NAME,
    VERSION,
)
from NMR.io import JsonReportWriter
from NMR.logging_config import LOGGER
from NMR.models import AnalysisReport, Spectrum, SpectrumPoint, SpectrumType
from NMR.prediction import HeuristicSpectrumPredictor
from NMR.system import NmrAiIdentificationSystem


class DemoSpectrumFactory:
    """
    示例谱图工厂。

    用于生成可运行演示数据，模拟真实 1H NMR 采样点。生成过程包括多个
    高斯峰叠加和轻量随机噪声。
    """

    @staticmethod
    def create_demo_spectrum(
        structure_key: str = "ethyl_acetate",
        seed: int = DEFAULT_RANDOM_SEED,
        point_count: int = 1400,
    ) -> Spectrum:
        """
        创建示例 1H NMR 谱图。

        Args:
            structure_key: 内置结构模板键。
            seed: 随机种子。
            point_count: 采样点数量。

        Returns:
            Spectrum: 示例谱图。

        Raises:
            ValueError: 当采样点数量非法或结构键不存在时抛出。
        """
        if point_count < 100:
            raise ValueError("示例谱图采样点数量至少为 100。")

        random.seed(seed)
        predictor = HeuristicSpectrumPredictor()
        template_peaks = predictor.predict(structure_key)

        min_shift = 0.0
        max_shift = 11.0
        step = (max_shift - min_shift) / (point_count - 1)
        points: List[SpectrumPoint] = []

        for index in range(point_count):
            shift = min_shift + index * step
            intensity = 0.0

            for peak in template_peaks:
                # 高斯峰模型用于模拟真实谱图峰形。
                sigma = 0.035 if peak.shift < 6.0 else 0.05
                amplitude = peak.area * 120.0
                exponent = -((shift - peak.shift) ** 2) / (2 * sigma ** 2)
                intensity += amplitude * math.exp(exponent)

            baseline = 3.0 + 0.08 * shift
            noise = random.gauss(0.0, 1.5)
            points.append(
                SpectrumPoint(shift=shift, intensity=max(0.0, intensity + baseline + noise))
            )

        return Spectrum(
            spectrum_type=SpectrumType.PROTON,
            points=points,
            metadata={
                "source": "demo",
                "simulated_structure": structure_key,
                "note": "该谱图由内置模板模拟生成，仅用于系统演示。",
            },
        )


def print_report_summary(report: AnalysisReport) -> None:
    """
    在控制台打印报告摘要。

    Args:
        report: 谱图分析报告。

    Raises:
        ValueError: 当报告为空时抛出。
    """
    if report is None:
        raise ValueError("报告不能为空。")

    print("=" * 80)
    print(f"报告编号: {report.report_id}")
    print(f"谱图类型: {report.spectrum_type}")
    print(f"质量评分: {report.quality_score:.2%}")
    print(f"检出峰数量: {len(report.detected_peaks)}")
    print("-" * 80)

    print("主要检出峰:")
    for peak in report.detected_peaks:
        print(
            f"  - {peak.shift:>5.2f} ppm | 强度 {peak.intensity:>8.2f} | "
            f"面积 {peak.area:>7.2f} | {peak.assignment}"
        )

    print("-" * 80)
    print("结构候选:")
    for index, candidate in enumerate(report.candidates, start=1):
        print(
            f"  {index}. {candidate.name} | {candidate.formula} | "
            f"评分 {candidate.score:.2%} | SMILES: {candidate.smiles}"
        )

    print("-" * 80)
    print("风险提示:")
    for warning in report.warnings:
        print(f"  - {warning}")
    print("=" * 80)


def main() -> None:
    """
    主程序入口。

    使用内置示例谱图模拟"谱图上传 -> 峰识别 -> 结构推测 -> 报告导出"
    的完整流程。

    TODO:
        1. 接入真实 NMR 厂商数据格式解析器；
        2. 将启发式峰识别替换为深度学习峰检测模型；
        3. 将内置结构库替换为可检索知识图谱和向量数据库；
        4. 增加二维 NMR 联合解析能力。
    """
    try:
        LOGGER.info("启动 %s v%s 演示流程。", MODULE_NAME, VERSION)

        demo_spectrum = DemoSpectrumFactory.create_demo_spectrum(
            structure_key="ethyl_acetate",
            point_count=1400,
        )

        system = NmrAiIdentificationSystem()
        report = system.analyze_spectrum(demo_spectrum)

        output_path = JsonReportWriter.write(report, DEFAULT_OUTPUT_REPORT_PATH)
        print_report_summary(report)

        LOGGER.info("报告已导出至: %s", output_path.resolve())

    except (ValueError, OSError, FileNotFoundError) as exc:
        LOGGER.exception("系统运行失败: %s", exc)
        raise


if __name__ == "__main__":
    main()
