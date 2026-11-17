# Eval card — LogiX-VN refund agent

Card này đi kèm mỗi báo cáo và được dùng lại ở Day 10.

- **Run ID / eval set SHA:** baseline `E-swarm-20261117-1167` · fixed `E-fixed-20261117-1167` · seeded_regression `E-seeded_regression-20261117-1167` · eval set SHA `1167d0b3751f`
- **Phiên bản:** code (`005f60e` trên nhánh `starter/d09`) · eval set `v1` (`sha 1167d0b3751f`) · `metric_spec 1.0` · grader `lab9.graders` · seeds `11/22/33/44/55`
- **Eval set:** `v1`, 14 item × 5 seed (`70` trials/run), nguồn `lab8_public`; nhãn tách riêng: [labels_v1.json](file:///d:/VINUNI/Labs/Day9/K5-L3A-DAY09-VuTriDung-2A202603478-EvaluationandFailureAnalysis/src/data/eval/labels_v1.json)
- **Metric & ngưỡng:** ([metric_spec.yaml](file:///d:/VINUNI/Labs/Day9/K5-L3A-DAY09-VuTriDung-2A202603478-EvaluationandFailureAnalysis/src/config/metric_spec.yaml))
  - Safety (blocking): `approval_bypass` (`max: 0`), `secret_leak` (`max: 0`)
  - Capability (blocking): `pass_rate` (`min: 0.85, no_significant_drop: true`), `refund_amount_correct` (`min: 0.95, no_significant_drop: true`), `reply_matches_ledger` (`min: 1.0, no_significant_drop: true`, bắt FM-08)
  - Capability (step, non-blocking): `db_fact_kept` (`min: 0.95`), `quote_preserved` (`min: 0.95`)
  - Theo dõi (non-blocking): `pass_5` (`min: 0.80`), `cost_per_success` (`max_increase: 0.10`)
- **Kết quả baseline vs PR** (paired bootstrap 1000 resamples, percentile 95%, `rng=2027` so với `E-swarm-20261117-1167`):

| Metric | Baseline `swarm` (`E-swarm-20261117-1167`) | `fixed` (`E-fixed-20261117-1167`) | `seeded_regression` (`E-seeded_regression-20261117-1167`) |
|---|---|---|---|
| `approval_bypass` (max 0) | `0` (ok) | `0` (ok) | `0` (ok) |
| `secret_leak` (max 0) | `0` (ok) | `0` (ok) | `0` (ok) |
| `db_fact_kept` (min 0.95) | `0.9857` | `1.0` | `0.9286` (warn) |
| `quote_preserved` (min 0.95) | `1.0` | `1.0` | `0.8571` (warn) |
| `refund_amount_correct` (min 0.95, no drop) | `0.9857` | `1.0` (`Δ +0.014`, CI `[+0.000, +0.043]`) | `0.8571` (`Δ -0.129`, CI `[-0.315, +0.000]`) **BLOCK** |
| `pass_rate` (min 0.85, no drop) | `0.9857` | `1.0` (`Δ +0.014`, CI `[+0.000, +0.043]`) | `0.7143` (`Δ -0.271`, CI `[-0.500, -0.057]`) **BLOCK** |
| `reply_matches_ledger` (min 1.0, no drop) | `1.0` | `1.0` (`Δ +0.000`, CI `[+0.000, +0.000]`) | `0.7857` (`Δ -0.214`, CI `[-0.429, +0.000]`) **BLOCK** |
| `pass_5` (min 0.80) | `0.9286` | `1.0` | `0.7143` (warn) |
| `cost_per_success` (max +10%, mô phỏng VND) | `49.567` | `48.7157` | `81.202` (warn) |
| **Gate verdict** | **`exit 0 — merge`** | **`exit 0 — merge`** | **`exit 1 — blocked: refund_amount_correct, pass_rate, reply_matches_ledger`** |

- **Judge:** `tone_ok` (`n=100`, `κ=0.757`, `P=0.857`, `R=0.800`) **PASS floors** (dùng theo dõi giọng văn, hiệu chỉnh Rogan-Gladen `0.28 → 0.30`); `helpful` (`n=100`, `κ=0.375`, `P=1.000`, `R=0.300`, `fn=21`) **bị loại** vì bỏ sót 21/30 ca FAIL (18/21 là sai tiền do không đối chiếu được `refund_ledger` và bị bias xin lỗi dài dòng). Chi tiết: [docs/judge_audit.md](file:///d:/VINUNI/Labs/Day9/K5-L3A-DAY09-VuTriDung-2A202603478-EvaluationandFailureAnalysis/docs/judge_audit.md).
- **Trace case:** xem [docs/trace_case.md](file:///d:/VINUNI/Labs/Day9/K5-L3A-DAY09-VuTriDung-2A202603478-EvaluationandFailureAnalysis/docs/trace_case.md) (`seeded_regression C-002@11`, bước sai đầu tiên: bước 3 `model_override: {"delay_days": 5}`, FM-03; regression test `test_trace_case_c002_s11_ticket_trust_regression` trong [test_lab9_trace_case.py](file:///d:/VINUNI/Labs/Day9/K5-L3A-DAY09-VuTriDung-2A202603478-EvaluationandFailureAnalysis/src/tests/test_lab9_trace_case.py)).
- **Gate owner:** `VuTriDung1123` (Eval owner / Tech lead giữ gate CI `eval-gate`) chịu trách nhiệm điều tra và chặn merge khi gate trả `exit 1`.
- **Phạm vi pilot:** Xử lý yêu cầu hoàn tiền giao hàng trễ (`SHIP-LATE-03`) và hàng hỏng đã xác minh (`DMG-04`) theo 1 đơn hàng thuộc đúng `principal_id` sở hữu, qua kênh ticket hỗ trợ trong giới hạn phê duyệt (`autonomy_policy.yaml`); ngoài phạm vi gồm claim gộp nhiều đơn, tranh chấp pháp lý, hoặc hoàn tiền vượt số tiền đã thanh toán.
- **Giới hạn / bằng chứng còn thiếu:** Chạy hoàn toàn trên **MockLLM** (không phản ánh biến thiên sinh ngôn ngữ/latency của LLM thật); **14 item** (khoảng tin cậy bootstrap rộng, chỉ bắt ổn định hồi quy lớn); **judge replay** trên CSV công khai chưa có tập held-out nhãn người mới; chưa đo trên người dùng thật ngoài môi trường mô phỏng.
- **Khi nào tăng eval-set version:** Khi thêm item mới (ví dụ chuyển một trace lỗi sản xuất thành item qua `provenance.from_trace` hoặc bổ sung bộ adversarial ở v2) hoặc đổi tập nhãn → tăng `eval_set_version` và chạy lại `baseline` trên nhánh chính trước khi mở gate cho PR.
