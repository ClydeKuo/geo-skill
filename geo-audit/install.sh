#!/bin/sh
# 把 geo-audit skill 链接到各 AI 编程工具读取 skill 的目录。
#
# 用法：bash install.sh [--project DIR] [--user] [--tools claude,agents,cursor]
#   --project DIR  安装到项目目录（默认：本 skill 所在的 git 仓库根目录），使用相对链接
#   --user         安装到用户目录（$HOME），使用绝对链接
#   --tools        claude  -> .claude/skills/   （Claude Code；Cursor 也会读取）
#                  agents  -> .agents/skills/   （Codex、Cursor）
#                  cursor  -> .cursor/skills/   （Cursor 专用目录，一般不需要）
#                  默认 claude,agents
# 已存在且指向本 skill 的链接会跳过；已存在的其他文件/目录不会被覆盖（报错，退出码 1）。
set -u

SKILL_DIR=$(cd "$(dirname "$0")" && pwd -P)
NAME=geo-audit
PROJECT=""
USER_INSTALL=0
TOOLS="claude,agents"

while [ $# -gt 0 ]; do
  case "$1" in
    --project) PROJECT="${2:-}"; [ -n "$PROJECT" ] || { echo "error: --project 需要目录参数" >&2; exit 2; }; shift 2 ;;
    --user) USER_INSTALL=1; shift ;;
    --tools) TOOLS="${2:-}"; [ -n "$TOOLS" ] || { echo "error: --tools 需要取值，如 claude,agents" >&2; exit 2; }; shift 2 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "error: 未知参数 $1" >&2; exit 2 ;;
  esac
done

if [ -z "$PROJECT" ] && [ "$USER_INSTALL" -eq 0 ]; then
  PROJECT=$(git -C "$SKILL_DIR" rev-parse --show-toplevel 2>/dev/null) || {
    echo "error: 本 skill 不在 git 仓库中，请用 --project DIR 或 --user 指定安装位置" >&2; exit 2; }
fi

STATUS=0

relpath() { python3 -c 'import os.path,sys;print(os.path.relpath(sys.argv[1],sys.argv[2]))' "$1" "$2"; }

link_one() {  # $1=base 目录 $2=子目录 $3=relative|absolute
  dir="$1/$2"
  target="$dir/$NAME"
  if [ -e "$target" ] || [ -L "$target" ]; then
    if [ -L "$target" ] && [ "$(cd "$target" 2>/dev/null && pwd -P)" = "$SKILL_DIR" ]; then
      echo "skip $target"
    else
      echo "error: $target already exists（未覆盖）" >&2
      STATUS=1
    fi
    return
  fi
  mkdir -p "$dir" || { STATUS=1; return; }
  dir_real=$(cd "$dir" && pwd -P)
  if [ "$3" = relative ]; then
    src=$(relpath "$SKILL_DIR" "$dir_real")
  else
    src="$SKILL_DIR"
  fi
  if ln -s "$src" "$target"; then echo "linked $target -> $src"; else STATUS=1; fi
}

install_base() {  # $1=base $2=relative|absolute
  old_ifs=$IFS; IFS=,
  for tool in $TOOLS; do
    case "$tool" in
      claude) link_one "$1" ".claude/skills" "$2" ;;
      agents) link_one "$1" ".agents/skills" "$2" ;;
      cursor) link_one "$1" ".cursor/skills" "$2" ;;
      "") ;;
      *) echo "error: 未知工具 $tool（可选 claude,agents,cursor）" >&2; STATUS=1 ;;
    esac
  done
  IFS=$old_ifs
}

[ -n "$PROJECT" ] && install_base "$PROJECT" relative
[ "$USER_INSTALL" -eq 1 ] && install_base "$HOME" absolute
exit $STATUS
