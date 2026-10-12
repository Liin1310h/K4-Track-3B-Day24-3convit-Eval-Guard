# Đánh giá LLM Judge Phase B

Nhóm: {{Tên nhóm}}

Người phụ trách: Nguyễn Đức Tâm - 2A202602921

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T18:18:35.027819+00:00 (01:18 ngày 13/10/2026, UTC+7).
Models generation/judge: generation `gpt-4o-mini-2024-07-18` (`metadata.models.generation`, là nguồn
của answer A); judge `gpt-4o-mini` (`metadata.models.judge`), dùng cho cả pairwise judge (Task 5) và
binary helper `judge_binary`. Cả hai judge gọi với `temperature=0` và JSON mode.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

Cách đọc: lượt 1 gửi (A, B) theo thứ tự gốc, lượt 2 gửi (B, A). Cột lượt 2 và scores lượt 2 đã được
quy về A/B gốc. Riêng `reasoning_pass2` trong JSON giữ nguyên lời judge, nên chữ "Answer A" trong
reasoning lượt 2 chính là B gốc. Bảng tóm tắt reasoning bên dưới đã viết lại theo A/B gốc.

| id | Answer A (pipeline, độ dài) | Answer B (model_answer, độ dài) | winner_pass1 | winner_pass2 (quy về gốc) | final_winner | position_consistent | scores lượt 1 A / B | scores lượt 2 A / B |
|---|---|---|---|---|---|---|---|---|
| 1 | "Nhân viên được nghỉ 3 ngày làm việc khi kết hôn." (48) | "Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn." (57) | B | B | B | true | 0.7 / 1.0 | 0.8 / 1.0 |
| 5 | "Không tìm thấy." (15) | "Cần Giám đốc phòng ban phê duyệt." (33) | B | A | tie | false | 0.0 / 0.5 | 0.5 / 0.0 |
| 12 | "Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là 1 tháng lương." (85) | "Nhân viên được thưởng Tết tối thiểu 1 tháng lương." (50) | A | tie | tie | false | 1.0 / 0.7 | 1.0 / 1.0 |
| 21 | "Nhân viên Senior có 9 năm thâm niên sẽ được 18 ngày phép năm (15 ngày cơ bản + 3 ngày cộng thêm). Lương của nhân viên này sẽ nằm trong khoảng lương của vị trí Senior theo quy định của công ty. Không tìm thấy thông tin cụ thể về lương trong context." (248) | "Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu." (82) | B | B | B | true | 0.7 / 1.0 | 0.7 / 1.0 |
| 41 | "Nhân viên được nghỉ 15 ngày phép năm." (37) | "Nhân viên được nghỉ 12 ngày phép năm." (37) | A | A | A | true | 1.0 / 0.0 | 1.0 / 0.2 |

| id | Reasoning lượt 1 (tóm tắt) | Reasoning lượt 2 (tóm tắt, theo A/B gốc) |
|---|---|---|
| 1 | B chính xác và đầy đủ vì nêu "có lương"; A thiếu ý này. Cả hai đều súc tích. | Vẫn chọn B gốc với cùng lý do: B nêu nghỉ có lương, A thiếu. |
| 5 | B "không khớp reference nhưng có thông tin về phê duyệt" nên được 0.5; A không cung cấp thông tin nên 0.0. | Đảo ngược: B gốc sai người phê duyệt nên 0.0; A gốc (từ chối) "không sai, là phản hồi trung lập" nên 0.5. |
| 12 | A chính xác và nêu rõ điều kiện từ 6 tháng; B đúng nhưng bị trừ vì không nhắc lại điều kiện thời gian. | Cả hai chính xác, đầy đủ, khớp reference, không thừa thông tin, nên cho tie 1.0 / 1.0. |
| 21 | B nêu đủ số ngày phép và khoảng lương; A không có khoảng lương cụ thể. | Giống lượt 1: B gốc đủ cả phép và lương, A gốc thiếu khoảng lương. |
| 41 | A đúng theo chính sách v2024 (15 ngày); B dựa trên chính sách đã bị thay thế. | Giống lượt 1: A gốc theo v2024, B gốc theo v2023 cũ. |

Position bias count/rate: 2/5 cặp không nhất quán (ids 5 và 12), rate = 0.4.
Verbosity win rate: 0.333 (1/3); decisive cases: 3 (ids 1, 21, 41), với `a_wins_a_longer` = 0 và
`b_wins_b_longer` = 1.

**Hai case không nhất quán.** Cả hai đều là cặp mà hai answer có chất lượng gần nhau:

- **Id 5, cả hai answer đều không đạt.** A từ chối, còn B nêu sai người phê duyệt: reference yêu
  cầu Tổng Giám đốc (CEO) vì 55 triệu vượt ngưỡng 50 triệu. Ở cả hai lượt, judge chọn answer đứng ở
  vị trí thứ hai, và lý do đổi theo vị trí. Lượt 1 coi "có thông tin" tốt hơn từ chối. Lượt 2 coi
  "không sai" tốt hơn trả lời sai. Đây là dấu hiệu position bias khi judge phải chọn giữa hai answer
  cùng kém. Kết quả cuối là tie, hợp lý vì không answer nào đúng. Prompt hiện chưa quy định nên xếp
  "từ chối" và "trả lời sai sự kiện chính" thế nào. Với tài liệu chính sách, trả lời sai người phê
  duyệt có hại hơn từ chối.
- **Id 12, cả hai answer đều đúng** (tối thiểu 1 tháng lương). Lượt 1 chọn A, answer đứng trước và
  dài hơn vì nhắc lại câu hỏi. Judge trừ điểm B vì "không nêu điều kiện 6 tháng", dù điều kiện này đã
  có sẵn trong câu hỏi. Lượt 2 cho tie 1.0 / 1.0. Lượt 1 có dấu hiệu ưu tiên answer đứng trước và
  lặp lại câu hỏi. Swap-and-average đã trung hòa case này thành tie, khớp với nhận xét của human cho
  B: "Đúng và súc tích".

**Ba case nhất quán (1, 21, 41).** Cả ba đều có khác biệt nội dung rõ ràng: thiếu ý "có lương", thiếu
khoảng lương, hoặc dùng phiên bản v2023 đã hết hiệu lực. Judge giữ cùng winner ở cả hai lượt, và lý
do bám vào reference.

**Verbosity.** Chỉ có 1/3 case decisive mà answer thắng dài hơn, là id 1. Phần dài thêm ở đây ("có
lương") chính là một ý có trong reference, nên B thắng vì đầy đủ hơn chứ không phải vì dài hơn. Ở id
21, answer ngắn hơn lại thắng: A dài 248 ký tự nhưng thiếu khoảng lương. Ở id 41, hai answer dài bằng
nhau. Vậy các case decisive không cho thấy verbosity bias. Dấu hiệu duy nhất liên quan đến độ dài nằm
ở lượt 1 của id 12, và đã bị swap loại.

**Kết luận.** Tỷ lệ 40% không nhất quán là dấu hiệu thống kê trên 5 cặp. Đọc nội dung cho thấy các
case không nhất quán xuất hiện khi hai answer gần bằng nhau (cùng sai hoặc cùng đúng), không xuất hiện
ở case có khác biệt rõ. Dữ liệu chưa đủ để kết luận nguyên nhân. Cần tiếp tục dùng swap-and-average và
coi tie là "không phân định được".

**Self-preference.** Answer A do gpt-4o-mini sinh, và judge cũng là gpt-4o-mini. Kết quả cuối: A thắng
1/5 (id 41), B thắng 2/5, tie 2/5. Mẫu này không cho thấy judge ưu tiên answer do cùng model sinh ra,
nhưng 5 cặp quá ít để loại trừ khả năng đó.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| # | question_id | model_answer gốc | Judge label | Reasoning của judge (tóm tắt) | human_label | Agree |
|---|---|---|---|---|---|---|
| 1 | 1 | "Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn." | 1 | Đúng theo reference về số ngày nghỉ. | 1 | có |
| 2 | 5 | "Cần Giám đốc phòng ban phê duyệt." | 0 | Sai: cần Tổng Giám đốc phê duyệt, không phải Giám đốc phòng ban. | 0 | có |
| 3 | 12 | "Nhân viên được thưởng Tết tối thiểu 1 tháng lương." | 1 | Đúng mức thưởng cho nhân viên chính thức từ 6 tháng. | 1 | có |
| 4 | 21 | "Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu." | 1 | Đúng cả số ngày phép và khoảng lương Senior. | 1 | có |
| 5 | 23 | "Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết." | 1 | Đúng số tiền hoàn trả và lý do nghỉ trước hạn cam kết. | 1 | có |
| 6 | 29 | "Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu." | 0 | Thiếu Kế toán trưởng; phạt quá hạn 15 ngày phải là 80.000 VNĐ. | 0 | có |
| 7 | 33 | "Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng." | 1 | Đúng số ngày phép và tổng phụ cấp. | 1 | có |
| 8 | 41 | "Nhân viên được nghỉ 12 ngày phép năm." | 0 | Sai vì dùng chính sách cũ v2023 thay vì v2024 (15 ngày). | 0 | có |
| 9 | 46 | "Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần." | 1 | Đúng phủ định và hành động thay thế (nghỉ không lương). | 1 | có |
| 10 | 50 | "Được, miễn là đảm bảo kết nối an toàn." | 0 | Sai vì chính sách cấm VPN cá nhân. | 0 | có |

Cohen’s κ: 1.0.

Observed/chance agreement và diễn giải:

- Observed agreement p_o = 10/10 = 1.0.
- Judge có 6 nhãn 1 và 4 nhãn 0; human cũng có 6 nhãn 1 và 4 nhãn 0.
- Chance agreement p_e = 0.6 × 0.6 + 0.4 × 0.4 = 0.36 + 0.16 = 0.52.
- κ = (p_o − p_e) / (1 − p_e) = (1.0 − 0.52) / (1 − 0.52) = 1.0. Theo thang Landis–Koch đây là mức
  "almost perfect", và cao hơn ngưỡng 0.6 của bonus Phase B.

κ = 1 nghĩa là nhãn 0/1 của judge khớp hoàn toàn với human trên 10 câu này. Cả bốn câu nhãn 0 đều có
lỗi rõ ràng mà judge bắt được: sai người phê duyệt (5), thiếu Kế toán trưởng và tính phạt sai (29),
dùng phiên bản v2023 (41), cho phép VPN cá nhân (50). Hai bẫy adversarial là phủ định (46) và
policy contradiction (50) cũng được chấm đúng.

Nhãn đúng không có nghĩa là reasoning đúng. Ở id 1, reasoning khen answer "đầy đủ ... điều kiện không
trừ vào phép năm", nhưng model_answer không nhắc ý này; ý đó chỉ có trong reference. Ở id 12, reasoning
nói answer "nêu rõ điều kiện" 6 tháng, trong khi answer không nêu điều kiện nào. Ở id 46, reasoning
nói answer "không bỏ qua điều kiện cần sự phê duyệt của trưởng phòng", trong khi answer cũng không có
ý này. Vậy κ chỉ đo mức đồng thuận về nhãn, không chứng minh lập luận của judge chính xác.

Nhãn binary khớp với kết quả pairwise ở 5 id chung, vì B của pairwise chính là các model_answer này.
B nhãn 1 thì thắng (ids 1, 21) hoặc hòa với một A cũng đúng (id 12). B nhãn 0 thì thua (id 41) hoặc
hòa với một A cũng không đạt (id 5).

## Giới hạn và cách dùng judge

- **Một model, một prompt, một lần chạy.** Judge chỉ dùng gpt-4o-mini, `temperature=0`, chạy một lần.
  Chưa đo độ dao động giữa các lần chạy hay giữa các model.
- **Mẫu nhỏ.** Chỉ có 5 cặp và 10 nhãn. Với 10 nhãn, chỉ cần một nhãn lệch là κ giảm còn khoảng
  0.78–0.80 (judge đổi một nhãn 0→1 cho κ ≈ 0.78; đổi một nhãn 1→0 cho κ = 0.8). Vì vậy κ = 1.0 chưa
  đủ để kết luận judge luôn đồng thuận với người.
- **Bộ 10 câu human chủ yếu có lỗi rõ ràng.** Chưa có case khó như đúng một phần, làm tròn số, hay
  phủ định nhiều tầng. κ trên các case này có thể thấp hơn.
- **Judge và generator cùng họ gpt-4o-mini**, nên có nguy cơ self-preference. Mẫu này không thấy dấu
  hiệu (A chỉ thắng 1/5) nhưng chưa thể loại trừ. Cách kiểm chứng: chạy lại 10 nhãn và 5 cặp với một
  judge khác họ (ví dụ Claude Sonnet 5.5), rồi so κ và tỷ lệ A thắng.
- **Prompt pairwise chưa quy định cách xếp "từ chối" và "trả lời sai"** (id 5). Cách kiểm chứng: thêm
  quy tắc "answer sai sự kiện chính kém hơn answer từ chối", chạy lại 5 cặp, rồi xem id 5 có thành
  nhất quán không và κ trên 10 nhãn có giữ được ≥ 0.8 không.
- **Reasoning có thể gán cho answer những ý chỉ có trong reference** (ids 1, 12, 46). Khi review, phải
  đối chiếu trực tiếp với answer, không lấy reasoning làm bằng chứng.
- **Cách dùng đề xuất:** dùng judge làm tín hiệu sàng lọc và regression, luôn chạy hai lượt có swap.
  Case tie hoặc không nhất quán chuyển cho người review. Calibrate lại với nhãn người mỗi khi đổi model
  hoặc prompt. Không xem judge là đáp án tuyệt đối.
