# -*- coding: utf-8 -*-
"""
谱图信号处理与峰识别模块。

实现了谱图去噪、基线校正、局部极大值峰识别、梯形积分与峰合并。
"""

from __future__ import annotations

import math
import statistics
from typing import List, Sequence, Tuple

from NMR.config import DEFAULT_NOISE_THRESHOLD_RATIO, DEFAULT_PEAK_MIN_DISTANCE
from NMR.logging_config import LOGGER
from NMR.models import ParsedSpectrum, Peak, Spectrum, SpectrumPoint


class SpectrumProcessor:
    """
    谱图智能解析与一键数字化处理器。

    当前实现包含:
    1. 移动平均去噪；
    2. 基线校正；
    3. 局部极大值峰识别；
    4. 简化梯形积分。

    复杂度:
        对于 n 个采样点，主要处理流程时间复杂度为 O(n)，空间复杂度为 O(n)。
    """

    def __init__(
        self,
        noise_threshold_ratio: float = DEFAULT_NOISE_THRESHOLD_RATIO,
        peak_min_distance: float = DEFAULT_PEAK_MIN_DISTANCE,
    ) -> None:
        """
        初始化谱图处理器。

        Args:
            noise_threshold_ratio: 噪声阈值比例，范围为 0 到 1。
            peak_min_distance: 峰之间最小化学位移距离，单位 ppm。

        Raises:
            ValueError: 当配置参数非法时抛出。
        """
        if not 0 < noise_threshold_ratio < 1:
            raise ValueError("噪声阈值比例必须位于 0 到 1 之间。")
        if peak_min_distance <= 0:
            raise ValueError("峰最小距离必须大于 0。")

        self.noise_threshold_ratio = noise_threshold_ratio
        self.peak_min_distance = peak_min_distance

    def parse(self, spectrum: Spectrum) -> ParsedSpectrum:
        """
        解析谱图并提取峰特征。

        Args:
            spectrum: 原始谱图。

        Returns:
            ParsedSpectrum: 谱图解析结果。

        Raises:
            ValueError: 当谱图为空或采样点数量不足时抛出。
        """
        if spectrum is None or not spectrum.points:
            raise ValueError("谱图不能为空。")
        if len(spectrum.points) < 3:
            raise ValueError("谱图采样点数量至少需要 3 个。")

        sorted_points = sorted(spectrum.points, key=lambda point: point.shift)
        denoised_points = self._denoise(sorted_points)
        corrected_points = self._baseline_correct(denoised_points)
        peaks = self._detect_peaks(corrected_points)
        quality_score = self._estimate_quality(sorted_points, corrected_points, peaks)

        LOGGER.info(
            "谱图解析完成: 类型=%s, 采样点=%d, 峰数量=%d, 质量=%.3f",
            spectrum.spectrum_type.value,
            len(spectrum.points),
            len(peaks),
            quality_score,
        )

        return ParsedSpectrum(
            raw_spectrum=spectrum,
            denoised_points=corrected_points,
            peaks=peaks,
            quality_score=quality_score,
        )

    # ------------------------------------------------------------------
    # 内部处理步骤
    # ------------------------------------------------------------------

    def _denoise(self, points: Sequence[SpectrumPoint], window_size: int = 5) -> List[SpectrumPoint]:
        """
        使用移动平均进行轻量级去噪。

        Args:
            points: 原始采样点。
            window_size: 移动平均窗口大小。

        Returns:
            List[SpectrumPoint]: 去噪后的采样点。
        """
        if window_size < 1:
            raise ValueError("窗口大小必须大于 0。")

        half_window = window_size // 2
        result: List[SpectrumPoint] = []

        for index, point in enumerate(points):
            left = max(0, index - half_window)
            right = min(len(points), index + half_window + 1)
            local_values = [item.intensity for item in points[left:right]]
            averaged_intensity = sum(local_values) / len(local_values)
            result.append(SpectrumPoint(point.shift, averaged_intensity))

        return result

    def _baseline_correct(self, points: Sequence[SpectrumPoint]) -> List[SpectrumPoint]:
        """
        基线校正。

        Args:
            points: 去噪采样点。

        Returns:
            List[SpectrumPoint]: 基线校正后的采样点。
        """
        intensities = [point.intensity for point in points]
        baseline = min(intensities)
        return [
            SpectrumPoint(point.shift, max(0.0, point.intensity - baseline))
            for point in points
        ]

    def _detect_peaks(self, points: Sequence[SpectrumPoint]) -> List[Peak]:
        """
        识别局部极大值谱峰。

        Args:
            points: 基线校正后的采样点。

        Returns:
            List[Peak]: 识别到的谱峰列表。
        """
        max_intensity = max(point.intensity for point in points)
        if max_intensity <= 0:
            return []

        threshold = max_intensity * self.noise_threshold_ratio
        candidate_peaks: List[Peak] = []

        for index in range(1, len(points) - 1):
            previous_point = points[index - 1]
            current_point = points[index]
            next_point = points[index + 1]

            is_local_maximum = (
                current_point.intensity >= previous_point.intensity
                and current_point.intensity > next_point.intensity
                and current_point.intensity >= threshold
            )

            if not is_local_maximum:
                continue

            left_index, right_index = self._expand_peak_region(points, index, threshold)
            area = self._integrate(points[left_index:right_index + 1])
            width = abs(points[right_index].shift - points[left_index].shift)
            confidence = min(1.0, current_point.intensity / max_intensity)
            assignment = self._assign_peak_region(current_point.shift)

            candidate_peaks.append(
                Peak(
                    shift=current_point.shift,
                    intensity=current_point.intensity,
                    area=area,
                    width=width,
                    assignment=assignment,
                    confidence=confidence,
                )
            )

        return self._merge_close_peaks(candidate_peaks)

    def _expand_peak_region(
        self,
        points: Sequence[SpectrumPoint],
        peak_index: int,
        threshold: float,
    ) -> Tuple[int, int]:
        """
        以峰顶为中心扩展积分区域。

        Args:
            points: 采样点列表。
            peak_index: 峰顶索引。
            threshold: 噪声阈值。

        Returns:
            Tuple[int, int]: 积分区域左右索引。
        """
        left_index = peak_index
        right_index = peak_index
        boundary_threshold = threshold * 0.45

        while left_index > 0 and points[left_index].intensity > boundary_threshold:
            left_index -= 1

        while (
            right_index < len(points) - 1
            and points[right_index].intensity > boundary_threshold
        ):
            right_index += 1

        return left_index, right_index

    def _integrate(self, points: Sequence[SpectrumPoint]) -> float:
        """
        使用梯形法近似积分。

        Args:
            points: 峰区域采样点。

        Returns:
            float: 近似积分面积。
        """
        if len(points) < 2:
            return points[0].intensity if points else 0.0

        area = 0.0
        for left, right in zip(points, points[1:]):
            delta_shift = abs(right.shift - left.shift)
            area += (left.intensity + right.intensity) * delta_shift / 2.0

        return area

    def _merge_close_peaks(self, peaks: Sequence[Peak]) -> List[Peak]:
        """
        合并距离过近的谱峰。

        Args:
            peaks: 候选谱峰列表。

        Returns:
            List[Peak]: 合并后的谱峰列表。
        """
        if not peaks:
            return []

        sorted_peaks = sorted(peaks, key=lambda peak: peak.shift)
        merged: List[Peak] = [sorted_peaks[0]]

        for peak in sorted_peaks[1:]:
            last_peak = merged[-1]
            if abs(peak.shift - last_peak.shift) < self.peak_min_distance:
                # 保留强度更高的峰，并合并面积以避免积分信息丢失。
                stronger_peak = peak if peak.intensity > last_peak.intensity else last_peak
                merged[-1] = Peak(
                    shift=stronger_peak.shift,
                    intensity=stronger_peak.intensity,
                    area=peak.area + last_peak.area,
                    width=max(peak.width, last_peak.width),
                    assignment=stronger_peak.assignment,
                    confidence=max(peak.confidence, last_peak.confidence),
                )
            else:
                merged.append(peak)

        return merged

    def _estimate_quality(
        self,
        raw_points: Sequence[SpectrumPoint],
        corrected_points: Sequence[SpectrumPoint],
        peaks: Sequence[Peak],
    ) -> float:
        """
        估算谱图质量评分。

        Args:
            raw_points: 原始采样点。
            corrected_points: 校正后采样点。
            peaks: 识别到的谱峰列表。

        Returns:
            float: 质量评分，范围为 0 到 1。
        """
        if not peaks:
            return 0.2

        raw_values = [point.intensity for point in raw_points]
        corrected_values = [point.intensity for point in corrected_points]

        signal = max(corrected_values)
        noise = statistics.pstdev(raw_values) if len(raw_values) > 1 else 0.0
        signal_to_noise = signal / (noise + 1e-9)

        peak_density_penalty = min(0.25, len(peaks) / max(1, len(raw_points)) * 10)
        quality = 0.45 + min(0.45, math.log1p(signal_to_noise) / 8) - peak_density_penalty
        return round(max(0.0, min(1.0, quality)), 4)

    def _assign_peak_region(self, shift: float) -> str:
        """
        根据 1H NMR 常见化学位移区域进行启发式归属。

        Args:
            shift: 化学位移。

        Returns:
            str: 峰归属说明。
        """
        if 0.0 <= shift < 1.8:
            return "脂肪族氢信号"
        if 1.8 <= shift < 3.2:
            return "邻近杂原子或羰基的脂肪族氢信号"
        if 3.2 <= shift < 5.5:
            return "醇、醚、卤代烃或烯丙位相关氢信号"
        if 5.5 <= shift < 6.8:
            return "烯烃氢信号"
        if 6.8 <= shift < 8.5:
            return "芳香环氢信号"
        if 8.5 <= shift < 10.5:
            return "醛基或强去屏蔽芳香氢信号"
        if 10.5 <= shift <= 13.5:
            return "羧酸、酚羟基或氢键相关活泼氢信号"
        return "非常规或待确认信号"
