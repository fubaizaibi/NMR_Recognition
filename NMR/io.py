# -*- coding: utf-8 -*-
"""
输入输出模块 — 谱图文件加载与报告导出。

支持从 CSV/JSON 读取谱图数据，以及将分析报告写入 JSON 文件。
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from NMR.config import SUPPORTED_INPUT_SUFFIXES
from NMR.models import AnalysisReport, Spectrum, SpectrumPoint, SpectrumType


class SpectrumInputLoader:
    """
    谱图输入加载器。

    支持从 CSV、JSON 文件读取一维谱图数据。CSV 格式要求包含 shift 和 intensity 两列。
    JSON 格式要求包含 spectrum_type 和 points 字段，points 为对象列表。

    Raises:
        FileNotFoundError: 当文件不存在时抛出。
        ValueError: 当文件格式或数据内容非法时抛出。
    """

    @staticmethod
    def load_from_file(file_path: str | Path) -> Spectrum:
        """
        从文件加载谱图数据。

        Args:
            file_path: 谱图文件路径。

        Returns:
            Spectrum: 谱图对象。

        Raises:
            FileNotFoundError: 当文件不存在时抛出。
            ValueError: 当文件后缀或文件内容不合法时抛出。
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"谱图文件不存在: {path}")
        if path.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
            raise ValueError(
                f"不支持的文件类型: {path.suffix}，支持类型: "
                f"{sorted(SUPPORTED_INPUT_SUFFIXES)}"
            )

        if path.suffix.lower() == ".csv":
            return SpectrumInputLoader._load_csv(path)
        return SpectrumInputLoader._load_json(path)

    @staticmethod
    def _load_csv(path: Path) -> Spectrum:
        """
        从 CSV 文件加载谱图数据。

        Args:
            path: CSV 文件路径。

        Returns:
            Spectrum: 谱图对象。

        Raises:
            ValueError: 当 CSV 字段或数值非法时抛出。
        """
        points: List[SpectrumPoint] = []
        spectrum_type = SpectrumType.PROTON

        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            required_fields = {"shift", "intensity"}
            if not reader.fieldnames or not required_fields.issubset(reader.fieldnames):
                raise ValueError("CSV 文件必须包含 shift 和 intensity 列。")

            for row_index, row in enumerate(reader, start=2):
                try:
                    points.append(
                        SpectrumPoint(
                            shift=float(row["shift"]),
                            intensity=float(row["intensity"]),
                        )
                    )
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"CSV 第{row_index}行数据非法。") from exc

        return Spectrum(
            spectrum_type=spectrum_type,
            points=points,
            metadata={"source": str(path), "format": "csv"},
        )

    @staticmethod
    def _load_json(path: Path) -> Spectrum:
        """
        从 JSON 文件加载谱图数据。

        Args:
            path: JSON 文件路径。

        Returns:
            Spectrum: 谱图对象。

        Raises:
            ValueError: 当 JSON 结构或数值非法时抛出。
        """
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        try:
            spectrum_type = SpectrumType(payload["spectrum_type"])
            raw_points = payload["points"]
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError("JSON 文件必须包含合法的 spectrum_type 和 points 字段。") from exc

        if not isinstance(raw_points, list):
            raise ValueError("points 字段必须是列表。")

        points = []
        for index, item in enumerate(raw_points):
            try:
                points.append(
                    SpectrumPoint(
                        shift=float(item["shift"]),
                        intensity=float(item["intensity"]),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"JSON 第{index}个采样点非法。") from exc

        return Spectrum(
            spectrum_type=spectrum_type,
            points=points,
            metadata={"source": str(path), "format": "json"},
        )


class JsonReportWriter:
    """
    JSON 报告写入器。

    将谱图分析报告写入本地 JSON 文件，便于后续 Web 平台或企业 API 读取。
    """

    @staticmethod
    def write(report: AnalysisReport, output_path: str | Path) -> Path:
        """
        将报告写入 JSON 文件。

        Args:
            report: 分析报告对象。
            output_path: 输出文件路径。

        Returns:
            Path: 实际写入的文件路径。

        Raises:
            ValueError: 当报告对象为空时抛出。
            OSError: 当文件写入失败时抛出。
        """
        if report is None:
            raise ValueError("报告对象不能为空。")

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        report_dict = asdict(report)
        with path.open("w", encoding="utf-8") as file:
            json.dump(report_dict, file, ensure_ascii=False, indent=2)

        return path
