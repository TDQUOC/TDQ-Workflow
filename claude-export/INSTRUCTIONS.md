# INSTRUCTIONS — Dựng bundle export cấu hình Claude Code

Bộ công cụ tĩnh này nằm trong repo TDQWorkflow (`claude-export/`), tái dùng được
nhiều lần: mỗi khi cấu hình máy nguồn đổi (thêm plugin, đổi skill...), chạy lại
đủ 7 bước dưới đây để sinh một bundle export mới. Bundle SINH RA nằm ở đường dẫn
đích do người chạy chỉ định — KHÔNG bao giờ đặt bên trong `claude-export/`.

Biến dùng xuyên suốt (đặt trước khi bắt đầu):
```bash
EXPORT_DEST="$HOME/Documents/claude-code-export"   # đổi nếu muốn đích khác
REPO_SRC="/Users/truongdinhquoc/Documents/TDQWorkflow"
```

## Bước 1 — Thu thập trạng thái thật máy nguồn

```bash
mkdir -p "$EXPORT_DEST"
python3 -m json.tool ~/.claude/settings.json > /dev/null   # xác nhận JSON hợp lệ
python3 -m json.tool ~/.claude/plugins/installed_plugins.json > /dev/null
python3 -m json.tool ~/.claude/plugins/known_marketplaces.json > /dev/null
python3 -c "import json; d=json.load(open('$HOME/.claude.json')); print(list(d.get('mcpServers',{}).keys()))"
claude --version && node --version && python3 --version && git --version && uv --version && graphify --version
codex --version 2>/dev/null || true
agy --version 2>/dev/null || true
```

## Bước 2 — Lọc secret/runtime

- KHÔNG bao giờ copy giá trị thật của `TAVILY_API_KEY_PRIMARY`/`TAVILY_API_KEY_BACKUP`
  hay bất kỳ token/oauth nào trong `~/.claude.json` (`oauthAccount`, `machineID`, `userID`).
- Khi copy `settings.json`, thay 2 giá trị key thật bằng placeholder tường minh
  (`"<TAVILY_API_KEY_PRIMARY — điền lại>"`, tương tự cho BACKUP).
- Loại trừ hoàn toàn (không copy) các mục sau nếu có trong đường copy:
  `history.jsonl`, `sessions/`, `projects/*/*.jsonl`, `debug/`, `logs/`, `cache/`,
  `shell-snapshots/`, `file-history/`, `telemetry/`, `image-cache/`, `paste-cache/`,
  `ide/`, `daemon*`, `plugins/cache/`, `plugins/plugin-catalog-cache.json`,
  `plugins/data/`, `.DS_Store`, `*.bak*`.

## Bước 3 — Copy file cấu hình local + repo TDQWorkflow

```bash
mkdir -p "$EXPORT_DEST/config"
cp ~/.claude/settings.json "$EXPORT_DEST/config/settings.json"      # sửa 2 key theo Bước 2 SAU KHI copy
cp ~/.claude/CLAUDE.md "$EXPORT_DEST/config/CLAUDE.md"
cp ~/.claude/plugin-tiers.json "$EXPORT_DEST/config/plugin-tiers.json"
cp -R ~/.claude/skills/graphify "$EXPORT_DEST/config/skills-graphify"
cp -R ~/.claude/.remember "$EXPORT_DEST/config/remember"
cp ~/.claude/statusline.sh "$EXPORT_DEST/config/statusline.sh"
cp -R ~/.claude/scripts "$EXPORT_DEST/config/scripts"
cp ~/.claude/plugins/installed_plugins.json "$EXPORT_DEST/config/installed_plugins.json"
cp ~/.claude/plugins/known_marketplaces.json "$EXPORT_DEST/config/known_marketplaces.json"
rsync -a --exclude='.git' --exclude='*.bak*' --exclude='__pycache__' \
  --exclude='.remember/logs' --exclude='graphify-out/cache' \
  "$REPO_SRC/" "$EXPORT_DEST/tdqworkflow-repo/"
```
(`.git` loại trừ theo mặc định — repo không có remote, giữ `.git` không cần thiết
và làm bundle nặng hơn; muốn giữ lịch sử thì bỏ `--exclude='.git'`. 4 exclude còn lại
khớp danh sách loại trừ Bước 2 khi chúng lọt vào bên trong chính repo: file `*.bak*`
lẻ tẻ, thư mục cache bytecode `__pycache__`, log runtime của plugin remember
`.remember/logs/`, và cache runtime của graphify `graphify-out/cache/` — rsync không
tự đọc `.gitignore` nên phải loại tay; cả 4 đều là dữ liệu untracked/regenerate-được,
không phải nội dung repo cần giữ.)

## Bước 4 — Rewrite path marketplace `tdq-local` theo vị trí đích (BẮT BUỘC)

Không làm bước này, plugin `tdq-workflow` sẽ KHÔNG load được trên máy đích.

```bash
NEW_REPO_PATH="$EXPORT_DEST/tdqworkflow-repo"
python3 - "$EXPORT_DEST/config/settings.json" "$NEW_REPO_PATH" <<'PYEOF'
import json, sys
path, new_path = sys.argv[1], sys.argv[2]
d = json.load(open(path))
d.setdefault("extraKnownMarketplaces", {}).setdefault("tdq-local", {})["source"] = {
    "source": "directory", "path": new_path,
}
json.dump(d, open(path, "w"), indent=2)
PYEOF
python3 - "$EXPORT_DEST/config/known_marketplaces.json" "$NEW_REPO_PATH" <<'PYEOF'
import json, sys
path, new_path = sys.argv[1], sys.argv[2]
d = json.load(open(path))
d.setdefault("tdq-local", {})["source"] = {"source": "directory", "path": new_path}
d["tdq-local"]["installLocation"] = new_path
json.dump(d, open(path, "w"), indent=2)
PYEOF
```

## Bước 5 — Điền manifest

```bash
python3 -c "
import json
plugins = json.load(open('$EXPORT_DEST/config/installed_plugins.json'))['plugins']
mkts = json.load(open('$EXPORT_DEST/config/known_marketplaces.json'))
mcp = json.load(open('$HOME/.claude.json')).get('mcpServers', {})
manifest = json.load(open('claude-export/MANIFEST.template.json'))
manifest['plugins'] = {k: v for k, v in plugins.items()
                        if any(e.get('scope') == 'user' for e in v)}
manifest['marketplaces'] = mkts
manifest['mcp_servers'] = {k: {kk: vv for kk, vv in v.items() if kk != 'headers'}
                            for k, v in mcp.items()}
json.dump(manifest, open('$EXPORT_DEST/manifest.json', 'w'), indent=2)
"
python3 -m json.tool "$EXPORT_DEST/manifest.json" > /dev/null
```
(Điền `cli_dependencies` bằng version thu được ở Bước 1; điền `excluded` bằng
đúng danh sách loại trừ ở Bước 2.)

## Bước 6 — Điền README

Copy `claude-export/README.template.md` thành `$EXPORT_DEST/README.md`, điền:
tên bundle + ngày export, danh sách plugin/marketplace thật (đọc từ
`manifest.json` vừa sinh ở Bước 5 — số lượng phải khớp 100%), giữ nguyên 2
placeholder API key (không điền giá trị thật).

## Bước 7 — Ghi log

```bash
echo "$(date '+%Y-%m-%d %H:%M') — EXPORT_DEST=$EXPORT_DEST" >> claude-export/EXPORT_LOG.md
echo "$(date '+%Y-%m-%d %H:%M') — <tóm tắt: số file copy, số plugin liệt kê, cảnh báo nếu có>" >> claude-export/EXPORT_LOG.md
```

Muốn TẮT ghi log cho lần chạy này (ngoại lệ có chủ đích, KHÔNG phải mặc định):
đặt biến trước khi chạy 2 lệnh `echo` trên:
```bash
TDQ_EXPORT_NO_LOG=1
```
Khi biến này = 1, bỏ qua cả 2 lệnh ghi log ở trên — không thêm entry mới.
