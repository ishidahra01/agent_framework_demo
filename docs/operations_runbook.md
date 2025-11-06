# 運用ランブック

## デプロイメント

### 初回デプロイ

```bash
# 1. Azure リソースグループ作成
az group create --name agent-framework-prd-rg --location japaneast

# 2. インフラストラクチャデプロイ
az deployment group create \
  --resource-group agent-framework-prd-rg \
  --template-file infra/bicep/main.bicep \
  --parameters environment=prd location=japaneast

# 3. 環境変数設定
# デプロイ結果から接続文字列等を取得し .env に設定

# 4. API デプロイ
cd apps/api
pip install -r requirements.txt
# App Service へデプロイ

# 5. Worker デプロイ
cd apps/worker
pip install -r requirements.txt
# Container Apps or VM へデプロイ
```

### 更新デプロイ

```bash
# コード更新のみの場合
git pull origin main
# API/Worker を再起動

# インフラ更新の場合
az deployment group create \
  --resource-group agent-framework-prd-rg \
  --template-file infra/bicep/main.bicep \
  --parameters environment=prd
```

## 日常運用

### ヘルスチェック

```bash
# API ヘルスチェック
curl https://api.example.com/health

# Worker 状態確認
# Service Bus キュー長を確認
az servicebus queue show \
  --resource-group agent-framework-prd-rg \
  --namespace-name agent-sb-prd \
  --name agent-jobs \
  --query "countDetails"
```

### ログ確認

```bash
# Application Insights でログ検索
# KQL クエリ例:
traces
| where timestamp > ago(1h)
| where severityLevel >= 3
| order by timestamp desc

# ジョブエラーの確認
traces
| where customDimensions.job_id != ""
| where severityLevel == 3
| project timestamp, message, customDimensions.job_id
```

### メトリクス確認

Application Insights → Metrics で以下を監視:
- リクエスト数
- 失敗率
- レスポンスタイム
- カスタムメトリクス (トークン使用量等)

## トラブルシューティング

### ジョブが完了しない

**症状**: ジョブがキューに残り続ける

**原因調査**:
```bash
# デッドレターキューを確認
az servicebus queue show \
  --resource-group agent-framework-prd-rg \
  --namespace-name agent-sb-prd \
  --name agent-jobs \
  --query "countDetails.deadLetterMessageCount"

# Worker ログを確認
# Application Insights でエラーログを検索
```

**対処**:
1. Worker が起動しているか確認
2. エラーログから原因特定
3. 必要に応じて Worker 再起動
4. ジョブ再投入

### API レスポンスが遅い

**症状**: API のレスポンスタイムが 5 秒以上

**原因調査**:
```bash
# Application Insights でパフォーマンス分析
# Dependencies タブで外部呼び出しを確認
```

**対処**:
1. キャッシュ設定確認
2. データベースクエリ最適化
3. スケールアウト検討
4. レート制限調整

### メモリ不足

**症状**: Worker がクラッシュする

**原因調査**:
```bash
# メモリ使用量確認
# Azure Monitor でメトリクス確認
```

**対処**:
1. 短期メモリ TTL 短縮
2. ジョブ並行実行数削減
3. Worker インスタンスサイズ増加

### Citation が不足

**症状**: レポートに引用が含まれない

**原因調査**:
- Agent ログで Tool 実行結果確認
- Policy 設定確認

**対処**:
1. Tool の Citation 抽出ロジック確認
2. Policy の `require_citations` 設定確認
3. 必要に応じてジョブ再実行

## アラート対応

### エラー率アラート

**条件**: エラー率 > 5% (5分間)

**対応手順**:
1. Application Insights でエラー詳細確認
2. 共通エラーパターンの特定
3. 一時的な障害か確認
4. 必要に応じてロールバック

### キュー滞留アラート

**条件**: キュー長 > 100

**対応手順**:
1. Worker 稼働状況確認
2. Worker スケールアウト
3. ジョブ失敗率確認
4. 必要に応じて一部ジョブキャンセル

### トークン使用量超過

**条件**: 月間トークン数が予算の 80% 超過

**対応手順**:
1. トークン使用量の大きいジョブ特定
2. レート制限強化
3. 不要なジョブ停止
4. 予算増額検討

## バックアップとリストア

### データバックアップ

```bash
# Storage Account のバックアップは自動
# Geo-redundant storage により保護

# AI Search インデックスのバックアップ
# カスタムスクリプトで定期エクスポート

# 設定のバックアップ
# Git リポジトリで管理
```

### リストア手順

```bash
# Storage からのリストア
az storage blob download-batch \
  --account-name <storage-account> \
  --source checkpoints \
  --destination ./restore/

# AI Search インデックスのリストア
# エクスポートデータからインポート
```

## スケーリング

### 手動スケール

```bash
# Worker インスタンス数変更
# Azure Portal または CLI で設定

# App Service のスケール
az webapp scale \
  --resource-group agent-framework-prd-rg \
  --name agent-api-prd \
  --number-of-workers 5
```

### 自動スケール設定

```bash
# App Service の自動スケール
az monitor autoscale create \
  --resource-group agent-framework-prd-rg \
  --resource agent-api-prd \
  --resource-type Microsoft.Web/serverfarms \
  --min-count 2 \
  --max-count 10 \
  --count 2

# CPU ベースのルール追加
az monitor autoscale rule create \
  --resource-group agent-framework-prd-rg \
  --autoscale-name agent-api-autoscale \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

## セキュリティ

### 定期確認事項

- [ ] アクセスログレビュー (週次)
- [ ] 脆弱性スキャン (月次)
- [ ] 証明書更新確認 (四半期)
- [ ] アクセス権レビュー (四半期)

### インシデント対応

1. **検知**: セキュリティアラート受信
2. **隔離**: 影響範囲の特定と隔離
3. **調査**: ログ分析、原因特定
4. **対応**: 脆弱性修正、アクセス遮断
5. **報告**: インシデントレポート作成
6. **改善**: 再発防止策実施

## メンテナンス

### 定期メンテナンス

**週次**:
- ログレビュー
- メトリクス確認
- デッドレターキュー確認

**月次**:
- パフォーマンスレビュー
- コストレビュー
- セキュリティアップデート

**四半期**:
- ディザスタリカバリテスト
- キャパシティプランニング
- アーキテクチャレビュー

### アップデート手順

```bash
# 1. ステージング環境でテスト
# 2. メンテナンス通知
# 3. 本番デプロイ
# 4. ヘルスチェック
# 5. ロールバック準備
```

## 連絡先

- **開発チーム**: dev-team@example.com
- **運用チーム**: ops-team@example.com
- **セキュリティチーム**: security@example.com
- **オンコール**: oncall@example.com

## 参考資料

- [アーキテクチャドキュメント](./architecture.md)
- [セキュリティコンプライアンス](./security_compliance.md)
- [Azure OpenAI ドキュメント](https://learn.microsoft.com/azure/ai-services/openai/)
