# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok (`judge_tone_public.csv`) | 100 | 0.757 | 0.857 | 0.800 | Có (`tp=24, fp=4, fn=6, tn=66`; fail obs `0.28` → RG `0.30`) | dùng (đã đạt ngưỡng, cần hiệu chỉnh RG & siết rubric) |
| helpful (`judge_helpful_public.csv`) | 100 | 0.375 | 1.000 | 0.300 | Không — `κ < 0.6` và `R < 0.7` (`tp=9, fp=0, fn=21, tn=70`; fail obs `0.09` → RG `0.30`) | **loại** (cấm dùng làm gate) |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú (lỗi & hành động sửa rubric) |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`): `"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."` | PASS | FAIL | Người đúng | Xưng `"em"` + `"nha"` quá suồng sã; judge nhầm là thân thiện. **Sửa rubric `tone_ok`:** thêm rule FAIL nếu dùng khẩu ngữ/xưng hô không chuẩn CSKH (`em/anh/nha/bạn`), bắt buộc dùng `"LogiX"` – `"anh/chị"`. |
| 2 | `H-029` (`tone_ok`): `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` | PASS | FAIL | Người đúng | Giọng ra lệnh (`"không cần nhắn thêm"`); judge chỉ nhìn từ `"Dạ, vui lòng"`. **Sửa rubric `tone_ok`:** thêm few-shot ví dụ câu có `"Dạ"` nhưng đuôi đuổi khách/ra lệnh phải chấm FAIL. |
| 3 | `H-042` (`tone_ok`): `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` | FAIL | PASS | Người đúng | Câu ngắn gọn, lịch sự, đủ thông tin; judge phạt nhầm vì thiếu lời xin lỗi. **Sửa rubric `tone_ok`:** nêu rõ KHÔNG bắt buộc xin lỗi trong câu báo đã hoàn tiền thành công. |
| 4 | `H-051` (`tone_ok`): `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` | FAIL | PASS | Người đúng | Chính sách CS LogiX cho phép dùng từ `"refund"`; judge tự phạt vì chêm tiếng Anh. **Sửa rubric `tone_ok`:** whitelist thuật ngữ chuyên ngành được phép (`refund`, `order`, `claim`). |
| 5 | `H-063` (`tone_ok`): `"Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ."` | PASS | FAIL | Người đúng | Hứa `"sẽ hoàn thêm"` ngoài kết quả hệ thống; judge bỏ sót. **Sửa rubric `tone_ok`:** thêm điều kiện FAIL khi cam kết/hứa hẹn chi trả ngoài dữ liệu xác nhận. |
| 6 | `H-070` (`tone_ok`): `"Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂"` | PASS | FAIL | Người đúng | Dùng emoji cười trong ngữ cảnh khiếu nại. **Sửa rubric `tone_ok`:** cấm emoji/icon trong phản hồi khiếu nại & tài chính. |
| 7 | `H-081` (`tone_ok`): `"Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ."` | FAIL | PASS | Judge đúng | Nhãn người sai do đọc nhầm ticket (lưu ý ở tập gốc). **Hành động:** sửa nhãn ground truth trong tập calibration (double-annotation các ca tranh chấp). |
| 8 | `H-088` (`tone_ok`): `"Dạ, dạ, LogiX đã hoàn 40.000đ cho đơn O-233 ạ."` | FAIL | PASS | Biên (cần chốt rubric) | Lỗi lặp chữ nhỏ (`"Dạ, dạ"`): người bỏ qua, judge phạt. **Sửa rubric `tone_ok`:** quy định rõ lỗi lặp từ/gõ nhẹ có tính FAIL hay chỉ warning, kèm ví dụ minh họa. |
| 9 | `H-094` (`tone_ok`): `"Da, LogiX da hoan 40.000đ cho don O-341, xin loi vi su bat tien."` | PASS | FAIL | Người đúng | Mất dấu tiếng Việt như dịch máy; judge bỏ qua. **Sửa rubric `tone_ok`:** bắt buộc tiếng Việt có dấu chuẩn, hoặc bắt thêm bằng rule code/regex kiểm dấu. |
| 10 | `HL-015` & `HL-016` (`helpful`): `"Dạ, LogiX thành thật xin lỗi ... LogiX đã hoàn 55.000đ..."` (ledger ghi `40.000đ` / `35.000đ`) | PASS | FAIL | Người đúng | **18/21 ca FN của `helpful` đều là sai tiền** so với `refund_ledger` (nhiều ca xin lỗi dài dòng khiến judge dính *verbosity/apology bias*), cộng thêm **3/21 ca FN sai xưng hô** (`HL-047`, `HL-091`, `HL-097`). **Hành động:** loại bỏ tiêu chí tiền khỏi LLM judge; chuyển sang **code grader** đối chiếu `reply` với `refund_ledger` (M3). |

## Kết luận
- **Tiêu chí bị loại và lý do (`helpful`):** `judge_helpful` **không được dùng làm gate** vì đạt `κ = 0.375 < 0.6` và `Recall = 0.300 < 0.7` trên `n = 100`. Ma trận nhầm lẫn `{tp: 9, fp: 0, fn: 21, tn: 70}` cho thấy dù `Precision = 1.000` và tỉ lệ lỗi quan sát chỉ là `0.09` (9%), judge đã bỏ sót tới **21/30 (70%)** các ca `FAIL` thực sự (tỉ lệ lỗi hiệu chỉnh theo Rogan-Gladen lên tới `0.30` = 30%). Phân tích 21 ca `FN` cho thấy 18 ca là **nói sai số tiền hoàn so với ledger** (judge chỉ đọc text không thấy DB và bị thiên lệch bởi lời xin lỗi dài dòng ở các ca như `HL-016`, `HL-028`, `HL-035`, `HL-041`), và 3 ca là sai xưng hô (`Ok bạn...`). Nếu dùng `judge_helpful` làm gate sẽ tạo cảm giác an toàn giả và cho lọt lỗi sai tiền nghiêm trọng — đúng nguyên tắc của lab, tính đúng của tiền phải chấm bằng **code** (sẽ làm ở M3 cho FM-08), không dùng LLM judge.
- **Tiêu chí được giữ (`tone_ok`):** Đạt toàn bộ ngưỡng FLOORS (`κ = 0.757 ≥ 0.6`, `P = 0.857 ≥ 0.8`, `R = 0.800 ≥ 0.7`, `{tp: 24, fp: 4, fn: 6, tn: 66}`), có thể dùng để đánh giá giọng văn kèm hiệu chỉnh Rogan-Gladen (`0.28 → 0.30`) sau khi cập nhật rubric như bảng audit trên (cấm xưng hô suồng sã/emoji/mất dấu/hứa ngoài hệ thống, không phạt thiếu xin lỗi hay từ `refund`, và sửa lại nhãn người sai ở `H-081`).
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.
