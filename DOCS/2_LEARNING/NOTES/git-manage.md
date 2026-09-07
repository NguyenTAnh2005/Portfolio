# `🎯 Note về Quản lý code với Git`

<blockquote>
</blockquote>

> Tài liệu tổng hợp các kỹ thuật Git cần biết khi làm việc nhóm / dùng branch + PR.

---

## 1. Commit tốt hơn

### 1.1. `git add -p` — Add từng phần thay đổi (staging theo hunk)

**Vấn đề nó giải quyết:** Khi bạn sửa nhiều thứ không liên quan trong cùng 1 file (vd: vừa fix bug vừa refactor tên biến), nếu `git add file.py` rồi commit, bạn sẽ có 1 commit "tả pí lù" chứa nhiều việc khác nhau — khó review, khó revert sau này nếu chỉ 1 phần bị lỗi.

**Cách dùng:**

```bash
git add -p                # hoặc git add --patch
# hoặc chỉ định file cụ thể
git add -p app/services/project_service.py
```

Git sẽ chia file thành từng "hunk" (đoạn thay đổi liền nhau) và hỏi bạn từng cái:

| Phím | Ý nghĩa                                                     |
| ---- | ----------------------------------------------------------- |
| `y`  | Stage hunk này                                              |
| `n`  | Bỏ qua hunk này                                             |
| `s`  | Split — chia hunk nhỏ hơn nữa (nếu hunk gộp quá nhiều dòng) |
| `e`  | Edit thủ công hunk trước khi stage (nâng cao)               |
| `q`  | Thoát, không xử lý phần còn lại                             |

**Quy tắc thực dụng:** Nếu thấy mình đang add nguyên file chỉ vì "lười tách", đó là dấu hiệu nên dừng lại — rất có thể bạn đang gộp 2 việc vào 1 commit.

---

### 1.2. Conventional Commits

**Format chuẩn:**

```
<type>(<scope tùy chọn>): <mô tả ngắn gọn, thì hiện tại>

[phần thân - giải thích thêm, tùy chọn]

[footer - vd: BREAKING CHANGE, Closes #12]
```

**Các `type` phổ biến:**

| Type       | Khi nào dùng                                                           |
| ---------- | ---------------------------------------------------------------------- |
| `feat`     | Thêm tính năng mới                                                     |
| `fix`      | Sửa bug                                                                |
| `refactor` | Đổi cấu trúc code, không đổi hành vi (không phải feat, không phải fix) |
| `docs`     | Chỉ sửa tài liệu/comment                                               |
| `style`    | Format code (khoảng trắng, dấu chấm phẩy...), không ảnh hưởng logic    |
| `test`     | Thêm/sửa test                                                          |
| `chore`    | Việc lặt vặt (update dependency, cấu hình build...)                    |
| `perf`     | Cải thiện hiệu năng                                                    |

**Ví dụ áp dụng vào project của bạn:**

```
feat(project): thêm endpoint list project với pagination

fix(crud): sửa lỗi get_by_id trả None khi id không tồn tại thay vì raise 404

refactor(service): đổi import sang module-level để tránh trùng tên hàm

docs(readme): thêm hướng dẫn setup PostgreSQL local
```

**Vì sao nên dùng:**

- Đọc `git log --oneline` là biết ngay commit nào là tính năng, commit nào là fix.
- Một số tool (changelog generator, semantic-release) tự động đọc prefix này để tạo release notes.
- Ép bạn suy nghĩ "commit này thực chất là loại thay đổi gì" → commit sẽ tự nhiên nhỏ và rõ ràng hơn.

---

## 2. Xử lý tình huống "lỡ tay"

### 2.1. `git commit --amend` — Sửa commit gần nhất

**Dùng khi:** Vừa commit xong thì phát hiện quên add 1 file, hoặc gõ sai message.

```bash
# Sửa message của commit gần nhất
git commit --amend -m "fix: sửa message đúng hơn"

# Quên add file, giữ nguyên message cũ
git add file_quen_add.py
git commit --amend --no-edit
```

⚠️ **Lưu ý quan trọng:** `--amend` **tạo ra 1 commit mới thay thế commit cũ** (đổi hash). Nếu commit đó **đã push lên remote và người khác đã pull về**, amend rồi push lại sẽ gây lệch lịch sử → tránh amend commit đã push trừ khi chắc chắn không ai khác đang dùng nhánh đó (hoặc dùng `git push --force-with-lease` một cách có ý thức).

---

### 2.2. `git reset --soft HEAD~1` — Undo commit, giữ code

**3 loại reset, phân biệt rõ:**

| Lệnh                 | Commit | Staging area            | Working directory (code) |
| -------------------- | ------ | ----------------------- | ------------------------ |
| `--soft`             | Undo   | Giữ nguyên (vẫn staged) | Giữ nguyên               |
| `--mixed` (mặc định) | Undo   | Reset về chưa staged    | Giữ nguyên               |
| `--hard`             | Undo   | Reset                   | **Mất luôn thay đổi** ⚠️ |

```bash
git reset --soft HEAD~1   # commit biến mất, code + staging vẫn còn → sửa rồi commit lại
git reset HEAD~1          # commit biến mất, code còn nhưng phải add lại
git reset --hard HEAD~1   # commit biến mất, code cũng mất luôn (cẩn thận!)
```

**Tình huống thực tế:** Commit xong 3 commit nhỏ lẻ tẻ, muốn gộp lại thành 1 commit sạch trước khi push:

```bash
git reset --soft HEAD~3   # undo 3 commit, code + thay đổi vẫn nằm ở staging
git commit -m "feat(project): thêm search/filter/pagination cho project list"
```

---

### 2.3. `git stash` — Tạm cất code đang dở

**Dùng khi:** Đang code dở ở nhánh A, sếp/bug khẩn cấp bắt bạn chuyển sang nhánh B ngay, nhưng chưa muốn commit code dở ở A.

```bash
# Nếu có dạng tạo mới file thì nên git add . cho xử lý ổn nhất
git add .
# chỉ thay đổi file thì chỉ cần git stash
git stash                     # cất code đang dở (cả staged lẫn chưa staged)
git stash push -m "wip: đang làm useListQuery hook"   # cất kèm mô tả, dễ nhớ

git checkout main             # chuyển nhánh, code đang dở "biến mất" tạm thời
# ... làm việc khác ...

git checkout feature/xyz      # quay lại nhánh cũ
git stash list                 # xem danh sách các stash đang có
git stash pop                  # lấy stash gần nhất ra + xóa khỏi danh sách
git stash apply stash@{0}      # lấy ra nhưng KHÔNG xóa khỏi danh sách (nếu muốn áp cho nhiều nhánh)
```

**Lưu ý:** Mặc định `git stash` không cất file **chưa được track** (file mới tạo). Muốn cất luôn:

```bash
git stash -u    # bao gồm cả untracked files
```

<blockquote>
## `"Tracked" và "untracked" là gì?`

\*\* Ví dụ: Ban đầu viết gitignore không kịp track file `__pycache__`, vô tình up lên git ở các commit trước, bây giờ cần xử lý sao cho git không up lên ở các lần sau nữa.

- **Tracked** = file đã từng được `git add` + `git commit` ít nhất 1 lần → Git đang "theo dõi" nó, mọi thay đổi sau này đều được Git ghi nhận.
- **Untracked** = file Git chưa từng biết tới (file mới tạo, chưa `git add` bao giờ).

`.gitignore` chỉ có tác dụng với file **chưa từng được track** — nó nói với Git "đừng thèm để ý mấy file này". Nhưng với file **đã tracked** rồi, Git vẫn tiếp tục theo dõi nó **bất kể** bạn có thêm vào `.gitignore` hay không. Đây là lý do dù bạn cập nhật `.gitignore`, mấy thư mục `__pycache__` vẫn nằm ì trong repo GitHub.

**`git rm -r --cache <path>` làm gì?**

- `git rm` bình thường = xoá file khỏi cả ổ đĩa lẫn Git.
- Thêm `--cache` = chỉ xoá khỏi **vùng theo dõi của Git (index/staging)**, **file thật trên máy bạn vẫn còn nguyên**.
- Thêm `-r` = làm đệ quy (áp dụng cho cả thư mục con).

Nói cách khác: `git rm -r --cache .` = "Git ơi, quên hết mấy file này đi, coi như chưa từng track" — nhưng file vẫn nằm trên ổ cứng bạn.

Vì `git rm --cache` **không tự đọc `.gitignore`** để biết cái nào cần bỏ — nó chỉ làm đúng theo path bạn chỉ định. Nên cách phổ biến là: bỏ track **hết** (`git rm -r --cache .`), sau đó `git add .` lại — lúc `add` lại này Git **mới** đọc `.gitignore` và tự động **loại trừ** những file bị ignore (như `__pycache__`, `.pyc`). Kết quả cuối cùng: mọi thứ quay lại y như cũ, trừ mấy file/thư mục bạn vừa thêm vào `.gitignore` thì bị bỏ track thật sự.

```
git rm -r --cache .     # bỏ track hết (file trên máy vẫn còn)
git add .                # track lại, nhưng .gitignore mới sẽ loại pycache ra
git status                # kiểm tra: chỉ nên thấy pycache/.pyc bị "deleted"
git commit -m "chore: stop tracking pycache files"
git push
```

Sau `git push`, các thư mục `__pycache__` sẽ **biến mất khỏi GitHub** (nhưng vẫn còn trên máy bạn), và từ giờ về sau Git sẽ không track lại chúng nữa.

</blockquote>

---
