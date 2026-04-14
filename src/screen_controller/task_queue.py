"""
Task Queue - 异步任务队列
后台执行耗时操作
"""

import asyncio
import threading
import uuid
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务对象"""
    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    on_progress: Optional[Callable] = None
    on_complete: Optional[Callable] = None


class TaskQueue:
    """异步任务队列"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self._lock = threading.Lock()
        self._workers: List[asyncio.Task] = []
    
    def start(self):
        """启动队列"""
        if self.running:
            return
        
        self.running = True
        self._loop = asyncio.new_event_loop()
        
        def run_loop():
            asyncio.set_event_loop(self._loop)
            for i in range(self.max_workers):
                worker = self._loop.create_task(self._worker(f"worker-{i}"))
                self._workers.append(worker)
            self._loop.run_forever()
        
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        print(f"✅ 任务队列已启动 ({self.max_workers} workers)")
    
    def stop(self):
        """停止队列"""
        self.running = False
        for worker in self._workers:
            worker.cancel()
        self._loop.call_soon_threadsafe(self._loop.stop)
        print("⏹️ 任务队列已停止")
    
    async def _worker(self, name: str):
        """工作线程"""
        while self.running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self._execute_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    async def _execute_task(self, task: Task):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            # 运行任务
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, task.func, *task.args, **task.kwargs
                )
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            logger.error(f"Task {task.id} failed: {e}")
        
        task.completed_at = datetime.now()
        task.progress = 100.0
        
        # 回调
        if task.on_complete:
            try:
                task.on_complete(task)
            except:
                pass
    
    def submit(
        self,
        func: Callable,
        *args,
        name: str = "",
        on_progress: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        **kwargs
    ) -> str:
        """
        提交任务
        
        Returns:
            task_id
        """
        task_id = str(uuid.uuid4())[:8]
        
        task = Task(
            id=task_id,
            name=name or func.__name__,
            func=func,
            args=args,
            kwargs=kwargs,
            on_progress=on_progress,
            on_complete=on_complete
        )
        
        with self._lock:
            self.tasks[task_id] = task
        
        asyncio.run_coroutine_threadsafe(self.queue.put(task), self._loop)
        
        print(f"📋 任务已提交: {task.name} ({task_id})")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """列出任务"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            return True
        return False
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total": len(self.tasks),
            "pending": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "running": len([t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]),
            "completed": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
        }


# 快捷函数
_queue: Optional[TaskQueue] = None

def get_queue(max_workers: int = 4) -> TaskQueue:
    global _queue
    if _queue is None:
        _queue = TaskQueue(max_workers)
        _queue.start()
    return _queue

def submit_task(func: Callable, *args, **kwargs) -> str:
    return get_queue().submit(func, *args, **kwargs)

def get_task_status(task_id: str) -> Optional[Dict]:
    task = get_queue().get_task(task_id)
    if task:
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status.value,
            "progress": task.progress,
            "result": task.result,
            "error": task.error
        }
    return None
