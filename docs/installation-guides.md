# Databricks MCP Server - Detailed Installation Guides

Complete setup instructions for all major MCP clients and development environments.

> **언어 / Language**: [한국어](#한국어-가이드) | [English](#english-guide)

---

## 한국어 가이드

이 가이드는 Databricks MCP 서버를 다양한 MCP 클라이언트에서 설정하는 방법을 상세하게 설명합니다.

### 목차
- [사전 준비사항](#사전-준비사항)
- [1. Claude Desktop](#1-claude-desktop)
- [2. Claude Code (CLI)](#2-claude-code-cli)
- [3. Cursor IDE](#3-cursor-ide)
- [4. Cline (VS Code 확장)](#4-cline-vs-code-확장)
- [5. Continue (VS Code 확장)](#5-continue-vs-code-확장)
- [6. Zed Editor](#6-zed-editor)
- [7. Windsurf IDE](#7-windsurf-ide)
- [8. OpenAI Codex (CLI)](#8-openai-codex-cli)
- [9. Dify](#9-dify)
- [10. n8n](#10-n8n)
- [문제 해결](#문제-해결-korean)

---

### 사전 준비사항

모든 클라이언트 설정을 시작하기 전에 다음을 준비해야 합니다:

#### 1. Python 환경 (권장)
```bash
# Python 3.10 이상 확인
python --version

# uv 설치 (권장 방법)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Databricks 인증 정보
다음 중 하나를 준비하세요:

**옵션 A: OAuth U2M (권장 - 개발용)**
- Databricks 워크스페이스 URL
- OAuth 자동 인증 (첫 실행 시 브라우저 열림)

**옵션 B: Personal Access Token (PAT)**
1. Databricks 워크스페이스 로그인
2. 우측 상단 사용자 메뉴 → Settings
3. Developer → Access tokens
4. "Generate new token" 클릭
5. 토큰 복사 및 안전하게 보관

**옵션 C: Service Principal (프로덕션용)**
- Client ID
- Client Secret
- Account Admin에게 요청하여 생성

#### 3. Databricks 워크스페이스 URL 확인
```
AWS:   https://your-workspace.cloud.databricks.com
Azure: https://adb-<workspace-id>.<random>.azuredatabricks.net
GCP:   https://<workspace-id>.gcp.databricks.com
```

#### 4. Account API 설정 (선택사항)

**Account-level 작업이 필요한 경우만 설정:**

Account API를 사용하면 다음 작업이 가능합니다:
- 여러 워크스페이스 관리
- 사용자 및 그룹 관리
- 워크스페이스 생성/삭제
- 계정 수준 권한 관리

**필수 정보:**
- `DATABRICKS_ACCOUNT_ID`: Account ID (UUID 형식)
- `DATABRICKS_ACCOUNT_HOST`:
  - AWS/GCP: `https://accounts.cloud.databricks.com`
  - Azure: `https://accounts.azuredatabricks.net`

**Account ID 확인 방법:**
1. Databricks Account Console 접속
2. 우측 상단 프로필 → Account Settings
3. Account ID 복사

**권한 요구사항:**
- Account Admin 역할 필요
- 또는 Service Principal에 Account Admin 권한 부여

**💡 팁**: Workspace-level 작업만 필요하면 Account API 설정은 건너뛰어도 됩니다.

---

### 1. Claude Desktop

Claude Desktop은 Anthropic의 공식 데스크톱 애플리케이션으로, MCP 서버를 가장 쉽게 설정할 수 있습니다.

#### 1.1 설정 파일 위치

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### 1.2 설정 파일 열기

**방법 1: Claude Desktop UI 사용**
1. Claude Desktop 실행
2. Settings (설정) 열기
3. Developer 탭 선택
4. "Edit Config" 버튼 클릭

**방법 2: 직접 파일 편집**
```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows (메모장)
notepad %APPDATA%\Claude\claude_desktop_config.json
```

#### 1.3 기본 설정 (OAuth)

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 1.4 PAT 사용 설정

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi1234567890abcdef..."
      }
    }
  }
}
```

#### 1.5 Service Principal 설정 (프로덕션)

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_CLIENT_ID": "your-service-principal-client-id",
        "DATABRICKS_CLIENT_SECRET": "your-service-principal-secret"
      }
    }
  }
}
```

#### 1.6 여러 워크스페이스 설정

```json
{
  "mcpServers": {
    "databricks-prod": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://prod-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_prod_token..."
      }
    },
    "databricks-dev": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://dev-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 1.7 Account API 설정 (Account-level 작업용)

**Account API를 사용하려면** (사용자 관리, 워크스페이스 관리 등):

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m",
        "DATABRICKS_ACCOUNT_ID": "12345678-90ab-cdef-1234-567890abcdef",
        "DATABRICKS_ACCOUNT_HOST": "https://accounts.cloud.databricks.com"
      }
    }
  }
}
```

**필수 환경 변수:**
- `DATABRICKS_ACCOUNT_ID`: Databricks Account ID (Account Console에서 확인)
- `DATABRICKS_ACCOUNT_HOST`: Account API 호스트
  - AWS/GCP: `https://accounts.cloud.databricks.com`
  - Azure: `https://accounts.azuredatabricks.net`

**Account ID 확인 방법:**
1. Databricks Account Console 로그인
2. 우측 상단 프로필 → Account Settings
3. Account ID 복사

**사용 가능한 Account-level 도구:**
- `list_account_workspaces` - 모든 워크스페이스 목록
- `create_workspace` - 새 워크스페이스 생성
- `list_account_users` - 계정 사용자 관리
- `assign_workspace_permissions` - 워크스페이스 권한 할당

⚠️ **권한 요구사항**: Account Admin 권한 필요

#### 1.8 설정 적용 및 확인

1. 설정 파일 저장
2. Claude Desktop **완전히 종료** (Cmd+Q / Alt+F4)
3. Claude Desktop 재시작
4. 새 대화 시작
5. 입력창 하단에 **🔨 아이콘** (MCP 서버 표시) 확인
6. 아이콘 클릭하여 "databricks" 서버 활성 상태 확인

#### 1.9 첫 실행 (OAuth 사용 시)

OAuth 인증을 사용하는 경우:
1. 처음 MCP 도구 사용 시 브라우저 창이 자동으로 열립니다
2. Databricks에 로그인
3. "Authorize" 클릭
4. 브라우저 탭 닫기
5. Claude Desktop으로 돌아가서 계속 사용

#### 1.10 테스트

Claude Desktop에서 다음과 같이 요청해보세요:

```
"List all my Databricks clusters"
"Show me the tables in my Unity Catalog"
"Execute this SQL: SELECT * FROM samples.nyctaxi.trips LIMIT 10"
```

---

### 2. Claude Code (CLI)

Claude Code는 터미널에서 사용하는 Anthropic의 CLI 도구입니다.

#### 2.1 설정 파일 위치

**모든 플랫폼:**
```bash
~/.config/claude/config.json
```

#### 2.2 설정 파일 생성/편집

```bash
# 디렉토리 생성
mkdir -p ~/.config/claude

# 파일 편집
nano ~/.config/claude/config.json
# 또는
code ~/.config/claude/config.json
# 또는
vim ~/.config/claude/config.json
```

#### 2.3 기본 설정

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 2.4 .databrickscfg 프로파일 사용

이미 Databricks CLI를 사용하고 있다면, 기존 설정을 재사용할 수 있습니다:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_CONFIG_PROFILE": "production"
      }
    }
  }
}
```

`~/.databrickscfg` 파일:
```ini
[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi...

[development]
host = https://dev-workspace.cloud.databricks.com
auth_type = oauth-u2m
```

#### 2.5 테스트

```bash
# Claude Code 실행
claude

# 프롬프트에서 테스트
> List my Databricks clusters
> Show tables in catalog 'main'
```

---

### 3. Cursor IDE

Cursor는 AI 기능이 통합된 코드 에디터입니다.

#### 3.1 설정 파일 위치

**프로젝트별 설정 (권장):**
```
your-project/.cursor/mcp.json
```

**전역 설정:**
```
~/.cursor/mcp.json
```

#### 3.2 UI를 통한 설정

1. Cursor 실행
2. `Cmd+,` (macOS) 또는 `Ctrl+,` (Windows/Linux) - 설정 열기
3. "Developer" 섹션 찾기
4. "Edit Config" 클릭
5. "MCP Tools" 선택
6. "Add Custom MCP" 클릭

#### 3.3 수동 설정 파일 생성

**프로젝트별 설정:**
```bash
# 프로젝트 루트에서
mkdir -p .cursor
nano .cursor/mcp.json
```

**기본 설정:**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 3.4 환경 변수 설정 (민감 정보)

토큰을 설정 파일에 직접 저장하지 않으려면:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "${DATABRICKS_TOKEN}"
      }
    }
  }
}
```

그리고 환경 변수 설정:
```bash
# ~/.bashrc 또는 ~/.zshrc
export DATABRICKS_TOKEN="dapi..."
```

#### 3.5 원클릭 설치 (Cursor 내장 기능)

Cursor의 최신 버전은 MCP 서버 마켓플레이스를 제공합니다:

1. Cursor에서 `Cmd+K` (AI 채팅 열기)
2. MCP 아이콘 클릭
3. "Browse MCP Servers" 선택
4. "databricks-mcp" 검색
5. "Install" 클릭 (사용 가능한 경우)

#### 3.6 중요 제한사항

⚠️ **현재 Cursor는 처음 40개의 도구만 에이전트에 전달합니다.**

Databricks MCP는 82개의 도구를 제공하므로, 필요에 따라 서버를 활성화/비활성화해야 할 수 있습니다.

#### 3.7 설정 확인

1. Cursor 재시작
2. AI 채팅 열기 (`Cmd+K`)
3. MCP 아이콘 확인 (활성화 시 녹색)
4. 테스트 프롬프트:
```
@databricks list my clusters
```

---

### 4. Cline (VS Code 확장)

Cline은 VS Code를 위한 강력한 AI 코딩 어시스턴트입니다.

#### 4.1 Cline 설치

1. VS Code 열기
2. Extensions (확장) 패널 열기 (`Cmd+Shift+X`)
3. "Cline" 검색
4. "Install" 클릭

#### 4.2 MCP 서버 설정 접근

**방법 1: Cline UI 사용**
1. VS Code에서 Cline 패널 열기
2. 상단 네비게이션 바에서 "MCP Servers" 아이콘 클릭
3. "Installed" 탭 선택
4. 하단의 "Configure MCP Servers" 버튼 클릭

**방법 2: 설정 파일 직접 편집**
```bash
# VS Code 설정 디렉토리
code ~/.vscode/extensions/cline/mcp_settings.json
```

#### 4.3 기본 설정

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      },
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

#### 4.4 자동 승인 설정

특정 도구를 자동으로 승인하려면:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      },
      "disabled": false,
      "alwaysAllow": [
        "list_clusters",
        "get_cluster",
        "list_jobs",
        "list_tables"
      ]
    }
  }
}
```

#### 4.5 Transport 타입

Cline은 두 가지 전송 방식을 지원합니다:

**STDIO (로컬 프로세스):**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": { ... }
    }
  }
}
```

**SSE (원격 HTTP):**
```json
{
  "mcpServers": {
    "databricks-remote": {
      "url": "https://your-mcp-server.com/sse",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

#### 4.6 여러 워크스페이스 설정

```json
{
  "mcpServers": {
    "databricks-production": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_prod..."
      },
      "disabled": false
    },
    "databricks-staging": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://staging.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_staging..."
      },
      "disabled": true
    }
  }
}
```

#### 4.7 설정 확인

1. VS Code 재시작 또는 Cline 리로드
2. Cline 패널에서 MCP Servers 아이콘 클릭
3. "databricks" 서버가 활성화되어 있는지 확인
4. 녹색 상태 표시기 확인

#### 4.8 테스트

Cline 채팅에서:
```
Can you list all my Databricks clusters using the MCP server?
Show me tables in the 'main' catalog
```

---

### 5. Continue (VS Code 확장)

Continue는 다양한 LLM을 지원하는 VS Code AI 코딩 어시스턴트입니다.

#### 5.1 Continue 설치

1. VS Code 열기
2. Extensions 패널 (`Cmd+Shift+X`)
3. "Continue" 검색
4. "Install" 클릭

#### 5.2 설정 파일 위치

**작업 공간별:**
```
.continue/mcpServers/
```

**전역:**
```
~/.continue/mcpServers/
```

#### 5.3 설정 파일 생성

**작업 공간에서:**
```bash
# 프로젝트 루트에서
mkdir -p .continue/mcpServers
cd .continue/mcpServers
```

**YAML 형식으로 생성:**
```bash
nano databricks-mcp.yaml
```

#### 5.4 YAML 설정 예제

```yaml
mcpServers:
  - name: Databricks MCP
    command: uvx
    args:
      - databricks-mcp
    env:
      DATABRICKS_HOST: https://your-workspace.cloud.databricks.com
      DATABRICKS_AUTH_TYPE: oauth-u2m
```

#### 5.5 JSON 설정 예제 (대안)

Claude Desktop이나 Cursor의 설정을 재사용할 수 있습니다:

```bash
# Claude Desktop 설정 복사
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   .continue/mcpServers/databricks.json
```

또는 직접 생성:
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      }
    }
  }
}
```

#### 5.6 복잡한 설정 예제

```yaml
mcpServers:
  - name: Databricks Production
    command: uvx
    args:
      - databricks-mcp
    env:
      DATABRICKS_HOST: https://prod-workspace.cloud.databricks.com
      DATABRICKS_CLIENT_ID: ${DATABRICKS_PROD_CLIENT_ID}
      DATABRICKS_CLIENT_SECRET: ${DATABRICKS_PROD_CLIENT_SECRET}

  - name: Databricks Development
    command: uvx
    args:
      - databricks-mcp
    env:
      DATABRICKS_HOST: https://dev-workspace.cloud.databricks.com
      DATABRICKS_AUTH_TYPE: oauth-u2m
```

#### 5.7 원격 MCP 서버 설정

Continue는 HTTP 기반 원격 서버도 지원합니다:

```yaml
mcpServers:
  - name: Databricks Remote
    transport: streamable-http
    url: https://your-mcp-server.com/mcp
    headers:
      Authorization: Bearer ${MCP_TOKEN}
```

#### 5.8 설정 확인

1. VS Code 재시작
2. Continue 패널 열기
3. 설정 아이콘 클릭
4. "MCP Servers" 섹션 확인
5. "databricks" 서버가 연결됨으로 표시되는지 확인

#### 5.9 테스트

Continue 채팅에서:
```
@databricks list my clusters
@databricks show tables in main.default
```

---

### 6. Zed Editor

Zed는 고성능 협업 코드 에디터입니다.

#### 6.1 설정 파일 접근

**방법 1: Zed UI 사용**
1. Zed 열기
2. `Cmd+,` (설정 열기)
3. "Preferences" > "Settings" 클릭
4. JSON 편집기가 열립니다

**방법 2: 직접 파일 편집**
```bash
# macOS/Linux
~/.config/zed/settings.json

# 열기
code ~/.config/zed/settings.json
```

#### 6.2 MCP 확장 설치 (간편한 방법)

1. Zed에서 Agent 패널 열기
2. 우측 상단 메뉴 클릭
3. "View Server Extensions" 선택
4. "databricks" 검색 (커뮤니티 확장 사용 가능 시)
5. "Install" 클릭

#### 6.3 수동 설정

`settings.json`에 다음을 추가:

```json
{
  "context_servers": {
    "databricks": {
      "settings": {},
      "command": {
        "path": "uvx",
        "args": ["databricks-mcp"],
        "env": {
          "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
          "DATABRICKS_AUTH_TYPE": "oauth-u2m"
        }
      }
    }
  }
}
```

#### 6.4 완전한 설정 예제

```json
{
  "context_servers": {
    "databricks-production": {
      "settings": {
        "description": "Production Databricks workspace"
      },
      "command": {
        "path": "uvx",
        "args": ["databricks-mcp"],
        "env": {
          "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
          "DATABRICKS_TOKEN": "dapi_prod_token"
        }
      }
    },
    "databricks-development": {
      "settings": {
        "description": "Development Databricks workspace"
      },
      "command": {
        "path": "uvx",
        "args": ["databricks-mcp"],
        "env": {
          "DATABRICKS_HOST": "https://dev.cloud.databricks.com",
          "DATABRICKS_AUTH_TYPE": "oauth-u2m"
        }
      }
    }
  }
}
```

#### 6.5 도구 활성화

1. 설정 파일 저장
2. Zed 재시작
3. Agent 패널 열기
4. "Configure profiles" 선택
5. "databricks" 프로파일 선택
6. "Configure MCP Tools" 클릭
7. 사용할 도구 선택

#### 6.6 서버 상태 확인

1. Agent 패널 설정 보기 열기
2. MCP 서버 이름 옆의 표시기 확인:
   - 🟢 녹색 점 = "Server is active" (정상 작동)
   - 🔴 빨간 점 = "Server error" (오류 발생)
   - ⚪ 회색 점 = "Server inactive" (비활성)

#### 6.7 현재 제한사항 (2025)

⚠️ **Zed의 MCP 지원 제한:**
- 최신 MCP 스펙 (2025-06-18)은 아직 완전히 지원되지 않음
- HTTP 스트리밍은 지원되지 않음 (stdio만 지원)
- 프롬프트만 지원 (슬래시 명령으로 표시)
- 여러 프롬프트 인수는 지원되지 않음

#### 6.8 테스트

Zed Agent에서:
```
/databricks-prompt list-clusters
```

또는 자연어:
```
Show me all my Databricks clusters
List tables in the main catalog
```

---

### 7. Windsurf IDE

Windsurf는 Codeium이 개발한 AI 기반 IDE입니다.

#### 7.1 설정 파일 위치

```
~/.codeium/windsurf/mcp_config.json
```

#### 7.2 UI를 통한 설정

**방법 1: 설정 메뉴**
1. Windsurf 열기
2. Settings > Advanced Settings
3. "Cascade" 섹션까지 스크롤
4. "Add New Server" 클릭
5. 서버 정보 입력

**방법 2: Command Palette**
1. `Cmd+Shift+P` (macOS) 또는 `Ctrl+Shift+P` (Windows/Linux)
2. "Open Windsurf Settings Page" 입력
3. "Cascade" > "MCP Servers" 섹션 찾기
4. "Add Custom Server +" 클릭

**방법 3: Cascade 툴바**
1. Windsurf에서 Cascade 열기
2. 툴바의 🔨 (Hammer) 아이콘 클릭
3. "Configure" 버튼 클릭

#### 7.3 기본 설정

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      },
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

#### 7.4 로컬 서버 설정 (Node.js)

빌드된 MCP 서버를 로컬에서 실행하는 경우:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "node",
      "args": ["/path/to/databricks-mcp/build/index.js"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      },
      "disabled": false
    }
  }
}
```

#### 7.5 Docker 기반 설정

Docker를 사용하는 경우:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DATABRICKS_HOST",
        "-e", "DATABRICKS_TOKEN",
        "your-dockerhub-username/databricks-mcp"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      }
    }
  }
}
```

#### 7.6 원격 MCP 서버 설정

원격 호스팅 MCP 서버를 사용하는 경우:

```json
{
  "mcpServers": {
    "databricks-remote": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-mcp-server.com/sse"
      ],
      "env": {
        "MCP_TOKEN": "your-auth-token"
      }
    }
  }
}
```

#### 7.7 여러 환경 설정

```json
{
  "mcpServers": {
    "databricks-production": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
        "DATABRICKS_CLIENT_ID": "prod-client-id",
        "DATABRICKS_CLIENT_SECRET": "prod-secret"
      },
      "disabled": false,
      "alwaysAllow": ["list_clusters", "list_jobs"]
    },
    "databricks-staging": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://staging.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_staging..."
      },
      "disabled": false
    },
    "databricks-development": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://dev.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      },
      "disabled": true
    }
  }
}
```

#### 7.8 사전 구성된 서버 사용

Windsurf는 인기있는 MCP 서버들을 사전 구성하여 제공합니다:

1. Windsurf에서 Plugins 아이콘 클릭 (사이드바)
2. "MCP Servers" 탭 선택
3. 사용 가능한 서버 목록 확인
4. "databricks-mcp" 찾기 (사용 가능한 경우)
5. "Install" 또는 "Enable" 클릭

#### 7.9 설정 확인

1. Windsurf 재시작
2. Cascade 패널 열기
3. 🔨 아이콘 클릭하여 MCP 도구 목록 확인
4. "databricks" 서버가 연결되어 있는지 확인
5. 사용 가능한 도구 목록 확인

#### 7.10 테스트

Cascade에서:
```
@databricks list all my clusters
@databricks show me tables in the main catalog
@databricks execute SQL: SELECT * FROM samples.nyctaxi.trips LIMIT 5
```

---

### 8. OpenAI Codex (CLI)

OpenAI Codex는 터미널에서 실행되는 경량 코딩 에이전트로, MCP 서버를 완전히 지원합니다.

#### 8.1 Codex 설치

```bash
# npm을 통한 설치
npm install -g @openai/codex

# 또는 직접 실행
npx @openai/codex
```

#### 8.2 설정 파일 위치

```
~/.codex/config.toml
```

#### 8.3 MCP 서버 추가

**명령어를 통한 추가:**
```bash
codex mcp add databricks \
  --env DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
  --env DATABRICKS_AUTH_TYPE=oauth-u2m \
  -- uvx databricks-mcp
```

**PAT 사용:**
```bash
codex mcp add databricks \
  --env DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
  --env DATABRICKS_TOKEN=dapi... \
  -- uvx databricks-mcp
```

**Service Principal 사용:**
```bash
codex mcp add databricks \
  --env DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
  --env DATABRICKS_CLIENT_ID=your-client-id \
  --env DATABRICKS_CLIENT_SECRET=your-secret \
  -- uvx databricks-mcp
```

#### 8.4 수동 설정 (config.toml)

```bash
# 설정 파일 편집
nano ~/.codex/config.toml
```

**기본 설정:**
```toml
[[mcp_servers]]
name = "databricks"
command = "uvx"
args = ["databricks-mcp"]

[mcp_servers.env]
DATABRICKS_HOST = "https://your-workspace.cloud.databricks.com"
DATABRICKS_AUTH_TYPE = "oauth-u2m"
```

**여러 워크스페이스 설정:**
```toml
[[mcp_servers]]
name = "databricks-prod"
command = "uvx"
args = ["databricks-mcp"]

[mcp_servers.env]
DATABRICKS_HOST = "https://prod-workspace.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi_prod..."

[[mcp_servers]]
name = "databricks-dev"
command = "uvx"
args = ["databricks-mcp"]

[mcp_servers.env]
DATABRICKS_HOST = "https://dev-workspace.cloud.databricks.com"
DATABRICKS_AUTH_TYPE = "oauth-u2m"
```

#### 8.5 MCP 서버 목록 확인

```bash
# Codex TUI에서
codex

# TUI 내에서
/mcp
```

활성 연결된 MCP 서버 목록이 표시됩니다.

#### 8.6 MCP 서버 관리

**서버 제거:**
```bash
codex mcp remove databricks
```

**서버 목록:**
```bash
codex mcp list
```

#### 8.7 Codex를 MCP 서버로 사용

Codex 자체를 MCP 서버로 실행할 수도 있습니다:

```bash
# MCP 서버로 Codex 시작
codex mcp-server

# MCP Inspector로 테스트
npx @modelcontextprotocol/inspector codex mcp-server
```

#### 8.8 Docker MCP Toolkit 사용

Docker MCP Toolkit을 통해 220개 이상의 MCP 서버에 안전하게 접근할 수 있습니다:

```bash
# Docker MCP Toolkit 설치
npm install -g @docker/mcp-toolkit

# Databricks MCP 서버 추가
docker-mcp add databricks
```

#### 8.9 테스트

Codex TUI에서:
```bash
# Codex 시작
codex

# 프롬프트에서
> List all my Databricks clusters
> Show tables in catalog 'main'
> Execute SQL: SELECT * FROM samples.nyctaxi.trips LIMIT 5
```

#### 8.10 OpenAI Agents SDK와 통합

Codex를 OpenAI Agents SDK와 함께 사용:

```python
from openai import OpenAI
from codex_mcp import CodexMCPServer

# MCP 서버로 Codex 초기화
server = CodexMCPServer()

# Agent에서 사용
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "List my Databricks clusters"}
    ],
    tools=server.get_tools()
)
```

---

### 9. Dify

Dify는 v1.6.0부터 양방향 MCP 지원을 제공하는 LLMOps 플랫폼입니다.

#### 9.1 Dify에서 MCP 서버 사용

Dify는 두 가지 방식으로 MCP를 지원합니다:
1. **MCP 도구를 Dify로 가져오기** (MCP 서버 소비)
2. **Dify 앱을 MCP 서버로 게시** (MCP 서버 제공)

#### 9.2 MCP 서버 추가 (Dify에서 사용)

**방법 1: Dify UI를 통한 추가**

1. Dify 워크스페이스에 로그인
2. **Tools** (도구) 페이지로 이동
3. **MCP** 섹션 선택
4. **Add Server** (서버 추가) 클릭
5. 서버 정보 입력:

```json
{
  "name": "databricks",
  "type": "stdio",
  "command": "uvx",
  "args": ["databricks-mcp"],
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m"
  }
}
```

**방법 2: 환경 변수 사용**

Dify 서버 환경에서 직접 설정:

```bash
export DIFY_MCP_SERVERS='[
  {
    "name": "databricks",
    "command": "uvx",
    "args": ["databricks-mcp"],
    "env": {
      "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
      "DATABRICKS_TOKEN": "dapi..."
    }
  }
]'
```

#### 9.3 Agent 워크플로우에서 사용

**1. Agent 노드 생성:**
- Workflow에서 **Agent** 노드 추가
- MCP Tools 섹션에서 **databricks** 선택
- 사용할 도구 선택:
  - `list_clusters`
  - `execute_sql`
  - `list_tables`
  - 등

**2. Agent가 자동으로 도구 호출:**
```
User: "Show me all running clusters"
→ Agent가 list_clusters 도구를 자동 호출
→ 결과 반환
```

#### 9.4 워크플로우 노드로 사용

**개별 MCP 도구를 노드로 추가:**

1. Workflow 편집기 열기
2. **Add Node** 클릭
3. **MCP Tool** 카테고리 선택
4. **databricks** > **execute_sql** 선택
5. 파라미터 설정:
   ```json
   {
     "warehouse_id": "{{warehouse_id}}",
     "sql": "SELECT * FROM main.default.my_table"
   }
   ```

이 방식은 LLM 결정 없이 명시적인 호출 순서를 제어합니다.

#### 9.5 Dify 앱을 MCP 서버로 게시

Dify 워크플로우를 MCP 서버로 노출하여 Claude, Cursor 등에서 사용:

**1. 워크플로우 준비:**

Start 노드의 모든 입력 파라미터에 대해:
- **파라미터 이름**: 명확한 이름 (예: `cluster_name`, `sql_query`)
- **파라미터 설명**: 상세한 설명 작성
  ```
  예: "The name of the Databricks cluster to query"
  ```

**2. 서비스 설명 작성:**

워크플로우 설정에서:
```
Service Description: "Query Databricks clusters and execute SQL through a Dify workflow"
```

**3. MCP 서버 URL 생성:**

- 설정 완료 후 Dify가 MCP 서버 URL 발급
- 예: `https://your-dify.com/mcp/v1/workflows/abc123`

**4. Claude Desktop에서 사용:**

```json
{
  "mcpServers": {
    "dify-databricks": {
      "url": "https://your-dify.com/mcp/v1/workflows/abc123",
      "headers": {
        "Authorization": "Bearer YOUR_DIFY_API_KEY"
      }
    }
  }
}
```

**5. Cursor에서 사용:**

`.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "dify-databricks": {
      "url": "https://your-dify.com/mcp/v1/workflows/abc123",
      "headers": {
        "Authorization": "Bearer YOUR_DIFY_API_KEY"
      }
    }
  }
}
```

#### 9.6 Zapier/Composio 통합

Dify MCP는 Zapier와 Composio를 통해 8,000개 이상의 앱에 접근할 수 있습니다:

**Zapier MCP 추가:**
1. Tools 페이지에서 **MCP** 선택
2. **Zapier** 서버 추가
3. Zapier API 키 입력
4. 사용할 Zapier Actions 선택

**사용 예:**
```
"Databricks에서 데이터를 쿼리하고 결과를 Google Sheets에 저장"
→ Databricks MCP로 데이터 가져오기
→ Zapier MCP로 Google Sheets에 쓰기
```

#### 9.7 커뮤니티 MCP 서버 (dify-mcp-server)

서드파티 MCP 서버를 사용하여 Dify 워크플로우 호출:

**설치:**
```bash
npm install -g dify-mcp-server
```

**설정:**
```yaml
# config.yaml
dify:
  base_url: https://your-dify.com
  app_sks:
    - app-abc123-secret-key-1
    - app-def456-secret-key-2
```

**실행:**
```bash
dify-mcp-server --config config.yaml
```

**Claude Desktop 설정:**
```json
{
  "mcpServers": {
    "dify": {
      "command": "dify-mcp-server",
      "args": ["--config", "/path/to/config.yaml"]
    }
  }
}
```

#### 9.8 설정 확인

**MCP 서버 상태 확인:**
1. Dify Tools 페이지 열기
2. MCP 섹션에서 연결 상태 확인
3. 녹색 표시 = 정상 연결

**도구 테스트:**
1. Workflow에서 Agent 노드 생성
2. "List my Databricks clusters" 요청
3. Agent가 MCP 도구를 호출하는지 확인

#### 9.9 고급 설정

**여러 Databricks 워크스페이스:**

```json
[
  {
    "name": "databricks-prod",
    "command": "uvx",
    "args": ["databricks-mcp"],
    "env": {
      "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
      "DATABRICKS_TOKEN": "dapi_prod..."
    }
  },
  {
    "name": "databricks-dev",
    "command": "uvx",
    "args": ["databricks-mcp"],
    "env": {
      "DATABRICKS_HOST": "https://dev.cloud.databricks.com",
      "DATABRICKS_AUTH_TYPE": "oauth-u2m"
    }
  }
]
```

**권한 설정:**
- Dify Admin 권한으로 MCP 서버 추가
- 팀 멤버에게 도구 사용 권한 부여
- API 키 별도 관리

#### 9.10 테스트

**Agent 워크플로우에서:**
```
User: "What clusters are running in my Databricks workspace?"
→ Dify Agent가 databricks MCP 서버 호출
→ list_clusters 도구 사용
→ 결과를 자연어로 포맷팅하여 반환
```

**워크플로우 노드로:**
```
[Start] → [MCP: list_clusters] → [LLM: 결과 분석] → [End]
```

---

### 10. n8n

n8n은 워크플로우 자동화 플랫폼으로, MCP를 클라이언트와 서버 양방향으로 지원합니다.

#### 10.1 n8n MCP 지원 개요

n8n은 두 가지 방식으로 MCP를 지원합니다:
1. **MCP 클라이언트**: n8n에서 외부 MCP 서버 도구 호출
2. **MCP 서버**: n8n 워크플로우를 MCP 서버로 노출

#### 10.2 n8n 설치

```bash
# npm을 통한 전역 설치
npm install -g n8n

# Docker 사용
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n

# npx로 직접 실행
npx n8n
```

#### 10.3 MCP Client Tool 노드 사용

n8n에서 Databricks MCP 서버 호출:

**1. 워크플로우 생성:**
1. n8n 대시보드에서 "New Workflow" 클릭
2. 노드 추가 → "AI" 카테고리
3. "MCP Client Tool" 노드 선택

**2. MCP 서버 연결 설정:**

노드 설정에서:
```json
{
  "transport": "stdio",
  "command": "uvx",
  "args": ["databricks-mcp"],
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m"
  }
}
```

**3. HTTP Streamable 전송 방식:**

원격 MCP 서버를 사용하는 경우:
```json
{
  "transport": "http-streamable",
  "url": "https://your-mcp-server.com/mcp",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN"
  }
}
```

#### 10.4 Agent에서 MCP 도구 사용

**AI Agent 노드 설정:**

1. **Agent 노드 추가**:
   - "AI" → "AI Agent" 노드 추가
   - Model 선택 (OpenAI, Anthropic 등)

2. **MCP Tools 연결**:
   - Tools 섹션에서 "MCP Client Tool" 추가
   - Databricks MCP 서버 설정

3. **프롬프트 예제**:
```
Input: "List all running Databricks clusters and their current state"
→ Agent가 자동으로 list_clusters MCP 도구 호출
→ 결과 분석 및 응답
```

#### 10.5 n8n을 MCP 서버로 노출

n8n 워크플로우를 MCP 서버로 만들어 Claude, Cursor 등에서 사용:

**1. MCP Server Trigger 노드 사용:**

1. 새 워크플로우 생성
2. "MCP Server Trigger" 노드 추가
3. 도구 이름 및 설명 입력:
   ```
   Tool Name: query_databricks
   Description: Execute SQL queries on Databricks and format results
   ```

4. 파라미터 정의:
   ```json
   {
     "sql": {
       "type": "string",
       "description": "SQL query to execute",
       "required": true
     },
     "warehouse_id": {
       "type": "string",
       "description": "SQL Warehouse ID"
     }
   }
   ```

5. 워크플로우 로직 구성:
   - HTTP Request 노드로 Databricks API 호출
   - 결과 처리 및 포맷팅
   - Return 노드로 결과 반환

**2. n8n MCP 서버 URL:**

워크플로우 활성화 후 MCP 서버 URL 확인:
```
http://localhost:5678/mcp/workflows/<workflow-id>
```

**3. Claude Desktop에서 n8n MCP 서버 사용:**

```json
{
  "mcpServers": {
    "n8n-databricks": {
      "url": "http://localhost:5678/mcp/workflows/<workflow-id>",
      "headers": {
        "Authorization": "Bearer YOUR_N8N_API_KEY"
      }
    }
  }
}
```

#### 10.6 커뮤니티 노드 사용

**n8n-nodes-mcp 설치:**

```bash
# n8n Community Nodes에서 설치
cd ~/.n8n
npm install n8n-nodes-mcp
```

이 커스텀 노드는 다음을 지원합니다:
- ✅ HTTP Streamable transport
- ✅ SSE (Server-Sent Events)
- ✅ Command-line transport
- ✅ Bearer & generic header 인증

#### 10.7 실전 예제: Databricks 자동화

**자동화 시나리오: 매일 클러스터 상태 모니터링**

```
[Schedule Trigger: Daily 9 AM]
  ↓
[MCP Client Tool: list_clusters]
  ↓
[Code: Filter running clusters]
  ↓
[IF: Any cluster issues?]
  ↓ Yes
[Slack: Send alert]
  ↓ No
[Email: Daily report]
```

**워크플로우 설정:**

1. **Schedule Trigger** - 매일 오전 9시
2. **MCP Client Tool** - Databricks MCP 서버 호출
3. **Code 노드** - 클러스터 상태 분석
4. **IF 노드** - 문제 감지
5. **Slack/Email** - 알림 전송

#### 10.8 환경 변수 설정

n8n에서 환경 변수 사용:

**n8n 서버 시작 시:**
```bash
export N8N_MCP_DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export N8N_MCP_DATABRICKS_TOKEN="dapi..."

n8n start
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_MCP_DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
      - N8N_MCP_DATABRICKS_TOKEN=dapi...
    volumes:
      - n8n_data:/home/node/.n8n
```

#### 10.9 Account API 설정

Account-level 작업을 위한 설정:

```json
{
  "transport": "stdio",
  "command": "uvx",
  "args": ["databricks-mcp"],
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m",
    "DATABRICKS_ACCOUNT_ID": "your-account-id",
    "DATABRICKS_ACCOUNT_HOST": "https://accounts.cloud.databricks.com"
  }
}
```

#### 10.10 테스트

**간단한 테스트 워크플로우:**

1. Manual Trigger 노드 추가
2. MCP Client Tool 노드 추가 (Databricks 설정)
3. Tool: `list_clusters`
4. Parameters: `{}`
5. Workflow 실행 → 클러스터 목록 확인

---

### 문제 해결 (Korean)

#### 일반적인 문제

##### 1. "uvx: command not found" 오류

**해결 방법:**
```bash
# uv 설치
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 설치 확인
uvx --version
```

**대안: pip 사용**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "python",
      "args": ["-m", "databricks_mcp"],
      "env": { ... }
    }
  }
}
```

##### 2. "Could not connect to Databricks" 오류

**확인 사항:**
1. DATABRICKS_HOST가 정확한지 확인 (끝에 슬래시 없음)
2. 네트워크 연결 확인
3. 워크스페이스 URL이 올바른지 확인

```json
// ❌ 잘못된 예
"DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com/"

// ✅ 올바른 예
"DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com"
```

##### 3. "Authentication failed" 오류

**OAuth 사용 시:**
- 브라우저가 자동으로 열리는지 확인
- 팝업 차단기 비활성화
- 올바른 계정으로 로그인했는지 확인

**PAT 사용 시:**
- 토큰이 만료되지 않았는지 확인
- 토큰이 올바르게 복사되었는지 확인 (공백 없이)
- 토큰이 필요한 권한을 가지고 있는지 확인

**Service Principal 사용 시:**
- Client ID와 Secret이 정확한지 확인
- Service Principal이 워크스페이스에 추가되었는지 확인
- 필요한 권한이 부여되었는지 확인

##### 4. MCP 서버 아이콘이 보이지 않음

**해결 방법:**
1. 클라이언트 애플리케이션 완전히 종료
2. 설정 파일 JSON 구문 확인 (쉼표, 괄호 등)
3. 클라이언트 재시작
4. 로그 확인 (클라이언트별 로그 위치 참조)

##### 5. 일부 도구만 작동함

**원인:**
- 권한 부족
- 필요한 Databricks 기능이 활성화되지 않음
- 워크스페이스 티어 제한

**해결 방법:**
1. Databricks에서 사용자 권한 확인
2. Unity Catalog, MLflow 등 필요한 기능 활성화 확인
3. 워크스페이스 관리자에게 문의

##### 6. 성능이 느림

**최적화 방법:**
- 사용하지 않는 MCP 서버 비활성화
- alwaysAllow 리스트 사용하여 자주 쓰는 도구 자동 승인
- 로컬에 토큰 캐시 (OAuth)

#### 클라이언트별 문제

##### Claude Desktop

**문제:** 서버가 연결되지 않음
```bash
# 로그 확인
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log

# Windows
type %APPDATA%\Claude\logs\mcp*.log
```

##### Cursor

**문제:** 40개 도구 제한
- 필요한 기능만 포함하는 커스텀 래퍼 작성 고려
- 여러 MCP 서버 인스턴스로 기능 분할

##### Cline / Continue

**문제:** 도구 승인 프롬프트가 계속 나타남
- `alwaysAllow` 리스트에 자주 사용하는 도구 추가

##### Zed

**문제:** 프롬프트만 표시됨
- Zed의 현재 MCP 지원은 제한적
- 직접 도구 호출은 향후 업데이트 예정

##### Windsurf

**문제:** Docker 컨테이너가 시작되지 않음
- Docker Desktop 실행 확인
- 이미지가 올바르게 빌드되었는지 확인
- 로그 확인: `docker logs <container-id>`

#### 디버깅 팁

##### 1. 상세 로깅 활성화

환경 변수 추가:
```json
{
  "env": {
    "DATABRICKS_HOST": "...",
    "DATABRICKS_DEBUG": "true",
    "DATABRICKS_LOG_LEVEL": "DEBUG"
  }
}
```

##### 2. 수동으로 MCP 서버 테스트

```bash
# 서버 직접 실행
uvx databricks-mcp

# 환경 변수 설정하여 실행
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
DATABRICKS_AUTH_TYPE=oauth-u2m \
uvx databricks-mcp
```

##### 3. Databricks CLI로 연결 테스트

```bash
# Databricks CLI 설치
pip install databricks-cli

# 연결 테스트
databricks workspace list
```

##### 4. 네트워크 테스트

```bash
# 워크스페이스 도달 가능 여부 확인
curl -I https://your-workspace.cloud.databricks.com

# API 엔드포인트 테스트
curl -H "Authorization: Bearer dapi..." \
  https://your-workspace.cloud.databricks.com/api/2.0/clusters/list
```

#### 도움 받기

문제가 계속되면:

1. **GitHub Issues**: https://github.com/YuujinHwang/databricks-mcp/issues
2. **MCP 공식 문서**: https://modelcontextprotocol.io/
3. **Databricks 문서**: https://docs.databricks.com/
4. **커뮤니티 포럼**:
   - Databricks Community
   - MCP Discord
   - Stack Overflow (#mcp, #databricks)

이슈 제출 시 포함할 정보:
- 사용 중인 MCP 클라이언트 및 버전
- 운영 체제 및 버전
- 설정 파일 (민감한 정보 제거)
- 오류 메시지
- 로그 출력

---

## English Guide

This guide provides detailed setup instructions for the Databricks MCP Server across all major MCP clients.

### Table of Contents
- [Prerequisites](#prerequisites)
- [1. Claude Desktop](#1-claude-desktop-en)
- [2. Claude Code (CLI)](#2-claude-code-cli-en)
- [3. Cursor IDE](#3-cursor-ide-en)
- [4. Cline (VS Code Extension)](#4-cline-vs-code-extension)
- [5. Continue (VS Code Extension)](#5-continue-vs-code-extension)
- [6. Zed Editor](#6-zed-editor-en)
- [7. Windsurf IDE](#7-windsurf-ide-en)
- [8. OpenAI Codex (CLI)](#8-openai-codex-cli-en)
- [9. Dify](#9-dify-en)
- [10. n8n](#10-n8n-en)
- [Troubleshooting](#troubleshooting-english)

---

### Prerequisites

Before configuring any MCP client, ensure you have:

#### 1. Python Environment (Recommended)
```bash
# Check Python 3.10+
python --version

# Install uv (recommended)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Databricks Authentication
Prepare one of the following:

**Option A: OAuth U2M (Recommended for development)**
- Databricks workspace URL
- OAuth auto-authentication (browser opens on first use)

**Option B: Personal Access Token (PAT)**
1. Log into Databricks workspace
2. Click user menu (top-right) → Settings
3. Developer → Access tokens
4. Click "Generate new token"
5. Copy and securely store the token

**Option C: Service Principal (For production)**
- Client ID
- Client Secret
- Request creation from Account Admin

#### 3. Databricks Workspace URL
```
AWS:   https://your-workspace.cloud.databricks.com
Azure: https://adb-<workspace-id>.<random>.azuredatabricks.net
GCP:   https://<workspace-id>.gcp.databricks.com
```

#### 4. Account API Configuration (Optional)

**Only configure if you need Account-level operations:**

Account API enables:
- Multi-workspace management
- User and group administration
- Workspace creation/deletion
- Account-level permissions

**Required Information:**
- `DATABRICKS_ACCOUNT_ID`: Account ID (UUID format)
- `DATABRICKS_ACCOUNT_HOST`:
  - AWS/GCP: `https://accounts.cloud.databricks.com`
  - Azure: `https://accounts.azuredatabricks.net`

**How to Find Account ID:**
1. Access Databricks Account Console
2. Top-right profile → Account Settings
3. Copy Account ID

**Permission Requirements:**
- Account Admin role required
- Or Service Principal with Account Admin permissions

**💡 Tip**: Skip this if you only need Workspace-level operations.

---

### 1. Claude Desktop (EN)

Claude Desktop is Anthropic's official desktop application with the easiest MCP server setup.

#### 1.1 Configuration File Location

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### 1.2 Open Configuration File

**Method 1: Using Claude Desktop UI**
1. Launch Claude Desktop
2. Open Settings
3. Select Developer tab
4. Click "Edit Config" button

**Method 2: Direct File Edit**
```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows (Notepad)
notepad %APPDATA%\Claude\claude_desktop_config.json
```

#### 1.3 Basic Configuration (OAuth)

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 1.4 PAT Configuration

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi1234567890abcdef..."
      }
    }
  }
}
```

#### 1.5 Service Principal Configuration (Production)

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_CLIENT_ID": "your-service-principal-client-id",
        "DATABRICKS_CLIENT_SECRET": "your-service-principal-secret"
      }
    }
  }
}
```

#### 1.6 Multiple Workspaces Configuration

```json
{
  "mcpServers": {
    "databricks-prod": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://prod-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_prod_token..."
      }
    },
    "databricks-dev": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://dev-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 1.7 Apply Configuration and Verify

1. Save configuration file
2. **Completely quit** Claude Desktop (Cmd+Q / Alt+F4)
3. Restart Claude Desktop
4. Start a new conversation
5. Check for **🔨 icon** (MCP server indicator) at bottom of input box
6. Click icon to verify "databricks" server is active

#### 1.8 First Run (OAuth)

When using OAuth authentication:
1. On first MCP tool use, a browser window opens automatically
2. Log into Databricks
3. Click "Authorize"
4. Close browser tab
5. Return to Claude Desktop and continue

#### 1.9 Test

In Claude Desktop, try:

```
"List all my Databricks clusters"
"Show me the tables in my Unity Catalog"
"Execute this SQL: SELECT * FROM samples.nyctaxi.trips LIMIT 10"
```

---

### 2. Claude Code (CLI) (EN)

Claude Code is Anthropic's CLI tool for terminal use.

#### 2.1 Configuration File Location

**All platforms:**
```bash
~/.config/claude/config.json
```

#### 2.2 Create/Edit Configuration File

```bash
# Create directory
mkdir -p ~/.config/claude

# Edit file
nano ~/.config/claude/config.json
# or
code ~/.config/claude/config.json
# or
vim ~/.config/claude/config.json
```

#### 2.3 Basic Configuration

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 2.4 Using .databrickscfg Profiles

If you're already using Databricks CLI, reuse existing configuration:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_CONFIG_PROFILE": "production"
      }
    }
  }
}
```

`~/.databrickscfg` file:
```ini
[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi...

[development]
host = https://dev-workspace.cloud.databricks.com
auth_type = oauth-u2m
```

#### 2.5 Test

```bash
# Run Claude Code
claude

# Test in prompt
> List my Databricks clusters
> Show tables in catalog 'main'
```

---

### 3. Cursor IDE (EN)

Cursor is an AI-powered code editor.

#### 3.1 Configuration File Location

**Per-project (recommended):**
```
your-project/.cursor/mcp.json
```

**Global:**
```
~/.cursor/mcp.json
```

#### 3.2 UI-based Configuration

1. Launch Cursor
2. `Cmd+,` (macOS) or `Ctrl+,` (Windows/Linux) - Open Settings
3. Find "Developer" section
4. Click "Edit Config"
5. Select "MCP Tools"
6. Click "Add Custom MCP"

#### 3.3 Manual Configuration File Creation

**Per-project setup:**
```bash
# In project root
mkdir -p .cursor
nano .cursor/mcp.json
```

**Basic configuration:**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

#### 3.4 Environment Variables (Sensitive Data)

To avoid storing tokens directly in config:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "${DATABRICKS_TOKEN}"
      }
    }
  }
}
```

Then set environment variable:
```bash
# ~/.bashrc or ~/.zshrc
export DATABRICKS_TOKEN="dapi..."
```

#### 3.5 One-Click Install (Cursor Built-in)

Latest Cursor versions provide an MCP server marketplace:

1. In Cursor, press `Cmd+K` (Open AI chat)
2. Click MCP icon
3. Select "Browse MCP Servers"
4. Search for "databricks-mcp"
5. Click "Install" (if available)

#### 3.6 Important Limitation

⚠️ **Cursor currently only sends the first 40 tools to the Agent.**

Since Databricks MCP provides 82 tools, you may need to enable/disable servers as needed.

#### 3.7 Verify Configuration

1. Restart Cursor
2. Open AI chat (`Cmd+K`)
3. Check for MCP icon (green when active)
4. Test prompt:
```
@databricks list my clusters
```

---

### 4. Cline (VS Code Extension)

Cline is a powerful AI coding assistant for VS Code.

#### 4.1 Install Cline

1. Open VS Code
2. Open Extensions panel (`Cmd+Shift+X`)
3. Search "Cline"
4. Click "Install"

#### 4.2 Access MCP Server Configuration

**Method 1: Using Cline UI**
1. Open Cline panel in VS Code
2. Click "MCP Servers" icon in top navigation
3. Select "Installed" tab
4. Click "Configure MCP Servers" button at bottom

**Method 2: Direct File Edit**
```bash
# VS Code settings directory
code ~/.vscode/extensions/cline/mcp_settings.json
```

#### 4.3 Basic Configuration

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      },
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

#### 4.4 Auto-Approve Configuration

To automatically approve specific tools:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      },
      "disabled": false,
      "alwaysAllow": [
        "list_clusters",
        "get_cluster",
        "list_jobs",
        "list_tables"
      ]
    }
  }
}
```

#### 4.5 Transport Types

Cline supports two transport methods:

**STDIO (Local process):**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": { ... }
    }
  }
}
```

**SSE (Remote HTTP):**
```json
{
  "mcpServers": {
    "databricks-remote": {
      "url": "https://your-mcp-server.com/sse",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

#### 4.6 Multiple Workspaces

```json
{
  "mcpServers": {
    "databricks-production": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_prod..."
      },
      "disabled": false
    },
    "databricks-staging": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://staging.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_staging..."
      },
      "disabled": true
    }
  }
}
```

#### 4.7 Verify Configuration

1. Restart VS Code or reload Cline
2. Click MCP Servers icon in Cline panel
3. Verify "databricks" server is enabled
4. Check for green status indicator

#### 4.8 Test

In Cline chat:
```
Can you list all my Databricks clusters using the MCP server?
Show me tables in the 'main' catalog
```

---

### 5. Continue (VS Code Extension)

Continue is a VS Code AI coding assistant supporting multiple LLMs.

#### 5.1 Install Continue

1. Open VS Code
2. Extensions panel (`Cmd+Shift+X`)
3. Search "Continue"
4. Click "Install"

#### 5.2 Configuration File Location

**Per-workspace:**
```
.continue/mcpServers/
```

**Global:**
```
~/.continue/mcpServers/
```

#### 5.3 Create Configuration File

**In workspace:**
```bash
# In project root
mkdir -p .continue/mcpServers
cd .continue/mcpServers
```

**Create YAML format:**
```bash
nano databricks-mcp.yaml
```

#### 5.4 YAML Configuration Example

```yaml
mcpServers:
  - name: Databricks MCP
    command: uvx
    args:
      - databricks-mcp
    env:
      DATABRICKS_HOST: https://your-workspace.cloud.databricks.com
      DATABRICKS_AUTH_TYPE: oauth-u2m
```

#### 5.5 JSON Configuration Example (Alternative)

You can reuse configuration from Claude Desktop or Cursor:

```bash
# Copy Claude Desktop config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   .continue/mcpServers/databricks.json
```

Or create directly:
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      }
    }
  }
}
```

#### 5.6 Complex Configuration Example

```yaml
mcpServers:
  - name: Databricks Production
    command: uvx
    args:
      - databricks-mcp
    env:
      DATABRICKS_HOST: https://prod-workspace.cloud.databricks.com
      DATABRICKS_CLIENT_ID: ${DATABRICKS_PROD_CLIENT_ID}
      DATABRICKS_CLIENT_SECRET: ${DATABRICKS_PROD_CLIENT_SECRET}

  - name: Databricks Development
    command: uvx
    args:
      - databricks-mcp
    env:
      DATABRICKS_HOST: https://dev-workspace.cloud.databricks.com
      DATABRICKS_AUTH_TYPE: oauth-u2m
```

#### 5.7 Remote MCP Server Configuration

Continue also supports HTTP-based remote servers:

```yaml
mcpServers:
  - name: Databricks Remote
    transport: streamable-http
    url: https://your-mcp-server.com/mcp
    headers:
      Authorization: Bearer ${MCP_TOKEN}
```

#### 5.8 Verify Configuration

1. Restart VS Code
2. Open Continue panel
3. Click settings icon
4. Check "MCP Servers" section
5. Verify "databricks" server shows as connected

#### 5.9 Test

In Continue chat:
```
@databricks list my clusters
@databricks show tables in main.default
```

---

### 6. Zed Editor (EN)

Zed is a high-performance collaborative code editor.

#### 6.1 Access Configuration File

**Method 1: Using Zed UI**
1. Open Zed
2. `Cmd+,` (Open settings)
3. Click "Preferences" > "Settings"
4. JSON editor opens

**Method 2: Direct File Edit**
```bash
# macOS/Linux
~/.config/zed/settings.json

# Open
code ~/.config/zed/settings.json
```

#### 6.2 Install MCP Extension (Easy Way)

1. Open Agent panel in Zed
2. Click top-right menu
3. Select "View Server Extensions"
4. Search "databricks" (if community extension available)
5. Click "Install"

#### 6.3 Manual Configuration

Add to `settings.json`:

```json
{
  "context_servers": {
    "databricks": {
      "settings": {},
      "command": {
        "path": "uvx",
        "args": ["databricks-mcp"],
        "env": {
          "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
          "DATABRICKS_AUTH_TYPE": "oauth-u2m"
        }
      }
    }
  }
}
```

#### 6.4 Complete Configuration Example

```json
{
  "context_servers": {
    "databricks-production": {
      "settings": {
        "description": "Production Databricks workspace"
      },
      "command": {
        "path": "uvx",
        "args": ["databricks-mcp"],
        "env": {
          "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
          "DATABRICKS_TOKEN": "dapi_prod_token"
        }
      }
    },
    "databricks-development": {
      "settings": {
        "description": "Development Databricks workspace"
      },
      "command": {
        "path": "uvx",
        "args": ["databricks-mcp"],
        "env": {
          "DATABRICKS_HOST": "https://dev.cloud.databricks.com",
          "DATABRICKS_AUTH_TYPE": "oauth-u2m"
        }
      }
    }
  }
}
```

#### 6.5 Enable Tools

1. Save configuration file
2. Restart Zed
3. Open Agent panel
4. Select "Configure profiles"
5. Select "databricks" profile
6. Click "Configure MCP Tools"
7. Choose tools to enable

#### 6.6 Verify Server Status

1. Open Agent panel settings view
2. Check indicator next to MCP server name:
   - 🟢 Green dot = "Server is active" (working)
   - 🔴 Red dot = "Server error" (error)
   - ⚪ Gray dot = "Server inactive" (inactive)

#### 6.7 Current Limitations (2025)

⚠️ **Zed MCP Support Limitations:**
- Latest MCP spec (2025-06-18) not fully supported yet
- HTTP streaming not supported (stdio only)
- Only prompts supported (shown as slash commands)
- Multiple prompt arguments not supported

#### 6.8 Test

In Zed Agent:
```
/databricks-prompt list-clusters
```

Or natural language:
```
Show me all my Databricks clusters
List tables in the main catalog
```

---

### 7. Windsurf IDE (EN)

Windsurf is an AI-powered IDE developed by Codeium.

#### 7.1 Configuration File Location

```
~/.codeium/windsurf/mcp_config.json
```

#### 7.2 UI-based Configuration

**Method 1: Settings Menu**
1. Open Windsurf
2. Settings > Advanced Settings
3. Scroll to "Cascade" section
4. Click "Add New Server"
5. Enter server information

**Method 2: Command Palette**
1. `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "Open Windsurf Settings Page"
3. Find "Cascade" > "MCP Servers" section
4. Click "Add Custom Server +"

**Method 3: Cascade Toolbar**
1. Open Cascade in Windsurf
2. Click 🔨 (Hammer) icon in toolbar
3. Click "Configure" button

#### 7.3 Basic Configuration

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      },
      "disabled": false,
      "alwaysAllow": []
    }
  }
}
```

#### 7.4 Local Server Configuration (Node.js)

For locally built MCP servers:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "node",
      "args": ["/path/to/databricks-mcp/build/index.js"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      },
      "disabled": false
    }
  }
}
```

#### 7.5 Docker-based Configuration

Using Docker:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DATABRICKS_HOST",
        "-e", "DATABRICKS_TOKEN",
        "your-dockerhub-username/databricks-mcp"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      }
    }
  }
}
```

#### 7.6 Remote MCP Server Configuration

For remotely hosted MCP servers:

```json
{
  "mcpServers": {
    "databricks-remote": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-mcp-server.com/sse"
      ],
      "env": {
        "MCP_TOKEN": "your-auth-token"
      }
    }
  }
}
```

#### 7.7 Multiple Environments

```json
{
  "mcpServers": {
    "databricks-production": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
        "DATABRICKS_CLIENT_ID": "prod-client-id",
        "DATABRICKS_CLIENT_SECRET": "prod-secret"
      },
      "disabled": false,
      "alwaysAllow": ["list_clusters", "list_jobs"]
    },
    "databricks-staging": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://staging.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_staging..."
      },
      "disabled": false
    },
    "databricks-development": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://dev.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      },
      "disabled": true
    }
  }
}
```

#### 7.8 Using Pre-configured Servers

Windsurf provides popular MCP servers pre-configured:

1. Click Plugins icon in Windsurf sidebar
2. Select "MCP Servers" tab
3. View available servers list
4. Find "databricks-mcp" (if available)
5. Click "Install" or "Enable"

#### 7.9 Verify Configuration

1. Restart Windsurf
2. Open Cascade panel
3. Click 🔨 icon to view MCP tools list
4. Verify "databricks" server is connected
5. Check available tools list

#### 7.10 Test

In Cascade:
```
@databricks list all my clusters
@databricks show me tables in the main catalog
@databricks execute SQL: SELECT * FROM samples.nyctaxi.trips LIMIT 5
```

---

### 8. OpenAI Codex (CLI) (EN)

OpenAI Codex is a lightweight coding agent that runs in your terminal with full MCP server support.

#### 8.1 Install Codex

```bash
# Install via npm
npm install -g @openai/codex

# Or run directly
npx @openai/codex
```

#### 8.2 Configuration File Location

```
~/.codex/config.toml
```

#### 8.3 Add MCP Server

**Via command line:**
```bash
codex mcp add databricks \
  --env DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
  --env DATABRICKS_AUTH_TYPE=oauth-u2m \
  -- uvx databricks-mcp
```

**Using PAT:**
```bash
codex mcp add databricks \
  --env DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
  --env DATABRICKS_TOKEN=dapi... \
  -- uvx databricks-mcp
```

**Using Service Principal:**
```bash
codex mcp add databricks \
  --env DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
  --env DATABRICKS_CLIENT_ID=your-client-id \
  --env DATABRICKS_CLIENT_SECRET=your-secret \
  -- uvx databricks-mcp
```

#### 8.4 Manual Configuration (config.toml)

```bash
# Edit configuration file
nano ~/.codex/config.toml
```

**Basic configuration:**
```toml
[[mcp_servers]]
name = "databricks"
command = "uvx"
args = ["databricks-mcp"]

[mcp_servers.env]
DATABRICKS_HOST = "https://your-workspace.cloud.databricks.com"
DATABRICKS_AUTH_TYPE = "oauth-u2m"
```

**Multiple workspaces:**
```toml
[[mcp_servers]]
name = "databricks-prod"
command = "uvx"
args = ["databricks-mcp"]

[mcp_servers.env]
DATABRICKS_HOST = "https://prod-workspace.cloud.databricks.com"
DATABRICKS_TOKEN = "dapi_prod..."

[[mcp_servers]]
name = "databricks-dev"
command = "uvx"
args = ["databricks-mcp"]

[mcp_servers.env]
DATABRICKS_HOST = "https://dev-workspace.cloud.databricks.com"
DATABRICKS_AUTH_TYPE = "oauth-u2m"
```

#### 8.5 View MCP Server List

```bash
# In Codex TUI
codex

# Inside TUI
/mcp
```

This displays your actively connected MCP servers.

#### 8.6 Manage MCP Servers

**Remove server:**
```bash
codex mcp remove databricks
```

**List servers:**
```bash
codex mcp list
```

#### 8.7 Use Codex as MCP Server

You can also run Codex itself as an MCP server:

```bash
# Start Codex as MCP server
codex mcp-server

# Test with MCP Inspector
npx @modelcontextprotocol/inspector codex mcp-server
```

#### 8.8 Docker MCP Toolkit

Access 220+ MCP servers securely through Docker MCP Toolkit:

```bash
# Install Docker MCP Toolkit
npm install -g @docker/mcp-toolkit

# Add Databricks MCP server
docker-mcp add databricks
```

#### 8.9 Test

In Codex TUI:
```bash
# Start Codex
codex

# In prompt
> List all my Databricks clusters
> Show tables in catalog 'main'
> Execute SQL: SELECT * FROM samples.nyctaxi.trips LIMIT 5
```

#### 8.10 Integration with OpenAI Agents SDK

Use Codex with OpenAI Agents SDK:

```python
from openai import OpenAI
from codex_mcp import CodexMCPServer

# Initialize Codex as MCP server
server = CodexMCPServer()

# Use in Agent
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "List my Databricks clusters"}
    ],
    tools=server.get_tools()
)
```

---

### 9. Dify (EN)

Dify is an LLMOps platform with two-way MCP support since v1.6.0.

#### 9.1 MCP Support in Dify

Dify supports MCP in two ways:
1. **Consume MCP tools in Dify** (MCP client)
2. **Publish Dify apps as MCP servers** (MCP server)

#### 9.2 Add MCP Server (Use in Dify)

**Method 1: Via Dify UI**

1. Log into Dify workspace
2. Navigate to **Tools** page
3. Select **MCP** section
4. Click **Add Server**
5. Enter server information:

```json
{
  "name": "databricks",
  "type": "stdio",
  "command": "uvx",
  "args": ["databricks-mcp"],
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m"
  }
}
```

**Method 2: Environment Variables**

Set directly in Dify server environment:

```bash
export DIFY_MCP_SERVERS='[
  {
    "name": "databricks",
    "command": "uvx",
    "args": ["databricks-mcp"],
    "env": {
      "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
      "DATABRICKS_TOKEN": "dapi..."
    }
  }
]'
```

#### 9.3 Use in Agent Workflows

**1. Create Agent Node:**
- Add **Agent** node in Workflow
- Select **databricks** in MCP Tools section
- Choose tools to use:
  - `list_clusters`
  - `execute_sql`
  - `list_tables`
  - etc.

**2. Agent automatically calls tools:**
```
User: "Show me all running clusters"
→ Agent automatically calls list_clusters tool
→ Returns results
```

#### 9.4 Use as Workflow Nodes

**Add individual MCP tools as nodes:**

1. Open Workflow editor
2. Click **Add Node**
3. Select **MCP Tool** category
4. Choose **databricks** > **execute_sql**
5. Set parameters:
   ```json
   {
     "warehouse_id": "{{warehouse_id}}",
     "sql": "SELECT * FROM main.default.my_table"
   }
   ```

This approach provides explicit call ordering without LLM decisions.

#### 9.5 Publish Dify Apps as MCP Servers

Expose Dify workflows as MCP servers for use in Claude, Cursor, etc:

**1. Prepare Workflow:**

For all input parameters in Start node:
- **Parameter Name**: Clear name (e.g., `cluster_name`, `sql_query`)
- **Parameter Description**: Detailed description
  ```
  Example: "The name of the Databricks cluster to query"
  ```

**2. Write Service Description:**

In workflow settings:
```
Service Description: "Query Databricks clusters and execute SQL through a Dify workflow"
```

**3. Generate MCP Server URL:**

- After setup, Dify issues MCP server URL
- Example: `https://your-dify.com/mcp/v1/workflows/abc123`

**4. Use in Claude Desktop:**

```json
{
  "mcpServers": {
    "dify-databricks": {
      "url": "https://your-dify.com/mcp/v1/workflows/abc123",
      "headers": {
        "Authorization": "Bearer YOUR_DIFY_API_KEY"
      }
    }
  }
}
```

**5. Use in Cursor:**

`.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "dify-databricks": {
      "url": "https://your-dify.com/mcp/v1/workflows/abc123",
      "headers": {
        "Authorization": "Bearer YOUR_DIFY_API_KEY"
      }
    }
  }
}
```

#### 9.6 Zapier/Composio Integration

Dify MCP provides access to 8,000+ apps through Zapier and Composio:

**Add Zapier MCP:**
1. Select **MCP** on Tools page
2. Add **Zapier** server
3. Enter Zapier API key
4. Select Zapier Actions to use

**Usage example:**
```
"Query data from Databricks and save results to Google Sheets"
→ Get data with Databricks MCP
→ Write to Google Sheets with Zapier MCP
```

#### 9.7 Community MCP Server (dify-mcp-server)

Use third-party MCP server to call Dify workflows:

**Installation:**
```bash
npm install -g dify-mcp-server
```

**Configuration:**
```yaml
# config.yaml
dify:
  base_url: https://your-dify.com
  app_sks:
    - app-abc123-secret-key-1
    - app-def456-secret-key-2
```

**Run:**
```bash
dify-mcp-server --config config.yaml
```

**Claude Desktop configuration:**
```json
{
  "mcpServers": {
    "dify": {
      "command": "dify-mcp-server",
      "args": ["--config", "/path/to/config.yaml"]
    }
  }
}
```

#### 9.8 Verify Configuration

**Check MCP server status:**
1. Open Dify Tools page
2. Check connection status in MCP section
3. Green indicator = connected

**Test tools:**
1. Create Agent node in Workflow
2. Request "List my Databricks clusters"
3. Verify Agent calls MCP tools

#### 9.9 Advanced Configuration

**Multiple Databricks workspaces:**

```json
[
  {
    "name": "databricks-prod",
    "command": "uvx",
    "args": ["databricks-mcp"],
    "env": {
      "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
      "DATABRICKS_TOKEN": "dapi_prod..."
    }
  },
  {
    "name": "databricks-dev",
    "command": "uvx",
    "args": ["databricks-mcp"],
    "env": {
      "DATABRICKS_HOST": "https://dev.cloud.databricks.com",
      "DATABRICKS_AUTH_TYPE": "oauth-u2m"
    }
  }
]
```

**Permission settings:**
- Add MCP servers with Dify Admin rights
- Grant tool usage permissions to team members
- Manage API keys separately

#### 9.10 Test

**In Agent workflow:**
```
User: "What clusters are running in my Databricks workspace?"
→ Dify Agent calls databricks MCP server
→ Uses list_clusters tool
→ Returns results formatted in natural language
```

**As workflow nodes:**
```
[Start] → [MCP: list_clusters] → [LLM: Analyze results] → [End]
```

---

### 10. n8n (EN)

n8n is a workflow automation platform with bidirectional MCP support (both client and server).

#### 10.1 n8n MCP Support Overview

n8n supports MCP in two ways:
1. **MCP Client**: Call external MCP server tools from n8n
2. **MCP Server**: Expose n8n workflows as MCP servers

#### 10.2 Install n8n

```bash
# Global installation via npm
npm install -g n8n

# Using Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n

# Run directly with npx
npx n8n
```

#### 10.3 Using MCP Client Tool Node

Call Databricks MCP server from n8n:

**1. Create Workflow:**
1. Click "New Workflow" in n8n dashboard
2. Add node → "AI" category
3. Select "MCP Client Tool" node

**2. Configure MCP Server Connection:**

In node settings:
```json
{
  "transport": "stdio",
  "command": "uvx",
  "args": ["databricks-mcp"],
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m"
  }
}
```

**3. HTTP Streamable Transport:**

For remote MCP servers:
```json
{
  "transport": "http-streamable",
  "url": "https://your-mcp-server.com/mcp",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN"
  }
}
```

#### 10.4 Using MCP Tools in Agent

**Configure AI Agent Node:**

1. **Add Agent Node**:
   - "AI" → "AI Agent" node
   - Select Model (OpenAI, Anthropic, etc.)

2. **Connect MCP Tools**:
   - Add "MCP Client Tool" in Tools section
   - Configure Databricks MCP server

3. **Example Prompt**:
```
Input: "List all running Databricks clusters and their current state"
→ Agent automatically calls list_clusters MCP tool
→ Analyzes and responds with results
```

#### 10.5 Expose n8n as MCP Server

Make n8n workflows available to Claude, Cursor, etc:

**1. Use MCP Server Trigger Node:**

1. Create new workflow
2. Add "MCP Server Trigger" node
3. Enter tool name and description:
   ```
   Tool Name: query_databricks
   Description: Execute SQL queries on Databricks and format results
   ```

4. Define parameters:
   ```json
   {
     "sql": {
       "type": "string",
       "description": "SQL query to execute",
       "required": true
     },
     "warehouse_id": {
       "type": "string",
       "description": "SQL Warehouse ID"
     }
   }
   ```

5. Build workflow logic:
   - HTTP Request node to call Databricks API
   - Process and format results
   - Return node to send results back

**2. n8n MCP Server URL:**

After activating workflow, get MCP server URL:
```
http://localhost:5678/mcp/workflows/<workflow-id>
```

**3. Use n8n MCP Server in Claude Desktop:**

```json
{
  "mcpServers": {
    "n8n-databricks": {
      "url": "http://localhost:5678/mcp/workflows/<workflow-id>",
      "headers": {
        "Authorization": "Bearer YOUR_N8N_API_KEY"
      }
    }
  }
}
```

#### 10.6 Community Node

**Install n8n-nodes-mcp:**

```bash
# Install from n8n Community Nodes
cd ~/.n8n
npm install n8n-nodes-mcp
```

This custom node supports:
- ✅ HTTP Streamable transport
- ✅ SSE (Server-Sent Events)
- ✅ Command-line transport
- ✅ Bearer & generic header authentication

#### 10.7 Real-World Example: Databricks Automation

**Automation Scenario: Daily Cluster Health Monitoring**

```
[Schedule Trigger: Daily 9 AM]
  ↓
[MCP Client Tool: list_clusters]
  ↓
[Code: Filter running clusters]
  ↓
[IF: Any cluster issues?]
  ↓ Yes
[Slack: Send alert]
  ↓ No
[Email: Daily report]
```

**Workflow Configuration:**

1. **Schedule Trigger** - Daily at 9 AM
2. **MCP Client Tool** - Call Databricks MCP server
3. **Code Node** - Analyze cluster states
4. **IF Node** - Detect issues
5. **Slack/Email** - Send notifications

#### 10.8 Environment Variables

Configure environment variables in n8n:

**When starting n8n server:**
```bash
export N8N_MCP_DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export N8N_MCP_DATABRICKS_TOKEN="dapi..."

n8n start
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_MCP_DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
      - N8N_MCP_DATABRICKS_TOKEN=dapi...
    volumes:
      - n8n_data:/home/node/.n8n
```

#### 10.9 Account API Configuration

For Account-level operations:

```json
{
  "transport": "stdio",
  "command": "uvx",
  "args": ["databricks-mcp"],
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m",
    "DATABRICKS_ACCOUNT_ID": "your-account-id",
    "DATABRICKS_ACCOUNT_HOST": "https://accounts.cloud.databricks.com"
  }
}
```

#### 10.10 Test

**Simple Test Workflow:**

1. Add Manual Trigger node
2. Add MCP Client Tool node (configure Databricks)
3. Tool: `list_clusters`
4. Parameters: `{}`
5. Execute workflow → View cluster list

---

### Troubleshooting (English)

#### Common Issues

##### 1. "uvx: command not found" Error

**Solution:**
```bash
# Install uv
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uvx --version
```

**Alternative: Use pip**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "python",
      "args": ["-m", "databricks_mcp"],
      "env": { ... }
    }
  }
}
```

##### 2. "Could not connect to Databricks" Error

**Check:**
1. DATABRICKS_HOST is correct (no trailing slash)
2. Network connectivity
3. Workspace URL is valid

```json
// ❌ Wrong
"DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com/"

// ✅ Correct
"DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com"
```

##### 3. "Authentication failed" Error

**Using OAuth:**
- Check if browser opens automatically
- Disable popup blockers
- Verify logging in with correct account

**Using PAT:**
- Check token hasn't expired
- Verify token copied correctly (no spaces)
- Ensure token has necessary permissions

**Using Service Principal:**
- Verify Client ID and Secret are correct
- Check Service Principal added to workspace
- Ensure necessary permissions granted

##### 4. MCP Server Icon Not Visible

**Solution:**
1. Completely quit client application
2. Check JSON syntax in config file (commas, brackets)
3. Restart client
4. Check logs (see client-specific log locations)

##### 5. Only Some Tools Working

**Causes:**
- Insufficient permissions
- Required Databricks features not enabled
- Workspace tier limitations

**Solution:**
1. Check user permissions in Databricks
2. Verify necessary features enabled (Unity Catalog, MLflow, etc.)
3. Contact workspace administrator

##### 6. Slow Performance

**Optimization:**
- Disable unused MCP servers
- Use alwaysAllow list for frequently used tools
- Cache tokens locally (OAuth)

#### Client-Specific Issues

##### Claude Desktop

**Issue:** Server not connecting
```bash
# Check logs
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log

# Windows
type %APPDATA%\Claude\logs\mcp*.log
```

##### Cursor

**Issue:** 40 tool limit
- Consider writing custom wrapper with only needed functions
- Split functionality across multiple MCP server instances

##### Cline / Continue

**Issue:** Tool approval prompts keep appearing
- Add frequently used tools to `alwaysAllow` list

##### Zed

**Issue:** Only prompts showing
- Zed's current MCP support is limited
- Direct tool calls planned for future updates

##### Windsurf

**Issue:** Docker container won't start
- Check Docker Desktop is running
- Verify image built correctly
- Check logs: `docker logs <container-id>`

#### Debugging Tips

##### 1. Enable Verbose Logging

Add environment variables:
```json
{
  "env": {
    "DATABRICKS_HOST": "...",
    "DATABRICKS_DEBUG": "true",
    "DATABRICKS_LOG_LEVEL": "DEBUG"
  }
}
```

##### 2. Test MCP Server Manually

```bash
# Run server directly
uvx databricks-mcp

# Run with environment variables
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com \
DATABRICKS_AUTH_TYPE=oauth-u2m \
uvx databricks-mcp
```

##### 3. Test Connection with Databricks CLI

```bash
# Install Databricks CLI
pip install databricks-cli

# Test connection
databricks workspace list
```

##### 4. Network Test

```bash
# Check workspace reachable
curl -I https://your-workspace.cloud.databricks.com

# Test API endpoint
curl -H "Authorization: Bearer dapi..." \
  https://your-workspace.cloud.databricks.com/api/2.0/clusters/list
```

#### Getting Help

If issues persist:

1. **GitHub Issues**: https://github.com/YuujinHwang/databricks-mcp/issues
2. **MCP Official Docs**: https://modelcontextprotocol.io/
3. **Databricks Docs**: https://docs.databricks.com/
4. **Community Forums**:
   - Databricks Community
   - MCP Discord
   - Stack Overflow (#mcp, #databricks)

When filing issues, include:
- MCP client being used and version
- Operating system and version
- Configuration file (remove sensitive info)
- Error messages
- Log output

---

## Additional Resources

### Video Tutorials
- [MCP Setup with Claude Desktop](https://www.youtube.com/results?search_query=mcp+claude+desktop+setup) (Search YouTube)
- [Cursor MCP Configuration](https://www.youtube.com/results?search_query=cursor+mcp+setup) (Search YouTube)

### Community Examples
- [MCP Servers Collection](https://github.com/modelcontextprotocol/servers)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

### Official Documentation
- [Databricks MCP GitHub](https://github.com/YuujinHwang/databricks-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Databricks API Reference](https://docs.databricks.com/api/workspace/introduction)

---

## Contributing to This Guide

Found an error or want to add more clients? Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

---

**Last Updated**: 2025-11-11
**Version**: 1.2.0
**Maintained by**: YuujinHwang

## Changelog

### v1.2.0 (2025-11-11)
- Added n8n workflow automation platform
- Added Account API configuration in Prerequisites
- Added Account API setup to Claude Desktop section
- Now covers 10 major MCP clients (previously 9)
- Enhanced Account-level operations documentation

### v1.1.0 (2025-11-11)
- Added OpenAI Codex (CLI) setup guide
- Added Dify platform configuration
- Now covers 9 major MCP clients (previously 7)

### v1.0.0 (2025-11-11)
- Initial release with 7 MCP clients
- Bilingual documentation (Korean/English)
