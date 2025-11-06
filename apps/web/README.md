# Enterprise Agent Framework - Web UI

シンプルなダッシュボードUIを提供します。

## 開発環境のセットアップ

```bash
cd apps/web
npm install
npm run dev
```

ブラウザで http://localhost:3000 を開く

## 機能

- ジョブ投入フォーム
- ジョブ一覧表示
- ステータスリアルタイム更新
- 結果の表示
- Citations の可視化

## プロダクションビルド

```bash
npm run build
npm start
```

## 環境変数

`.env.local` ファイルを作成:

```
NEXT_PUBLIC_API_URL=http://localhost:8080
```
