"""
Scheduler - 定时任务系统
Cron 风格的定时自动化
"""

import schedule
import time
import threading
import uuid
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """调度类型"""
    ONCE = "once"
    EVERY = "every"
    CRON = "cron"


@dataclass
class ScheduledJob:
    """定时任务"""
    id: str
    name: str
    schedule_type: ScheduleType
    schedule_config: Dict
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    max_runs: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)


class Scheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.jobs: Dict[str, ScheduledJob] = {}
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("⏰ 定时调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("⏹️ 定时调度器已停止")
    
    def _run_loop(self):
        """运行循环"""
        while self.running:
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            time.sleep(1)
    
    def schedule_every(
        self,
        interval: int,
        unit: str,  # seconds, minutes, hours, days
        func: Callable,
        *args,
        name: str = "",
        max_runs: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        定时执行
        
        Args:
            interval: 间隔数值
            unit: 单位 (seconds/minutes/hours/days)
            func: 执行函数
            name: 任务名称
            max_runs: 最大执行次数
        """
        job_id = str(uuid.uuid4())[:8]
        
        # 创建 schedule job
        if unit == "seconds":
            sched_job = schedule.every(interval).seconds
        elif unit == "minutes":
            sched_job = schedule.every(interval).minutes
        elif unit == "hours":
            sched_job = schedule.every(interval).hours
        elif unit == "days":
            sched_job = schedule.every(interval).days
        else:
            raise ValueError(f"Unknown unit: {unit}")
        
        # 包装函数
        def wrapper():
            job = self.jobs.get(job_id)
            if not job or not job.enabled:
                return
            
            if job.max_runs and job.run_count >= job.max_runs:
                job.enabled = False
                return
            
            try:
                func(*args, **kwargs)
                job.run_count += 1
                job.last_run = datetime.now()
            except Exception as e:
                logger.error(f"Job {job_id} error: {e}")
        
        sched_job.do(wrapper)
        
        # 保存
        job = ScheduledJob(
            id=job_id,
            name=name or func.__name__,
            schedule_type=ScheduleType.EVERY,
            schedule_config={"interval": interval, "unit": unit},
            func=func,
            args=args,
            kwargs=kwargs,
            max_runs=max_runs
        )
        
        with self._lock:
            self.jobs[job_id] = job
        
        print(f"📅 定时任务已创建: {job.name} (每 {interval} {unit})")
        return job_id
    
    def schedule_daily(
        self,
        at_time: str,  # "HH:MM"
        func: Callable,
        *args,
        name: str = "",
        **kwargs
    ) -> str:
        """每天定时执行"""
        job_id = str(uuid.uuid4())[:8]
        
        def wrapper():
            job = self.jobs.get(job_id)
            if job and job.enabled:
                try:
                    func(*args, **kwargs)
                    job.run_count += 1
                    job.last_run = datetime.now()
                except Exception as e:
                    logger.error(f"Job {job_id} error: {e}")
        
        schedule.every().day.at(at_time).do(wrapper)
        
        job = ScheduledJob(
            id=job_id,
            name=name or func.__name__,
            schedule_type=ScheduleType.EVERY,
            schedule_config={"at": at_time},
            func=func,
            args=args,
            kwargs=kwargs
        )
        
        with self._lock:
            self.jobs[job_id] = job
        
        print(f"📅 每日任务已创建: {job.name} (每天 {at_time})")
        return job_id
    
    def schedule_once(
        self,
        delay_seconds: int,
        func: Callable,
        *args,
        name: str = "",
        **kwargs
    ) -> str:
        """延迟执行一次"""
        job_id = str(uuid.uuid4())[:8]
        
        def wrapper():
            job = self.jobs.get(job_id)
            if job and job.enabled:
                try:
                    func(*args, **kwargs)
                    job.run_count += 1
                    job.last_run = datetime.now()
                    job.enabled = False  # 只执行一次
                except Exception as e:
                    logger.error(f"Job {job_id} error: {e}")
        
        # 使用延迟执行
        def delayed_run():
            time.sleep(delay_seconds)
            wrapper()
        
        thread = threading.Thread(target=delayed_run, daemon=True)
        thread.start()
        
        job = ScheduledJob(
            id=job_id,
            name=name or func.__name__,
            schedule_type=ScheduleType.ONCE,
            schedule_config={"delay": delay_seconds},
            func=func,
            args=args,
            kwargs=kwargs
        )
        
        with self._lock:
            self.jobs[job_id] = job
        
        print(f"📅 延迟任务已创建: {job.name} ({delay_seconds}s 后执行)")
        return job_id
    
    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        """获取任务"""
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[ScheduledJob]:
        """列出所有任务"""
        return list(self.jobs.values())
    
    def enable_job(self, job_id: str) -> bool:
        """启用任务"""
        job = self.jobs.get(job_id)
        if job:
            job.enabled = True
            return True
        return False
    
    def disable_job(self, job_id: str) -> bool:
        """禁用任务"""
        job = self.jobs.get(job_id)
        if job:
            job.enabled = False
            return True
        return False
    
    def remove_job(self, job_id: str) -> bool:
        """删除任务"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False
    
    def clear_all(self):
        """清除所有任务"""
        schedule.clear()
        self.jobs.clear()
        print("🗑️ 所有定时任务已清除")


# 快捷函数
_scheduler: Optional[Scheduler] = None

def get_scheduler() -> Scheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
        _scheduler.start()
    return _scheduler

def schedule_every(interval: int, unit: str, func: Callable, *args, **kwargs) -> str:
    """每 X 单位执行"""
    return get_scheduler().schedule_every(interval, unit, func, *args, **kwargs)

def schedule_daily(at_time: str, func: Callable, *args,