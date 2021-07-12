# Python の Docker イメージを指定
FROM python:3.8

# wget をインストール
# RUN apt-get update && apt-get install -y wget

# CloudWatch エージェントをダウンロード/インストールする
# RUN wget https://s3.ap-northeast-1.amazonaws.com/amazoncloudwatch-agent-ap-northeast-1/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm && \
#     rpm -U ./amazon-cloudwatch-agent.rpm && \
#     rm rf /tmp/* && \


# ファイルを /app ディレクトリに追加
COPY script.py /app/

# requirements.txt を /usr/src/ ディレクトリに追加
COPY requirements.txt /usr/src/

# 依存ライブラリをインストールする
RUN pip install --no-cache-dir -r /usr/src/requirements.txt

# ルートディレクトリ設定
WORKDIR /app

# コマンド実行
CMD ["python", "script.py"]