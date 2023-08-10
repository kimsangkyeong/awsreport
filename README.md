# AWS Resource 현황파악용 자동화 Tool (AWS 리소스 정보 -> Excel 저장)
## 아키텍처
- awsreport 프로그램 구성도

![awsreport 프로그램 구성도](/image/awsreport_architecture.png)

### 특징

```
1. AWS의 현재 구성정보를 Boto3 SDK의 API를 이용하여 python으로 스냅샷 현황 정보를 엑셀로 생성한다.
2. 리소스 정보를 excel의 sheet로 분리하여 단순하게 리소스 정보 확인할 수 있다.
3. 개별 리소스의 경우 운영자의 관점에서 조회된 리소스와 참조 리소스의 정보를 논리적으로 이해할 수 있도록
   리소스의 Tag Name 정보를 함께 목록으로 제공하고 있다.
   (복수의 리소스 관리 정보를 빠르게 매핑하기 위해 Pandas의 DataFrame을 활용하였음) 
```

### 추가개발 필요내용
1. 리소스 갯수가 100개 이내 수준으로 1회 리소스 API를 호출하여 정보를 추출했으나, 대량의 리소스인 경우를 위해 Loop 처리하도록 기능 개선일 필요하다.
2. 주요하게 사용되는 OnLine 업무 서비스 수준의 리소스를 대상으로 추출하고 있는데, Data 분석용 리소스에 대하여 추가 개발이 필요하다.

### 산출물
- Python 프로그램
- 실행 방법 :  python awsreport.py

### 산출물 스크린샷
- awsreport 예시 - router

![awsreport 예시 - route](/image/awsreport_example_route.JPG)

- awsreport 예시 - subnet
![awsreport 예시 - subnet](/image/awsreport_example_subnet.JPG)

### 참고자료
1. [Python용 AWS SDK(Boto3)](https://aws.amazon.com/ko/sdk-for-python/)
2. [md 작성가이드](https://www.markdownguide.org/)

