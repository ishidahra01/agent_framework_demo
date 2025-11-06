# 市場規模調査の例

## タスク

「日本の電気自動車（EV）市場の市場規模を調査し、2024年から2029年までの5年間のCAGR（年平均成長率）を算出してください。一次情報と二次情報を突き合わせ、根拠となるURLと引用箇所、信頼度を添付して要約してください。」

## ジョブ投入

```bash
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task": "日本の電気自動車（EV）市場の市場規模を調査し、2024年から2029年までの5年間のCAGR（年平均成長率）を算出。一次情報と二次情報を突き合わせ、根拠となるURLと引用箇所、信頼度を添付して要約。",
    "constraints": {
      "budget_tokens": 50000,
      "time_limit_min": 45
    },
    "policy": {
      "require_human_approval": false,
      "require_citations": true,
      "allowed_domains": ["*.go.jp", "*.or.jp", "*.co.jp", "*.ac.jp"]
    },
    "metadata": {
      "project": "market-research-2024",
      "requester": "research-team"
    }
  }'
```

## 期待される実行フロー

### Phase 1: Planning (計画)

エージェントがタスクを以下のステップに分解：

1. **一次情報の収集**
   - 経済産業省の統計データ
   - 自動車工業会のレポート
   - 各自動車メーカーの公式発表

2. **二次情報の収集**
   - 市場調査会社のレポート
   - 業界ニュース
   - 学術論文

3. **データの検証**
   - 複数ソースでの数値照合
   - データの整合性確認
   - 信頼性スコアリング

4. **CAGR 算出**
   - 2024年ベースライン確認
   - 2029年予測値の特定
   - CAGR計算式適用

5. **レポート作成**
   - 要約作成
   - Citation リスト生成
   - 信頼度評価

### Phase 2: Execution (実行)

#### Step 1: Web Search
```
Query: "日本 電気自動車 EV 市場規模 2024"
Results:
  - [経産省] EV普及状況調査 (2024年3月)
  - [JAMA] 電動車統計 (2024年版)
  - [民間調査会社] 日本EV市場予測レポート
```

#### Step 2: RAG Search (内部知識ベース)
```
Query: "電気自動車 市場 過去データ"
Results:
  - 過去5年間のEV販売台数推移
  - 充電インフラ整備状況
  - 政府補助金政策の影響分析
```

#### Step 3: Fact Checking
```
Cross-reference:
  - 2024年市場規模: 複数ソースで一致
  - 2029年予測: 幅があるため平均値を使用
  - 成長率要因: 政策、技術、需要で確認
```

### Phase 3: Reflection (検証)

品質チェック:
- ✅ Citations: 5個以上のソースを引用
- ✅ 一次/二次情報の区別: 明確
- ✅ 数値の整合性: 検証済み
- ✅ 信頼性スコア: 全体 0.85/1.0

### Phase 4: Reporting (報告)

## 期待される出力例

```markdown
# 日本EV市場規模調査レポート

## エグゼクティブサマリー

日本の電気自動車（EV）市場は2024年時点で約XXX万台の規模であり、
2029年までに年平均成長率（CAGR）XX%で成長し、約XXX万台に達すると予測される。

## 主要な知見

### 1. 現在の市場規模（2024年）
- 新車販売台数: XXX万台
- 市場シェア: XX%
- 出典: [1][2]

### 2. 予測市場規模（2029年）
- 予測販売台数: XXX万台
- 予測市場シェア: XX%
- 出典: [3][4]

### 3. CAGR 算出
```
CAGR = ((2029年値 / 2024年値)^(1/5) - 1) × 100
     = ((XXX / XXX)^0.2 - 1) × 100
     = XX.X%
```

### 4. 成長要因
- 政府の脱炭素政策
- 充電インフラの整備進展
- バッテリー技術の向上とコスト低減

## データソースと信頼性

| No | ソース種別 | タイトル | URL | 信頼度 | 引用箇所 |
|----|----------|---------|-----|--------|---------|
| 1  | 一次情報 | 経済産業省 EV普及状況調査 | https://www.meti.go.jp/... | 0.95 | P.12, 図3 |
| 2  | 一次情報 | 日本自動車工業会統計 | https://www.jama.or.jp/... | 0.90 | 2024年版 |
| 3  | 二次情報 | 市場調査レポート A社 | https://www.example.co.jp/... | 0.80 | 要約セクション |
| 4  | 二次情報 | 業界ニュース B社 | https://news.example.com/... | 0.75 | 専門家コメント |
| 5  | 学術 | XX大学研究論文 | https://www.example.ac.jp/... | 0.85 | Abstract |

## 注意事項と制限

- 予測値は複数ソースの平均値を使用
- 為替レート変動の影響は考慮していない
- 政策変更により大きく変動する可能性あり

## メタデータ

- 調査実施日: 2024-01-01
- トークン使用量: 35,000 / 50,000
- 実行時間: 28分
- 品質スコア: 0.88 / 1.0
```

## ステータス確認

```bash
# ジョブステータス確認
curl http://localhost:8080/jobs/{job_id}

# レスポンス例
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "task": "日本のEV市場...",
  "progress": 1.0,
  "result": {
    "summary": "...",
    "findings": [...],
    "citations": [...],
    "confidence_score": 0.88
  }
}
```

## 人的承認が必要な場合

```bash
# 承認リクエスト確認
curl http://localhost:8080/jobs/{job_id}

{
  "status": "waiting_approval",
  "approval_required": {
    "reason": "External data export requested",
    "details": "..."
  }
}

# 承認処理
curl -X POST http://localhost:8080/jobs/{job_id}/approve \
  -H "Content-Type: application/json" \
  -d '{
    "approver": "manager@example.com",
    "approved": true,
    "comment": "Approved for market research project"
  }'
```

## トラブルシューティング

### エラー: Domain not allowed

```json
{
  "error": "Policy violation",
  "details": "Domain not in allowlist: example.net"
}
```

**対処**: `allowed_domains` に許可ドメインを追加

### エラー: Insufficient citations

```json
{
  "error": "Quality check failed",
  "details": "Only 2 citations found, minimum 3 required"
}
```

**対処**: より多くの情報ソースを含むよう再実行
