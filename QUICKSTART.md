# クイックスタートガイド

このガイドでは、Microsoft Agent Framework を使用したエンタープライズエージェントを最速でセットアップして実行する手順を説明します。

> **重要**: 本プロジェクトは Microsoft Agent Framework に移行済みです。詳細は [Agent Framework 移行ガイド](docs/AGENT_FRAMEWORK_MIGRATION.md) を参照してください。

## 前提条件

- Python 3.10 以上
- pip (Python パッケージマネージャー)
- Azure OpenAI リソース（本番環境用）
- （オプション）Azure CLI (`az login` で認証済み）

## 1. ローカル開発環境のセットアップ

### 環境変数の設定

```bash
# リポジトリのルートディレクトリで実行
cp .env.example .env

# .env ファイルを編集して必要な値を設定
```

#### Agent Framework を使用する場合（推奨）

```bash
# .env ファイルに以下を設定
USE_AGENT_FRAMEWORK=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini

# 認証方法 1: API キー
AZURE_OPENAI_API_KEY=your-api-key

# または認証方法 2: Azure CLI
# az login を実行
```

#### 開発/テスト用（認証情報なし）

```bash
# Agent Framework はモックモードで動作します
USE_AGENT_FRAMEWORK=true
LOG_LEVEL=DEBUG
ENVIRONMENT=dev
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

### ユニットテスト

```bash
# 依存関係のインストール
pip install pytest pytest-asyncio

# レガシー実装でテスト
export USE_AGENT_FRAMEWORK=false
pytest tests/unit/test_agent.py -v

# Agent Framework でテスト（モックモード）
export USE_AGENT_FRAMEWORK=true
pytest tests/unit/test_agent.py -v
```

### Agent Framework の検証

```bash
# 包括的なテストスクリプト
python test_agent_framework.py

# 出力例:
# ✓ Configuration loaded
# ✓ Function tools working
# ✓ Agent Framework implementation working
```

### 評価/ベンチマーク

```bash
python tests/eval/test_benchmarks.py
```

## 5. Agent Framework の使用例

### Python コードから直接使用

```python
import asyncio
from agents.deep_research.agent import DeepResearchAgent

async def main():
    # エージェントの作成
    agent = DeepResearchAgent()
    
    # リサーチタスクの実行
    result = await agent.run(
        "Python プログラミングのメリットについて調査してください"
    )
    
    # レポートの表示
    print(result["report"])

asyncio.run(main())
```

### 利用可能なツール

Agent Framework 実装では、以下のツールが利用可能です：

- `web_search`: Web 検索（Bing Search API）
- `rag_search`: 内部ナレッジベース検索
- `browse_url`: 安全な URL ブラウジング
- `analyze_data`: データ分析
- `verify_facts`: ファクトチェック

## 6. 実用例の確認

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
