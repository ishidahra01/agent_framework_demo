# エンタープライズ向けエージェント・ソリューションアクセラレータ（Deep Research / Long-Running / Memory / Observability）

> **重要な更新**  
> **本リポジトリは Microsoft Agent Framework を使用するように更新されました！**  
> Agent Framework は AutoGen と Semantic Kernel の後継として開発された、AI エージェントとマルチエージェント ワークフローを構築するための統合されたオープンソースフレームワークです。

> **目的**  
> 本リポジトリは、**Microsoft Agent Framework** と **Azure AI Foundry** を用いて、**長時間・複雑タスク（Deep Research 型）** を安全に遂行し、**メモリ（短期/長期）** と **オブザーバビリティ** を備えた **エンタープライズ実装の叩き台（MVP入力）** を提供します。  
> コードは拡張可能なモジュラー構成で、PoC → MVP → 本番の段階的拡張を前提に設計しています。

---

## 🎯 Microsoft Agent Framework について

**Microsoft Agent Framework** は、AI エージェントとマルチエージェント ワークフローを構築するための次世代フレームワークです：

- ✅ **統合された基盤**: AutoGen と Semantic Kernel の長所を組み合わせ
- ✅ **エンタープライズ機能**: 型安全、フィルター、テレメトリ、状態管理
- ✅ **柔軟なワークフロー**: グラフベースのオーケストレーション
- ✅ **Human-in-the-loop**: 実行時間の長いシナリオと承認フロー

📖 **詳細**: [Agent Framework 移行ガイド](docs/AGENT_FRAMEWORK_MIGRATION.md)

---

## ✅ 提供価値（What you get）

* **Deep Research エージェント**：情報収集 → 反省/計画更新 → 根拠付きレポート化（Citations/Fact-checking 付き）
* **長時間実行に対応**：チェックポイント/再開、ジョブ管理、並列サブタスク、人的承認（Human-in-the-loop）
* **メモリ**：
  * 短期（対話コンテキスト、作業メモ）
  * 長期（ユーザ/組織ナレッジ、プロジェクトごとの知識）
  * 記憶の可視化・編集・保持期間ポリシー
* **オブザーバビリティ**：トレーシング、メトリクス、ログ、プロンプトバージョン管理、原価・トークン利用量可視化
* **エンタープライズ機能**：Entra ID 認証、ネットワーク分離、鍵/接続情報のマネジメント、権限付きツール実行（MCP/API）

---

## 📁 リポジトリ構成

```
.
├─ apps/
│  ├─ api/                    # FastAPI / Azure Functions（選択式）でのエージェントAPI
│  ├─ worker/                 # 長時間ジョブ・並列実行ワーカー（Service Bus/Queue 連携）
│  └─ web/                    # 参考UI（ジョブ投入・進捗・可視化ダッシュボード）
│
├─ agents/
│  ├─ deep_research/          # メイン：調査エージェント（計画/実行/検証/要約）
│  ├─ tools/                  # Web検索、RAG、ブラウズ、ファイル、API(MCP) 等
│  ├─ memory/                 # 短期/長期メモリの実装（抽象IF + プラガブル実装）
│  └─ policies/               # セーフティ/ガバナンス、承認フロー、レート制御
│
├─ orchestrations/
│  ├─ plans/                  # 計画テンプレート（PRD調査/競合調査/法令チェック 等）
│  └─ workflows/              # DAG/ステートマシン定義（再実行/分岐/合流/チェックポイント）
│
├─ observability/
│  ├─ tracing/                # OpenTelemetry 設定（OTLP Exporter、サンプリング）
│  ├─ logging/                # 構造化ログ（JSON）、PIIマスク
│  ├─ dashboards/             # (Grafana/Azure Monitor Workbook) ダッシュボード定義
│  └─ prompts/                # Prompt Flow / バージョン管理（YAML）
│
├─ infra/
│  ├─ bicep/                  # Azure リソース定義（AI Foundry, AppInsights, SB, Storage..）
│  ├─ pipelines/              # GitHub Actions / Azure DevOps CI/CD
│  └─ configs/                # 環境毎（dev/stg/prd）の設定
│
├─ tests/
│  ├─ unit/                   # ユニットテスト
│  ├─ integration/            # 統合テスト
│  └─ eval/                   # エージェント評価（タスク成功率/根拠一致率/コスト）
│
├─ examples/                  # 使用例とサンプルタスク
│  ├─ research_market_sizing.md
│  └─ research_regulation.md
│
├─ docs/                      # ドキュメント
│  ├─ architecture.md
│  ├─ operations_runbook.md
│  └─ security_compliance.md
│
├─ .env.example               # 環境変数テンプレート
├─ README.md                  # 本ファイル
└─ LICENSE
```

---

## 🏗️ アーキテクチャ概要

```
[Client(UI/CLI)] 
   │ REST/WebSocket
   ▼
[apps/api]───(enqueue)──▶[Queue(Service Bus)]
   │                                 │
   │                                 ▼
   │                           [apps/worker]
   │                                │
   │                                ├─ invokes ─▶ [agents/deep_research]
   │                                │              ├─ tools/web_search
   │                                │              ├─ tools/rag (Azure AI Search / Cosmos + VS)
   │                                │              ├─ tools/browser (safe browsing)
   │                                │              └─ tools/mcp (社内API/ERP/PM等)
   │                                │
   │                                ├─ memory ─▶ [agents/memory] (短期: cache / 長期: vector + KV/DB)
   │                                │
   │                                └─ trace/log ─▶ [observability/* → App Insights / OTLP / Monitor]
   │
   └─ auth ─▶ [Microsoft Entra ID / Managed Identity]
```

**実行基盤**：
* Azure AI Foundry（モデル/推論）
* App Service or Functions（API/Worker）
* Service Bus（ジョブキュー）

**データレイヤー**：
* Blob/ADLS（成果物/キャッシュ）
* Azure AI Search or Cosmos DB + VS（長期記憶）
* Key Vault（Secrets）

**可観測性**：
* Application Insights + OpenTelemetry（Trace/Log/Metrics）
* コスト&トークン可視化

---

## 📋 前提条件（Prerequisites）

* Azure サブスクリプション（Owner/Contributor 相当）
* Azure AI Foundry（Azure OpenAI もしくは互換推論エンドポイントアクセス）
* Resource Group / Region（規約上のデータ保管要件に合致）
* Microsoft Entra ID（アプリ登録＋ロール/スコープ設計）
* 開発環境：
  * Python 3.10+ 
  * Node.js 20+
  * Docker（任意）
* CLI：`az`、`bicep`、`jq`（任意）
* （任意）GitHub Actions or Azure DevOps

---

## 🚀 クイックスタート

### 1. 環境変数の準備

```bash
cp .env.example .env
# 必要なキーを設定（Azure AI Foundry/Entra/Service Bus/Storage/AI Search/Key Vault 等）
```

### 2. 依存のインストール

```bash
# API/Worker（Python）
pip install -r apps/api/requirements.txt
pip install -r apps/worker/requirements.txt

# Web（Node）
cd apps/web && npm ci && cd ../..
```

### 3. ローカル実行（Mock/Dev）

```bash
# API (FastAPI)
uvicorn apps.api.main:app --reload --port 8080

# Worker
python apps/worker/main.py
```

### 4. サンプルタスク投入

```bash
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task":"市場規模の一次情報と二次情報を突き合わせ、5年CAGRを算出。根拠URLと引用箇所、信頼度を添付して要約。",
    "constraints":{"budget_tokens": 40000, "time_limit_min": 30},
    "policy":{"require_human_approval": true}
  }'
```

---

## 🤖 Microsoft Agent Framework の実装

本プロジェクトは Microsoft Agent Framework を使用して AI エージェントを実装しています。

### エージェントの作成

```python
from agents.deep_research.agent import DeepResearchAgent

# エージェントの初期化（Agent Framework を使用）
agent = DeepResearchAgent()

# リサーチタスクの実行
result = await agent.run("Python プログラミングについて調査")
```

### 実装の特徴

* **ChatAgent**: Azure OpenAI を使用した LLM 統合
* **ファンクションツール**: `@ai_function` デコレータによるツール定義
* **自動ツール呼び出し**: Agent Framework による動的なツール選択と実行
* **型安全**: Pydantic による厳密な型チェック

### 環境変数の設定

Agent Framework を使用する場合、以下の環境変数が必要です：

```bash
# Azure OpenAI 設定
export AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com"
export AZURE_OPENAI_CHAT_DEPLOYMENT_NAME="gpt-4o-mini"
export AZURE_OPENAI_API_KEY="<your-api-key>"

# または Azure CLI 認証を使用
# az login
```

### エージェント設定例

`agents/deep_research/config.yaml`:

```yaml
name: deep-research
roles:
  - researcher
  - fact_checker
  - writer
memory:
  short_term: inproc_cache
  long_term:
    type: azure_ai_search
    index: agent-mem-long
tools:
  - web_search_bing
  - browser_safe
  - rag_corpus
  - mcp_jira
policies:
  domain_allowlist: ["*.gov", "*.ac.jp", "*.co.jp", "*.microsoft.com"]
  require_citations: true
  human_approval:
    steps: ["external_data_export", "suspicious_domain"]
observability:
  tracing: opentelemetry
  logging: json
  prompt_versioning: enabled
```

---

## 💾 メモリ設計（短期/長期）

### 短期メモリ（セッション）

* **用途**：対話ウィンドウ最適化、Tool 結果の要点キャッシュ、プラン進行のステート
* **実装**：In-proc / Redis / Cosmos DB（TTL 付き）
* **保持期間**：セッション終了まで、または設定された TTL

### 長期メモリ（知識）

* **用途**：
  * タスク汎用の知識（社内ノウハウ、ナレッジ記事、FAQ）
  * ユーザ/案件プロファイル
  * 過去の調査結果とCitations
* **実装例**：
  * Azure AI Search（ベクタ/ハイブリッド検索）
  * Cosmos DB + Vector Search
  * Blob + embeddings
* **運用**：
  * 保持期間・Purge API
  * エクスポート/監査
  * PII マスキング

---

## 📊 オブザーバビリティ

### トレーシング

* **OpenTelemetry** で API→Worker→エージェント→ツール呼び出しまでを分散トレース
* スパン属性にトークン数、コスト、実行時間を記録

### ログ

* **構造化 JSON ログ**
* プロンプト/応答の要約ログ（機微情報はマスク）
* 失敗時の最小再現ログ
* PII 検出と自動マスキング

### メトリクス

* トークン/コスト
* ジョブ成功率
* 再試行率
* SLA 指標（待ち時間/実行時間）

### ダッシュボード

* Application Insights ワークブック
* Azure Monitor ダッシュボード
* （任意）Grafana

---

## ⏱️ 長時間ジョブ設計

### 戦略

* **ステートマシン**（`orchestrations/workflows`）でステップを分離
* **チェックポイント**（中間成果/計画/メモリ）を永続化 → 再開可能
* **並列サブタスク**（ソース毎の収集/検証/要約）＋ 合流時の一貫性検証
* **Human-in-the-loop**：危険操作・外部公開前に承認

### 実装部品

* Service Bus（キュー/トピック）
* ワーカー水平スケール
* 再試行/デッドレター
* チェックポイントストレージ（Blob/Cosmos DB）

---

## 🔒 セキュリティ / ガバナンス

### 認証/認可

* **Entra ID**（API → App Roles/Scopes、ユーザ/アプリ分離）
* **Managed Identity**（クラウド間資格情報）

### ネットワーク

* Private Link / NSG / Firewall（必要に応じて）
* Egress コントロール（到達可能ドメイン制御）

### データ保護

* **Key Vault**（Secrets/Keys/Certs）
* SAS/ACL
* ストレージ暗号化
* 監査ログ

### AI安全性

* ツール実行許可リスト
* 出力フィルタ
* 著作権/帰属
* Citations 必須化
* コンテンツフィルタリング

---

## 🚢 デプロイ（IaC）

### Azure リソースのデプロイ

```bash
# リソース一式（AI Foundry, App Insights, Service Bus, Storage, AI Search, Key Vault, App Service）
az deployment group create \
  -g <RESOURCE_GROUP> \
  -f infra/bicep/main.bicep \
  -p environment=dev location=japaneast
```

デプロイ後、`.env` へ出力値（接続文字列、エンドポイント、MI/Client ID 等）を反映

### CI/CD

GitHub Actions / Azure DevOps のパイプライン例は `infra/pipelines/` を参照

---

## ⚙️ 設定（環境別）

環境別設定ファイル：
* `infra/configs/dev.json`
* `infra/configs/stg.json`
* `infra/configs/prd.json`

### 代表的な環境変数

* `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`（または MI）
* `SERVICE_BUS_CONNECTION`, `STORAGE_ACCOUNT`, `AI_SEARCH_ENDPOINT/KEY`
* `APPINSIGHTS_CONNECTION_STRING`, `KEYVAULT_URI`
* `ENTRA_TENANT_ID`, `APP_CLIENT_ID`, `APP_CLIENT_SECRET`（または MI）

詳細は `.env.example` を参照

---

## 🔄 使い方（エンドツーエンド例）

1. **UI からジョブ投入**（apps/web）
2. **API が受領 → Queue に投入 → Worker がステートマシンを実行**
3. **中間成果をメモリへ格納 → パネルで進行/根拠を可視化**
4. **必要時に承認依頼 → 承認後に出力を確定**
5. **成果物（要約/表/参考URL/引用）を Blob に保管し、API が返却**

---

## 📈 評価（Evaluation）

`tests/eval/` にサンプル評価スイート

### 評価指標

* **事実整合性**（Citations 一致率）
* **再現性**（同条件での一貫性）
* **コスト/時間**
* **ユーザ満足度**

### 自動回帰テスト

計画/プロンプトの変更に対する品質モニタリング

---

## 🔧 カスタマイズのポイント

* **ドメイン拡張**：`agents/tools/` に社内API(MCP)や特化ツールを追加
* **知識ソース**：`agents/memory/` / `rag_corpus` を差し替え（SharePoint/Blob/DB）
* **ポリシー**：`agents/policies/` でドメイン許可、承認ルール、レート上限を調整
* **UI**：ダッシュボードにトレーシング/コストを重ね、運用と可視化を一体化

---

## ❓ よくある質問（FAQ）

### Q. 長時間タスクが途中で落ちたら？

A. ステートマシンのチェックポイントから再開。ワーカーは再試行ポリシーと DLQ（デッドレター）を実装。

### Q. 記憶の消去/保持期間は？

A. `.retention` ルールで TTL を設定。Purge API で選択的に削除可能。

### Q. Agent Framework への移行について

A. 本プロジェクトは Microsoft Agent Framework に移行済みです。詳細は [Agent Framework 移行ガイド](docs/AGENT_FRAMEWORK_MIGRATION.md) を参照してください。環境変数 `USE_AGENT_FRAMEWORK=false` を設定することで、レガシー実装も使用可能です。

### Q. Agent Framework を使用するメリットは？

A. 
- 統合された API と一貫したパターン
- エンタープライズグレードの機能（型安全、テレメトリ、状態管理）
- マルチエージェント オーケストレーションの組み込みサポート
- Microsoft の継続的なサポートとアップデート
- AutoGen と Semantic Kernel のベストプラクティスの統合

### Q. コスト管理は？

A. トークン/呼び出し/時間をメトリクス化し、ダッシュボードで可視化。上限超過時は計画を自動簡略化。

### Q. プロダクション環境への移行は？

A. 環境別設定（`infra/configs/`）を使用し、段階的にデプロイ。詳細は `docs/operations_runbook.md` を参照。

---

## 🗺️ ロードマップ（Roadmap）

* [ ] 研究計画の自動分解と**根拠リンク必須**テンプレート強化
* [ ] Citations の自動抽出精度向上（パッセージレベル）
* [ ] 評価スイート拡充（ドメイン別：法務/医療/製造）
* [ ] Web UI の承認ワークフロー（Slack/Teams 連携）
* [ ] プロンプトフローの A/B テスト & Canary 配信
* [ ] マルチモーダル対応（画像/PDF/動画解析）
* [ ] エージェント協調の最適化（自動ロール割り当て）

---

## 📄 ライセンス / 注意事項

* 本アクセラレータはサンプル実装です。実運用前に組織の**セキュリティ/法令/コンプライアンス**基準に適合させてください。
* 外部サイトの利用規約/著作権/ロボッツポリシーに留意し、**スクレイピング/二次利用**の可否を確認してください。
* AI モデルの出力は必ずしも正確ではありません。重要な意思決定には人間の検証を組み込んでください。

---

## 🤝 コントリビューション

プルリクエストを歓迎します。大きな変更の場合は、まず Issue を開いて変更内容を議論してください。

---

## 📚 関連リンク

* [Microsoft Agent Framework](https://github.com/microsoft/autogen)
* [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-services/)
* [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
* [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

---

**作成者**: ishidahra01  
**ライセンス**: MIT