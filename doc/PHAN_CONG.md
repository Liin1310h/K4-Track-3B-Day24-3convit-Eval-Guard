# Kế hoạch & phân công nhóm — K4 Track 3B (Eval + Guardrail)

> Tài liệu nội bộ của nhóm, do trưởng nhóm soạn. Không thay cho `doc/TEAM.md`. Phần
> đóng góp chính thức vẫn được khai trong TEAM.md, mục INDIVIDUAL.
> Nguồn: README.md, ASSIGNMENT, CHECKPOINTS, RUBRIC, RULES, SUBMISSION, REPORT_SCHEMAS,
> PIPELINE_INTERFACE, ENVIRONMENT.

## 1. Tổng quan và nguyên tắc chia việc

Bài có 4 khối điểm: Phase A (30đ), Phase B (35đ), Phase C (35đ). Task 13 Blueprint là
bắt buộc, để trống thì bị trừ 10đ. Ngoài ra có tối đa 10đ bonus. Ba phase **độc lập về
code**, nên mỗi người sở hữu trọn một phase: viết code, chạy live, viết report. Việc
chung (chuẩn bị môi trường, blueprint, nộp bài) được chia theo dữ liệu mà người đó nắm.

| | **TV1 — Trưởng nhóm** | **TV2** | **TV3** |
|---|---|---|---|
| Vai trò chính | Tích hợp pipeline + Phase A + nộp bài | Phase B (LLM Judge) + chủ biên Blueprint | Phase C (Guardrails) + số liệu latency |
| File code | `src/m1..m5_*.py`, `src/phase_a_ragas.py` | `src/phase_b_judge.py` | `src/phase_c_guard.py` |
| Tasks | CP0, Tasks 1–4 | Tasks 5–8, Task 13 (chủ biên) | Tasks 9a, 9b, 10, 11, 12 |
| Artifact JSON | `answers_50q.json`, `ragas_50q.json` | `judge_results.json` | `guard_results.json` |
| Report MD | `failure_clusters.md` | `bias_report.md`, `blueprint.md` | Mục latency/guard trong `blueprint.md` |
| Điểm phụ trách | 30 + điều kiện tiên quyết (không có answers thì A = 0) | 35 + Task 13 (−10 nếu trống) | 35 |
| Bonus mục tiêu | +4 (adversarial mean < factual mean, kèm phân tích bẫy) | +3 (κ > 0.6) | +3 (≥18/20 attacks + clean 8/8) |
| Việc chung | Merge PR, chạy `check_lab.py`, điền header TEAM, nộp link | Gom số liệu A/B/C vào blueprint, rà placeholder | Kiểm tra secrets/PII trước commit cuối |

**Lý do chia như vậy:** TV1 phải giữ pipeline m1–m5 vì cả `answers_50q.json` lẫn m4
(evaluator dùng cho Task 2) đều thuộc Phase A. Phase B ít code hạ tầng nhất nên TV2 nhận
thêm Blueprint. Phase C nặng nhất về môi trường (NeMo/Annoy cần C++ compiler, Presidio,
spaCy), nên TV3 chỉ đóng góp số liệu cho blueprint chứ không làm chủ biên.

## 2. Phụ thuộc giữa các phần

```text
TV1: m1–m5 + setup_answers --live ──► answers_50q.json ──┬─► Phase A (TV1)
                                                          └─► Phase B: 5 cặp A/B (TV2)
TV3: NeMo + Presidio (độc lập answers) ──────────────────────► Phase C (TV3)
ragas_50q + judge_results + guard_results ───────────────────► blueprint.md (TV2 chủ biên)
Tất cả artifacts + reports + TEAM ───────────────────────────► check_lab.py ─► nộp (TV1)
```

- `answers_50q.json` là **đường găng**: TV1 phải có file này trước buổi học. Thiếu nó
  thì Phase A bằng 0 và Phase B không có answer A.
- Phase B chỉ cần answers của 5 id 1, 5, 12, 21, 41. Phase C không cần answers.
  Vì vậy trong 90 phút trên lớp, **ba phase chạy song song**, không phải tuần tự.

## 3. Lịch trình và mốc

Deadline: theo README là **11:59 AM 13/10/2026 (UTC+7)**; ASSIGNMENT/RULES ghi mặc định
23:59 ngày lab. Nhóm **áp dụng mốc sớm hơn (11:59 13/10)** cho đến khi coach thông báo khác.

| Mốc | Thời điểm | TV1 | TV2 | TV3 |
|---|---|---|---|---|
| M0 — Chuẩn bị | Trước buổi học | Chép m1–m5, viết adapter, Qdrant v1.9.7, chạy `setup_answers.py --live`, push answers | Venv Python 3.11, test 1 lời gọi OpenAI bằng `JUDGE_MODEL`, đọc `human_labels_10q.json` | Cài C++ Build Tools, full requirements, `pip check`, import NeMo/Presidio/spaCy, tải `en_core_web_lg` |
| M1 — 15' đầu giờ | Đầu buổi | Xác nhận 50 answers (20/20/10), điền bảng thành viên | Xác nhận key + import | Xác nhận NeMo load được `guardrails/` |
| M2 — 90' thực hành | Trên lớp | Tasks 1–4, test offline, chạy live A | Tasks 5–8, test offline, chạy live B | Tasks 9a–12, test offline, chạy live C |
| M3 — Báo cáo | Tối 12/10 | `failure_clusters.md` + gửi số RAGAS cho TV2 | `bias_report.md` + bản nháp blueprint | Gửi bảng latency + attack/clean cho TV2, sửa false positives nếu có |
| M4 — Đóng băng | 08:00 13/10 | Merge tất cả, `check_lab.py --with-tests` | Blueprint hoàn chỉnh | Quét secrets/PII |
| M5 — Nộp | ≤ 11:00 13/10 | Push, ghi commit SHA vào TEAM, nộp link | Kiểm tra INDIVIDUAL của mình | Kiểm tra INDIVIDUAL của mình |

## 4. Quy tắc làm việc chung (bắt buộc với cả 3 người)

1. **Git là bằng chứng đóng góp.** Mỗi người làm trên branch riêng (`feat/phase-a`,
   `feat/phase-b`, `feat/phase-c`, `docs/blueprint`), commit bằng tài khoản của chính
   mình, mở PR vào `main`. TV1 review và merge. Không commit hộ người khác.
2. **Không commit `.env`, venv, cache model.** Key chỉ nằm trong `.env`. Trước mỗi commit,
   chạy `git status --short` và đọc diff.
3. **Live run có tốn phí:** mỗi phase chạy live **một lần thành công** do chủ phase thực
   hiện. Chỉ chạy lại khi đã sửa code. **Không** chạy thêm `pytest -m integration --run-live`
   sau khi runner B/C đã tạo artifacts.
4. **Không sửa số liệu bằng tay** trong `artifacts/*.json`. Không đổi fixtures hoặc ground
   truth để "đẹp điểm". Không dùng ground_truth thay answer. Không xóa policy cũ trong `data/`.
5. **Không còn `# TODO`** trong `src/phase_*.py` (mỗi module còn TODO bị trừ 5đ). Mỗi
   student test fail bị trừ 3đ. Trước khi mở PR: `python -m pytest tests/ -q` phải xanh với phase của mình.
6. **Dùng AI thì ghi lại** trong INDIVIDUAL: công cụ, phần được hỗ trợ, cách tự kiểm chứng.
   Mỗi người phải tự giải thích được code của mình.
7. Báo cáo Markdown **lấy số từ JSON**, không gõ ước lượng. Thay hết `{{...}}`; không để `?`
   hay bảng rỗng.

---

## 5. TV1 — Trưởng nhóm: Tích hợp pipeline + Phase A + Nộp bài

### 5.1 Phạm vi

- CP0: đưa 5 module m1–m5 từ bài RAG trước vào `src/` theo `doc/PIPELINE_INTERFACE.md`,
  rồi sinh `artifacts/answers_50q.json`.
- Phase A, Tasks 1–4 trong `src/phase_a_ragas.py`, cùng `doc/reports/failure_clusters.md`.
- Điều phối: merge PR, điền phần đầu và phần môi trường của `doc/TEAM.md`, chạy checker, nộp link.

### 5.2 Các bước

**Trước buổi học (CP0)**
1. Chép `m1_chunking.py`, `m2_search.py`, `m3_rerank.py`, `m4_eval.py`, `m5_enrichment.py`
   vào `src/`. Đối chiếu **từng dòng** trong bảng giao diện: kiểu trả về, thuộc tính
   `.text/.score/.metadata/.parent_id`, và `enrich_chunks` giữ nguyên số lượng và thứ tự.
2. Sửa m4 `evaluate_ragas` để trả `metadata.evaluator_models` gồm các model ID LLM và
   embedding **thực sự dùng**. Không lấy `JUDGE_MODEL` điền thay. Mỗi phần tử `per_question`
   có 4 thuộc tính float. Nếu m4 trả dict, bọc bằng `SimpleNamespace`.
3. `docker compose -f infra/docker-compose.yml up -d` (Qdrant `v1.9.7`), tải BGE-M3/reranker,
   rồi chạy `python scripts/setup_answers.py --live`.
4. Tự kiểm tra `answers_50q.json`: đủ 50 id; phân bố 20/20/10; `contexts` lấy từ
   search/rerank thật; `generation_mode` là `llm` (nếu là `extractive_fallback` thì ghi lý do);
   `generation_model` đúng `gpt-4o-mini` hoặc `null` khi fallback. Push lên `main` và báo nhóm.

**Trên lớp (Phase A)**
5. **Task 1** `group_by_distribution`: luôn trả đủ 3 key, kể cả khi nhóm rỗng.
6. **Task 2** `run_ragas_50q`: assert số `per_question` bằng số answers trước khi ghép,
   ghép theo đúng thứ tự hoặc id. Ép kiểu `float(...)`. Gặp NaN/inf thì **raise**, không
   thay bằng 0. Trả `RagasEvaluation(results, raw["metadata"]["evaluator_models"])`.
7. **Task 3** `bottom_10`: sắp tăng dần theo `avg_score`, hòa thì xếp theo `question_id`
   để kết quả ổn định. Trả 10 dòng đủ các khóa
   `rank/question_id/question/distribution/avg_score/worst_metric/diagnosis/suggested_fix`.
   **Diagnosis/fix phải cụ thể theo từng câu**, viết sau khi đọc answer, contexts và
   reference (ví dụ "retrieve nhầm `nghi_phep_nam_v2023` thay vì v2024"), không chỉ chép
   `DIAGNOSTIC_TREE`. Có thể bắt đầu từ cây chẩn đoán rồi bổ sung chi tiết.
8. **Task 4** `cluster_analysis`: lập ma trận worst_metric × distribution, đếm **mọi câu**.
   Chọn nhóm yếu nhất bằng **avg_score trung bình thấp nhất** và bỏ nhóm rỗng. Trả kèm
   `distribution_avg_scores`. Insight phải nêu số liệu thật.
9. `python -m pytest tests/test_phase_a.py -q` phải xanh. Sau đó chạy
   `python scripts/run_experiments.py --phase a --live`.

**Sau lớp**
10. Điền `failure_clusters.md`: bảng 4 metric × 3 distribution, 10 dòng bottom khớp JSON,
    phân tích **ít nhất 3 câu đại diện** (trích answer/context/reference), ma trận, nhóm yếu
    nhất, phần bẫy adversarial (version conflict v2023/v2024, mat_khau v1/v2, phủ định).
11. Gửi TV2 các số: mean theo distribution, faithfulness, avg tổng, evaluator models.
12. Cuối cùng: merge tất cả PR, chạy `python scripts/check_lab.py --with-tests`, kiểm tra
    `git check-ignore artifacts/*.json` không in gì, push, ghi `git rev-parse HEAD` vào TEAM,
    mở commit trên GitHub kiểm tra lại, rồi nộp link.

### 5.3 Đầu ra phải bàn giao

| Đầu ra | Tiêu chí chất lượng (Definition of Done) |
|---|---|
| `src/m1..m5_*.py` | Khớp 100% bảng giao diện; m4 ghi `evaluator_models` thật; không hard-code key |
| `artifacts/answers_50q.json` | 50 id, 20/20/10; answer ≠ ground_truth; contexts thật; mode/model đúng; pass schema |
| `src/phase_a_ragas.py` | Không còn TODO; `test_phase_a.py` xanh; không có NaN, list rỗng hay chọn nhóm theo tổng 20/20/10 |
| `artifacts/ragas_50q.json` | 50 per_question, 4 metric hữu hạn trong [0,1]; 10 bottom giữ nguyên diagnosis của Task 3; `models.evaluator` lấy từ m4 |
| `failure_clusters.md` | Mọi số khớp JSON; ≥3 case có trích dẫn; mỗi cụm lỗi có fix cụ thể và cách kiểm chứng khi chạy lại; ghi rõ giới hạn và fallback |
| Nộp bài | `check_lab.py` không còn lỗi; commit SHA nằm trong TEAM; repo đúng tên `K4-L3-DAY24-TenNhom-Eval-Guard` và người chấm truy cập được |

---

## 6. TV2 — Phase B (LLM Judge) + chủ biên Blueprint

### 6.1 Phạm vi

- Tasks 5–8 trong `src/phase_b_judge.py`.
- `doc/reports/bias_report.md`.
- Chủ biên `doc/reports/blueprint.md` (Task 13): viết kiến trúc, CI gates, monitoring, rồi
  gom số liệu từ TV1 và TV3.

### 6.2 Các bước

**Trước buổi học**
1. Tạo venv Python 3.11. Test một lời gọi OpenAI với `JUDGE_MODEL`, có
   `response_format={"type": "json_object"}`.
2. Đọc `fixtures/human_labels_10q.json` và `src/experiment_support.judge_binary` để hiểu
   luồng nhãn 0/1. **Không sửa helper để đưa human_label/human_note vào prompt.**

**Trên lớp**
3. **Task 5** `pairwise_judge`: prompt có question, **reference**, Answer A, Answer B và 3
   tiêu chí (chính xác theo reference, đầy đủ, súc tích). Dùng `temperature=0` và JSON mode.
   **Validate** `winner ∈ {A, B, tie}` và `scores.A/B` là số trong [0,1]. JSON sai thì retry
   tối đa 2 lần rồi raise; không âm thầm trả "tie". Dặn thêm trong prompt rằng độ dài không
   phải tiêu chí. Nếu đổi model thì cập nhật `JUDGE_MODEL`.
4. **Task 6** `swap_and_average`: lượt 2 gọi `(q, B, A)` với **cùng reference**. Quy
   winner về không gian gốc theo A↔B, tie giữ tie. Hoán đổi lại cả `scores_pass2`.
   Hai lượt cùng ý thì lấy kết quả đó, khác nhau thì `tie`. Ghi đủ reasoning của hai lượt.
5. **Task 7** `cohen_kappa`: kiểm tra 2 list cùng độ dài và khác rỗng, nếu không thì raise.
   Tính p_o và p_e. Trường hợp p_e = 1 (cả hai đều toàn một nhãn): đồng ý hoàn toàn thì
   trả 1.0, không thì 0.0. Kết quả phải nằm trong [-1,1]. Ba case test: [1,0,1,0] vs chính
   nó → 1; vs đảo ngược → −1; [1,1,0,0] vs [1,0,1,0] → 0.
6. **Task 8** `bias_report`: tính position_bias_count/rate; verbosity = (A thắng và A dài
   hơn + B thắng và B dài hơn) / số case decisive; trả đủ `verbosity_details`. Không có
   case decisive thì verbosity = 0.0. Interpretation phải nói rõ đây chỉ là **dấu hiệu**.
7. `python -m pytest tests/test_phase_b.py -q` phải xanh. Chờ TV1 xác nhận answers đã có
   trên `main`, rồi chạy `python scripts/run_experiments.py --phase b --live`.

**Sau lớp**
8. `bias_report.md`: bảng 5 cặp (id, winner lượt 1, winner lượt 2 đã quy đổi, final,
   consistent, scores, tóm tắt reasoning); bảng 10 nhãn (id, model_answer, judge, human,
   agree); κ kèm **phép tính p_o và p_e**; đọc nội dung các case lệch với human và các case
   winner dài hơn để kết luận có bias thật hay chỉ trùng hợp; nêu giới hạn (n=5 và n=10, một model).
9. `blueprint.md`: data flow Input → Presidio → NeMo input → RAG → NeMo output → response;
   failure action mỗi tầng (chặn, redact, fallback, log ra sao, secrets để đâu); CI gates
   đề xuất kèm lệnh job và cách script trả mã thoát khác 0; monitoring (metric, ngưỡng cảnh
   báo, cách lấy mẫu, false positive, drift, privacy, người xử lý); 3–5 cải tiến đo được, gắn
   với số liệu của nhóm. Ghi rõ đây là **đề xuất, chưa triển khai workflow**.

### 6.3 Đầu ra phải bàn giao

| Đầu ra | Tiêu chí chất lượng |
|---|---|
| `src/phase_b_judge.py` | Không còn TODO; `test_phase_b.py` xanh; có validate JSON; không có đường nào leak human labels |
| `artifacts/judge_results.json` | `pair_sources` đúng 3 nguồn; 5 cặp × 2 lượt = 10 lời gọi; 10 binary judgments trên **model_answer gốc**, label kiểu int 0/1; ids/judge_labels/human_labels cùng thứ tự; κ thật |
| `bias_report.md` | Đủ 5 + 10 dòng khớp JSON; có phép tính κ; phân biệt "dấu hiệu thống kê" với "nguyên nhân"; nếu κ ≤ 0.6 thì diễn giải trung thực, không chỉnh để đạt bonus |
| `blueprint.md` | Không còn `{{}}`; latency ngoài Task 12 ghi "chưa đo" kèm kế hoạch đo; không dùng input_guard_ms làm full-guard; số liệu A/B/C khớp 3 JSON; nêu ngưỡng 15/20 (bắt buộc) và 18/20 (CI/bonus) |

---

## 7. TV3 — Phase C (Guardrails) + số liệu latency

### 7.1 Phạm vi

- Tasks 9a, 9b, 10, 11, 12 trong `src/phase_c_guard.py`.
- `artifacts/guard_results.json`.
- Mục "Phạm vi và số đo latency" và các số guard trong `blueprint.md`, gửi cho TV2 hoặc tự
  commit vào branch `docs/blueprint`.

### 7.2 Các bước

**Trước buổi học (quan trọng nhất)**
1. Cài Microsoft C++ Build Tools (Desktop development with C++), tạo venv Python 3.11, cài
   `requirements.txt` với `-c constraints-core.txt`, chạy `pip check`, chạy lệnh import
   `ragas, nemoguardrails, presidio_analyzer, spacy`, rồi `python -m spacy download en_core_web_lg`.
2. Thử `setup_presidio()` và `setup_nemo_rails()` có load được không. Lỗi ở đâu thì ghi lỗi
   thật vào TEAM ngay.

**Trên lớp**
3. **Task 9a** `pii_scan`: trả `has_pii`, `entities` (type/text/score/start/end) và
   `anonymized` (thay bằng `<TYPE>`). Phải bắt được CCCD 12 số, CMND 9 số, SĐT VN, email.
   **Cẩn thận false positive:** analyzer tiếng Anh có thể gắn PERSON/LOCATION/DATE_TIME vào
   câu tiếng Việt sạch. Nên giới hạn `entities=[...]` ở các loại nhạy cảm (VN_CCCD, VN_PHONE,
   EMAIL_ADDRESS, PHONE_NUMBER…) và/hoặc đặt ngưỡng score, rồi kiểm tra trên cả 8 câu clean.
4. **Task 9b** `check_input_rail` (async): `generate_async` với
   `options={"rails": ["input"], "log": {"activated_rails": True}}`. Quyết định block lấy từ
   `result.log.activated_rails`, đọc response từ `result.response[0]["content"]`.
   **Tuyệt đối không** suy block từ từ khóa "xin lỗi" hay "không thể": câu clean 102 bắt
   đầu bằng đúng "Xin lỗi, tôi không thể…".
5. **Task 10** `run_adversarial_suite`: nhận list bất kỳ (runner truyền 28 inputs). Giữ
   nguyên `input`; `expected` chỉ dùng để so sánh. Thứ tự Presidio → NeMo input. Chỉ gọi
   `asyncio.run` **một lần** cho cả batch. Mỗi dòng trả đủ
   `id/category/input/expected/actual/blocked_by/passed`.
6. **Task 11** `check_output_rail` (async): gửi user + assistant với `rails: ["output"]`.
   Bị flag thì `final_answer` là câu thay thế từ rail; an toàn thì **giữ nguyên answer**.
   Kiểm tra 4 case: 201 và 202 giữ nguyên (202 có `helpdesk@cty.vn` được phép); 203 (CCCD)
   và 204 (mật khẩu) phải bị thay.
7. **Task 12** `measure_p95_latency`: tạo engine trước; trong **một** event loop chạy
   **2 lượt warm-up thật** (Presidio + NeMo) và loại chúng khỏi mẫu; sau đó lấy ≥20 mẫu,
   xoay vòng 8 câu clean, dùng `perf_counter` và đơn vị ms; **luôn đo cả hai tầng**, không
   short-circuit; trả kết quả qua `summarize_latency(samples, warmup_runs=2)`.
8. `python -m pytest tests/test_phase_c.py -q` phải xanh, rồi chạy
   `python scripts/run_experiments.py --phase c --live --latency-samples 20`.
9. Đọc kết quả: attack nào lọt thì phân tích nguyên nhân; câu clean nào bị chặn thì sửa
   (thu hẹp entity Presidio, xem log NeMo) và chạy lại. **Không** sửa
   `adversarial_set_20.json` hay `clean_set_8.json`. Nếu sửa `guardrails/config.yml` thì
   ghi lý do trong blueprint và TEAM.

**Sau lớp**
10. Gửi TV2 (hoặc tự điền vào blueprint): n_samples, warmup_runs, percentile_method, bảng
    P50/P95/P99 của Presidio, NeMo input và input guard; `latency_budget_ok`; bottleneck
    nếu vượt 500ms; attacks x/20 kèm bảng các case fail; false_positive_rate; guard model IDs.
11. Trước commit cuối: quét repo tìm key (`sk-`), đảm bảo không có PII thật ngoài dữ liệu
    mẫu của lab.

### 7.3 Đầu ra phải bàn giao

| Đầu ra | Tiêu chí chất lượng |
|---|---|
| `src/phase_c_guard.py` | Không còn TODO; `test_phase_c.py` xanh; không có heuristic từ khóa refusal; `asyncio.run` không nằm trong vòng lặp |
| `guard_results.json`, khối adversarial | Đủ 20 dòng; **≥15/20 passed** (mục tiêu ≥18/20 để lấy bonus) |
| `guard_results.json`, khối clean | Đủ 8 dòng; **8/8 allowed, false_positive_rate = 0** (bắt buộc; always-block bị 0đ Task 10) |
| `guard_results.json`, khối output | 4 case: safe giữ nguyên, unsafe bị thay hoặc redact |
| `guard_results.json`, khối latency | scope `input_layers_sequential`; warmup_runs = 2; ≥20 mẫu dương; percentile linear; số đo thật, kể cả khi vượt 500ms |
| Phần guard trong blueprint | Bảng latency khớp JSON; RAG, output và full guard ghi "chưa đo" kèm kế hoạch đo |

---

## 8. Checklist cuối cùng (TV1 chạy, cả nhóm xác nhận)

- [ ] `python scripts/check_lab.py --with-tests`: không còn lỗi
- [ ] Không còn `# TODO` trong `src/phase_a_ragas.py`, `phase_b_judge.py`, `phase_c_guard.py`
- [ ] 4 file JSON trong `artifacts/` đã commit (`git check-ignore` không in gì)
- [ ] `failure_clusters.md`, `bias_report.md`, `blueprint.md`: không còn `{{`, `?` hay bảng rỗng
- [ ] `doc/TEAM.md`: tên nhóm, link repo, trưởng nhóm, deadline, commit SHA, bảng 3 thành
      viên kèm bằng chứng (link commit/PR), phần môi trường, **3 mục INDIVIDUAL do chính
      từng người viết**
- [ ] Không có `.env`, key, venv hay cache trong repo
- [ ] Repo `K4-L3-DAY24-TenNhom-Eval-Guard` truy cập được; đã mở đúng commit trên GitHub
- [ ] Đã nộp link + commit SHA qua kênh coach công bố, trước deadline

## 9. Rủi ro và phương án dự phòng

| Rủi ro | Ảnh hưởng | Phương án |
|---|---|---|
| m1–m5 bài trước không chạy, hoặc Qdrant/model chưa tải | Không có answers, Phase A = 0, Phase B thiếu A | TV1 bắt đầu sớm nhất; TV2 và TV3 hỗ trợ debug; nếu generation lỗi thì dùng `extractive_fallback` hợp lệ và ghi rõ |
| NeMo/Annoy không build được trên máy TV3 | Không có Phase C | TV3 cài sớm; dự phòng chạy Phase C trên máy TV1 hoặc TV2 (người chạy commit artifact, TEAM ghi rõ ai chạy) |
| Clean bị chặn nhầm | Mất 10đ Task 10 | Thu hẹp entity Presidio, đọc `activated_rails`, chạy lại một lần |
| κ thấp | Mất bonus +3 | Báo cáo trung thực, phân tích case lệch; không leak nhãn |
| Hết quota hoặc lỗi API giữa chừng | Report thiếu | Mỗi phase chạy một lần sau khi test offline xanh; đổi key thì cập nhật `.env`, không commit |
