[api] 2025-10-30 15:08:38,514 - infotransform.utils.logging_config - INFO - Logging configured for environment: development
[next]   ▲ Next.js 14.2.33
[next]   - Local:        http://localhost:8502
[next] 
[next]  ✓ Starting...
[next] [Next.js] API rewrites configured to: http://localhost:8501
[api] /Users/owen/Desktop/dev_projects/InfoTransform/.venv/lib/python3.11/site-packages/pydub/utils.py:170: RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
[api]   warn("Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work", RuntimeWarning)
[api] INFO:     Started server process [90256]
[api] INFO:     Waiting for application startup.
[next]  ✓ Ready in 1282ms
[api] INFO:     Application startup complete.
[next]  ○ Compiling / ...
[next]  ✓ Compiled / in 1334ms (855 modules)
[next]  GET / 200 in 1787ms
[next]  ✓ Compiled in 375ms (424 modules)
[api] [OK] Processors initialized successfully
[api] [INFO] Azure Document Intelligence not configured
[api]        Image-based/scanned PDFs may fail to process
[api]        See README.md for Azure setup instructions
[api] INFO:     127.0.0.1:53908 - "GET /api/models HTTP/1.1" 200 OK
[api] INFO:     127.0.0.1:53913 - "GET /api/models HTTP/1.1" 200 OK
[api] 2025-10-30 15:08:58,612 - infotransform.processors.async_converter - INFO - Initialized ThreadPoolExecutor with 20 workers
[api] 2025-10-30 15:08:58,613 - infotransform.utils.file_lifecycle - INFO - FileLifecycleManager started
[api] 2025-10-30 15:08:58,613 - infotransform.utils.result_cache - INFO - Result cache initialized: TTL=2.0h, max_entries=10000, db=/Users/owen/Desktop/dev_projects/InfoTransform/backend/infotransform/data/processing_logs.db
[api] 2025-10-30 15:08:58,615 - infotransform.utils.result_cache - INFO - Result cache started
[api] 2025-10-30 15:08:58,615 - infotransform.processors.ai_batch_processor - INFO - BatchProcessor started with 5 workers
[api] 2025-10-30 15:08:58,615 - infotransform.api.document_transform_api - INFO - StreamingProcessor started
[api] 2025-10-30 15:08:58,617 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 202518325(1).docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/202518325(1).docx
[api] 2025-10-30 15:08:58,618 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: CJ0029-102802 .docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/CJ0029-102802 .docx
[api] 2025-10-30 15:08:58,624 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: oct+27-29.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/oct+27-29.pdf
[api] 2025-10-30 15:08:58,624 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 202518256.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/202518256.docx
[api] 2025-10-30 15:08:58,625 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 202518325.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/202518325.docx
[api] 2025-10-30 15:08:58,626 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: Assessment 1 MSIN0056 _ Innovation Management.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Assessment 1 MSIN0056 _ Innovation Management.pdf
[api] 2025-10-30 15:08:58,627 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: B1021-1 .docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/B1021-1 .docx
[api] 2025-10-30 15:08:58,627 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: cargo-ops-demo.zip to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/cargo-ops-demo.zip
[api] 2025-10-30 15:08:58,627 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: China_updated.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/China_updated.pdf
[api] 2025-10-30 15:08:58,628 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf
[api] 2025-10-30 15:08:58,628 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: IMG_0714.PNG to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/IMG_0714.PNG
[api] 2025-10-30 15:08:58,629 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: IMG_0715.JPG to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/IMG_0715.JPG
[api] 2025-10-30 15:08:58,629 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: IMG_0716.JPG to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/IMG_0716.JPG
[api] 2025-10-30 15:08:58,629 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: midQ14.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/midQ14.docx
[api] 2025-10-30 15:08:58,636 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: oct+27-29.pptx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/oct+27-29.pptx
[api] 2025-10-30 15:08:58,636 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: q7.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/q7.docx
[api] 2025-10-30 15:08:58,637 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: q14.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/q14.docx
[api] 2025-10-30 15:08:58,645 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: Slides_12_13_13_15.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Slides_12_13_13_15.pdf
[api] 2025-10-30 15:08:58,648 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: Untitled presentation (1).pptx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Untitled presentation (1).pptx
[api] 2025-10-30 15:08:58,651 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: Untitled presentation (2).pptx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Untitled presentation (2).pptx
[api] 2025-10-30 15:08:58,651 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: USA Travel History.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/USA Travel History.pdf
[api] 2025-10-30 15:08:58,652 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: WechatIMG301.jpg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/WechatIMG301.jpg
[api] 2025-10-30 15:08:58,654 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: WechatIMG303.jpeg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/WechatIMG303.jpeg
[api] 2025-10-30 15:08:58,661 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: WechatIMG303.jpg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/WechatIMG303.jpg
[api] 2025-10-30 15:08:58,661 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 1.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/1.png
[api] 2025-10-30 15:08:58,662 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 2.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/2.png
[api] 2025-10-30 15:08:58,662 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 3.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/3.png
[api] 2025-10-30 15:08:58,663 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 4.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/4.png
[api] 2025-10-30 15:08:58,664 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 5.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/5.png
[api] 2025-10-30 15:08:58,664 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 6.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/6.png
[api] 2025-10-30 15:08:58,664 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 7.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/7.png
[api] 2025-10-30 15:08:58,665 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 8.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/8.png
[api] 2025-10-30 15:08:58,666 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 9.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/9.png
[api] 2025-10-30 15:08:58,666 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 10.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/10.png
[api] 2025-10-30 15:08:58,667 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 11.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/11.png
[api] 2025-10-30 15:08:58,667 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 000016.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000016.png
[api] 2025-10-30 15:08:58,667 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 000018.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000018.png
[api] 2025-10-30 15:08:58,668 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 000020.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000020.png
[api] 2025-10-30 15:08:58,668 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 000021.png to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/000021.png
[api] 2025-10-30 15:08:58,668 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 809c31583be9e41d1eadc9d735a7dde8.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/809c31583be9e41d1eadc9d735a7dde8.docx
[api] 2025-10-30 15:08:58,669 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 17776 a3.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17776 a3.docx
[api] 2025-10-30 15:08:58,671 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 17776 a3 edited.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17776 a3 edited.docx
[api] 2025-10-30 15:08:58,672 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 17835.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17835.docx
[api] 2025-10-30 15:08:58,672 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 17878.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17878.docx
[api] 2025-10-30 15:08:58,673 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 17878-03(6).docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/17878-03(6).docx
[api] 2025-10-30 15:08:58,673 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 18155.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/18155.docx
[api] 2025-10-30 15:08:58,674 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 18155(1).docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/18155(1).docx
[api] 2025-10-30 15:08:58,674 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 18226.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/18226.docx
[api] 2025-10-30 15:08:58,676 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 1761054989736.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/1761054989736.pdf
[api] 2025-10-30 15:08:58,755 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: 2025032401238.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/2025032401238.pdf
[api] 2025-10-30 15:08:58,755 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: as3.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/as3.pdf
[api] 2025-10-30 15:08:58,756 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: cases.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/cases.docx
[api] 2025-10-30 15:08:58,756 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: cases (1).docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/cases (1).docx
[api] 2025-10-30 15:08:58,756 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: Copy-17878.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Copy-17878.docx
[api] 2025-10-30 15:08:58,759 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: D16-1058.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/D16-1058.pdf
[api] 2025-10-30 15:08:58,759 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: document-schema-creator.zip to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/document-schema-creator.zip
[api] 2025-10-30 15:08:58,761 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ECON3460 Week 9 Ageing Population and Natalism 1.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ECON3460 Week 9 Ageing Population and Natalism 1.pdf
[api] 2025-10-30 15:08:58,762 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ECON3460 Week 9 Ageing Population and Natalism.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ECON3460 Week 9 Ageing Population and Natalism.pdf
[api] 2025-10-30 15:08:58,765 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: employment pass card sg.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/employment pass card sg.pdf
[api] 2025-10-30 15:08:58,766 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: employment pass card sg_compressed.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/employment pass card sg_compressed.pdf
[api] 2025-10-30 15:08:58,770 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: employment pass sg.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/employment pass sg.pdf
[api] 2025-10-30 15:08:58,770 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: Employment Verification with signature (Including compensation) 2025-10-19.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/Employment Verification with signature (Including compensation) 2025-10-19.pdf
[api] 2025-10-30 15:08:58,771 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: EP Detail.jpg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/EP Detail.jpg
[api] 2025-10-30 15:08:58,774 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ep1.jpeg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ep1.jpeg
[api] 2025-10-30 15:08:58,776 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ep2.jpeg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ep2.jpeg
[api] 2025-10-30 15:08:58,779 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ep2.pdf to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ep2.pdf
[api] 2025-10-30 15:08:58,780 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ex3.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ex3.docx
[api] 2025-10-30 15:08:58,781 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: ex4.docx to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/ex4.docx
[api] 2025-10-30 15:08:58,781 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: hottest-engagement-rings-768x1024.jpg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/hottest-engagement-rings-768x1024.jpg
[api] 2025-10-30 15:08:58,781 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: hq720.jpg to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/hq720.jpg
[api] 2025-10-30 15:08:58,781 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: hw-be-node-delivery-slot-question (1).zip to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/hw-be-node-delivery-slot-question (1).zip
[api] 2025-10-30 15:08:58,781 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Saved file: hw-be-node-delivery-slot-question.zip to /Users/owen/Desktop/dev_projects/InfoTransform/data/uploads/hw-be-node-delivery-slot-question.zip
[api] INFO:     127.0.0.1:54977 - "POST /api/transform HTTP/1.1" 200 OK
[api] 2025-10-30 15:08:58,803 - infotransform.api.document_transform_api - INFO - Extracted 125 files from cargo-ops-demo.zip
[api] 2025-10-30 15:08:58,803 - infotransform.api.document_transform_api - INFO - Expanded ZIP cargo-ops-demo.zip: 125 files
[api] 2025-10-30 15:08:58,804 - infotransform.api.document_transform_api - INFO - Extracted 4 files from document-schema-creator.zip
[api] 2025-10-30 15:08:58,804 - infotransform.api.document_transform_api - INFO - Expanded ZIP document-schema-creator.zip: 4 files
[api] 2025-10-30 15:08:58,819 - infotransform.api.document_transform_api - INFO - Extracted 67 files from hw-be-node-delivery-slot-question (1).zip
[api] 2025-10-30 15:08:58,819 - infotransform.api.document_transform_api - INFO - Expanded ZIP hw-be-node-delivery-slot-question (1).zip: 67 files
[api] 2025-10-30 15:08:58,834 - infotransform.api.document_transform_api - INFO - Extracted 67 files from hw-be-node-delivery-slot-question.zip
[api] 2025-10-30 15:08:58,835 - infotransform.api.document_transform_api - INFO - Expanded ZIP hw-be-node-delivery-slot-question.zip: 67 files
[api] 2025-10-30 15:08:58,835 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Processed 4 ZIP files, total files: 331
[api] 2025-10-30 15:08:58,835 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Starting processing run: 331 files, model=document_metadata, ai_model=openai.gpt-5-mini-2025-08-07
[api] 2025-10-30 15:08:58,836 - infotransform.db.processing_logs_db - INFO - Database schema initialized successfully
[api] 2025-10-30 15:08:58,836 - infotransform.db.processing_logs_db - INFO - ProcessingLogsDB initialized at backend/infotransform/data/processing_logs.db (WAL mode: True)
[api] WARNING:  WatchFiles detected changes in 'data/temp_extracts/infotransform_zip_q3ii7zj6/document-schema-creator/scripts/test_schema.py'. Reloading...
[api] 2025-10-30 15:08:58,945 - infotransform.processors.vision - INFO - Successfully processed CJ0029-102802 .docx (17685 bytes)
[api] 2025-10-30 15:08:58,959 - infotransform.processors.vision - INFO - Successfully processed China_updated.pdf (62514 bytes)
[api] INFO:     Shutting down
[api] 2025-10-30 15:08:59,059 - infotransform.processors.vision - INFO - Successfully processed 202518256.docx (18445 bytes)
[api] 2025-10-30 15:08:59,080 - infotransform.processors.vision - INFO - Successfully processed q14.docx (14947 bytes)
[api] 2025-10-30 15:08:59,145 - infotransform.processors.vision - INFO - Successfully processed B1021-1 .docx (17279 bytes)
[api] INFO:     Waiting for connections to close. (CTRL+C to force quit)
[api] 2025-10-30 15:08:59,276 - infotransform.processors.vision - INFO - Successfully processed midQ14.docx (18507 bytes)
[api] 2025-10-30 15:08:59,381 - infotransform.processors.vision - INFO - Successfully processed 202518325.docx (25430 bytes)
[api] 2025-10-30 15:08:59,433 - infotransform.processors.vision - INFO - Successfully processed 202518325(1).docx (24507 bytes)
[api] 2025-10-30 15:08:59,619 - infotransform.processors.vision - INFO - Successfully processed ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf (184400 bytes)
[api] 2025-10-30 15:08:59,627 - infotransform.processors.vision - INFO - Successfully processed USA Travel History.pdf (383224 bytes)
[api] 2025-10-30 15:08:59,934 - infotransform.processors.vision - INFO - Successfully processed q7.docx (17071 bytes)
[api] 2025-10-30 15:09:00,011 - infotransform.processors.vision - INFO - Successfully processed oct+27-29.pdf (4781815 bytes)
[api] 2025-10-30 15:09:00,241 - infotransform.processors.vision - INFO - Successfully processed Assessment 1 MSIN0056 _ Innovation Management.pdf (319994 bytes)
[api] 2025-10-30 15:09:02,426 - infotransform.processors.vision - INFO - Successfully processed Slides_12_13_13_15.pdf (3018743 bytes)
[api] 2025-10-30 15:09:12,084 - infotransform.processors.vision - INFO - Successfully processed placeholder-user.jpg (1635 bytes)
[api] 2025-10-30 15:09:13,635 - infotransform.processors.vision - INFO - Successfully processed placeholder.jpg (1064 bytes)
[api] 2025-10-30 15:09:14,145 - infotransform.processors.vision - INFO - Successfully processed Untitled presentation (1).pptx (1286902 bytes)
[api] 2025-10-30 15:09:14,233 - infotransform.processors.vision - INFO - Successfully processed placeholder-logo.png (568 bytes)
[api] 2025-10-30 15:09:16,769 - infotransform.processors.vision - INFO - Successfully processed sscpl-logo.png (85744 bytes)
[api] 2025-10-30 15:09:18,619 - infotransform.processors.vision - INFO - Successfully processed Untitled presentation (2).pptx (1286801 bytes)
[api] 2025-10-30 15:09:35,457 - infotransform.processors.vision - INFO - Successfully processed IMG_0715.JPG (56203 bytes)
[api] 2025-10-30 15:09:38,225 - infotransform.processors.vision - INFO - Successfully processed IMG_0716.JPG (55123 bytes)
[api] 2025-10-30 15:09:39,328 - infotransform.processors.vision - INFO - Successfully processed 2.png (122433 bytes)
[api] 2025-10-30 15:09:39,510 - infotransform.processors.vision - INFO - Successfully processed 809c31583be9e41d1eadc9d735a7dde8.docx (27510 bytes)
[api] 2025-10-30 15:09:39,625 - infotransform.processors.vision - INFO - Successfully processed 17776 a3.docx (832860 bytes)
[api] 2025-10-30 15:09:39,626 - infotransform.processors.vision - INFO - Successfully processed 4.png (140692 bytes)
[api] 2025-10-30 15:09:39,679 - infotransform.processors.vision - INFO - Successfully processed 17835.docx (438335 bytes)
[api] 2025-10-30 15:09:39,737 - infotransform.processors.vision - INFO - Successfully processed 17776 a3 edited.docx (763862 bytes)
[api] 2025-10-30 15:09:39,802 - infotransform.processors.vision - INFO - Successfully processed 17878.docx (17355 bytes)
[api] 2025-10-30 15:09:39,826 - infotransform.processors.vision - INFO - Successfully processed 18155.docx (18971 bytes)
[api] 2025-10-30 15:09:39,850 - infotransform.processors.vision - INFO - Successfully processed 17878-03(6).docx (23658 bytes)
[api] 2025-10-30 15:09:39,868 - infotransform.processors.vision - INFO - Successfully processed 18155(1).docx (19459 bytes)
[api] 2025-10-30 15:09:39,877 - infotransform.processors.vision - WARNING - No text content extracted from 1761054989736.pdf
[api] 2025-10-30 15:09:40,162 - infotransform.processors.vision - INFO - Successfully processed 18226.docx (335168 bytes)
[api] 2025-10-30 15:09:40,284 - infotransform.processors.vision - INFO - Successfully processed as3.pdf (88759 bytes)
[api] 2025-10-30 15:09:40,380 - infotransform.processors.vision - INFO - Successfully processed cases.docx (19291 bytes)
[api] 2025-10-30 15:09:40,458 - infotransform.processors.vision - INFO - Successfully processed WechatIMG303.jpg (1215859 bytes)
[api] 2025-10-30 15:09:40,487 - infotransform.processors.vision - INFO - Successfully processed cases (1).docx (19291 bytes)
[api] 2025-10-30 15:09:40,507 - infotransform.processors.vision - INFO - Successfully processed Copy-17878.docx (17662 bytes)
[api] 2025-10-30 15:09:40,537 - infotransform.processors.vision - INFO - Successfully processed SKILL.md (9228 bytes)
[api] 2025-10-30 15:09:40,555 - infotransform.processors.vision - INFO - Successfully processed schema_examples.md (8340 bytes)
[api] 2025-10-30 15:09:40,578 - infotransform.processors.vision - INFO - Successfully processed test_data_templates.md (6522 bytes)
[api] 2025-10-30 15:09:40,777 - infotransform.processors.vision - INFO - Successfully processed ECON3460 Week 9 Ageing Population and Natalism 1.pdf (556653 bytes)
[api] 2025-10-30 15:09:40,790 - infotransform.processors.vision - INFO - Successfully processed D16-1058.pdf (1436424 bytes)
[api] 2025-10-30 15:09:40,811 - infotransform.processors.vision - WARNING - No text content extracted from employment pass card sg.pdf
[api] 2025-10-30 15:09:40,935 - infotransform.processors.vision - WARNING - No text content extracted from employment pass card sg_compressed.pdf
[api] 2025-10-30 15:09:40,979 - infotransform.processors.vision - WARNING - No text content extracted from employment pass sg.pdf
[api] 2025-10-30 15:09:40,979 - infotransform.processors.vision - INFO - Successfully processed ECON3460 Week 9 Ageing Population and Natalism.pdf (556653 bytes)
[api] 2025-10-30 15:09:41,057 - infotransform.processors.vision - INFO - Successfully processed 3.png (183760 bytes)
[api] 2025-10-30 15:09:41,110 - infotransform.processors.vision - INFO - Successfully processed Employment Verification with signature (Including compensation) 2025-10-19.pdf (69521 bytes)
[api] 2025-10-30 15:09:41,142 - infotransform.processors.vision - INFO - Successfully processed 10.png (73786 bytes)
[api] 2025-10-30 15:09:41,213 - infotransform.processors.vision - WARNING - No text content extracted from ep2.pdf
[api] 2025-10-30 15:09:41,471 - infotransform.processors.vision - INFO - Successfully processed ex3.docx (441359 bytes)
[api] 2025-10-30 15:09:41,652 - infotransform.processors.vision - INFO - Successfully processed ex4.docx (14763 bytes)
[api] 2025-10-30 15:09:43,434 - infotransform.processors.vision - INFO - Successfully processed WechatIMG301.jpg (413280 bytes)
[api] 2025-10-30 15:09:46,261 - infotransform.processors.vision - INFO - Successfully processed 5.png (167961 bytes)
[api] 2025-10-30 15:09:46,326 - infotransform.processors.vision - INFO - Successfully processed PRD.md (2604 bytes)
[api] 2025-10-30 15:09:46,371 - infotransform.processors.vision - INFO - Successfully processed README.md (3130 bytes)
[api] 2025-10-30 15:09:46,409 - infotransform.processors.vision - INFO - Successfully processed PRD.md (2604 bytes)
[api] 2025-10-30 15:09:46,460 - infotransform.processors.vision - INFO - Successfully processed README.md (3130 bytes)
[api] 2025-10-30 15:09:46,905 - infotransform.processors.vision - INFO - Successfully processed 2025032401238.pdf (33730736 bytes)
[api] 2025-10-30 15:09:46,909 - infotransform.processors.vision - INFO - Successfully processed 000016.png (30170 bytes)
[api] 2025-10-30 15:09:47,410 - infotransform.processors.vision - INFO - Successfully processed 7.png (132258 bytes)
[api] 2025-10-30 15:09:48,844 - infotransform.processors.vision - INFO - Successfully processed WechatIMG303.jpeg (424927 bytes)
[api] 2025-10-30 15:09:49,374 - infotransform.processors.vision - INFO - Successfully processed 9.png (151641 bytes)
[api] 2025-10-30 15:09:51,856 - infotransform.processors.vision - INFO - Successfully processed 000018.png (60482 bytes)
[api] 2025-10-30 15:09:52,223 - infotransform.processors.vision - INFO - Successfully processed IMG_0714.PNG (220097 bytes)
[api] 2025-10-30 15:09:52,248 - infotransform.processors.vision - INFO - Successfully processed 8.png (150352 bytes)
[api] 2025-10-30 15:09:52,557 - infotransform.processors.vision - INFO - Successfully processed hq720.jpg (63805 bytes)
[api] 2025-10-30 15:09:54,036 - infotransform.processors.vision - INFO - Successfully processed 6.png (171636 bytes)
[api] 2025-10-30 15:09:55,243 - infotransform.processors.vision - INFO - Successfully processed 1.png (165910 bytes)
[api] 2025-10-30 15:10:01,011 - infotransform.processors.vision - INFO - Successfully processed hottest-engagement-rings-768x1024.jpg (109639 bytes)
[api] 2025-10-30 15:10:04,508 - infotransform.processors.vision - INFO - Successfully processed 11.png (138930 bytes)
[api] 2025-10-30 15:10:09,746 - infotransform.processors.vision - INFO - Successfully processed ep2.jpeg (2829471 bytes)
[api] 2025-10-30 15:10:12,640 - infotransform.processors.vision - INFO - Successfully processed EP Detail.jpg (317182 bytes)
[api] 2025-10-30 15:10:12,925 - infotransform.processors.vision - INFO - Successfully processed 000020.png (37512 bytes)
[api] 2025-10-30 15:10:16,983 - infotransform.processors.vision - INFO - Successfully processed ep1.jpeg (2916148 bytes)
[api] 2025-10-30 15:10:36,536 - infotransform.processors.vision - INFO - Successfully processed 000021.png (46209 bytes)
[api] 2025-10-30 15:10:58,876 - infotransform.api.document_transform_api - INFO - [47f93933-faff-4ef5-91b4-91c1bb24a35e] Markdown conversion complete: 331 files in 120.04s
[api] 2025-10-30 15:10:59,127 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 1 items with model: document_metadata
[api] 2025-10-30 15:10:59,131 - infotransform.utils.token_counter - INFO - Token count for '202518325(1).docx' (batch_analysis): 2,108 tokens
[api] 2025-10-30 15:11:12,931 - infotransform.processors.ai_batch_processor - INFO - Batch processed: 1 items in 13.80s (13.80s per item)
[api] 2025-10-30 15:11:12,933 - infotransform.processors.ai_batch_processor - INFO - Processing batch of 15 items with model: document_metadata
[api] 2025-10-30 15:11:12,946 - infotransform.utils.token_counter - INFO - Token count for 'Assessment 1 MSIN0056 _ Innovation Management.pdf' (batch_analysis): 4,606 tokens
[api] 2025-10-30 15:11:12,949 - infotransform.utils.token_counter - INFO - Token count for 'China_updated.pdf' (batch_analysis): 1,064 tokens
[api] 2025-10-30 15:11:12,950 - infotransform.utils.token_counter - INFO - Token count for 'IMG_0714.PNG' (batch_analysis): 1,061 tokens
[api] 2025-10-30 15:11:12,952 - infotransform.utils.token_counter - INFO - Token count for '202518325.docx' (batch_analysis): 2,546 tokens
[api] 2025-10-30 15:11:12,953 - infotransform.utils.token_counter - INFO - Token count for 'placeholder-user.jpg' (batch_analysis): 135 tokens
[api] 2025-10-30 15:11:12,975 - infotransform.utils.token_counter - INFO - Token count for 'IMG_0715.JPG' (batch_analysis): 655 tokens
[api] 2025-10-30 15:11:12,977 - infotransform.utils.token_counter - INFO - Token count for 'placeholder-logo.png' (batch_analysis): 198 tokens
[api] 2025-10-30 15:11:12,978 - infotransform.utils.token_counter - INFO - Token count for 'ECON3460 Persuasive Presentation Task Sheet and Rubric FINAL.pdf' (batch_analysis): 2,401 tokens
[api] 2025-10-30 15:11:12,981 - infotransform.utils.token_counter - INFO - Token count for 'IMG_0716.JPG' (batch_analysis): 766 tokens
[api] 2025-10-30 15:11:12,982 - infotransform.utils.token_counter - INFO - Token count for 'sscpl-logo.png' (batch_analysis): 113 tokens
[api] 2025-10-30 15:11:12,986 - infotransform.utils.token_counter - INFO - Token count for '202518256.docx' (batch_analysis): 1,633 tokens
[api] 2025-10-30 15:11:12,991 - infotransform.utils.token_counter - INFO - Token count for 'B1021-1 .docx' (batch_analysis): 1,152 tokens
[api] 2025-10-30 15:11:13,013 - infotransform.utils.token_counter - INFO - Token count for 'placeholder.jpg' (batch_analysis): 154 tokens
[api] 2025-10-30 15:11:13,019 - infotransform.utils.result_cache - INFO - Cache HIT: dd14bae8c2bfe9a1... (retrieved in 85.8ms, hit_count=5)
[api] 2025-10-30 15:11:13,020 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for CJ0029-102802 .docx (retrieved in 86.2ms)
[api] 2025-10-30 15:11:13,095 - infotransform.utils.result_cache - INFO - Cache HIT: 962388f25bac0a09... (retrieved in 161.6ms, hit_count=1)
[api] 2025-10-30 15:11:13,096 - infotransform.processors.ai_batch_processor - INFO - Cache HIT for oct+27-29.pdf (retrieved in 161.9ms)
