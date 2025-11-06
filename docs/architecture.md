# アーキテクチャドキュメント

## システム概要

本システムは、Azure AI Foundry を活用したエンタープライズ向けの Deep Research エージェントフレームワークです。長時間実行タスク、メモリ管理、オブザーバビリティを備えた実装を提供します。

## アーキテクチャ図

```
┌─────────────────┐
│   Client UI     │
│   (Web/CLI)     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────────────────────────┐
│          API Layer (FastAPI)                │
│  - Job submission                           │
│  - Status queries                           │
│  - Approval handling                        │
└────────┬────────────────────────────────────┘
         │ Enqueue
         ▼
┌─────────────────────────────────────────────┐
│     Azure Service Bus (Job Queue)           │
│  - Reliable message delivery                │
│  - Dead-letter queue                        │
│  - Message retry                            │
└────────┬────────────────────────────────────┘
         │ Dequeue
         ▼
┌─────────────────────────────────────────────┐
│          Worker Layer                       │
│  - Job processing                           │
│  - Agent orchestration                      │
│  - Checkpoint management                    │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│       Deep Research Agent                   │
│  ┌─────────────────────────────────────┐   │
│  │  Planning → Execution → Reflection  │   │
│  │          ↓                          │   │
│  │      Reporting                      │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Components:                                │
│  - Tool Registry                            │
│  - Memory Manager                           │
│  - Policy Manager                           │
└────────┬────────────────────────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
    │  Tools │    │ Memory │    │Policies│    │  Obs   │
    └────────┘    └────────┘    └────────┘    └────────┘
```

## コンポーネント詳細

### 1. API Layer

**技術**: FastAPI + Uvicorn

**責務**:
- REST API エンドポイント提供
- リクエスト検証
- ジョブキューへの投入
- ステータス管理

**エンドポイント**:
- `POST /jobs` - ジョブ作成
- `GET /jobs/{job_id}` - ステータス取得
- `GET /jobs` - ジョブ一覧
- `DELETE /jobs/{job_id}` - ジョブキャンセル
- `POST /jobs/{job_id}/approve` - 承認処理

### 2. Job Queue

**技術**: Azure Service Bus

**機能**:
- 信頼性の高いメッセージ配信
- デッドレターキュー
- 自動リトライ
- セッション管理

**設定**:
- Lock Duration: 5分
- Max Delivery Count: 10
- Dead Lettering: 有効

### 3. Worker Layer

**技術**: Python async/await

**責務**:
- キューからジョブ取得
- エージェント実行
- チェックポイント管理
- エラーハンドリング

**スケーリング**:
- 水平スケール可能
- 並行処理数: 環境別設定

### 4. Deep Research Agent

**フェーズ**:

1. **Planning (計画)**
   - タスク分解
   - ステップ定義
   - 制約確認

2. **Execution (実行)**
   - ツール呼び出し
   - 情報収集
   - 中間結果保存

3. **Reflection (検証)**
   - 結果検証
   - Citation 確認
   - 品質スコア算出

4. **Reporting (報告)**
   - レポート生成
   - Citation 付与
   - 成果物出力

### 5. Tools (ツール)

**種類**:
- **Web Search**: Bing Search API
- **RAG**: Azure AI Search (ベクトル検索)
- **Browser**: 安全なブラウジング
- **MCP**: 社内 API アクセス

**特徴**:
- プラガブル設計
- 標準インターフェース
- エラーハンドリング

### 6. Memory (メモリ)

**短期メモリ**:
- 実装: In-process Cache / Redis
- 用途: セッション状態、作業メモ
- TTL: 30分～1時間

**長期メモリ**:
- 実装: Azure AI Search
- 用途: ナレッジベース、過去の研究
- 保持: 環境別設定

### 7. Policies (ポリシー)

**種類**:
- **Domain Allowlist**: アクセス可能ドメイン制限
- **Citation Policy**: 引用必須化
- **Rate Limiting**: レート制限
- **Approval Policy**: 承認フロー

### 8. Observability (可観測性)

**コンポーネント**:

1. **Tracing**
   - OpenTelemetry
   - 分散トレーシング
   - スパン属性（トークン数、コスト）

2. **Logging**
   - 構造化 JSON ログ
   - PII マスキング
   - ログレベル制御

3. **Metrics**
   - ジョブ成功率
   - トークン使用量
   - レスポンスタイム
   - エラー率

## データフロー

### ジョブ実行フロー

```
1. クライアント → API: ジョブ投入
2. API → Service Bus: メッセージエンキュー
3. Worker ← Service Bus: メッセージ取得
4. Worker → Agent: ジョブ実行開始
5. Agent → Tools: 情報収集
6. Agent → Memory: 中間結果保存
7. Agent → Policies: ポリシーチェック
8. Agent → Checkpoint: 進捗保存
9. Agent → Worker: 実行完了
10. Worker → Storage: 結果保存
11. API ← Worker: ステータス更新
12. クライアント ← API: 結果取得
```

### チェックポイント機構

```
実行中:
  ├─ Step 1 完了 → Checkpoint 1 保存
  ├─ Step 2 完了 → Checkpoint 2 保存
  ├─ Step 3 失敗
  └─ リカバリ: Checkpoint 2 から再開
```

## セキュリティ

### 認証・認可

- **Entra ID (Azure AD)**: 
  - ユーザー認証
  - アプリケーション認証
  - RBAC (Role-Based Access Control)

- **Managed Identity**:
  - Azure リソース間認証
  - パスワードレス

### ネットワーク

- **Private Link**: VNet 内通信
- **NSG**: ネットワークセキュリティグループ
- **Egress Control**: アウトバウンド制限

### データ保護

- **暗号化**:
  - 保管時: Storage Service Encryption
  - 転送時: TLS 1.2+

- **Key Vault**:
  - シークレット管理
  - キー管理
  - 証明書管理

## スケーラビリティ

### 水平スケール

- **API**: App Service の自動スケール
- **Worker**: インスタンス数増加
- **Queue**: パーティション分割

### 垂直スケール

- **Azure AI Search**: SKU アップグレード
- **Service Bus**: Premium tier
- **Storage**: パフォーマンス tier

## 監視とアラート

### メトリクス

- CPU/メモリ使用率
- リクエスト数/秒
- エラー率
- ジョブ処理時間

### アラート条件

- エラー率 > 5%
- レスポンスタイム > 10秒
- キュー長 > 100
- デッドレターメッセージ発生

### ダッシュボード

- **Application Insights**: リアルタイム監視
- **Azure Monitor**: メトリクス可視化
- **Custom Dashboard**: ビジネスメトリクス

## ディザスタリカバリ

### バックアップ

- **Storage**: Geo-redundant storage
- **Database**: Point-in-time restore
- **Configuration**: Git リポジトリ

### RTO/RPO

- **RTO (Recovery Time Objective)**: 4時間
- **RPO (Recovery Point Objective)**: 1時間

## パフォーマンス目標

- **API レスポンス**: < 500ms (95th percentile)
- **ジョブ投入**: < 1秒
- **ジョブ処理**: タスク依存（制約指定可能）
- **可用性**: 99.9%

## コスト最適化

### 戦略

1. **リソース選択**: 適切な SKU 選択
2. **自動スケール**: 需要に応じたスケーリング
3. **トークン制限**: 予算管理
4. **キャッシング**: 重複処理削減

### モニタリング

- トークン使用量の追跡
- リソース使用率の監視
- コスト予測アラート
