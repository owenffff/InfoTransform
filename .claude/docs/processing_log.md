next]  GET /favicon.ico 200 in 4ms
[api] 2025-10-31 00:31:29,506 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Saved file: 中医内科学（新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (张伯礼，吴勉华) (Z-Library).pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/中医内科学（新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (张伯礼，吴勉华) (Z-Library).pdf
[api] 2025-10-31 00:31:29,669 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Saved file: 中医舌诊完全图解 (吴中朝, 王彤) (Z-Library).pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/中医舌诊完全图解 (吴中朝, 王彤) (Z-Library).pdf
[api] 2025-10-31 00:31:29,704 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Saved file: 中医诊断学 (新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (李灿东) (Z-Library).pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/中医诊断学 (新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (李灿东) (Z-Library).pdf
[api] 2025-10-31 00:31:29,729 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Saved file: 舌诊十讲 (张坚著) (Z-Library).pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/舌诊十讲 (张坚著) (Z-Library).pdf
[api] 2025-10-31 00:31:29,776 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Saved file: 舌诊快速入门 (周幸来，周幸秋，孙冰主编) (Z-Library).pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/舌诊快速入门 (周幸来，周幸秋，孙冰主编) (Z-Library).pdf
[api] 2025-10-31 00:31:29,912 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Saved file: 象脉学 (许跃远著) (Z-Library).pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/象脉学 (许跃远著) (Z-Library).pdf
[api] INFO:     127.0.0.1:60239 - "POST /api/transform HTTP/1.1" 200 OK
[api] 2025-10-31 00:31:29,913 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Starting processing run: 6 files, model=report_summary, ai_model=openai.gpt-5-mini-2025-08-07
[api] 2025-10-31 00:31:36,793 - infotransform.processors.vision - INFO - Successfully processed 舌诊快速入门 (周幸来，周幸秋，孙冰主编) (Z-Library).pdf (36878148 bytes)
[api] 2025-10-31 00:31:36,860 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Starting direct processing for 舌诊快速入门 (周幸来，周幸秋，孙冰主编) (Z-Library).pdf
[api] 2025-10-31 00:31:36,870 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Acquired semaphore for 舌诊快速入门 (周幸来，周幸秋，孙冰主编) (Z-Library).pdf (active: 1/20)
[api] 2025-10-31 00:31:37,007 - infotransform.utils.token_counter - INFO - Token count for '舌诊快速入门 (周幸来，周幸秋，孙冰主编) (Z-Library).pdf' (direct_processing): 4,864 tokens
[api] 2025-10-31 00:31:37,623 - infotransform.processors.vision - WARNING - No text content extracted from 舌诊十讲 (张坚著) (Z-Library).pdf
[api] 2025-10-31 00:31:43,473 - infotransform.processors.vision - INFO - Successfully processed 中医诊断学 (新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (李灿东) (Z-Library).pdf (24889573 bytes)
[api] 2025-10-31 00:31:43,587 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Starting direct processing for 中医诊断学 (新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (李灿东) (Z-Library).pdf
[api] 2025-10-31 00:31:43,618 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Acquired semaphore for 中医诊断学 (新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (李灿东) (Z-Library).pdf (active: 2/20)
[api] 2025-10-31 00:31:43,826 - infotransform.utils.token_counter - INFO - Token count for '中医诊断学 (新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (李灿东) (Z-Library).pdf' (direct_processing): 327,958 tokens
[api] 2025-10-31 00:31:48,015 - infotransform.processors.vision - INFO - Successfully processed 中医内科学（新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (张伯礼，吴勉华) (Z-Library).pdf (28377981 bytes)
[api] 2025-10-31 00:31:48,065 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Starting direct processing for 中医内科学（新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (张伯礼，吴勉华) (Z-Library).pdf
[api] 2025-10-31 00:31:48,065 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Acquired semaphore for 中医内科学（新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (张伯礼，吴勉华) (Z-Library).pdf (active: 3/20)
[api] 2025-10-31 00:31:48,273 - infotransform.utils.token_counter - INFO - Token count for '中医内科学（新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (张伯礼，吴勉华) (Z-Library).pdf' (direct_processing): 640,077 tokens
[api] 2025-10-31 00:31:52,041 - infotransform.processors.vision - INFO - Successfully processed 象脉学 (许跃远著) (Z-Library).pdf (131589380 bytes)
[api] 2025-10-31 00:31:52,116 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Starting direct processing for 象脉学 (许跃远著) (Z-Library).pdf
[api] 2025-10-31 00:31:52,116 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Acquired semaphore for 象脉学 (许跃远著) (Z-Library).pdf (active: 4/20)
[api] 2025-10-31 00:31:52,120 - infotransform.utils.token_counter - INFO - Token count for '象脉学 (许跃远著) (Z-Library).pdf' (direct_processing): 960 tokens
[api] 2025-10-31 00:31:56,269 - infotransform.processors.structured_analyzer_agent - ERROR - Error in structured analysis: status_code: 400, model_name: openai.gpt-5-mini-2025-08-07, body: {'message': 'litellm.BadRequestError: OpenAIException - Input tokens exceed the configured limit of 272000 tokens. Your messages resulted in 440393 tokens. Please reduce the length of the messages.. Received Model Group=openai.gpt-5-mini-2025-08-07\nAvailable Model Group Fallbacks=None', 'type': 'invalid_request_error', 'param': 'messages', 'code': '400'}
[api] 2025-10-31 00:31:56,294 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Completed processing for 中医内科学（新世纪第四版；全国中医药行业高等教育十三五规划教材；全国高等中医药院校规划教材第十版) (张伯礼，吴勉华) (Z-Library).pdf in 8.23s (success=False)
[api] 2025-10-31 00:32:00,566 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Completed processing for 舌诊快速入门 (周幸来，周幸秋，孙冰主编) (Z-Library).pdf in 23.71s (success=True)
[api] 2025-10-31 00:32:13,633 - infotransform.processors.vision - WARNING - PDF 中医舌诊完全图解 (吴中朝, 王彤) (Z-Library).pdf extracted very little text (22 chars). This may be an image-based PDF. Azure Document Intelligence: not configured
[api] 2025-10-31 00:32:13,633 - infotransform.processors.vision - INFO - Successfully processed 中医舌诊完全图解 (吴中朝, 王彤) (Z-Library).pdf (88867815 bytes)
[api] 2025-10-31 00:32:13,637 - infotransform.api.document_transform_api - INFO - [81231cf0-8a4a-4057-9c1e-d8a4e0b74e6e] Markdown conversion complete: 6 files in 43.71s
[api] 2025-10-31 00:32:13,638 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Starting direct processing for 中医舌诊完全图解 (吴中朝, 王彤) (Z-Library).pdf
[api] 2025-10-31 00:32:13,638 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Acquired semaphore for 中医舌诊完全图解 (吴中朝, 王彤) (Z-Library).pdf (active: 3/20)
[api] 2025-10-31 00:32:13,641 - infotransform.utils.token_counter - INFO - Token count for '中医舌诊完全图解 (吴中朝, 王彤) (Z-Library).pdf' (direct_processing): 19 tokens
[api] ERROR:    Exception in ASGI application
[api]   + Exception Group Traceback (most recent call last):
[api]   |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_utils.py", line 79, in collapse_excgroups
[api]   |     yield
[api]   |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/responses.py", line 271, in __call__
[api]   |     async with anyio.create_task_group() as task_group:
[api]   |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/anyio/_backends/_asyncio.py", line 781, in __aexit__
[api]   |     raise BaseExceptionGroup(
[api]   | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
[api]   +-+---------------- 1 ----------------
[api]     | Traceback (most recent call last):
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 409, in run_asgi
[api]     |     result = await app(  # type: ignore[func-returns-value]
[api]     |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
[api]     |     return await self.app(scope, receive, send)
[api]     |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/applications.py", line 1133, in __call__
[api]     |     await super().__call__(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/applications.py", line 113, in __call__
[api]     |     await self.middleware_stack(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
[api]     |     raise exc
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
[api]     |     await self.app(scope, receive, _send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/cors.py", line 93, in __call__
[api]     |     await self.simple_response(scope, receive, send, request_headers=headers)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/cors.py", line 144, in simple_response
[api]     |     await self.app(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
[api]     |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
[api]     |     raise exc
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
[api]     |     await app(scope, receive, sender)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
[api]     |     await self.app(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/routing.py", line 716, in __call__
[api]     |     await self.middleware_stack(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/routing.py", line 736, in app
[api]     |     await route.handle(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/routing.py", line 290, in handle
[api]     |     await self.app(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/routing.py", line 123, in app
[api]     |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
[api]     |     raise exc
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
[api]     |     await app(scope, receive, sender)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/routing.py", line 110, in app
[api]     |     await response(scope, receive, send)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/responses.py", line 270, in __call__
[api]     |     with collapse_excgroups():
[api]     |   File "/Users/owen/.local/share/uv/python/cpython-3.11.6-macos-aarch64-none/lib/python3.11/contextlib.py", line 155, in __exit__
[api]     |     self.gen.throw(typ, value, traceback)
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_utils.py", line 85, in collapse_excgroups
[api]     |     raise exc
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/responses.py", line 274, in wrap
[api]     |     await func()
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/responses.py", line 254, in stream_response
[api]     |     async for chunk in self.body_iterator:
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/backend/infotransform/utils/file_lifecycle.py", line 278, in generate_with_cleanup
[api]     |     async for chunk in self.content_generator:
[api]     |   File "/Users/owen/Desktop/dev_projects/InfoTransform/backend/infotransform/api/document_transform_api.py", line 685, in process_files_optimized
[api]     |     ai_result_dict["cached"] = ai_result_dict.get("usage", {}).get("cached", False)
[api]     |                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[api]     | AttributeError: 'NoneType' object has no attribute 'get'
[api]     +------------------------------------
[api] 
[api] During handling of the above exception, another exception occurred:
[api] 
[api] Traceback (most recent call last):
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/uvicorn/protocols/http/httptools_impl.py", line 409, in run_asgi
[api]     result = await app(  # type: ignore[func-returns-value]
[api]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
[api]     return await self.app(scope, receive, send)
[api]            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/applications.py", line 1133, in __call__
[api]     await super().__call__(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/applications.py", line 113, in __call__
[api]     await self.middleware_stack(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 186, in __call__
[api]     raise exc
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/errors.py", line 164, in __call__
[api]     await self.app(scope, receive, _send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/cors.py", line 93, in __call__
[api]     await self.simple_response(scope, receive, send, request_headers=headers)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/cors.py", line 144, in simple_response
[api]     await self.app(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/middleware/exceptions.py", line 63, in __call__
[api]     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
[api]     raise exc
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
[api]     await app(scope, receive, sender)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/middleware/asyncexitstack.py", line 18, in __call__
[api]     await self.app(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/routing.py", line 716, in __call__
[api]     await self.middleware_stack(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/routing.py", line 736, in app
[api]     await route.handle(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/routing.py", line 290, in handle
[api]     await self.app(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/routing.py", line 123, in app
[api]     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
[api]     raise exc
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
[api]     await app(scope, receive, sender)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/fastapi/routing.py", line 110, in app
[api]     await response(scope, receive, send)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/responses.py", line 270, in __call__
[api]     with collapse_excgroups():
[api]   File "/Users/owen/.local/share/uv/python/cpython-3.11.6-macos-aarch64-none/lib/python3.11/contextlib.py", line 155, in __exit__
[api]     self.gen.throw(typ, value, traceback)
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/_utils.py", line 85, in collapse_excgroups
[api]     raise exc
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/responses.py", line 274, in wrap
[api]     await func()
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/starlette/responses.py", line 254, in stream_response
[api]     async for chunk in self.body_iterator:
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/backend/infotransform/utils/file_lifecycle.py", line 278, in generate_with_cleanup
[api]     async for chunk in self.content_generator:
[api]   File "/Users/owen/Desktop/dev_projects/InfoTransform/backend/infotransform/api/document_transform_api.py", line 685, in process_files_optimized
[api]     ai_result_dict["cached"] = ai_result_dict.get("usage", {}).get("cached", False)
[api]                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[api] AttributeError: 'NoneType' object has no attribute 'get'
[api] 2025-10-31 00:32:16,781 - infotransform.processors.ai_batch_processor - INFO - [DIRECT] Completed processing for 象脉学 (许跃远著) (Z-Library).pdf in 24.66s (success=True)