"""
SEO AIOS 自动化工作流引擎
Automation Workflow Engine
"""

from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from enum import Enum
import json


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepType(Enum):
    """步骤类型"""
    TRIGGER = "trigger"           # 触发器
    GENERATE = "generate"          # AI生成
    REWRITE = "rewrite"           # AI改写
    CRAWL = "crawl"               # 爬取
    ANALYZE = "analyze"           # 分析
    PUBLISH = "publish"           # 发布
    WAIT = "wait"                 # 等待
    CONDITION = "condition"        # 条件判断
    NOTIFICATION = "notification"  # 通知


class WorkflowStep:
    """工作流步骤"""

    def __init__(self, step_type: str, config: Dict, name: str = None):
        self.step_type = StepType(step_type)
        self.config = config
        self.name = name or step_type
        self.status = WorkflowStatus.PENDING
        self.result = None
        self.error = None

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'type': self.step_type.value,
            'config': self.config,
            'status': self.status.value,
            'result': self.result,
            'error': self.error
        }


class WorkflowDefinition:
    """工作流定义"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.variables: Dict = {}
        self.created_at = datetime.utcnow()

    def add_step(self, step: WorkflowStep):
        """添加步骤"""
        self.steps.append(step)
        return self

    def set_variable(self, key: str, value: Any):
        """设置变量"""
        self.variables[key] = value

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'description': self.description,
            'steps': [s.to_dict() for s in self.steps],
            'variables': self.variables,
            'created_at': self.created_at.isoformat()
        }


class WorkflowEngine:
    """
    工作流引擎
    执行自动化SEO任务
    """

    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self._register_default_workflows()

    def _register_default_workflows(self):
        """注册默认工作流"""

        # 工作流1: 关键词→生成→发布
        self.register_workflow(self._create_keyword_to_publish_workflow())

        # 工作流2: 爬取→改写→发布
        self.register_workflow(self._create_crawl_rewrite_publish_workflow())

        # 工作流3: 批量内容生成
        self.register_workflow(self._create_batch_generation_workflow())

        # 工作流4: 竞品分析
        self.register_workflow(self._create_competitor_analysis_workflow())

    def register_workflow(self, workflow: WorkflowDefinition):
        """注册工作流"""
        self.workflows[workflow.name] = workflow

    def get_workflow(self, name: str) -> Optional[WorkflowDefinition]:
        """获取工作流"""
        return self.workflows.get(name)

    def list_workflows(self) -> List[Dict]:
        """列出所有工作流"""
        return [
            {'name': w.name, 'description': w.description, 'steps': len(w.steps)}
            for w in self.workflows.values()
        ]

    def execute_workflow(self, workflow_name: str, context: Dict) -> Dict:
        """
        执行工作流

        Args:
            workflow_name: 工作流名称
            context: 执行上下文

        Returns:
            执行结果
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            return {'success': False, 'error': f'工作流 {workflow_name} 不存在'}

        results = {
            'workflow': workflow_name,
            'started_at': datetime.utcnow().isoformat(),
            'steps': [],
            'success': True
        }

        # 合并变量
        variables = {**workflow.variables, **context}

        for i, step in enumerate(workflow.steps):
            step_result = self._execute_step(step, variables)
            results['steps'].append(step_result)

            if not step_result.get('success', False):
                results['success'] = False
                results['error'] = f"步骤 {step.name} 执行失败: {step_result.get('error')}"
                break

            # 更新变量
            if step_result.get('output'):
                variables.update(step_result['output'])

        results['completed_at'] = datetime.utcnow().isoformat()
        results['variables'] = variables

        return results

    def _execute_step(self, step: WorkflowStep, context: Dict) -> Dict:
        """执行单个步骤"""
        step.status = WorkflowStatus.RUNNING

        try:
            if step.step_type == StepType.GENERATE:
                result = self._execute_generate(step.config, context)
            elif step.step_type == StepType.REWRITE:
                result = self._execute_rewrite(step.config, context)
            elif step.step_type == StepType.CRAWL:
                result = self._execute_crawl(step.config, context)
            elif step.step_type == StepType.ANALYZE:
                result = self._execute_analyze(step.config, context)
            elif step.step_type == StepType.PUBLISH:
                result = self._execute_publish(step.config, context)
            elif step.step_type == StepType.WAIT:
                result = self._execute_wait(step.config, context)
            elif step.step_type == StepType.CONDITION:
                result = self._execute_condition(step.config, context)
            elif step.step_type == StepType.NOTIFICATION:
                result = self._execute_notification(step.config, context)
            else:
                result = {'success': True, 'output': {}}

            step.status = WorkflowStatus.COMPLETED
            step.result = result
            return {'success': True, 'output': result.get('output', {})}

        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error = str(e)
            return {'success': False, 'error': str(e)}

    def _execute_generate(self, config: Dict, context: Dict) -> Dict:
        """执行内容生成"""
        from app.services.content_generator import ContentGenerator

        topic = config.get('topic', context.get('keyword', ''))
        keywords = config.get('keywords', [topic])
        length = config.get('length', 1500)

        # 获取AI配置
        ai_config = context.get('ai_config')
        if not ai_config:
            return {'success': False, 'error': '缺少AI配置'}

        generator = ContentGenerator(ai_config)
        result = generator.generate(topic, keywords, length)

        return {'success': True, 'output': {'article': result}}

    def _execute_rewrite(self, config: Dict, context: Dict) -> Dict:
        """执行内容改写"""
        from app.services.content_rewriter import ContentRewriter

        content = config.get('content', context.get('article', {}).get('content', ''))
        style = config.get('style', 'semantic')

        ai_config = context.get('ai_config')
        if not ai_config:
            return {'success': False, 'error': '缺少AI配置'}

        rewriter = ContentRewriter(ai_config)
        result = rewriter.rewrite(content, rewrite_type=style)

        return {'success': True, 'output': {'rewritten_content': result}}

    def _execute_crawl(self, config: Dict, context: Dict) -> Dict:
        """执行爬取"""
        from app.services.crawler import WebCrawler

        url = config.get('url', context.get('target_url'))
        max_depth = config.get('max_depth', 1)

        crawler = WebCrawler()
        result = crawler.crawl_url(url, max_depth=max_depth)

        return {'success': True, 'output': {'crawled_content': result}}

    def _execute_analyze(self, config: Dict, context: Dict) -> Dict:
        """执行分析"""
        from app.services.serp_analyzer import SERPAnalyzer

        keyword = config.get('keyword', context.get('keyword'))

        analyzer = SERPAnalyzer()
        result = analyzer.analyze_keyword(keyword)

        return {'success': True, 'output': {'analysis': result}}

    def _execute_publish(self, config: Dict, context: Dict) -> Dict:
        """执行发布"""
        # 这里可以集成WordPress发布或其他发布方式
        target = config.get('target', 'local')

        if target == 'wordpress':
            # WordPress发布
            return {'success': True, 'output': {'published': True, 'target': 'wordpress'}}
        else:
            # 本地保存
            return {'success': True, 'output': {'published': True, 'target': 'local'}}

    def _execute_wait(self, config: Dict, context: Dict) -> Dict:
        """执行等待"""
        import time
        seconds = config.get('seconds', 60)
        time.sleep(seconds)
        return {'success': True, 'output': {'waited': seconds}}

    def _execute_condition(self, config: Dict, context: Dict) -> Dict:
        """执行条件判断"""
        condition = config.get('condition', '')
        value = context.get(condition)

        # 简单条件判断
        if value:
            return {'success': True, 'output': {'condition_met': True}}
        else:
            return {'success': True, 'output': {'condition_met': False}}

    def _execute_notification(self, config: Dict, context: Dict) -> Dict:
        """执行通知"""
        # 可以集成邮件、Slack等通知
        return {'success': True, 'output': {'notified': True}}

    # ===== 默认工作流创建 =====

    def _create_keyword_to_publish_workflow(self) -> WorkflowDefinition:
        """创建关键词→生成→发布工作流"""
        wf = WorkflowDefinition(
            name="keyword_to_publish",
            description="从关键词到内容发布的完整流程"
        )

        wf.add_step(WorkflowStep(StepType.TRIGGER, {'type': 'keyword'}, "关键词触发"))
        wf.add_step(WorkflowStep(StepType.ANALYZE, {'keyword': '{{keyword}}'}, "SERP分析"))
        wf.add_step(WorkflowStep(StepType.GENERATE, {
            'topic': '{{keyword}}',
            'keywords': ['{{keyword}}'],
            'length': 1500
        }, "AI生成内容"))
        wf.add_step(WorkflowStep(StepType.WAIT, {'seconds': 5}, "等待处理"))
        wf.add_step(WorkflowStep(StepType.PUBLISH, {'target': 'local'}, "发布内容"))

        return wf

    def _create_crawl_rewrite_publish_workflow(self) -> WorkflowDefinition:
        """创建爬取→改写→发布工作流"""
        wf = WorkflowDefinition(
            name="crawl_rewrite_publish",
            description="爬取竞品内容→AI改写→自动发布"
        )

        wf.add_step(WorkflowStep(StepType.TRIGGER, {'type': 'url'}, "URL触发"))
        wf.add_step(WorkflowStep(StepType.CRAWL, {
            'url': '{{url}}',
            'max_depth': 1
        }, "爬取内容"))
        wf.add_step(WorkflowStep(StepType.REWRITE, {
            'style': 'semantic'
        }, "AI改写"))
        wf.add_step(WorkflowStep(StepType.PUBLISH, {'target': 'wordpress'}, "发布到WordPress"))

        return wf

    def _create_batch_generation_workflow(self) -> WorkflowDefinition:
        """创建批量生成工作流"""
        wf = WorkflowDefinition(
            name="batch_generation",
            description="批量生成多篇SEO优化文章"
        )

        wf.add_step(WorkflowStep(StepType.TRIGGER, {'type': 'keywords'}, "关键词列表"))
        wf.add_step(WorkflowStep(StepType.GENERATE, {
            'keywords': '{{keywords}}',
            'length': 1200
        }, "批量生成"))
        wf.add_step(WorkflowStep(StepType.PUBLISH, {'target': 'local'}, "批量发布"))

        return wf

    def _create_competitor_analysis_workflow(self) -> WorkflowDefinition:
        """创建竞品分析工作流"""
        wf = WorkflowDefinition(
            name="competitor_analysis",
            description="分析竞争对手并生成差异化内容"
        )

        wf.add_step(WorkflowStep(StepType.TRIGGER, {'type': 'keyword'}, "关键词触发"))
        wf.add_step(WorkflowStep(StepType.CRAWL, {
            'url': '{{competitor_url}}',
            'max_depth': 2
        }, "爬取竞品"))
        wf.add_step(WorkflowStep(StepType.ANALYZE, {'keyword': '{{keyword}}'}, "SERP分析"))
        wf.add_step(WorkflowStep(StepType.REWRITE, {
            'style': 'humanize'
        }, "差异化改写"))
        wf.add_step(WorkflowStep(StepType.PUBLISH, {'target': 'local'}, "发布内容"))

        return wf


# 全局工作流引擎
_workflow_engine = None


def get_workflow_engine() -> WorkflowEngine:
    """获取工作流引擎实例"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
