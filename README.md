# Evaluation

## 環境設置
```
pip install requirements.txt
```
也可以手動下載缺少的 package

## problem history 格式

請見：50_phistory.json、100_phistory.json </br>
每個 user 的答題例使已經依照 **AC 的時間**排好了

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

其中 RSEvaluator 所需要的參數 rs 是一個 class 的 instance </br>
rs 需要有一個名叫 "getRankList(self, sim_ph)" 的 method </br>
該 method 會接收一個 problem history 的 dict 來給 rs 去產生推薦題目的排名（list[pid]）

## 模擬推薦的原始碼
請見 RSEvaluator.py
