python library (why not go)
1. tiktoken 
2. vector

concurrent.futures.Future 通常用于处理 CPU-bound 任务（计算密集型任务），例如并行计算。它在多线程和多进程环境中都能使用。
asyncio.create_task() 主要用于处理 I/O-bound 任务（I/O 密集型任务），例如网络请求、文件操作等。它适用于异步编程场景，可以在单线程中处理多个协程任务。
