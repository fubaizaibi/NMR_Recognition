# -*- coding: utf-8 -*-
"""
结构知识库模块。

模拟化学知识图谱和候选结构库。
真实系统中可连接 PubChem、MetaboLights、企业内部 ELN/LIMS 或向量数据库。
"""

from __future__ import annotations

from typing import Dict, List


class StructureDatabase:
    """
    结构知识库。

    该类模拟化学知识图谱和候选结构库。真实系统中可连接 PubChem、
    MetaboLights、企业内部 ELN/LIMS 或向量数据库。
    """

    def __init__(self) -> None:
        """初始化内置结构库。"""
        self._records: List[Dict[str, str]] = [
            {
                "key": "ethanol",
                "name": "乙醇",
                "smiles": "CCO",
                "formula": "C2H6O",
                "class": "醇类",
            },
            {
                "key": "acetone",
                "name": "丙酮",
                "smiles": "CC(=O)C",
                "formula": "C3H6O",
                "class": "酮类",
            },
            {
                "key": "toluene",
                "name": "甲苯",
                "smiles": "Cc1ccccc1",
                "formula": "C7H8",
                "class": "芳香烃",
            },
            {
                "key": "ethyl_acetate",
                "name": "乙酸乙酯",
                "smiles": "CCOC(=O)C",
                "formula": "C4H8O2",
                "class": "酯类",
            },
            {
                "key": "benzaldehyde",
                "name": "苯甲醛",
                "smiles": "O=Cc1ccccc1",
                "formula": "C7H6O",
                "class": "芳香醛",
            },
            {
                "key": "phenol",
                "name": "苯酚",
                "smiles": "Oc1ccccc1",
                "formula": "C6H6O",
                "class": "酚类",
            },
        ]

    def list_records(self) -> List[Dict[str, str]]:
        """
        返回结构库记录。

        Returns:
            List[Dict[str, str]]: 结构记录列表。
        """
        return list(self._records)
