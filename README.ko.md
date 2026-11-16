# geo-audit

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md) | **한국어** | [Deutsch](README.de.md) | [Français](README.fr.md) | [Español](README.es.md)

오픈 Agent Skills 형식의 skill입니다. URL만으로 하나 이상의 국가·언어 시장에서 웹사이트가 AI 검색(ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Doubao, DeepSeek, Naver AI 브리핑, Le Chat 등)에 어떻게 노출되는지 외부에서 감사하고, 모든 권고에 연구 근거의 강도를 표시한 개선 보고서를 만듭니다. 보고서는 사용자가 질문한 언어로 작성됩니다.

- 프로필이 있는 시장: 중국 `cn`, 미국 `us`, 일본 `jp`, 한국 `kr`, 독일 `de`, 프랑스 `fr`, 스페인어권 `es`. 그 밖의 시장은 범용 프로필을 사용합니다

## 설치

```bash
# 현재 저장소에 설치 (Claude Code는 .claude/skills, Codex와 Cursor는 .agents/skills를 읽습니다)
bash geo-audit/install.sh

# 홈 디렉터리에 설치 (모든 프로젝트에서 사용)
bash geo-audit/install.sh --user

# 다른 프로젝트에 설치
bash geo-audit/install.sh --project /path/to/project

# Cursor 전용 .cursor/skills에도 링크 추가 (보통 불필요. Cursor는 .agents/skills와 .claude/skills도 읽습니다)
bash geo-audit/install.sh --tools claude,agents,cursor
```

설치 스크립트는 심볼릭 링크만 만들며, 같은 이름의 기존 파일이나 디렉터리를 덮어쓰지 않습니다.

## 도구별 사용법

자연어로 요청하면 됩니다. 예: "https://example.com 의 GEO 감사를 해 주세요. 대상 시장은 한국과 미국입니다"

| 도구 | 설명 |
|---|---|
| Claude Code | 바로 사용할 수 있습니다. |
| Codex CLI | 웹 검색과 샌드박스 네트워크 접근을 켜야 합니다. 그렇지 않으면 스크립트가 페이지를 가져오지 못하고 사이트 외부 조사도 할 수 없습니다: `codex --search exec -s workspace-write -c sandbox_workspace_write.network_access=true "<요청 내용>"` (대화형 모드도 같습니다: `codex --search -s workspace-write -c sandbox_workspace_write.network_access=true`) |
| Cursor | Cursor 공식 디렉터리 규칙에 따라 설치합니다 (`.agents/skills` / `.claude/skills` / `.cursor/skills`). **Cursor에서는 아직 테스트하지 않았습니다.** |

## 요구 사항

- Python 3.10 이상 (표준 라이브러리만 사용)
- 선택: 렌더링 비교용 Chrome / Chromium. 환경 변수 `GEO_BROWSER`로 브라우저 경로를 지정할 수 있습니다

## 스크립트 단독 실행

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com --markets jp,us
python3 geo-audit/scripts/page_audit.py https://example.com/ja/ --lang ja-JP --save-html out/html
python3 geo-audit/scripts/render_diff.py https://example.com/ja/ --lang ja-JP --timeout 30
# 특정 국가에서의 접속 가능 여부를 확인할 때는 그 국가의 출구 프록시를 쓸 수 있습니다 (속도 제한 회피용으로는 쓰지 마세요)
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://<프록시>:<포트>
```

## 테스트

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
