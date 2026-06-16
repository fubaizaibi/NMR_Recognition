# -*- coding: utf-8 -*-
"""
数据模型模块 — 枚举与数据类定义。

包含 NMR 谱图鉴定系统核心数据结构的类型定义。
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class SpectrumType(str, Enum):
    """
    谱图类型枚举。

    Attributes:
        PROTON: 一维氢谱。
        CARBON: 一维碳谱。
        HSQC: 二维 HSQC 谱。
        HMBC: 二维 HMBC 谱。
        COSY: 二维 COSY 谱。
    """

    PROTON = "1H"
    CARBON = "13C"
    HSQC = "HSQC"
    HMBC = "HMBC"
    COSY = "COSY"


@dataclass(frozen=True)
class SpectrumPoint:
    """
    谱图采样点。

    Args:
        shift: 化学位移，单位 ppm。
        intensity: 信号强度。

    Raises:
        ValueError: 当化学位移或强度不是有限数字时抛出。
    """

    shift: float
    intensity: float

    def __post_init__(self) -> None:
        """校验采样点字段合法性。"""
        if not math.isfinite(self.shift):
            raise ValueError("化学位移必须是有限数字。")
        if not math.isfinite(self.intensity):
            raise ValueError("信号强度必须是有限数字。")


@dataclass
class Peak:
    """
    谱峰特征。

    Args:
        shift: 峰顶化学位移，单位 ppm。
        intensity: 峰顶强度。
        area: 近似积分面积。
        width: 近似峰宽，单位 ppm。
        assignment: 峰归属说明。
        confidence: 峰识别置信度，范围为 0 到 1。

    Raises:
        ValueError: 当数值字段不合法时抛出。
    """

    shift: float
    intensity: float
    area: float
    width: float
    assignment: str = "未归属"
    confidence: float = 0.0

    def __post_init__(self) -> None:
        """校验谱峰字段合法性。"""
        if not all(
            math.isfinite(value)
            for value in (self.shift, self.intensity, self.area, self.width)
        ):
            raise ValueError("谱峰数值字段必须是有限数字。")
        if self.width < 0:
            raise ValueError("峰宽不能为负数。")
        if not 0 <= self.confidence <= 1:
            raise ValueError("置信度必须位于 0 到 1 之间。")


@dataclass
class Spectrum:
    """
    核磁谱图数据。

    Args:
        spectrum_type: 谱图类型。
        points: 一维谱图采样点列表。
        metadata: 谱图元数据。

    Raises:
        ValueError: 当谱图类型或采样点为空时抛出。
    """

    spectrum_type: SpectrumType
    points: List[SpectrumPoint]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """校验谱图数据合法性。"""
        if not isinstance(self.spectrum_type, SpectrumType):
            raise ValueError("谱图类型必须是 SpectrumType 枚举。")
        if not self.points:
            raise ValueError("谱图采样点不能为空。")


@dataclass
class ParsedSpectrum:
    """
    谱图解析结果。

    Args:
        raw_spectrum: 原始谱图。
        denoised_points: 去噪后的采样点。
        peaks: 识别到的谱峰列表。
        quality_score: 谱图质量评分，范围为 0 到 1。
    """

    raw_spectrum: Spectrum
    denoised_points: List[SpectrumPoint]
    peaks: List["Peak"]
    quality_score: float


@dataclass
class MolecularCandidate:
    """
    分子结构候选。

    Args:
        name: 化合物候选名称。
        smiles: SMILES 字符串。
        formula: 分子式。
        score: 匹配评分，范围为 0 到 1。
        evidence: 支持该候选的证据列表。
        predicted_peaks: 理论谱峰列表。
    """

    name: str
    smiles: str
    formula: str
    score: float
    evidence: List[str]
    predicted_peaks: List["Peak"]


@dataclass
class AnalysisReport:
    """
    谱图智能鉴定报告。

    Args:
        report_id: 报告编号。
        spectrum_type: 谱图类型。
        quality_score: 谱图质量评分。
        detected_peaks: 检出的谱峰列表。
        candidates: 结构候选列表。
        reasoning: 专家级解析推理文本。
        warnings: 风险提示或边界条件说明。
    """

    report_id: str
    spectrum_type: str
    quality_score: float
    detected_peaks: List["Peak"]
    candidates: List["MolecularCandidate"]
    reasoning: str
    warnings: List[str]
