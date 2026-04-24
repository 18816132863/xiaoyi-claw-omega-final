#!/usr/bin/env python3
"""
学习系统 - V1.0.0

提供经验积累、知识更新和能力提升能力。
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


class LearningType(Enum):
    """学习类型"""
    SUPERVISED = "supervised"      # 监督学习
    UNSUPERVISED = "unsupervised"  # 无监督学习
    REINFORCEMENT = "reinforcement"  # 强化学习
    TRANSFER = "transfer"          # 迁移学习
    META = "meta"                  # 元学习


class KnowledgeType(Enum):
    """知识类型"""
    FACT = "fact"              # 事实知识
    PROCEDURE = "procedure"    # 过程知识
    CONCEPT = "concept"        # 概念知识
    METACOGNITIVE = "metacognitive"  # 元认知知识
    HEURISTIC = "heuristic"    # 启发式知识


@dataclass
class Knowledge:
    """知识条目"""
    id: str
    type: KnowledgeType
    content: str
    context: str
    confidence: float
    source: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0


@dataclass
class Experience:
    """经验"""
    id: str
    situation: str
    action: str
    outcome: str
    success: bool
    lessons: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningResult:
    """学习结果"""
    new_knowledge: List[Knowledge]
    updated_knowledge: List[Knowledge]
    insights: List[str]
    confidence: float


class LearningSystem:
    """学习系统"""
    
    def __init__(self, storage_path: str = "memory/learning"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_base: Dict[str, Knowledge] = {}
        self.experience_base: List[Experience] = []
        self.learning_history: List[LearningResult] = []
        
        self._load_knowledge()
    
    def _load_knowledge(self):
        """加载已有知识"""
        knowledge_file = self.storage_path / "knowledge.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for k in data.get("knowledge", []):
                        knowledge = Knowledge(
                            id=k["id"],
                            type=KnowledgeType(k["type"]),
                            content=k["content"],
                            context=k["context"],
                            confidence=k["confidence"],
                            source=k["source"]
                        )
                        self.knowledge_base[knowledge.id] = knowledge
            except:
                pass
    
    def _save_knowledge(self):
        """保存知识"""
        knowledge_file = self.storage_path / "knowledge.json"
        data = {
            "knowledge": [
                {
                    "id": k.id,
                    "type": k.type.value,
                    "content": k.content,
                    "context": k.context,
                    "confidence": k.confidence,
                    "source": k.source
                }
                for k in self.knowledge_base.values()
            ]
        }
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def learn(self,
              experience: Experience,
              learning_type: LearningType = LearningType.REINFORCEMENT) -> LearningResult:
        """
        从经验中学习
        
        Args:
            experience: 经验
            learning_type: 学习类型
        
        Returns:
            学习结果
        """
        new_knowledge = []
        updated_knowledge = []
        insights = []
        
        if learning_type == LearningType.REINFORCEMENT:
            # 强化学习：根据结果调整
            if experience.success:
                # 成功经验 -> 强化
                knowledge = self._extract_knowledge(experience)
                if knowledge:
                    new_knowledge.append(knowledge)
                    insights.append(f"成功模式: {knowledge.content[:50]}")
            else:
                # 失败经验 -> 调整
                knowledge = self._extract_failure_knowledge(experience)
                if knowledge:
                    new_knowledge.append(knowledge)
                    insights.append(f"失败教训: {knowledge.content[:50]}")
        
        elif learning_type == LearningType.SUPERVISED:
            # 监督学习：从明确反馈中学习
            for lesson in experience.lessons:
                knowledge = Knowledge(
                    id=f"k_{len(self.knowledge_base)}",
                    type=KnowledgeType.FACT,
                    content=lesson,
                    context=experience.situation,
                    confidence=0.8,
                    source="supervised_learning"
                )
                new_knowledge.append(knowledge)
        
        elif learning_type == LearningType.META:
            # 元学习：学习如何学习
            meta_insights = self._meta_learn(experience)
            insights.extend(meta_insights)
        
        # 更新知识库
        for k in new_knowledge:
            self.knowledge_base[k.id] = k
        
        for k in updated_knowledge:
            k.updated_at = datetime.now()
        
        # 保存经验
        self.experience_base.append(experience)
        
        # 计算置信度
        confidence = self._calculate_learning_confidence(new_knowledge, updated_knowledge)
        
        result = LearningResult(
            new_knowledge=new_knowledge,
            updated_knowledge=updated_knowledge,
            insights=insights,
            confidence=confidence
        )
        
        self.learning_history.append(result)
        self._save_knowledge()
        
        return result
    
    def _extract_knowledge(self, experience: Experience) -> Optional[Knowledge]:
        """从成功经验中提取知识"""
        if not experience.lessons:
            # 自动提取
            lesson = f"在 {experience.situation[:30]} 情况下，执行 {experience.action[:30]} 成功"
        else:
            lesson = experience.lessons[0]
        
        return Knowledge(
            id=f"k_{len(self.knowledge_base)}",
            type=KnowledgeType.PROCEDURE,
            content=lesson,
            context=experience.situation,
            confidence=0.7,
            source="experience"
        )
    
    def _extract_failure_knowledge(self, experience: Experience) -> Optional[Knowledge]:
        """从失败经验中提取知识"""
        lesson = f"避免: 在 {experience.situation[:30]} 情况下执行 {experience.action[:30]}"
        
        return Knowledge(
            id=f"k_{len(self.knowledge_base)}",
            type=KnowledgeType.HEURISTIC,
            content=lesson,
            context=experience.situation,
            confidence=0.6,
            source="failure_experience"
        )
    
    def _meta_learn(self, experience: Experience) -> List[str]:
        """元学习"""
        insights = []
        
        # 分析学习模式
        if len(self.experience_base) > 10:
            recent = self.experience_base[-10:]
            success_rate = sum(1 for e in recent if e.success) / len(recent)
            
            if success_rate > 0.8:
                insights.append("元学习: 当前学习策略高效")
            elif success_rate < 0.5:
                insights.append("元学习: 需要调整学习策略")
        
        return insights
    
    def _calculate_learning_confidence(self, new: List[Knowledge], updated: List[Knowledge]) -> float:
        """计算学习置信度"""
        if not new and not updated:
            return 0.0
        
        # 基于新知识数量
        base = min(len(new) * 0.2, 0.5)
        
        # 基于知识置信度
        if new:
            avg_confidence = sum(k.confidence for k in new) / len(new)
            base += avg_confidence * 0.3
        
        return min(base, 1.0)
    
    def query_knowledge(self, query: str, top_k: int = 5) -> List[Knowledge]:
        """查询知识"""
        results = []
        query_lower = query.lower()
        
        for k in self.knowledge_base.values():
            score = 0
            if query_lower in k.content.lower():
                score += 0.5
            if query_lower in k.context.lower():
                score += 0.3
            
            # 使用频率加成
            score += min(k.usage_count * 0.01, 0.2)
            
            if score > 0:
                results.append((k, score))
        
        # 排序并返回
        results.sort(key=lambda x: -x[1])
        
        # 更新使用计数
        for k, _ in results[:top_k]:
            k.usage_count += 1
        
        return [k for k, _ in results[:top_k]]
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        return {
            "total_knowledge": len(self.knowledge_base),
            "total_experiences": len(self.experience_base),
            "learning_sessions": len(self.learning_history),
            "knowledge_by_type": {
                t.value: sum(1 for k in self.knowledge_base.values() if k.type == t)
                for t in KnowledgeType
            },
            "success_rate": (
                sum(1 for e in self.experience_base if e.success) / len(self.experience_base)
                if self.experience_base else 0
            )
        }
    
    def transfer_knowledge(self, source_context: str, target_context: str) -> List[Knowledge]:
        """迁移知识"""
        # 找到源上下文的知识
        source_knowledge = [
            k for k in self.knowledge_base.values()
            if source_context.lower() in k.context.lower()
        ]
        
        # 创建迁移后的知识
        transferred = []
        for k in source_knowledge:
            new_k = Knowledge(
                id=f"k_{len(self.knowledge_base)}_{k.id}",
                type=k.type,
                content=k.content,
                context=target_context,
                confidence=k.confidence * 0.8,  # 迁移降低置信度
                source=f"transfer_from_{k.id}"
            )
            transferred.append(new_k)
            self.knowledge_base[new_k.id] = new_k
        
        self._save_knowledge()
        return transferred


# 全局学习系统
_learning_system: Optional[LearningSystem] = None


def get_learning_system() -> LearningSystem:
    """获取全局学习系统"""
    global _learning_system
    if _learning_system is None:
        _learning_system = LearningSystem()
    return _learning_system
