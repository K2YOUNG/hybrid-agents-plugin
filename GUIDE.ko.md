# hybrid-agents 처음 쓰는 사람을 위한 안내

이 플러그인에는 `hybrid-agent-orchestrator` 스킬 하나가 들어 있습니다. Claude Code에서 이 스킬을 부르면 메인 에이전트가 일을 나눕니다. 코딩, 글쓰기, 그림, 반복 작업을 미리 정해 둔 에이전트(Claude, Codex, agy, Copilot)에게 맡기고 결과는 메인 에이전트가 직접 확인합니다.

## 에이전트에게 설치 맡기기

Claude Code(또는 다른 코딩 에이전트)에 아래 문장을 붙여 넣습니다.

```
https://github.com/K2YOUNG/hybrid-agents-plugin/blob/main/GUIDE.ko.md 를 따라 hybrid-agents 플러그인을 설치하고 설정해줘. 명령은 직접 실행하고 내가 해야 할 일이 생기면 멈추고 알려줘.
```

## AI 에이전트가 읽을 부분

사용자가 이 안내를 건넸다면 아래 순서로 설치를 진행합니다.

1. "준비물"의 `--version` 명령을 실행하고 빠진 에이전트 CLI를 사용자에게 알립니다. 사용자가 요청하기 전에는 설치하지 않습니다.
2. 1단계의 두 명령을 실행하고 2단계의 `claude plugin list`로 `hybrid-agents`가 설치됐는지 확인합니다.
3. 여기서 멈춥니다. 사용자에게 Claude Code를 끄고 같은 폴더에서 `claude -c`로 다시 켜 달라고 요청합니다. 이렇게 하면 플러그인이 불러와진 상태로 이 대화가 다시 열립니다. 에이전트는 자기 세션을 직접 재시작하지 못합니다.
4. 재시작 뒤에는 `/hybrid-agents:hybrid-agent-orchestrator <할 일>` 같은 첫 요청을 제안합니다. 설정 질문은 스킬이 직접 묻습니다. 답은 사용자가 고르게 하고 대신 고르지 않습니다.

아래 일은 사용자에게 넘기고 기다립니다.

- Codex, agy, Copilot 로그인 (직접 입력이 필요합니다)
- 3번의 재시작
- 4번의 설정 질문
- 다른 에이전트가 전달받은 지시를 거절할 때 그 에이전트 창에서 하는 확인

비밀번호나 토큰은 사용자 대신 입력하지 않습니다.

## 준비물

- Claude Code (설치와 로그인까지 끝난 상태)
- 일을 맡길 에이전트의 CLI. 쓰려는 것만 있으면 됩니다.
  - Codex CLI (`codex`)
  - Antigravity CLI (`agy`)
  - GitHub Copilot CLI (`copilot`)
- Python 3

터미널에서 설치 여부를 확인합니다. 버전이 나오면 설치된 것입니다.

```
claude --version
codex --version
agy --version
copilot --version
python3 --version
```

herdr는 없어도 됩니다.

## 1단계. 플러그인 설치

터미널에서 아래 두 줄을 실행합니다.

```
claude plugin marketplace add K2YOUNG/hybrid-agents-plugin
claude plugin install hybrid-agents@hybrid-agents
```

Claude Code가 켜져 있었다면 껐다가 다시 켭니다.

## 2단계. 설치 확인

```
claude plugin list
```

목록에 `hybrid-agents`가 있으면 설치가 끝났습니다.

## 3단계. 첫 실행과 역할 정하기

Claude Code에서 스킬 이름 뒤에 할 일을 적습니다.

```
/hybrid-agents:hybrid-agent-orchestrator 이 저장소 README를 처음 쓰는 사람 기준으로 다시 써줘
```

처음 한 번은 일을 시작하기 전에 세 가지를 묻습니다.

1. **메인 에이전트**: 일을 나누고 결과를 검사하는 에이전트입니다. 기본값은 스킬을 부른 에이전트(`invoker`)입니다.
2. **일마다 맡을 에이전트**: `claude`, `codex`, `agy`, `copilot` 중에서 고릅니다.

   | 일 | 하는 일 | 기본값 |
   | --- | --- | --- |
   | `coding` | 코드 작성, 버그 수정 | `claude` |
   | `prose` | 논문, 보고서, README 같은 글 | `agy` |
   | `design` | 그림, 슬라이드, HTML 페이지 | `codex` |
   | `bulk` | 긴 로그 요약이나 테스트 대량 생성 같은 반복 작업 | `agy` |
   | `review` | 다른 에이전트 결과의 두 번째 검토 | `codex` |

3. **실행 중인 에이전트 사용 여부**: `ask`는 매번 물어보고(기본값) `new`는 항상 새 세션을 엽니다.

잘 모르겠으면 "기본값으로 해줘"라고 답하면 됩니다. 설치하지 않은 에이전트에는 역할을 주지 마세요. 답은 `~/.config/hybrid-agents/config.json`에 저장되고 다음부터는 묻지 않습니다.

## 4단계. 실행 중인 에이전트 고르기

`ask`로 정했다면 다른 에이전트에게 일을 넘기기 전에 지금 켜져 있는 에이전트 목록을 보여 주고 고르게 합니다. 목록에는 이름, 위치, 상태(`idle`, `working` 등), 작업 폴더가 나오고 마지막 항목은 "새 세션 시작"입니다.

- 켜져 있는 에이전트를 고르면 그 에이전트가 하던 대화에 이어서 일을 받습니다.
- 켜져 있는 에이전트가 없거나 이번 요청은 새 세션으로 하겠다고 말하면 묻지 않고 새 세션을 엽니다.
- 목록은 Herdr 앱(`hc`)과 herdr에서 돌고 있는 에이전트, Remote Control로 연결된 Claude 세션에서 가져옵니다. 이 도구들을 쓰지 않으면 늘 새 세션이 열립니다.
- 한 번 고른 에이전트는 그 요청이 끝날 때까지 다시 묻지 않고 씁니다.
- 고른 에이전트가 "사용자 확인이 필요하다"며 일을 받지 않기도 합니다. 다른 에이전트가 전한 지시는 바로 따르지 않게 설정된 경우입니다. 그 에이전트 창에 직접 한 줄 확인해 주면 됩니다.

## 5단계. 결과 받기

메인 에이전트는 맡긴 일의 결과를 직접 확인하고 나서 보고합니다. 코드는 diff를 보고 테스트를 돌립니다. 글은 숫자와 인용을 원본 파일과 대조하고 그림은 렌더링해서 숫자와 라벨을 봅니다. 마지막 보고에는 누가 무엇을 만들었는지, 무엇을 확인했고 무엇을 확인하지 못했는지가 들어갑니다.

## 요청 예시

| 요청 | 맡는 역할 |
| --- | --- |
| "로그인 버그 고쳐줘" | `coding` |
| "실험 결과로 논문 4장 초안 써줘" | `prose` |
| "`results.csv`로 막대그래프 SVG 만들어줘" | `design` |
| "`logs/` 폴더 로그 전부 요약해줘" | `bulk` |
| "이 변경 사항 한 번 더 검토해줘" | `review` |

글쓰기를 다른 에이전트가 맡으면 메인 에이전트는 본문을 직접 쓰지 않습니다. 쓸 내용(brief)과 숫자·출처 목록(fact pack)을 넘기고 초안이 오면 사실만 검토합니다.

"이번 글은 Codex가 써줘"처럼 요청에 직접 적으면 저장된 설정보다 그 말이 우선합니다. 이 효과는 그 요청에만 적용됩니다.

## 설정 바꾸기

Claude Code에서 말로 요청하면 됩니다.

- "hybrid-agent-orchestrator 역할 설정에서 coding을 codex로 바꿔줘"
- "hybrid-agent-orchestrator 역할 설정을 처음부터 다시 할래"

`~/.config/hybrid-agents/config.json` 파일을 지워도 다음 실행 때 처음부터 다시 묻습니다.

## 자주 생기는 문제

- **맡긴 에이전트를 쓸 수 없을 때** (사용량 초과, 로그인 만료, 시간 초과 반복): 정해진 순서로 다음 에이전트에게 넘어갑니다. 글은 agy → Codex → Claude, 그림은 Codex → agy → Claude, 반복 작업은 agy → Codex → Claude 순서입니다.
- **herdr가 없을 때**: 문제없습니다. 이 단계를 건너뛰고 일회성 CLI 호출이나 공유 마크다운 메일박스로 일을 주고받습니다.
- **agy가 파일을 쓰지 못할 때** (종료 코드 15): `~/.gemini/antigravity-cli/settings.json`의 `permissions.allow`에 `write_file(<폴더>)` 규칙을 추가합니다.

## 업데이트와 삭제

```
claude plugin marketplace update hybrid-agents
claude plugin update hybrid-agents@hybrid-agents
```

```
claude plugin uninstall hybrid-agents@hybrid-agents
```

저장한 역할 설정까지 지우려면 `~/.config/hybrid-agents/config.json`도 삭제합니다.
