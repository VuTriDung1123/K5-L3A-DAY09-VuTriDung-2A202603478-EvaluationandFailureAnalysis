# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, report `E-seeded_regression-20261117-1167` (trace `R-seeded_regression-C-002-s11`) |
| Triệu chứng | `lab8.metrics.trial_pass` fail (`status resolved != denied`); ledger ghi `refund_vnd=20000`, `refund_count=1` và reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`, trong khi nhãn chuẩn là `status=denied`, `refund_vnd=0`. |
| Bước sai đầu tiên | Bước `3` (`model_override`): `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Bước `1` (`handoff`) sanitize `facts: {}` đúng và bước `2` (`investigator`) trả về đúng DB `O-202` với `delay_days=2` (< 3 ngày theo `SHIP-LATE-03`). Chỉ tới bước `3`, agent mới lấy số `5 ngày` trong `ticket` ghi đè fact của DB, làm bước `4` (`quote`) tính sai `20000`. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên `fixed C-002@11` (`R-fixed-C-002-s11`): hoàn toàn không có event `model_override`; bước `3` (`quote`) giữ nguyên `delay_days=2` từ DB nên trả `amount_vnd=0, reason="no_entitlement"`, bước `4` (`reply`) báo chưa đủ điều kiện, ledger `refund_vnd=0`, `lab8 grader: PASS (ok)`. |
| Regression test | `test_trace_case_c002_s11_ticket_trust_regression` trong [test_lab9_trace_case.py](file:///d:/VINUNI/Labs/Day9/K5-L3A-DAY09-VuTriDung-2A202603478-EvaluationandFailureAnalysis/src/tests/test_lab9_trace_case.py): kiểm tra `DbFactKept`, `RefundAmountCorrect`, `TrialPass` đều `False` trên `seeded_regression C-002@11` và đều `True` trên `fixed C-002@11` (đã chạy `pytest` và thấy fail đúng trên variant lỗi, pass trên `fixed`). |
| Chưa chắc chắn | Trên MockLLM ta biết chắc ghi đè do nhánh `ticket_trust` trong `variant_agent.py`; trên LLM thật, trace mới chỉ chứng minh bước 3 đã ghi đè `delay_days=5`, chưa tự chứng minh nguyên nhân gốc là system prompt yếu hay parser trích nhầm từ ticket nếu không xem thêm prompt thô. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
