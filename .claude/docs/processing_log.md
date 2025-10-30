owen@macmini InfoTransform % npm run dev  

> infotransform@1.0.0 dev
> dotenv -- concurrently -k --kill-others-on-fail --names "next,api" "npm run dev:next" "npm run dev:api"

[api] 
[api] > infotransform@1.0.0 dev:api
[api] > dotenv -- npm run python:app
[api] 
[next] 
[next] > infotransform@1.0.0 dev:next
[next] > dotenv -- npm --prefix frontend run dev
[next] 
[api] 
[api] > infotransform@1.0.0 python:app
[api] > uv run python app.py
[api] 
[next] 
[next] > frontend@0.1.0 dev
[next] > node -e "const port = process.env.PORT || 3000; require('child_process').spawn('npx', ['next', 'dev', '-p', port], {stdio: 'inherit', shell: true})"
[next] 
[api] 2025-10-30 15:40:58,335 - infotransform.utils.logging_config - INFO - Logging configured for environment: development
[api] [START] Starting server on http://localhost:8501
[api] [DOCS] API documentation available at http://localhost:8501/docs
[api] INFO:     Will watch for changes in these directories: ['/Users/owen/Desktop/dev_projects/InfoTransform']
[api] INFO:     Uvicorn running on http://0.0.0.0:8501 (Press CTRL+C to quit)
[api] INFO:     Started reloader process [52594] using WatchFiles
[api] 2025-10-30 15:40:58,431 - infotransform.utils.logging_config - INFO - Logging configured for environment: development
[next]   ▲ Next.js 14.2.33
[next]   - Local:        http://localhost:8502
[next] 
[next]  ✓ Starting...
[next] [Next.js] API rewrites configured to: http://localhost:8501
[api] /Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/pydub/utils.py:170: RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
[api]   warn("Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work", RuntimeWarning)
[api] INFO:     Started server process [52597]
[api] INFO:     Waiting for application startup.
[api] INFO:     Application startup complete.
[next]  ✓ Ready in 1168ms
[next]  ○ Compiling / ...
[next]  ✓ Compiled / in 1047ms (855 modules)
[next]  GET / 200 in 1288ms
[next]  ✓ Compiled in 192ms (424 modules)
[next]  GET / 200 in 25ms
[api] [OK] Processors initialized successfully
[api] [INFO] Azure Document Intelligence not configured
[api]        Image-based/scanned PDFs may fail to process
[api]        See README.md for Azure setup instructions
[api] INFO:     127.0.0.1:64915 - "GET /api/models HTTP/1.1" 200 OK
[api] INFO:     127.0.0.1:64915 - "GET /api/models HTTP/1.1" 200 OK
[next]  ✓ Compiled /favicon.ico in 117ms (463 modules)
[next]  GET /favicon.ico 200 in 152ms
[api] 2025-10-30 15:41:19,414 - infotransform.processors.async_converter - INFO - Initialized ThreadPoolExecutor with 20 workers
[api] 2025-10-30 15:41:19,415 - infotransform.utils.file_lifecycle - INFO - FileLifecycleManager started
[api] 2025-10-30 15:41:19,415 - infotransform.utils.result_cache - INFO - Result cache initialized: TTL=2.0h, max_entries=10000, db=/Users/owen/Desktop/dev_projects/InfoTransform/backend/infotransform/data/processing_logs.db
[api] 2025-10-30 15:41:19,418 - infotransform.utils.result_cache - INFO - Result cache started
[api] 2025-10-30 15:41:19,418 - infotransform.processors.ai_batch_processor - INFO - BatchProcessor started with 5 workers
[api] 2025-10-30 15:41:19,418 - infotransform.api.document_transform_api - INFO - StreamingProcessor started
[api] 2025-10-30 15:41:19,419 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 202518256.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/202518256.docx
[api] 2025-10-30 15:41:19,419 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 202518325.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/202518325.docx
[api] 2025-10-30 15:41:19,420 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: Assessment 1 MSIN0056 _ Innovation Management.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Assessment 1 MSIN0056 _ Innovation Management.pdf
[api] 2025-10-30 15:41:19,420 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: B1021-1 .docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/B1021-1 .docx
[api] 2025-10-30 15:41:19,421 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: cargo-ops-demo.zip to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/cargo-ops-demo.zip
[api] 2025-10-30 15:41:19,421 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: China_updated.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/China_updated.pdf
[api] 2025-10-30 15:41:19,421 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf
[api] 2025-10-30 15:41:19,422 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: IMG_0714.PNG to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/IMG_0714.PNG
[api] 2025-10-30 15:41:19,422 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: IMG_0715.JPG to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/IMG_0715.JPG
[api] 2025-10-30 15:41:19,423 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: IMG_0716.JPG to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/IMG_0716.JPG
[api] 2025-10-30 15:41:19,423 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: midQ14.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/midQ14.docx
[api] 2025-10-30 15:41:19,428 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: oct+27-29.pptx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/oct+27-29.pptx
[api] 2025-10-30 15:41:19,428 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: q7.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/q7.docx
[api] 2025-10-30 15:41:19,429 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: q14.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/q14.docx
[api] 2025-10-30 15:41:19,432 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: Slides_12_13_13_15.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Slides_12_13_13_15.pdf
[api] 2025-10-30 15:41:19,434 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: Untitled presentation (1).pptx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Untitled presentation (1).pptx
[api] 2025-10-30 15:41:19,437 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: Untitled presentation (2).pptx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Untitled presentation (2).pptx
[api] 2025-10-30 15:41:19,438 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: USA Travel History.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/USA Travel History.pdf
[api] 2025-10-30 15:41:19,438 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: WechatIMG301.jpg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/WechatIMG301.jpg
[api] 2025-10-30 15:41:19,438 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: WechatIMG303.jpeg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/WechatIMG303.jpeg
[api] 2025-10-30 15:41:19,440 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: WechatIMG303.jpg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/WechatIMG303.jpg
[api] 2025-10-30 15:41:19,440 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 1.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/1.png
[api] 2025-10-30 15:41:19,441 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 2.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/2.png
[api] 2025-10-30 15:41:19,441 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 3.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/3.png
[api] 2025-10-30 15:41:19,442 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 4.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/4.png
[api] 2025-10-30 15:41:19,442 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 5.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/5.png
[api] 2025-10-30 15:41:19,443 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 6.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/6.png
[api] 2025-10-30 15:41:19,443 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 7.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/7.png
[api] 2025-10-30 15:41:19,443 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 8.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/8.png
[api] 2025-10-30 15:41:19,444 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 9.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/9.png
[api] 2025-10-30 15:41:19,444 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 10.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/10.png
[api] 2025-10-30 15:41:19,445 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 11.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/11.png
[api] 2025-10-30 15:41:19,445 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 000016.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000016.png
[api] 2025-10-30 15:41:19,446 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 000018.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000018.png
[api] 2025-10-30 15:41:19,446 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 000020.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000020.png
[api] 2025-10-30 15:41:19,447 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 000021.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000021.png
[api] 2025-10-30 15:41:19,454 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 809c31583be9e41d1eadc9d735a7dde8.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/809c31583be9e41d1eadc9d735a7dde8.docx
[api] 2025-10-30 15:41:19,456 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 17776 a3.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17776 a3.docx
[api] 2025-10-30 15:41:19,457 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 17776 a3 edited.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17776 a3 edited.docx
[api] 2025-10-30 15:41:19,460 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 17835.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17835.docx
[api] 2025-10-30 15:41:19,461 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 17878.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17878.docx
[api] 2025-10-30 15:41:19,461 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 17878-03(6).docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17878-03(6).docx
[api] 2025-10-30 15:41:19,461 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 18155.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/18155.docx
[api] 2025-10-30 15:41:19,462 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 18155(1).docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/18155(1).docx
[api] 2025-10-30 15:41:19,463 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 18226.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/18226.docx
[api] 2025-10-30 15:41:19,467 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Saved file: 1761054989736.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/1761054989736.pdf
[api] INFO:     127.0.0.1:49374 - "POST /api/transform HTTP/1.1" 200 OK
[api] 2025-10-30 15:41:19,500 - infotransform.api.document_transform_api - INFO - Extracted 125 files from cargo-ops-demo.zip
[api] 2025-10-30 15:41:19,500 - infotransform.api.document_transform_api - INFO - Expanded ZIP cargo-ops-demo.zip: 125 files
[api] 2025-10-30 15:41:19,500 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Processed 1 ZIP files, total files: 170
[api] 2025-10-30 15:41:19,500 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Starting processing run: 170 files, model=document_metadata, ai_model=openai.gpt-5-mini-2025-08-07
[api] 2025-10-30 15:41:19,502 - infotransform.db.processing_logs_db - INFO - Database schema initialized successfully
[api] 2025-10-30 15:41:19,502 - infotransform.db.processing_logs_db - INFO - ProcessingLogsDB initialized at backend/infotransform/data/processing_logs.db (WAL mode: True)
[api] 2025-10-30 15:41:19,636 - infotransform.processors.vision - INFO - Successfully processed q14.docx (14947 bytes)
[api] 2025-10-30 15:41:19,648 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 1 items with model: document_metadata
[api] 2025-10-30 15:41:19,706 - infotransform.processors.vision - INFO - Successfully processed China_updated.pdf (62514 bytes)
[api] 2025-10-30 15:41:19,799 - infotransform.processors.vision - INFO - Successfully processed 202518256.docx (18445 bytes)
[api] 2025-10-30 15:41:19,807 - infotransform.utils.result_cache - INFO - Cache HIT: 03a0d355ecfb67fa... (retrieved in 157.4ms, hit_count=1)
[api] 2025-10-30 15:41:19,817 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for q14.docx (retrieved in 167.5ms)
[api] 2025-10-30 15:41:19,822 - infotransform.processors.vision - INFO - Successfully processed B1021-1 .docx (17279 bytes)
[api] 2025-10-30 15:41:19,827 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 1 items in 0.18s (0.18s per item)
[api] 2025-10-30 15:41:19,972 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 3 items with model: document_metadata
[api] 2025-10-30 15:41:19,997 - infotransform.processors.vision - INFO - Successfully processed USA Travel History.pdf (383224 bytes)
[api] 2025-10-30 15:41:20,061 - infotransform.processors.vision - INFO - Successfully processed midQ14.docx (18507 bytes)
[api] 2025-10-30 15:41:20,065 - infotransform.utils.result_cache - INFO - Cache HIT: a3dcc4c40bf4a22c... (retrieved in 69.5ms, hit_count=1)
[api] 2025-10-30 15:41:20,079 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for B1021-1 .docx (retrieved in 84.3ms)
[api] 2025-10-30 15:41:20,112 - infotransform.utils.result_cache - INFO - Cache HIT: 3547ae4d59b6e708... (retrieved in 124.4ms, hit_count=1)
[api] 2025-10-30 15:41:20,117 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 202518256.docx (retrieved in 129.5ms)
[api] 2025-10-30 15:41:20,170 - infotransform.utils.result_cache - INFO - Cache HIT: 6b06ec6e2f500fef... (retrieved in 191.1ms, hit_count=1)
[api] 2025-10-30 15:41:20,242 - infotransform.processors.vision - INFO - Successfully processed q7.docx (17071 bytes)
[api] 2025-10-30 15:41:20,243 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for China_updated.pdf (retrieved in 264.0ms)
[api] 2025-10-30 15:41:20,266 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 3 items in 0.29s (0.10s per item)
[api] 2025-10-30 15:41:20,267 - infotransform.processors.vision - INFO - Successfully processed ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf (184400 bytes)
[api] 2025-10-30 15:41:20,381 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 4 items with model: document_metadata
[api] 2025-10-30 15:41:20,549 - infotransform.utils.result_cache - INFO - Cache HIT: 967f4293d3852ba9... (retrieved in 155.6ms, hit_count=1)
[api] 2025-10-30 15:41:20,559 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for USA Travel History.pdf (retrieved in 165.6ms)
[api] 2025-10-30 15:41:20,577 - infotransform.processors.vision - INFO - Successfully processed 202518325.docx (25430 bytes)
[api] 2025-10-30 15:41:20,579 - infotransform.utils.result_cache - INFO - Cache HIT: fbd32546de023b98... (retrieved in 178.7ms, hit_count=1)
[api] 2025-10-30 15:41:20,588 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for q7.docx (retrieved in 188.4ms)
[api] 2025-10-30 15:41:20,589 - infotransform.utils.result_cache - INFO - Cache HIT: 8e96da9c132e8044... (retrieved in 194.7ms, hit_count=1)
[api] 2025-10-30 15:41:20,594 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for midQ14.docx (retrieved in 199.8ms)
[api] 2025-10-30 15:41:20,598 - infotransform.utils.result_cache - INFO - Cache HIT: c12bc9fc780ccf83... (retrieved in 197.5ms, hit_count=1)
[api] 2025-10-30 15:41:20,630 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf (retrieved in 229.7ms)
[api] 2025-10-30 15:41:20,647 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 4 items in 0.27s (0.07s per item)
[api] 2025-10-30 15:41:20,651 - infotransform.processors.ai_batch_processor - INFO - Adjusting batch size from 15 to 18 (avg response time: 0.11s)
[api] 2025-10-30 15:41:20,775 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 1 items with model: document_metadata
[api] 2025-10-30 15:41:20,805 - infotransform.processors.vision - INFO - Successfully processed Assessment 1 MSIN0056 _ Innovation Management.pdf (319994 bytes)
[api] 2025-10-30 15:41:20,828 - infotransform.utils.result_cache - INFO - Cache HIT: 0b0489d6f17ba60e... (retrieved in 22.7ms, hit_count=1)
[api] 2025-10-30 15:41:20,828 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 202518325.docx (retrieved in 22.9ms)
[api] 2025-10-30 15:41:20,829 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 1 items in 0.05s (0.05s per item)
[api] 2025-10-30 15:41:20,829 - infotransform.processors.ai_batch_processor - INFO - Adjusting batch size from 18 to 20 (avg response time: 0.10s)
[api] 2025-10-30 15:41:20,933 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 1 items with model: document_metadata
[api] 2025-10-30 15:41:20,981 - infotransform.utils.result_cache - INFO - Cache HIT: 3461935a24c20869... (retrieved in 43.6ms, hit_count=1)
[api] 2025-10-30 15:41:21,017 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for Assessment 1 MSIN0056 _ Innovation Management.pdf (retrieved in 79.5ms)
[api] 2025-10-30 15:41:21,019 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 1 items in 0.09s (0.09s per item)
[api] 2025-10-30 15:41:23,023 - infotransform.processors.vision - INFO - Successfully processed Slides_12_13_13_15.pdf (3018743 bytes)
[api] 2025-10-30 15:41:23,029 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 1 items with model: document_metadata
[api] 2025-10-30 15:41:23,232 - infotransform.utils.token_counter - INFO - Token count for 'Slides_12_13_13_15.pdf' (batch_analysis): 9,300 tokens
[api] 2025-10-30 15:41:29,847 - infotransform.processors.vision - INFO - Successfully processed placeholder-user.jpg (1635 bytes)
[api] 2025-10-30 15:41:33,241 - infotransform.processors.vision - INFO - Successfully processed placeholder.jpg (1064 bytes)
[api] 2025-10-30 15:41:33,338 - infotransform.processors.vision - INFO - Successfully processed Untitled presentation (2).pptx (1286801 bytes)
[api] 2025-10-30 15:41:34,840 - infotransform.processors.vision - INFO - Successfully processed placeholder-logo.png (568 bytes)
[api] 2025-10-30 15:41:35,962 - infotransform.processors.vision - INFO - Successfully processed Untitled presentation (1).pptx (1286902 bytes)
[api] 2025-10-30 15:41:38,871 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 1 items in 15.84s (15.84s per item)
[api] 2025-10-30 15:41:38,973 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 5 items with model: document_metadata
[api] 2025-10-30 15:41:38,981 - infotransform.utils.token_counter - INFO - Token count for 'placeholder.jpg' (batch_analysis): 178 tokens
[api] 2025-10-30 15:41:38,989 - infotransform.utils.token_counter - INFO - Token count for 'Untitled presentation (1).pptx' (batch_analysis): 1,175 tokens
[api] 2025-10-30 15:41:38,992 - infotransform.utils.token_counter - INFO - Token count for 'Untitled presentation (2).pptx' (batch_analysis): 1,101 tokens
[api] 2025-10-30 15:41:38,993 - infotransform.utils.token_counter - INFO - Token count for 'placeholder-user.jpg' (batch_analysis): 136 tokens
[api] 2025-10-30 15:41:38,994 - infotransform.utils.token_counter - INFO - Token count for 'placeholder-logo.png' (batch_analysis): 201 tokens
[api] 2025-10-30 15:41:39,856 - infotransform.processors.vision - INFO - Successfully processed sscpl-logo.png (85744 bytes)
[api] 2025-10-30 15:41:49,529 - infotransform.processors.vision - INFO - Successfully processed IMG_0715.JPG (56203 bytes)
[api] 2025-10-30 15:41:50,334 - infotransform.processors.vision - INFO - Successfully processed IMG_0716.JPG (55123 bytes)
[api] 2025-10-30 15:41:53,128 - infotransform.processors.vision - INFO - Successfully processed 2.png (122433 bytes)
[api] 2025-10-30 15:41:53,301 - infotransform.processors.vision - INFO - Successfully processed 809c31583be9e41d1eadc9d735a7dde8.docx (27510 bytes)
[api] 2025-10-30 15:41:53,462 - infotransform.processors.vision - INFO - Successfully processed 17776 a3.docx (832860 bytes)
[api] 2025-10-30 15:41:53,584 - infotransform.processors.vision - INFO - Successfully processed 17776 a3 edited.docx (763862 bytes)
[api] 2025-10-30 15:41:53,620 - infotransform.processors.vision - INFO - Successfully processed 17835.docx (438335 bytes)
[api] 2025-10-30 15:41:53,638 - infotransform.processors.vision - INFO - Successfully processed 17878.docx (17355 bytes)
[api] 2025-10-30 15:41:53,666 - infotransform.processors.vision - INFO - Successfully processed 17878-03(6).docx (23658 bytes)
[api] 2025-10-30 15:41:53,686 - infotransform.processors.vision - INFO - Successfully processed 18155.docx (18971 bytes)
[api] 2025-10-30 15:41:53,706 - infotransform.processors.vision - INFO - Successfully processed 18155(1).docx (19459 bytes)
[api] 2025-10-30 15:41:53,828 - infotransform.processors.vision - INFO - Successfully processed 18226.docx (335168 bytes)
[api] 2025-10-30 15:41:53,836 - infotransform.processors.vision - WARNING - No text content extracted from 1761054989736.pdf
[api] 2025-10-30 15:41:57,668 - infotransform.processors.vision - INFO - Successfully processed WechatIMG303.jpeg (424927 bytes)
[api] 2025-10-30 15:41:58,247 - infotransform.processors.vision - INFO - Successfully processed 000016.png (30170 bytes)
[api] 2025-10-30 15:41:58,648 - infotransform.processors.vision - INFO - Successfully processed 7.png (132258 bytes)
[api] 2025-10-30 15:41:59,626 - infotransform.processors.vision - INFO - Successfully processed 10.png (73786 bytes)
[api] 2025-10-30 15:42:02,882 - infotransform.processors.vision - INFO - Successfully processed 4.png (140692 bytes)
[api] 2025-10-30 15:42:03,006 - infotransform.processors.vision - INFO - Successfully processed WechatIMG301.jpg (413280 bytes)
[api] 2025-10-30 15:42:03,775 - infotransform.processors.vision - INFO - Successfully processed IMG_0714.PNG (220097 bytes)
[api] 2025-10-30 15:42:04,300 - infotransform.processors.vision - INFO - Successfully processed 1.png (165910 bytes)
[api] 2025-10-30 15:42:04,992 - infotransform.processors.vision - INFO - Successfully processed 000018.png (60482 bytes)
[api] 2025-10-30 15:42:05,042 - infotransform.processors.vision - INFO - Successfully processed 5.png (167961 bytes)
[api] 2025-10-30 15:42:07,429 - infotransform.processors.vision - INFO - Successfully processed 6.png (171636 bytes)
[api] 2025-10-30 15:42:07,683 - infotransform.processors.vision - INFO - Successfully processed 3.png (183760 bytes)
[api] 2025-10-30 15:42:08,393 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 5 items in 29.42s (5.88s per item)
[api] 2025-10-30 15:42:08,394 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 20 items with model: document_metadata
[api] 2025-10-30 15:42:08,405 - infotransform.utils.token_counter - INFO - Token count for '10.png' (batch_analysis): 436 tokens
[api] 2025-10-30 15:42:08,408 - infotransform.utils.token_counter - INFO - Token count for 'WechatIMG301.jpg' (batch_analysis): 324 tokens
[api] 2025-10-30 15:42:08,409 - infotransform.utils.token_counter - INFO - Token count for 'sscpl-logo.png' (batch_analysis): 121 tokens
[api] 2025-10-30 15:42:08,409 - infotransform.utils.token_counter - INFO - Token count for 'IMG_0715.JPG' (batch_analysis): 512 tokens
[api] 2025-10-30 15:42:08,410 - infotransform.utils.token_counter - INFO - Token count for '000016.png' (batch_analysis): 137 tokens
[api] 2025-10-30 15:42:08,411 - infotransform.utils.token_counter - INFO - Token count for '4.png' (batch_analysis): 629 tokens
[api] 2025-10-30 15:42:08,412 - infotransform.utils.token_counter - INFO - Token count for 'WechatIMG303.jpeg' (batch_analysis): 318 tokens
[api] 2025-10-30 15:42:08,412 - infotransform.utils.token_counter - INFO - Token count for '2.png' (batch_analysis): 497 tokens
[api] 2025-10-30 15:42:08,413 - infotransform.utils.token_counter - INFO - Token count for 'IMG_0716.JPG' (batch_analysis): 847 tokens
[api] 2025-10-30 15:42:08,413 - infotransform.utils.token_counter - INFO - Token count for 'IMG_0714.PNG' (batch_analysis): 979 tokens
[api] 2025-10-30 15:42:08,414 - infotransform.utils.token_counter - INFO - Token count for '7.png' (batch_analysis): 853 tokens
[api] 2025-10-30 15:42:08,417 - infotransform.utils.result_cache - INFO - Cache HIT: 15309992b80e98bd... (retrieved in 21.8ms, hit_count=1)
[api] 2025-10-30 15:42:08,417 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 17835.docx (retrieved in 21.9ms)
[api] 2025-10-30 15:42:08,424 - infotransform.utils.result_cache - INFO - Cache HIT: f7974b974b9f9da5... (retrieved in 28.7ms, hit_count=1)
[api] 2025-10-30 15:42:08,424 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 17878.docx (retrieved in 28.9ms)
[api] 2025-10-30 15:42:08,425 - infotransform.utils.result_cache - INFO - Cache HIT: 589ca0019287db54... (retrieved in 29.3ms, hit_count=1)
[api] 2025-10-30 15:42:08,425 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 18155.docx (retrieved in 29.3ms)
[api] 2025-10-30 15:42:08,425 - infotransform.utils.result_cache - INFO - Cache HIT: 5f81fa9f979990ec... (retrieved in 30.2ms, hit_count=1)
[api] 2025-10-30 15:42:08,425 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 17776 a3 edited.docx (retrieved in 30.3ms)
[api] 2025-10-30 15:42:08,432 - infotransform.utils.result_cache - INFO - Cache HIT: 382007f1ba252e1f... (retrieved in 37.7ms, hit_count=1)
[api] 2025-10-30 15:42:08,432 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 17776 a3.docx (retrieved in 37.8ms)
[api] 2025-10-30 15:42:08,433 - infotransform.utils.result_cache - INFO - Cache HIT: 35cf7c365547d1f8... (retrieved in 37.3ms, hit_count=1)
[api] 2025-10-30 15:42:08,433 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 18155(1).docx (retrieved in 37.4ms)
[api] 2025-10-30 15:42:08,433 - infotransform.utils.result_cache - INFO - Cache HIT: f06ff353f0d4329b... (retrieved in 37.8ms, hit_count=1)
[api] 2025-10-30 15:42:08,433 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 17878-03(6).docx (retrieved in 37.9ms)
[api] 2025-10-30 15:42:08,449 - infotransform.utils.result_cache - INFO - Cache HIT: 1921093e34f70af1... (retrieved in 54.6ms, hit_count=1)
[api] 2025-10-30 15:42:08,449 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 809c31583be9e41d1eadc9d735a7dde8.docx (retrieved in 54.7ms)
[api] 2025-10-30 15:42:08,450 - infotransform.utils.result_cache - INFO - Cache HIT: 4718bcf6c9c7ab8c... (retrieved in 54.2ms, hit_count=1)
[api] 2025-10-30 15:42:08,450 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for 18226.docx (retrieved in 54.3ms)
[api] 2025-10-30 15:42:09,003 - infotransform.processors.vision - INFO - Successfully processed 8.png (150352 bytes)
[api] 2025-10-30 15:42:09,877 - infotransform.processors.vision - INFO - Successfully processed 11.png (138930 bytes)
[api] 2025-10-30 15:42:10,390 - infotransform.processors.vision - INFO - Successfully processed 9.png (151641 bytes)
[api] 2025-10-30 15:42:29,902 - infotransform.processors.vision - INFO - Successfully processed 000020.png (37512 bytes)
[api] 2025-10-30 15:42:38,771 - infotransform.processors.vision - INFO - Successfully processed WechatIMG303.jpg (1215859 bytes)
[api] 2025-10-30 15:42:39,892 - infotransform.processors.vision - INFO - Successfully processed 000021.png (46209 bytes)
[api] 2025-10-30 15:43:04,393 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 20 items in 56.00s (2.80s per item)
[api] 2025-10-30 15:43:04,496 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 11 items with model: document_metadata
[api] 2025-10-30 15:43:04,528 - infotransform.utils.token_counter - INFO - Token count for '9.png' (batch_analysis): 868 tokens
[api] 2025-10-30 15:43:04,536 - infotransform.utils.token_counter - INFO - Token count for '5.png' (batch_analysis): 868 tokens
[api] 2025-10-30 15:43:04,538 - infotransform.utils.token_counter - INFO - Token count for '3.png' (batch_analysis): 1,075 tokens
[api] 2025-10-30 15:43:04,548 - infotransform.utils.token_counter - INFO - Token count for '1.png' (batch_analysis): 657 tokens
[api] 2025-10-30 15:43:04,549 - infotransform.utils.token_counter - INFO - Token count for '000021.png' (batch_analysis): 450 tokens
[api] 2025-10-30 15:43:04,553 - infotransform.utils.token_counter - INFO - Token count for '8.png' (batch_analysis): 693 tokens
[api] 2025-10-30 15:43:04,557 - infotransform.utils.token_counter - INFO - Token count for '000020.png' (batch_analysis): 478 tokens
[api] 2025-10-30 15:43:04,558 - infotransform.utils.token_counter - INFO - Token count for '6.png' (batch_analysis): 719 tokens
[api] 2025-10-30 15:43:04,558 - infotransform.utils.token_counter - INFO - Token count for '000018.png' (batch_analysis): 293 tokens
[api] 2025-10-30 15:43:04,559 - infotransform.utils.token_counter - INFO - Token count for '11.png' (batch_analysis): 750 tokens
[api] 2025-10-30 15:43:04,560 - infotransform.utils.token_counter - INFO - Token count for 'WechatIMG303.jpg' (batch_analysis): 304 tokens
[api] 2025-10-30 15:43:19,543 - infotransform.api.document_transform_api - INFO - [9d09963b-60ca-4fca-851c-b54da1f13be2] Markdown conversion complete: 170 files in 120.04s
