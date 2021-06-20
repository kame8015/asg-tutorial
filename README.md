# SQS を用いたスケーリング

## Lambda と IAM Role を作成する

`/cfn/sqs-lambda.template.yml` を使ってスタックを作成

### 作成した Lambda に awscli を使ってテストを投げてみる

```
$ aws lambda invoke --invocation-type RequestResponse \
    --function-name tst-dva-lambda-sqs \
    --payload file://input.json outputfile.json \
    --cli-binary-format raw-in-base64-out \
    --profile {prifile_name}
```

レスポンスは以下の通り

```
{
    "StatusCode": 200,
    "ExecutedVersion": "$LATEST"
}
```

CloudWatch ロググループも参照して、きちんと `test` という文字列が出力されていることを確認  
ロググループ名は `/aws/lambda/tst-dva-lambda-sqs` となっている

### SQS と EventSourceMapping を作成する

キューイングを行う SQS と、  
SQS にメッセージが積まれたら Lambda が起動するように EventSourceMapping を作成する  
`/cfn/sqs-mapping.template.yml` を使ってスタックを作成

マネジメントコンソールから SQS が作成されていることと、  
Lambda の画面でトリガーに SQS が紐付けられていることを確認

### boto3(Python SDK) を使って SQS にメッセージを投げる

```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python send_message.py # profile_name は適宜変更のこと
```

send_message の成功レスポンスが返ってくることを確認

CloudWatch ロググループを参照して、`Hello, SQS!` が出力されていることを確認  
SQS のキューにはメッセージが残っていないことを確認

---

## EC2 AutoScalingGroup を作成して SSH 接続したりメトリクスを収集する

参考：[CloudFormation を用いた EC2 AutoScalingGroup スタックの作成](https://techblog.asia-quest.jp/aws/cloudformation%E3%82%92%E7%94%A8%E3%81%84%E3%81%9Fec2-autoscalinggroup%E3%82%B9%E3%82%BF%E3%83%83%E3%82%AF%E3%81%AE%E4%BD%9C%E6%88%90/)

### ネットワーク設定のスタックを作成

`/cfn/network-config.template.yml` スタックで以下のことを行う

- VPC を作る
- サブネットを切る
- インターネットゲートウェイを作る
- VPC にインターネットゲートウェイをアタッチする
- ルートテーブルを作る
- ルートテーブルにインターネットに出られるように設定を行う
- サブネットにルートテーブルを関連付ける
- 特定の IP アドレスからの SSH 接続を許可するセキュリティグループを作る
- 作ったリソースを他のスタックが参照できるようにする

1. 自分のグローバル IP アドレスを確認  
   https://www.cman.jp/network/support/go_access.cgi

1. SSHSecurityGroup の CidrIp に自分のグローバル IP アドレスを記述

1. `asg-tutorial-network-config` という名前でスタックを作成する

### 起動設定と AutoScalingGroup のスタックを作成

`/cfn/autoscaling-group.template.yml`スタックで以下のことを行う

- 起動設定を作る
  - AMI は Amazon Linux AMI
  - インスタンスタイプは`t2.micro`
  - 作成したセキュリティグループと関連付ける
- AutoScalingGroup を作る
  - 作成したサブネットと関連付ける
  - インスタンスは 1 つだけ起動する
  - 作成したインスタンスは名前をつける

1. AWS マネジメントコンソールから `asg-tutorial-key` という名前のキーペアを作成する
   - 自動保存された秘密鍵を移動させて SSH 接続できるように準備をする
     ```
     $ cd Downloads/
     $ mv asg-tutorial-key.pem ~/.ssh/
     $ chmod 600 ~/.ssh/asg-tutorial-key.pem
     ```
1. `asg-tutorial-autoscaling` という名前でスタックを作成する
   - 作成したキーペアをパラメータとして選択する
1. AWS マネジメントコンソールから EC2 インスタンスが起動していることを確認する
1. EC2 インスタンスに SSH 接続する  
   EC2 インスタンスのパブリック DNS をコピーしておく
   ```
   $ ssh -i ~/.ssh/asg-tutorial-key.pem ec2-user@{public_dns}
   ```
1. CloudWatch メトリクスに ASG のメトリクス(InService となっているインスタンス数)が出力されていることを確認する

### CloudWatch Alarm を作成する

事前に SQS と AutoScalingGroup を作成しておく

`/cfn/alarm.template.yml` スタックで以下のことを行う

- SQS のメッセージ数と AutoScalingGroup の稼働中のインスタンス数を比較し、  
   メッセージ数の方が大きくなったらアラームを発火する

1. `tst-dva-alarm` という名前でスタックを作成する
1. アラームが作成されていることを確認し、アラームメトリクスの値として -1 が入っていることを確認する
1. SQS にメッセージを積む
1. アラームメトリクスの値が 0 になったことを確認する
1. SQS にメッセージをもう一つ積む
1. アラームメトリクスの値が 1 になり、アラーム状態に遷移することを確認する
1. ASG の DesiredCapacity を 2 にして、インスタンスが立ち上がることを確認する
1. アラームメトリクスの値が 0 になり、OK 状態に遷移することを確認する
