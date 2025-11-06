# クイックスタートガイド

このガイドでは、エンタープライズエージェントフレームワークを最速でセットアップして実行する手順を説明します。

## 前提条件

- Python 3.10 以上
- pip (Python パッケージマネージャー)
- （オプション）Azure サブスクリプション

## 1. ローカル開発環境のセットアップ

### 環境変数の設定

```bash
# リポジトリのルートディレクトリで実行
cp .env.example .env

# .env ファイルを編集して必要な値を設定
# 最低限必要な設定（開発モード）:
# - LOG_LEVEL=DEBUG
# - ENVIRONMENT=dev
```

### Python 依存関係のインストール

```bash
# API サービス
pip install -r apps/api/requirements.txt

# Worker サービス
pip install -r apps/worker/requirements.txt
```

## 2. ローカルでの実行

### API サーバーの起動

```bash
# ターミナル 1
cd apps/api
uvicorn main:app --reload --port 8080
```

API は http://localhost:8080 で起動します。

### API ドキュメントの確認

ブラウザで以下にアクセス:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Worker の起動（オプション）

```bash
# ターミナル 2
cd apps/worker
python main.py
```

## 3. サンプルリクエストの実行

### ジョブの投入

```bash
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Python プログラミング言語について調査し、主な特徴と用途をまとめてください。",
    "constraints": {
      "budget_tokens": 10000,
      "time_limit_min": 5
    },
    "policy": {
      "require_human_approval": false,
      "require_citations": true
    }
  }'
```

レスポンス例:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Job successfully queued for processing",
  "created_at": "2024-01-01T00:00:00.000Z"
}
```

### ジョブステータスの確認

```bash
# job_id を上記レスポンスから取得して使用
curl http://localhost:8080/jobs/550e8400-e29b-41d4-a716-446655440000
```

### すべてのジョブの一覧

```bash
curl http://localhost:8080/jobs
```

### ヘルスチェック

```bash
curl http://localhost:8080/health
```

## 4. テストの実行

```bash
# ユニットテスト
pip install pytest pytest-asyncio
pytest tests/unit/ -v

# 評価/ベンチマーク
python tests/eval/test_benchmarks.py
```

## 5. 実用例の確認

以下のファイルに詳細な使用例があります:

- **市場規模調査**: `examples/research_market_sizing.md`
- **法令調査**: `examples/research_regulation.md`

## トラブルシューティング

### ImportError が発生する場合

```bash
# Python パスを設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### モジュールが見つからない場合

```bash
# すべての依存関係を再インストール
pip install -r apps/api/requirements.txt --force-reinstall
```

### ポートが使用中の場合

```bash
# 別のポートで起動
uvicorn apps.api.main:app --port 8081
```

## 次のステップ

### ドキュメントを読む

- [アーキテクチャ](docs/architecture.md) - システム設計の詳細
- [運用ガイド](docs/operations_runbook.md) - デプロイと運用
- [セキュリティ](docs/security_compliance.md) - セキュリティとコンプライアンス

### Azure へのデプロイ

```bash
# Azure リソースのデプロイ
az deployment group create \
  --resource-group <your-rg> \
  --template-file infra/bicep/main.bicep \
  --parameters environment=dev
```

詳細は [運用ガイド](docs/operations_runbook.md) を参照してください。

### カスタマイズ

- **新しいツールの追加**: `agents/tools/` に新しいツールクラスを作成
- **ポリシーの調整**: `agents/policies/manager.py` を編集
- **メモリの設定**: `.env` で TTL や長期メモリを設定

## サポート

問題が発生した場合:

1. [README.md](README.md) の FAQ セクションを確認
2. GitHub Issues で既知の問題を検索
3. 新しい Issue を作成

---

**注意**: このフレームワークはサンプル実装です。本番環境で使用する前に、組織のセキュリティポリシーとコンプライアンス要件を満たすように調整してください。
