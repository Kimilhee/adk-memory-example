# AI Lamp POC Agent Engine 생성

# 환경 설정.

# gcloud config list 명령으로 아래와 같이 원하는 account와 project가 설정 되어 있어야 함!

account = software@knowre.com
project = ai-lamp-poc-dev

# 설정되어 있지 않으면 아래 명령어를 순서대로 실행하면 됨.

# 로그인 & ADC 설정(표준 모드에서 권장) - 아래 둘다 브라우저 띄워주는데 해당 계정에서 승인하면 됨.

gcloud auth login
gcloud auth application-default login

# 보유 프로젝트 나열(IDs 컬럼 확인)

gcloud projects list

gcloud config list

# 기본 프로젝트로 설정

gcloud config set project <YOUR_PROJECT_ID>
gcloud config list

# 추가로 set-quota-project 도 설정함.

gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>

# 그리고 원하는 세팅한 프로젝트를 환경변수에 직접 설정해줘야 함. (.env 로 설정해도 됨.)

os.environ["GOOGLE_CLOUD_PROJECT"] = "ai-lamp-poc-dev"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
