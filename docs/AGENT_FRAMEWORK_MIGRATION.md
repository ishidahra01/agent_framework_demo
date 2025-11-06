# Microsoft Agent Framework Migration Guide

このドキュメントは、Microsoft Agent Framework への移行について説明します。

## 概要

このプロジェクトは、**Microsoft Agent Framework**（AutoGen と Semantic Kernel の後継）を使用するように更新されました。Agent Framework は、AI エージェントとマルチエージェント ワークフローを構築するための統合された基盤を提供します。

## 主な変更点

### 1. 依存関係の追加

```bash
pip install agent-framework>=0.1.0
```

requirements.txt に `agent-framework` パッケージが追加されました。

### 2. 新しい実装

#### エージェント実装 (`agents/deep_research/agent_framework_impl.py`)

- `ChatAgent` と `AzureOpenAIChatClient` を使用
- Azure OpenAI との統合
- 自動的なツール呼び出し管理
- スレッドベースの会話管理

#### ファンクションツール (`agents/tools/functions.py`)

- `@ai_function` デコレータを使用したツール定義
- 型安全な実装
- Agent Framework との完全な互換性

### 3. 後方互換性

`agents/deep_research/agent.py` は、環境変数 `USE_AGENT_FRAMEWORK` に基づいて実装を自動的に選択します：

```python
# Agent Framework を使用（デフォルト）
USE_AGENT_FRAMEWORK=true

# レガシー実装を使用
USE_AGENT_FRAMEWORK=false
```

## 使用方法

### 基本的な使用

```python
from agents.deep_research.agent import DeepResearchAgent

# エージェントの作成
agent = DeepResearchAgent()

# リサーチタスクの実行
result = await agent.run("Python プログラミングのメリットについて調査してください")

print(result["report"])
```

### 環境変数の設定

Agent Framework を使用する場合、以下の環境変数が必要です：

```bash
# Azure OpenAI 設定
export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com"
export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o-mini"

# 認証方法 1: API キー
export AZURE_OPENAI_API_KEY="your-api-key"

# または認証方法 2: Azure CLI 認証
# az login を実行してください
```

### ツールのカスタマイズ

新しいツールを追加する場合：

```python
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function

@ai_function(
    name="custom_tool",
    description="カスタムツールの説明"
)
def custom_tool(
    param: Annotated[str, Field(description="パラメータの説明")],
) -> str:
    """ツールの実装"""
    # 処理
    return result
```

## Agent Framework の主な機能

### 1. AI エージェント

- **LLM との統合**: Azure OpenAI、OpenAI などをサポート
- **ツール統合**: ファンクションツール、MCP サーバー
- **マルチターン会話**: スレッドベースの会話管理
- **ストリーミング**: リアルタイムレスポンス

### 2. ワークフロー

- **グラフベースワークフロー**: 複雑なマルチステップタスク
- **型安全**: 実行時の検証
- **チェックポイント**: 長時間実行タスクのサポート
- **並列処理**: 複数のエージェントの同時実行

### 3. マルチエージェント オーケストレーション

- **Sequential（シーケンシャル）**: パイプライン処理
- **Concurrent（並行）**: 並列実行
- **Magentic**: 動的な協調

## API の互換性

既存の API エンドポイントはそのまま動作します：

```bash
# ジョブの投入
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task": "市場規模の調査",
    "constraints": {"budget_tokens": 40000},
    "policy": {"require_citations": true}
  }'

# ジョブステータスの確認
curl http://localhost:8080/jobs/{job_id}
```

## テスト

### ユニットテスト

```bash
# レガシー実装でテスト
export USE_AGENT_FRAMEWORK=false
pytest tests/unit/test_agent.py -v

# Agent Framework でテスト（モックモード）
export USE_AGENT_FRAMEWORK=true
pytest tests/unit/test_agent.py -v
```

### 統合テスト

```bash
# テストスクリプトの実行
python test_agent_framework.py
```

## トラブルシューティング

### Azure 認証エラー

```
Failed to retrieve Azure token
```

**解決方法**:
1. `az login` を実行してログイン
2. または `AZURE_OPENAI_API_KEY` 環境変数を設定

### モジュールが見つからない

```
ModuleNotFoundError: No module named 'agent_framework'
```

**解決方法**:
```bash
pip install agent-framework pydantic
```

### Agent Framework が利用できない場合

環境変数を設定してレガシー実装を使用：
```bash
export USE_AGENT_FRAMEWORK=false
```

## パフォーマンスとコスト

Agent Framework の使用により：

- ✅ **パフォーマンス向上**: 最適化された LLM 呼び出し
- ✅ **コスト削減**: 効率的なトークン使用
- ✅ **スケーラビリティ**: エンタープライズグレードのアーキテクチャ
- ✅ **可観測性**: 組み込みのトレーシングとメトリクス

## 参考リンク

- [Microsoft Agent Framework 公式ドキュメント](https://learn.microsoft.com/ja-jp/agent-framework/overview/agent-framework-overview)
- [GitHub リポジトリ](https://github.com/microsoft/agent-framework)
- [Python サンプル](https://github.com/microsoft/agent-framework/tree/main/python/samples)

## 次のステップ

1. Azure OpenAI リソースの設定
2. 環境変数の構成
3. カスタムツールの追加（必要に応じて）
4. ワークフローの最適化
5. マルチエージェント オーケストレーションの実装

## サポート

問題が発生した場合：

1. [README.md](README.md) の FAQ を確認
2. [GitHub Issues](https://github.com/ishidahra01/agent_framework_demo/issues) で既知の問題を検索
3. 新しい Issue を作成

---

**注意**: Agent Framework は現在パブリック プレビュー段階です。本番環境で使用する前に、十分なテストを実施してください。
