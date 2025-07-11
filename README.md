# 💻 Research-WebAppFlaskBusStopInfo

## Preview

![Preview](./Preview.png)

- ## Introduction

    > Flask, jinja, json 으로 간단한 버스 도착 정보 웹앱 만들기

- ## Requirements  

    > Python version : 3.9.8

    ```cmd
    pip install -r requirements.txt
    ```

- ## Note

    > [StudyGuide](./StudyGuide/StudyGuide.md)  
    > pip freeze > requirements.txt  
    > 사용한 API[공공데이터 포탈] -> [서울특별시_정류소정보조회 서비스](https://www.data.go.kr/data/15000303/openapi.do)  
    > 서울 특별시 버스 정보 조회 api 발급 신청시 신청 승인이 나더라도 월요일에 제공 서비스 서버와 동기화 되기 때문에 조금 기다려야 한다.  

---

# 버스정류장 버스도착정보 웹앱 #1

## 📌 개요

- 내가 지정한 즐겨찾기 버스 정류장의 도착정보를 관리해 주는 웹앱
- data.go.kr 사이트의 버스 도착정보 API 활용

## 📌 화면 및 기능

### 인증 화면

- 로그인 / 로그아웃 / 회원가입

### 홈 화면

- 데이터베이스 ID/PW 인증
- 메인화면: ‘내 버스정류장’ 목록 (리스트형 / 카드형 / 지도(구글맵 또는 네이버맵)으로 보기)
- ‘새 정류장’ 추가 등록 버튼
- 정류장 도착정보 보기 버튼
- 정류장 ‘삭제’ 버튼
- ‘새로고침’ 버튼

### 관리 화면

- 사용자별 정류장 등록 현황 조회
- 사용자 관리 기능: 사용자 삭제 / 서비스 중지 기능

## 📌 기술 스택

- Python Flask, Jinja 템플릿
- Bootstrap (UI 프레임워크)
- SQLite (로컬 DB)
- Google Map 또는 Naver Map API 연동
- JWT 인증 (로그인/세션 관리)
- REST API 설계 및 연동

## 📌 배포 및 운영

- 리버스 프록시 서버 구성 (예: Nginx)
- Python 환경에서 Flask 애플리케이션 실행
- Uvicorn (ASGI 서버)로 배포
- Docker 컨테이너로 패키징 및 배포
