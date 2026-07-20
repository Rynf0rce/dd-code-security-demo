# EKS 런타임 데모 배포 절차

`jinwoo-eks-cluster` (ap-northeast-3) 기준.

## 0. 사전 확인

```bash
aws-azure-login --profile jinwoo --mode gui     # 자격증명 갱신
kubectl config use-context arn:aws:eks:ap-northeast-3:782621889128:cluster/jinwoo-eks-cluster
kubectl get nodes
```

## 1. Datadog Agent 설치

**⚠️ `DD_SITE` 와 API Key 가 `DPN | GS Neotek` org 의 것인지 반드시 확인하십시오.**
9개 KT/DPN org 가 모두 `us3.datadoghq.com` 을 공유하므로 사이트 값만으로는
org 가 구분되지 않습니다. 잘못된 org 로 가도 **에러 없이 조용히** 들어갑니다.

```bash
helm repo add datadog https://helm.datadoghq.com
helm repo update

# 릴리스 이름(datadog)을 반드시 지정할 것 —
# 생략하면 "must either provide a name or specify --generate-name" 에러
helm install datadog datadog/datadog -f <values.yaml>
```

기존 `no_proxy_values.yaml` 을 재사용할 경우 EKS 용으로 아래를 수정해야 합니다:

| 항목 | 현재 (AKS 용) | EKS 용 |
|---|---|---|
| `providers.aks.enabled` | `true` | 제거 |
| `datadog.tags` | `dd-jinwoo-aks` | 데모용 태그로 변경 |
| `datadog.apiKey` | 평문 | `datadog.apiKeyExistingSecret` 권장 |

API Key 를 Secret 으로 분리하는 방법:

```bash
kubectl create secret generic datadog-secret \
  --from-literal api-key=<DPN org API key>
# values 에서:  datadog.apiKeyExistingSecret: datadog-secret
```

설치 확인:

```bash
kubectl get pods -l app=datadog
kubectl exec -it <datadog-agent-pod> -- agent status | grep -A5 "APM Agent"
```

## 2. 이미지 빌드 & 푸시

```bash
export AWS_ACCOUNT=782621889128
export REGION=ap-northeast-3
export REPO=gseps-inspection-api

aws ecr create-repository --repository-name $REPO --region $REGION || true
aws ecr get-login-password --region $REGION \
  | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com

IMAGE=$AWS_ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$REPO:1.0.0

# EKS 노드가 amd64 이면 플랫폼을 명시해야 합니다 (Apple Silicon 빌드 주의)
docker build --platform linux/amd64 -f Dockerfile.runtime -t $IMAGE .
docker push $IMAGE
```

## 3. 앱 배포

```bash
sed "s|__IMAGE__|$IMAGE|" k8s/deployment.yaml | kubectl apply -f -
kubectl -n gseps-demo rollout status deploy/gseps-inspection-api
kubectl -n gseps-demo logs deploy/gseps-inspection-api | head -30
```

`[db_init] 준비 완료` 로그가 보여야 정상입니다.

## 4. 취약점 트리거

```bash
kubectl -n gseps-demo port-forward svc/gseps-inspection-api 8080:80 &

# 정상 요청 — 먼저 트레이스를 만들어 서비스가 APM 에 등록되게 합니다
curl "http://localhost:8080/api/equipment?plant=A1"

# SQL Injection — IAST 가 taint 를 추적해 탐지
curl "http://localhost:8080/api/equipment?plant=A1%27%20OR%20%271%27%3D%271"

# 취약한 해시(MD5)
curl -X POST -d "pin=123456" http://localhost:8080/api/operator/auth

# SSTI
curl "http://localhost:8080/api/report?title=%7B%7B7*7%7D%7D"
```

IAST 는 요청 샘플링이 걸려 있으므로 **각 요청을 여러 번 반복**하십시오.

## 5. Datadog 에서 확인

| 대상 | 위치 |
|---|---|
| 서비스 등록 | APM > Services > `gseps-inspection-api` |
| Runtime Code Vulnerabilities (IAST) | Security > Code Security > Vulnerabilities |
| Runtime SCA | Security > Code Security > Vulnerabilities > Library |

정적 스캔 결과와 나란히 놓고 **"repo 스코프 vs 서비스 스코프"** 차이를 설명하는 것이
이 구간의 핵심입니다.

## 정리

```bash
kubectl delete namespace gseps-demo
helm uninstall datadog
```
