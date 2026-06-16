# -*- coding: utf-8 -*-
"""
NMR — AI驱动的化学核磁共振谱图智能鉴定系统包。

本包将原单文件 NMR_Identification.py 按功能拆分为多个模块：
  - config:         常量与配置
  - logging_config: 日志配置
  - models:         数据模型（枚举、数据类）
  - io:             输入输出与文件加载
  - processing:     谱图信号处理与峰识别
  - prediction:     理论谱图预测
  - database:       结构知识库
  - inference:      结构推测引擎
  - reasoning:      专家推理与报告生成
  - system:         系统应用服务层（门面类）
  - demo:           示例数据生成与命令行入口

用法:
    from NMR.system import NmrAiIdentificationSystem
    system = NmrAiIdentificationSystem()
    report = system.analyze_file("input.csv")
"""

from NMR.config import (
    MODULE_NAME,
    VERSION,
    AUTHOR,
    DEFAULT_RANDOM_SEED,
    DEFAULT_NOISE_THRESHOLD_RATIO,
    DEFAULT_PEAK_MIN_DISTANCE,
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_TOP_K_REPORT,
    DEFAULT_OUTPUT_REPORT_PATH,
    SUPPORTED_NUCLEI,
    SUPPORTED_INPUT_SUFFIXES,
    LOGGER_NAME,
)
from NMR.logging_config import configure_logging, LOGGER
from NMR.models import (
    SpectrumType,
    SpectrumPoint,
    Peak,
    Spectrum,
    ParsedSpectrum,
    MolecularCandidate,
    AnalysisReport,
)
from NMR.io import SpectrumInputLoader, JsonReportWriter
from NMR.processing import SpectrumProcessor
from NMR.prediction import HeuristicSpectrumPredictor
from NMR.database import StructureDatabase
from NMR.inference import StructureInferenceEngine
from NMR.reasoning import ExpertReasoningEngine
from NMR.system import NmrAiIdentificationSystem
from NMR.demo import DemoSpectrumFactory, print_report_summary, main

__all__ = [
    # 配置
    "MODULE_NAME",
    "VERSION",
    "AUTHOR",
    "DEFAULT_RANDOM_SEED",
    "DEFAULT_NOISE_THRESHOLD_RATIO",
    "DEFAULT_PEAK_MIN_DISTANCE",
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_TOP_K_REPORT",
    "DEFAULT_OUTPUT_REPORT_PATH",
    "SUPPORTED_NUCLEI",
    "SUPPORTED_INPUT_SUFFIXES",
    "LOGGER_NAME",
    # 日志
    "configure_logging",
    "LOGGER",
    # 数据模型
    "SpectrumType",
    "SpectrumPoint",
    "Peak",
    "Spectrum",
    "ParsedSpectrum",
    "MolecularCandidate",
    "AnalysisReport",
    # 输入输出
    "SpectrumInputLoader",
    "JsonReportWriter",
    # 信号处理
    "SpectrumProcessor",
    # 理论预测
    "HeuristicSpectrumPredictor",
    # 结构库
    "StructureDatabase",
    # 结构推测
    "StructureInferenceEngine",
    # 专家推理
    "ExpertReasoningEngine",
    # 系统服务
    "NmrAiIdentificationSystem",
    # 演示
    "DemoSpectrumFactory",
    "print_report_summary",
    "main",
]
