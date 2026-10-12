# Nhóm thực hiện K4 Track 3B

Tên nhóm: {{Tên nhóm}}

Repo chung: https://github.com/Liin1310h/K4-Track-3B-Day24-Eval-Guard

Trưởng nhóm/người nộp: Phạm Thị Thùy Linh - 2A202602909

Ngày lab/deadline áp dụng: 11:59 ngày 13/10/2026 (theo README; chờ coach xác nhận) — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Phạm Thị Thùy Linh | 2A202602909 | Trưởng nhóm; tích hợp m1-m5 và sinh 50 answers; Phase A (Tasks 1-4 trong `src/phase_a_ragas.py`); `doc/reports/failure_clusters.md` | Commit 8161cd3, 1beac6f; `artifacts/answers_50q.json`, `artifacts/ragas_50q.json` |
| 2 | Nguyễn Đức Tâm | 2A202602921 | Phase B (Tasks 5-8 trong `src/phase_b_judge.py`), chạy live Phase B; `doc/reports/bias_report.md`; chủ biên Task 13 `doc/reports/blueprint.md` | PR #1 (nhánh `feat/phase-b`): commit f4db003, 7a75c4e, 6fbbebc; `artifacts/judge_results.json` |
| 3 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 Home 10.0.26300; Python 3.11 (venv `.venv`); Microsoft C++ Build Tools (MSVC) cài bằng winget để build annoy 1.17.3.
Virtualenv/dependencies/imports: `pip install -r requirements/requirements.txt -c requirements/constraints-core.txt` thành công sau khi cài MSVC; `pip check` báo "No broken requirements found"; import `ragas, nemoguardrails, presidio_analyzer, spacy` chạy được sau khi thêm `import torch` vào `src/__init__.py` (lỗi DLL WinError 1114 của torch trên Windows nếu import sau ragas). Phải ghim `pyarrow>=15,<18` vì pyarrow mới đòi NumPy 2 trong khi lab ghim numpy 1.26.4. Model spaCy `en_core_web_lg` 3.8.0 đã cài.
Models/Qdrant/50 answers đã chuẩn bị: Qdrant `qdrant/qdrant:v1.9.7` chạy bằng Docker Compose; BGE-M3 và bge-reranker-v2-m3 tải qua sentence-transformers; `setup_answers.py --live` sinh 50 answers (20/20/10), toàn bộ `generation_mode=llm`, model `gpt-4o-mini-2024-07-18`, enrichment 102/102 chunk thành công. Giới hạn: hai PDF scan ảnh (BCTC, Nghị định 13) không có text layer nên bị bỏ qua; 12/50 câu trả lời là "Không tìm thấy." do prompt từ chối và chunking (xem failure_clusters.md). Chưa chạy Phase C nên chưa kiểm chứng NeMo hoạt động đầy đủ, chỉ mới import được.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### PhamThiThuyLinh-2A202602909

- Phần được giao và phần thực tế đã làm: trưởng nhóm. Đưa m1-m5 từ Day18 vào `src/` và sửa cho khớp `PIPELINE_INTERFACE.md` (m2 dùng Qdrant 1.9 API và báo lỗi thay vì chạy in-memory; m4 trả `metadata.evaluator_models` và không điền 0 khi NaN; m5 gọi API song song nhưng giữ thứ tự). Cài Tasks 1-4 trong `src/phase_a_ragas.py`. Sinh `artifacts/answers_50q.json`, chạy Phase A live, viết `failure_clusters.md`.
- Bằng chứng: commit 8161cd3 (m1-m5, Tasks 1-4, answers) và 1beac6f (`ragas_50q.json`) trên nhánh `feat/pipeline-phase-a`; `doc/reports/failure_clusters.md`.
- Cách kiểm tra: `python -m pytest tests/test_phase_a.py -q` (6 passed) và `tests/ -m support` (60 passed); live: `python scripts/setup_answers.py --live`, `python scripts/run_experiments.py --phase a --live`; `python scripts/check_lab.py` báo PASS cho `phase_a_ragas.py`, `answers_50q.json` và Phase A artifact.
- Điều đã học: bốn metric RAGAS đo bốn thứ khác nhau và không thể gộp thành một nguyên nhân; matrix worst_metric là thống kê, còn nhóm yếu phải chọn theo mean; câu từ chối "Không tìm thấy" nhận điểm 0 dù trung thực với context; `context_recall` của RAGAS có thể chấm 1.0 khi context thật ra thiếu ý (câu 9), và `faithfulness` có thể chấm 0 cho câu đúng cần tính toán (câu 31).
- Giới hạn/cách xử lý: diagnosis tự động trong Task 3 là heuristic dò từ khóa nên có chỗ sai (câu 9); đã đối chiếu thủ công contexts với file nguồn trong `data/` và ghi chỗ sửa trong báo cáo. Một lần chạy RAGAS, 50 câu, model đánh giá trùng model sinh. Chưa thử các đề xuất sửa pipeline.
- Nguồn/AI hỗ trợ nếu có: dùng Claude Code (Claude Opus 5.5 và Sonnet 5.5) để chép/sửa m1-m5, cài Tasks 1-4, soạn nháp báo cáo; tự kiểm chứng bằng test, chạy live, đọc contexts trong `ragas_50q.json` và đối chiếu với `data/`. Mã m1-m5 gốc là phần đã làm ở bài Day18 của chính mình.

### NguyenDucTam-2A202602921

- Phần được giao và phần thực tế đã làm: TV2, phụ trách Phase B và chủ biên Task 13. Cài Tasks 5-8 trong `src/phase_b_judge.py`: `pairwise_judge` (prompt có question, reference, A, B và 3 tiêu chí, dặn độ dài không phải tiêu chí; `temperature=0`, JSON mode; validate winner/scores, JSON sai thì retry tối đa 2 lần rồi raise), `swap_and_average` (lượt 2 đảo B/A, quy winner và scores về A/B gốc, hai lượt khác nhau thì tie), `cohen_kappa` (kiểm tra độ dài, list rỗng, nhãn 0/1; xử lý p_e = 1), `bias_report` (position/verbosity kèm `verbosity_details` và diễn giải dạng dấu hiệu). Chạy live Phase B, viết `bias_report.md`, soạn `blueprint.md` (kiến trúc, failure action, CI gates, monitoring, cải tiến).
- Bằng chứng: PR #1 từ nhánh `feat/phase-b`; commit f4db003 (code Tasks 5-8), 7a75c4e (`artifacts/judge_results.json`, `bias_report.md`), 6fbbebc (`blueprint.md`).
- Cách kiểm tra: `python -m pytest tests/test_phase_b.py -q` (8 passed); live `python scripts/run_experiments.py --phase b --live` một lần, validator trong runner pass; `python scripts/check_lab.py` báo PASS cho `phase_b_judge.py` và Phase B artifact. Tự đọc lại 5 cặp và 10 nhãn, đối chiếu với `ground_truth` trong `fixtures/test_set_50q.json`.
- Điều đã học: pairwise A/B và nhãn 0/1 trả lời hai câu hỏi khác nhau, không đổi qua lại được. Swap-and-average phát hiện được 2/5 cặp đổi winner khi đảo thứ tự, và cả hai đều là cặp có hai answer gần như nhau (cùng sai ở id 5, cùng đúng ở id 12). κ phải trừ phần đồng thuận ngẫu nhiên: p_e = 0.52 nên p_o cao chưa đủ để kết luận. Nhãn đúng không có nghĩa reasoning đúng: ở ids 1, 12, 46, judge gán cho answer những ý chỉ có trong reference.
- Giới hạn/cách xử lý: chỉ có 5 cặp và 10 nhãn, một judge cùng họ gpt-4o-mini với generator. κ = 1.0 rất nhạy, một nhãn lệch là giảm còn khoảng 0.78-0.8. Đã ghi các giới hạn này và cách kiểm chứng (judge khác họ, thêm quy tắc xếp "từ chối" và "trả lời sai") trong `bias_report.md` và `blueprint.md`. Số liệu Phase C trong blueprint chờ `guard_results.json` của TV3.
- Nguồn/AI hỗ trợ nếu có: dùng Claude Code (Claude Opus 5.5) để viết code Tasks 5-8, chạy test và live, soạn nháp `bias_report.md` và `blueprint.md`. Tự kiểm chứng bằng unit test, validator của runner và `check_lab.py`, và đối chiếu từng cặp, từng nhãn với reference.

<!-- Thành viên 3: sao chép mẫu dưới đây -->

### {{HoVaTen}}-{{MSSV}}

- Phần được giao và phần thực tế đã làm: {{Nhiệm vụ, file/hàm, mục đích}}.
- Bằng chứng: {{Commit/PR và artifacts/reports liên quan}}.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
