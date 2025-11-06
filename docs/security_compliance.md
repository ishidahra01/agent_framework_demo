# セキュリティとコンプライアンス

## セキュリティ原則

本システムは以下のセキュリティ原則に基づいて設計されています：

1. **Defense in Depth (多層防御)**
2. **Least Privilege (最小権限の原則)**
3. **Zero Trust (ゼロトラストモデル)**
4. **Secure by Default (デフォルトでセキュア)**

## データ分類

### データカテゴリ

| カテゴリ | 例 | 保護レベル |
|---------|-----|-----------|
| Public | 公開情報 | 低 |
| Internal | 社内ドキュメント | 中 |
| Confidential | 顧客情報 | 高 |
| Restricted | 個人情報、機密情報 | 最高 |

### PII (個人識別情報)

以下の情報は PII として扱い、特別な保護が必要：

- 氏名
- メールアドレス
- 電話番号
- 住所
- 社会保障番号
- クレジットカード情報

**保護措置**:
- ログ出力時の自動マスキング
- 暗号化保存
- アクセス制御
- 監査ログ

## 認証と認可

### Microsoft Entra ID (Azure AD) 統合

```yaml
認証フロー:
  1. ユーザーログイン → Entra ID
  2. トークン取得 (OAuth 2.0)
  3. API 呼び出し時にトークン検証
  4. ロール/スコープに基づく認可
```

### ロール定義

| ロール | 権限 | 対象ユーザー |
|-------|------|------------|
| Reader | ジョブ閲覧のみ | 一般ユーザー |
| Contributor | ジョブ作成・閲覧 | リサーチャー |
| Approver | 承認処理 | マネージャー |
| Admin | 全権限 | システム管理者 |

### API 認証

```python
# Bearer トークン認証
Authorization: Bearer <JWT_TOKEN>

# スコープ
- read:jobs
- write:jobs
- approve:jobs
- admin:system
```

## ネットワークセキュリティ

### ネットワーク分離

```
┌─────────────────────────────────────┐
│        Public Internet              │
└─────────────┬───────────────────────┘
              │ HTTPS only
              ▼
┌─────────────────────────────────────┐
│      Application Gateway            │
│      + WAF (Web Application FW)     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│         VNet (Virtual Network)      │
│  ┌────────────────────────────────┐ │
│  │  API Subnet (NSG)              │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Worker Subnet (NSG)           │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Data Subnet (Private Link)    │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Egress コントロール

**許可ドメイン** (環境変数で設定):
- `*.gov` - 政府サイト
- `*.ac.jp` - 学術機関
- `*.microsoft.com` - Microsoft サービス
- `*.azure.com` - Azure サービス

**ブロック**:
- 上記以外のドメインへのアクセス
- ポリシー違反時のアラート

## データ保護

### 暗号化

#### 保管時の暗号化 (Encryption at Rest)

- **Azure Storage**: AES-256
- **Azure SQL Database**: TDE (Transparent Data Encryption)
- **Azure AI Search**: Microsoft managed keys
- **Key Vault**: HSM-backed keys

#### 転送時の暗号化 (Encryption in Transit)

- **TLS 1.2+** のみ許可
- 証明書検証必須
- HTTP → HTTPS リダイレクト

### シークレット管理

```bash
# Key Vault にシークレット保存
az keyvault secret set \
  --vault-name agent-kv-prd \
  --name "OpenAI-ApiKey" \
  --value "<secret-value>"

# アプリケーションから取得 (Managed Identity)
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://agent-kv-prd.vault.azure.net/", 
                      credential=credential)
secret = client.get_secret("OpenAI-ApiKey")
```

## AI セキュリティ

### プロンプトインジェクション対策

1. **入力検証**: ユーザー入力のサニタイゼーション
2. **システムプロンプト保護**: ユーザー入力と分離
3. **出力フィルタリング**: 機微情報の自動削除

### コンテンツフィルタリング

Azure OpenAI の Content Safety 機能を使用:

- **Hate**: ヘイトスピーチ検出
- **Sexual**: 性的コンテンツ検出
- **Violence**: 暴力的コンテンツ検出
- **Self-harm**: 自傷行為コンテンツ検出

フィルタレベル:
- Low (0-2)
- Medium (2-4)
- High (4-6)

### Citations の検証

1. **ソース検証**: URL の有効性確認
2. **クロスリファレンス**: 複数ソースでの確認
3. **信頼性スコア**: ソースの信頼性評価
4. **日付確認**: 情報の鮮度確認

## 監査とコンプライアンス

### 監査ログ

全ての重要操作を記録:

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "user_id": "user@example.com",
  "action": "job.create",
  "resource": "job-12345",
  "result": "success",
  "ip_address": "203.0.113.1",
  "user_agent": "Mozilla/5.0..."
}
```

### 保持期間

| データ種別 | 保持期間 | 理由 |
|-----------|---------|------|
| 監査ログ | 7年 | 法的要件 |
| トランザクションログ | 90日 | 運用要件 |
| ジョブ結果 | 1年 | ビジネス要件 |
| 短期メモリ | 1時間 | パフォーマンス |

### コンプライアンスフレームワーク

#### GDPR (EU 一般データ保護規則)

- [ ] データ主体の権利 (アクセス、削除、訂正)
- [ ] データ処理の合法性
- [ ] データ保護影響評価 (DPIA)
- [ ] データ侵害通知 (72時間以内)

#### 個人情報保護法 (日本)

- [ ] 個人情報の適切な取得
- [ ] 利用目的の通知
- [ ] 安全管理措置
- [ ] 第三者提供の制限

#### SOC 2

- [ ] セキュリティ
- [ ] 可用性
- [ ] 処理の完全性
- [ ] 機密保持
- [ ] プライバシー

## インシデント対応

### インシデント分類

| レベル | 定義 | 対応時間 |
|-------|------|---------|
| P0 (Critical) | サービス停止、データ侵害 | 即時 |
| P1 (High) | 部分的な機能停止 | 1時間以内 |
| P2 (Medium) | パフォーマンス低下 | 4時間以内 |
| P3 (Low) | 軽微な問題 | 1営業日以内 |

### 対応フロー

```
1. 検知・報告
   ↓
2. トリアージ (優先度判定)
   ↓
3. 初動対応 (影響範囲の特定と隔離)
   ↓
4. 調査分析 (根本原因の特定)
   ↓
5. 復旧 (サービス回復)
   ↓
6. 事後対応 (報告書作成、再発防止)
```

### 連絡体制

- **P0/P1**: オンコールエンジニア即時対応
- **P2/P3**: 営業時間内対応
- **報告先**: セキュリティチーム、経営層

## 脆弱性管理

### 脆弱性スキャン

- **頻度**: 週次
- **ツール**: Azure Security Center, Dependabot
- **対象**: コード、依存関係、インフラ

### パッチ管理

- **Critical**: 24時間以内
- **High**: 7日以内
- **Medium**: 30日以内
- **Low**: 90日以内

## セキュリティテスト

### ペネトレーションテスト

- **頻度**: 年次
- **実施者**: 外部専門業者
- **範囲**: API、Web UI、インフラ

### セキュリティコードレビュー

- **頻度**: 全 PR
- **チェック項目**:
  - 入力検証
  - 認証・認可
  - シークレット管理
  - SQL インジェクション
  - XSS 対策

## トレーニング

全メンバーに対するセキュリティトレーニング:

- **新入社員**: 初日
- **定期研修**: 四半期ごと
- **フィッシング訓練**: 月次
- **インシデント対応訓練**: 半期ごと

## 問い合わせ先

- **セキュリティインシデント**: security-incident@example.com
- **脆弱性報告**: security-bugs@example.com
- **コンプライアンス**: compliance@example.com
