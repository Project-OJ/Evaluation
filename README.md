# Evaluation

## 環境設置
```
pip install requirements.txt
```
也可以手動下在缺少的 package

## problem history 格式

每個 user 的答題例使已經依照**AC 的時間**排好了

```
{
  uid (string):
  {
    pid (string):
    {
      "AC": (bool)
      "attempt_cnt": (int)
      "solved_time": (int)
    }
  }
}
```

## 範例程式
請見 RandomRS.py

其中 RSEvaluator 所需要的參數 rs 是一個 class 的 instance
rs 需要有一個名叫 "getRecom(self, sim_ph)" 的 method
該 method 會接收一個 problem history 的 dict 來給 rs 去產生推薦題目

## 模擬推薦的原始碼
請見 RSEvaluator.py
