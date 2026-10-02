# ArrowNavi ランディングページの保守

## 公開範囲と状態

この静的サイトでは、日本語・英語・韓国語をそれぞれ /ArrowNavi/、/ArrowNavi/en/、/ArrowNavi/ko/ で配信します。プライバシーポリシー、サポート、方角ヘルプは既存の日本語ページを維持し、英語・韓国語ページでは日本語で提供していることを表示します。

PR段階ではPagesへの公開と公開後の計測は未実施です。韓国語Webページの追加は、App Store Connectの韓国語ストアフロントのローカライズや配信設定を意味しません。このWeb変更ではASCの韓国語項目を確認・変更していないため、ASC側の状態はApp Store Connectで別途確認してください。

## スクリーンショットの出典と更新

画像はArrowNaviアプリリポジトリの正式なiPhone提出素材を加工せずにコピーしています。

- Source repository: tappe9/ArrowNavi
- Source commit: 9b6a010f8882118f87ad6783be4838cf76cca9cf
- 日本語: doc/app-store/screenshots/current/ja/iphone/01-direction.png
  - SHA-256: 2469994a6a29b672a85ad276d15b5b9bbafa6cb07faa29b79cab0c4689382e72
- 英語: doc/app-store/screenshots/current/en-US/iphone/01-direction.png
  - SHA-256: 7f60fe4535537811ab48d4ee193479df0f29f5f1856ac6b3cd3f512ac117d717
- 韓国語: doc/app-store/screenshots/current/ko/iphone/01-direction.png
  - SHA-256: c0e32742bf86dad514edfbb4ae281cee61189392c80223437a0fc5b3b6ede60f

サイト内のコピー先は ArrowNavi/assets/{ja,en,ko}-direction.png です。更新時はArrowNaviリポジトリの承認済みcurrent素材を選び、次の対応でコピーしてSHA-256を確認します。

    cp "$ARROWNAVI_REPO/doc/app-store/screenshots/current/ja/iphone/01-direction.png" ArrowNavi/assets/ja-direction.png
    cp "$ARROWNAVI_REPO/doc/app-store/screenshots/current/en-US/iphone/01-direction.png" ArrowNavi/assets/en-direction.png
    cp "$ARROWNAVI_REPO/doc/app-store/screenshots/current/ko/iphone/01-direction.png" ArrowNavi/assets/ko-direction.png
    shasum -a 256 ArrowNavi/assets/{ja,en,ko}-direction.png

更新した場合はアプリ側のcommit SHA、source path、コピー後の各hashをこの文書に記録してください。画像はロケールごとに1枚、1284×2778 px、512 KiB以下を維持し、App Store Connectへの登録にはアプリリポジトリのcurrent素材を使います。

## ローカル検証

サイトリポジトリのルートで実行します。

    python3 -m unittest discover -s tests -v
    git diff --check
    python3 -m http.server 8000

HTTPサーバー起動後、ブラウザで次の3ページと画像を確認します。

    http://127.0.0.1:8000/ArrowNavi/
    http://127.0.0.1:8000/ArrowNavi/en/
    http://127.0.0.1:8000/ArrowNavi/ko/

表示確認では320 px / 390 px / 広い画面、ライト/ダーク、文字拡大、Tabキーのフォーカス、言語切替とリンクを確認します。専用CSSは既存 assets/site.css の配色tokenを使います。

## 公開後の確認と計測

公開は別途承認後に行います。承認された場合はmainへのmerge後にGitHub Pagesのdeployment完了を確認し、公開URLへ新しいHTTPリクエストを行ってからブラウザで3言語の表示・リンク・画像を確認します。PR段階の確認を公開後の証拠として扱いません。

計測は公開後の別作業です。まずmainへのmerge前に、比較するbaselineの日付範囲（28〜56日）を決め、App Store ConnectでWeb参照元のインプレッション、初回ダウンロード、conversionを記録します。Appleが表示するconversionと独自に算出した率を使う場合は、分けて記録し、分母も明記します。公開後28〜56日が経過したら、同じ期間幅とWeb参照元条件で同じ指標を比較し、母数が少ない場合は率だけでなく絶対件数も併記します。analyticsやCookieを使わないためページ内CTAクリック数は取得できず、少ないデータから因果を断定しません。韓国語Webページの公開とASC韓国語ロケールの状態は別々に記録します。
