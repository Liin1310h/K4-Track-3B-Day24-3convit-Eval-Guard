# Phân tích lỗi Phase A

Nhóm: {{Tên nhóm}}

Người phụ trách: Phạm Thị Thùy Linh - 2A202602909

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T15:59:34.641344+00:00.
Generation mode/fallback và điều kiện chạy: cả 50 answers sinh bằng LLM (`generation_mode=llm`),
không có extractive fallback. Pipeline: chunk phân cấp (child 256 ký tự, không overlap) → m5 enrichment
(gpt-4o-mini thêm câu mô tả đầu mỗi chunk) → hybrid BM25 + BGE-M3 trên Qdrant 1.9.7 → rerank
bge-reranker-v2-m3, top 3 contexts. Prompt sinh câu trả lời yêu cầu "chỉ trả lời dựa trên context, nếu không có thì
nói 'Không tìm thấy.'". Hai PDF dạng ảnh scan (BCTC, Nghị định 13) bị bỏ qua vì không có lớp text.
Models generation/evaluator: generation = gpt-4o-mini-2024-07-18;
evaluator (từ m4) = gpt-4o-mini, text-embedding-3-small.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.875 | 0.425 | 0.550 |
| answer_relevancy | 0.443 | 0.381 | 0.370 |
| context_precision | 0.983 | 0.942 | 0.908 |
| context_recall | 0.825 | 0.746 | 0.683 |
| avg_score | 0.782 | 0.623 | 0.628 |

Trung bình toàn bộ 50 câu: faithfulness 0.630, avg_score 0.688. `context_precision` cao ở cả ba nhóm
(0.91-0.98) nên retrieval hiếm khi kéo về chunk rác; điểm thấp tập trung ở `faithfulness` và `answer_relevancy`.

## Bottom 10 và nguyên nhân

Bảng dưới là đúng 10 dòng từ Task 3 trong JSON (cột diagnosis/suggested_fix giữ nguyên chữ của exporter,
được sinh theo từng câu từ điểm, contexts và answer). Phần "Đối chiếu" bên dưới sửa lại những chỗ diagnosis tự động chưa đúng.

| Rank | ID | Distribution | avg_score | worst_metric | Question | Diagnosis | Suggested fix |
|---|---|---|---|---|---|---|---|
| 1 | 40 | multi_hop | 0.000 | faithfulness | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=0.00, context_recall=0.00): answer từ chối ('Không tìm thấy') dù có reference; contexts chỉ chứa 21% từ khóa của ground truth → lỗi retrieval | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; bổ sung BM25/HyQA cho thuật ngữ trong câu hỏi, tăng HYBRID/RERANK top_k; tách câu hỏi multi-hop thành sub-queries và gộp contexts |
| 2 | 39 | multi_hop | 0.250 | faithfulness | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=1.00, context_recall=0.00): answer từ chối ('Không tìm thấy') dù có reference; contexts đã chứa 79% từ khóa ground truth → lỗi ở bước generation; contexts trộn nhiều phiên bản (2022, 2024, v2.0) → nguy cơ version conflict | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank; tách câu hỏi multi-hop thành sub-queries và gộp contexts |
| 3 | 5 | factual | 0.250 | faithfulness | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=1.00, context_recall=0.00): answer từ chối ('Không tìm thấy') dù có reference; contexts chỉ chứa 43% từ khóa của ground truth → lỗi retrieval | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; bổ sung BM25/HyQA cho thuật ngữ trong câu hỏi, tăng HYBRID/RERANK top_k |
| 4 | 46 | adversarial | 0.375 | faithfulness | Nhân viên thử việc có được nghỉ phép năm không? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=0.83, context_recall=0.67): answer từ chối ('Không tìm thấy') dù có reference; contexts đã chứa 81% từ khóa ground truth → lỗi ở bước generation; contexts trộn nhiều phiên bản (2023) → nguy cơ version conflict | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank |
| 5 | 33 | multi_hop | 0.375 | faithfulness | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=1.00, context_recall=0.50): answer từ chối ('Không tìm thấy') dù có reference; contexts đã chứa 61% từ khóa ground truth → lỗi ở bước generation; contexts trộn nhiều phiên bản (2023, 2024) → nguy cơ version conflict | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank; tách câu hỏi multi-hop thành sub-queries và gộp contexts |
| 6 | 44 | adversarial | 0.396 | faithfulness | Bao lâu phải đổi mật khẩu một lần? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=0.58, context_recall=1.00): answer từ chối ('Không tìm thấy') dù có reference; contexts đã chứa 73% từ khóa ground truth → lỗi ở bước generation; contexts trộn nhiều phiên bản (2024, v2.0) → nguy cơ version conflict | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank |
| 7 | 48 | adversarial | 0.417 | faithfulness | Nhân viên thử việc có được hưởng bảo hiểm sức khỏe PVI không? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=1.00, context_recall=0.67): answer từ chối ('Không tìm thấy') dù có reference; contexts đã chứa 62% từ khóa ground truth → lỗi ở bước generation; contexts trộn nhiều phiên bản (2024) → nguy cơ version conflict | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank |
| 8 | 50 | adversarial | 0.417 | faithfulness | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | LLM hallucinating (faithfulness=0.00, answer_relevancy=-0.00, context_precision=1.00, context_recall=0.67): answer từ chối ('Không tìm thấy') dù có reference; contexts đã chứa 65% từ khóa ground truth → lỗi ở bước generation; contexts trộn nhiều phiên bản (2024) → nguy cơ version conflict | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank |
| 9 | 31 | multi_hop | 0.497 | faithfulness | Nhân viên đi công tác trong nước, ở khách sạn 2 đêm với giá 1.500.000 VNĐ/đêm. Công ty thanh toán tối đa bao nhiêu cho tiền khách sạn? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.49, context_precision=0.83, context_recall=0.67): contexts đã chứa 67% từ khóa ground truth → lỗi ở bước generation | prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; tách câu hỏi multi-hop thành sub-queries và gộp contexts |
| 10 | 9 | factual | 0.500 | faithfulness | Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? | LLM hallucinating (faithfulness=0.00, answer_relevancy=0.00, context_precision=1.00, context_recall=1.00): answer từ chối ('Không tìm thấy') dù có reference; contexts đã chứa 100% từ khóa ground truth → lỗi ở bước generation; contexts trộn nhiều phiên bản (2023, 2024) → nguy cơ version conflict | tăng recall (top_k rerank 3→5, query rewriting) trước khi cho phép từ chối; prompt bắt buộc trích dẫn đúng số liệu/điều kiện trong context, temperature=0; gắn metadata version/effective_date cho chunk, ưu tiên bản mới nhất khi rerank |

**Phát hiện chính: 9/10 câu bottom có answer là "Không tìm thấy."** Toàn bộ 50 câu có 12 câu bị từ chối
(factual 3, multi_hop 5, adversarial 4). Điểm trung bình của 12 câu này là 0.389, so với 0.782 của 38 câu còn lại.
`answer_relevancy` của câu từ chối luôn bằng 0 và `faithfulness` trung bình chỉ 0.146.

### Đối chiếu answer / contexts / reference

Mình đọc trực tiếp contexts của các câu đại diện và đối chiếu với file nguồn trong `data/`:

- **Câu 40 (multi_hop, avg 0.0) - lỗi retrieval.** Câu hỏi trộn "thử việc 90 ngày" với "vi phạm bảo mật".
  Cả 3 contexts đều nói về chính sách thử việc (bảo hiểm PVI, đánh giá thử việc, quyền lợi); không context nào chứa
  "1 giờ", "helpdesk", "9999" hay "malware". Truy vấn bị phần "thử việc" kéo đi, tài liệu `bao_mat_su_co.md` không được lấy.
  Câu trả lời "Không tìm thấy." ở đây thực ra trung thực với context, nhưng RAGAS vẫn chấm 0 mọi metric.
- **Câu 5 (factual, avg 0.25) - lỗi retrieval do cắt chunk.** Context 2 là bảng phê duyệt mua sắm trong `mua_sam.md`
  nhưng chunk con 256 ký tự dừng ở hàng "Dưới 5.000.000 VNĐ"; hàng "trên 50.000.000 VNĐ → CEO" không có trong contexts nào.
  Đúng tài liệu, sai ranh giới chunk.
- **Câu 9 (factual, avg 0.5) - diagnosis tự động sai.** Exporter báo "contexts chứa 100% từ khóa → lỗi generation", và
  RAGAS cũng cho `context_recall` = 1.0. Kiểm tra thủ công thì dòng "Sinh con (nam giới): 5 ngày làm việc liên tục"
  (có trong `nghi_phep_dac_biet.md`, dòng 8) **không xuất hiện** trong 3 contexts; các token "5", "ngày" chỉ khớp ngẫu nhiên.
  Đây cũng là lỗi retrieval/chunking, và là bằng chứng `context_recall` của RAGAS (gpt-4o-mini) có thể chấm quá tay.
- **Câu 31 (multi_hop, avg 0.497) - câu trả lời đúng nhưng faithfulness = 0.** Answer "2.400.000 VNĐ (1.200.000 x 2 đêm)"
  khớp ground truth, và context 0 có đúng dòng "Khách sạn: tối đa 1.200.000 VNĐ/đêm". RAGAS vẫn chấm `faithfulness` 0.0
  vì phép nhân 2 đêm không nằm nguyên văn trong context. Đây là hạn chế của evaluator với câu cần tính toán, không phải
  hallucination thật; nhãn "LLM hallucinating" của cây chẩn đoán cho dòng này nên đọc là "claim suy luận không được verify".
- **Câu 46 và 48 (adversarial, phủ định) - bẫy phủ định.** Ground truth là "KHÔNG" (thử việc không có phép năm, chưa hưởng PVI).
  Tài liệu thử việc có câu "Nhân viên thử việc **KHÔNG được ng|hỉ phép năm**" và ranh giới chunk rơi đúng giữa chữ "ng" và "hỉ"
  (contexts của câu 40 kết thúc ở "KHÔNG được ng", context của câu 46 bắt đầu bằng "hỉ phép năm**"). Nhiều khả năng mô hình không
  thấy khẳng định phủ định liền mạch nên chọn từ chối thay vì suy ra "không"; mình chưa kiểm chứng bằng cách chạy lại với chunk khác.
- **Câu 50 (adversarial, VPN cá nhân) - lỗi generation.** Context 0 chứa nguyên văn "Không sử dụng VPN cá nhân (NordVPN, ExpressVPN)
  trong mạng công ty", tức đủ để trả lời "KHÔNG", vậy mà pipeline vẫn trả "Không tìm thấy." Prompt từ chối quá cứng: câu hỏi nêu
  Manager và WFH mà context không nhắc hai điều này nên mô hình từ chối thay vì suy ra.
- **Câu 44 (adversarial, đổi mật khẩu) - bẫy phiên bản, retrieval chỉ lấy bản cũ.** Contexts gồm chính sách mật khẩu v1.0 ("mỗi 90 ngày")
  và ghi chú "đã được thay thế bởi Chính sách mật khẩu v2.0 từ ngày 01/07/2024"; chunk của v2.0 (120 ngày) không được lấy. Việc không trả
  "90 ngày" là hành vi an toàn đúng hướng (tránh đưa ra quy định hết hiệu lực), nhưng lý do là thiếu bản hiện hành, không phải do mô hình
  chủ động chọn bản mới nhất.
- **Câu 49 (adversarial, hỏi rõ về v2023) - làm đúng.** Contexts lấy được cả v2023 ("12 ngày") lẫn v2024 ("15 ngày, tăng từ 12 ngày");
  answer trả "12 ngày" theo bản cũ và nhắc bản 2024 đang hiệu lực.

**Kết luận về nguyên nhân (theo thứ tự ảnh hưởng):**
1. Chunking: child 256 ký tự không overlap cắt giữa bảng và danh sách; đoạn quyết định thường nằm ở chunk bên cạnh.
2. Chỉ 3 contexts sau rerank cho câu multi-hop cần ghép hai tài liệu (câu 33, 39, 40).
3. Prompt từ chối quá cứng: khi context thiếu một ý, mô hình trả "Không tìm thấy." thay vì trả lời phần có căn cứ.
4. Giới hạn của evaluator: `faithfulness` = 0 cho câu từ chối và cho phép tính; `context_recall` có thể chấm 1.0 khi thiếu ý thật (câu 9).

## Matrix và nhóm yếu nhất

Mỗi câu được đếm một lần theo worst_metric của nó (không phải tất cả đều là failure).

| worst_metric | factual | multi_hop | adversarial | Tổng |
|---|---|---|---|---|
| faithfulness | 2 | 12 | 4 | 18 |
| answer_relevancy | 16 | 8 | 3 | 27 |
| context_precision | 0 | 0 | 0 | 0 |
| context_recall | 2 | 0 | 3 | 5 |
| Tổng cột (kích thước nhóm) | 20 | 20 | 10 | 50 |

Lưu ý khi đọc matrix: 10 trong 12 câu bị từ chối có từ hai metric bằng 0 cùng lúc; hàm `min` của `RagasResult.worst_metric`
chọn metric đầu tiên theo thứ tự faithfulness → answer_relevancy → context_precision → context_recall. Vì vậy cột
`faithfulness` và `answer_relevancy` phản ánh một phần thứ tự này, không chỉ mức độ yếu của từng metric.
`context_precision` không bao giờ là worst_metric (0/50 câu).

Nhóm yếu theo mean thấp nhất: multi_hop; mean: 0.623
(factual 0.782, adversarial 0.628).
Worst metric xuất hiện nhiều nhất: answer_relevancy; số câu: 27.

Vì sao multi_hop yếu nhất: `faithfulness` chỉ 0.425 (factual 0.875). Có 5/20 câu bị từ chối; 15 câu còn lại vẫn có
`faithfulness` trung bình 0.517 vì câu trả lời ghép nhiều số liệu (cộng ngày nghỉ, cộng phụ cấp, nhân đơn giá) mà RAGAS
không verify được từng bước. Nhóm này cũng cần contexts từ hai tài liệu nhưng chỉ có 3 chunk. Khoảng cách với adversarial
rất nhỏ (0.623 so với 0.628, chênh 0.005 trên 10-20 câu) nên không nên kết luận hai nhóm khác nhau về bản chất.
Không dùng tổng 20/20/10 để chọn nhóm: đó chỉ là kích thước nhóm.

**Đề xuất sửa và cách kiểm chứng** (chưa thực hiện, vì pipeline sinh answers là phần thiết lập của lab):
1. Trả về parent chunk (2048 ký tự) thay cho child 256 ký tự khi đưa vào prompt, hoặc thêm overlap 64 ký tự cho child.
   Kiểm chứng: câu 5, 9, 46, 48 phải có câu quyết định trong contexts; `context_recall` thực (đối chiếu thủ công) tăng.
2. Tăng top_k rerank từ 3 lên 5 và tách câu multi-hop thành hai truy vấn con. Kiểm chứng: câu 33, 39, 40.
3. Nới prompt: "nếu context chỉ trả lời được một phần, hãy trả lời phần đó và nêu phần còn thiếu". Kiểm chứng: số câu từ chối
   giảm từ 12 xuống; cần theo dõi `faithfulness` không tụt vì bịa.
4. Gắn metadata phiên bản/ngày hiệu lực cho chunk và ưu tiên bản hiện hành (mật khẩu v2.0, nghỉ phép 2024).
Chạy lại `python scripts/setup_answers.py --live` rồi `python scripts/run_experiments.py --phase a --live`,
so sánh avg_score từng nhóm và số câu "Không tìm thấy" với bảng hiện tại.

## Bẫy adversarial và giới hạn

Adversarial mean (0.628) thấp hơn factual mean
(0.782), chênh 0.154, thỏa điều kiện bonus Phase A. Nhưng nguyên nhân chính là số câu từ chối
(4/10 câu adversarial so với 3/20 factual), không phải việc pipeline nhận ra hay trượt bẫy phiên bản.
Trong 6 câu adversarial được trả lời: câu 41 (15 ngày phép) và câu 43 (tối thiểu 12 ký tự) trả đúng theo bản hiện hành
v2024 và v2.0; câu 49 hỏi rõ về v2023, pipeline trả "12 ngày" cho bản cũ và còn nhắc bản 2024, cho thấy retrieval lấy được cả hai
phiên bản. Ngược lại câu 44 chỉ lấy được bản mật khẩu cũ rồi từ chối, và các bẫy phủ định/mâu thuẫn chính sách (46, 48, 50) bị từ chối
thay vì trả "KHÔNG". Điểm thấp hơn không tự chứng minh pipeline nhận ra version conflict.

Lưu ý về diagnosis tự động: ghi chú "contexts trộn nhiều phiên bản" của Task 3 là heuristic dò chuỗi (`v1.0`, `2024`...),
có dòng chỉ thấy một năm (ví dụ "2024") nhưng vẫn gắn nhãn cho nhóm adversarial; đọc ghi chú đó như gợi ý, không phải bằng chứng.

Giới hạn: chỉ 50 câu (10 adversarial) nên chênh lệch vài phần trăm không có ý nghĩa thống kê; một lần chạy RAGAS (không lặp, LLM judge
có nhiễu); một model đánh giá (gpt-4o-mini) vừa là model sinh nên có thể thiên vị; không có fallback extractive; hai PDF scan chưa OCR
nên mọi câu hỏi cần BCTC hoặc Nghị định 13 sẽ không thể trả lời từ corpus.
