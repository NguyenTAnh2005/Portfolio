# Ghi chú Git — Từ cơ bản đến xử lý tình huống thực tế

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

---

## 3. Đồng bộ nhánh với main

### 3.1. Merge vs Rebase — khác nhau ở đâu

Giả sử nhánh `feature` tách ra từ `main` tại điểm C2, sau đó `main` có thêm commit C3, còn `feature` có thêm commit C4.

```
main:     C1 - C2 - C3
                \
feature:         C4
```

**`git merge main` (đang đứng ở nhánh feature):**

```bash
git checkout feature
git merge main
```

→ Tạo ra **1 merge commit mới** (C5) có 2 cha là C3 và C4:

```
main:     C1 - C2 - C3
                \     \
feature:         C4 -- C5 (merge commit)
```

- ✅ Không viết lại lịch sử, an toàn tuyệt đối kể cả nhánh đã push và người khác đang dùng chung.
- ❌ Lịch sử có nhiều merge commit chằng chịt nếu sync nhiều lần → log rối hơn.

**`git rebase main` (đang đứng ở nhánh feature):**

```bash
git checkout feature
git rebase main
```

→ Git "gỡ" commit C4 ra, tạm giữ riêng, rồi **chơi lại (replay)** C4 lên trên đầu C3, tạo ra C4' (hash mới hoàn toàn):

```
main:     C1 - C2 - C3
                     \
feature:              C4' (bản sao của C4, nhưng hash khác)
```

- ✅ Lịch sử thẳng, sạch, dễ đọc — như thể bạn bắt đầu code từ commit mới nhất của main.
- ❌ **Viết lại lịch sử** (đổi hash của C4 → C4'). Nếu nhánh `feature` đã push lên remote và người khác đã pull, sau khi bạn rebase và push lại (`--force-with-lease`), họ sẽ bị lệch lịch sử, dễ conflict rối tung.

**Quy tắc thực dụng (rất phổ biến trong thực tế):**

- Nhánh cá nhân, chưa share cho ai / chưa mở PR → cứ rebase thoải mái, giữ lịch sử sạch.
- Nhánh đã có người khác cùng làm chung, hoặc `main`/`develop` (nhánh chung) → **không bao giờ rebase**, chỉ merge.
- Câu thần chú: _"Rebase local, merge shared"_ (rebase nhánh của riêng mình, merge nhánh dùng chung).

---

### 3.2. Sync nhánh feature với main (quy trình thường dùng)

```bash
git checkout feature
git fetch origin              # lấy thông tin mới nhất từ remote, chưa merge gì cả
git rebase origin/main         # replay commit của feature lên trên main mới nhất

# nếu có conflict, xử lý (xem mục 4), rồi:
git add <file đã resolve>
git rebase --continue

# sau khi rebase xong, vì lịch sử đã bị viết lại, cần force push (an toàn hơn --force):
git push --force-with-lease
```

`--force-with-lease` an toàn hơn `--force` thường vì nó sẽ **từ chối push** nếu remote có commit mới mà bạn chưa fetch về (tránh vô tình đè mất commit của người khác).

---

## 4. Xử lý conflict khi merge/rebase

Khi Git không tự động gộp được 2 thay đổi trên cùng 1 dòng/khu vực code, nó sẽ dừng lại và đánh dấu file bị conflict như sau:

```python
def get_by_id(db, id):
<<<<<<< HEAD
    return db.query(Project).filter(Project.id == id).first()
=======
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(404)
    return project
>>>>>>> feature/add-404-handling
```

**Cách đọc:**

- `<<<<<<< HEAD` đến `=======`: code hiện tại ở nhánh bạn đang đứng (khi merge) hoặc ở main (khi rebase).
- `=======` đến `>>>>>>> tên-nhánh-kia`: code từ nhánh/commit đang được merge/replay vào.

**Quy trình xử lý:**

1. Mở file, đọc kỹ 2 phiên bản, quyết định giữ bên nào / kết hợp cả 2 / viết lại hoàn toàn.
2. **Xóa hết** các dòng đánh dấu `<<<<<<<`, `=======`, `>>>>>>>` — Git không tự xóa giúp bạn.
3. Đảm bảo code sau khi resolve chạy được (không sót logic của 1 trong 2 bên).
4. Đánh dấu đã resolve:
   ```bash
   git add app/crud/project.py
   ```
5. Tiếp tục:
   ```bash
   git rebase --continue     # nếu đang rebase
   git commit                # nếu đang merge (Git tự tạo message merge, có thể sửa)
   ```

**Nếu rối quá, muốn hủy giữa chừng:**

```bash
git rebase --abort     # hủy toàn bộ rebase, về lại trạng thái trước khi bắt đầu
git merge --abort       # tương tự cho merge
```

**Mẹo giảm conflict:** Sync nhánh với main **thường xuyên** (mỗi ngày hoặc trước khi bắt đầu 1 task mới), thay vì để 2 tuần mới sync 1 lần — conflict dồn cục càng lâu càng khó resolve.

---

## 5. Squash commit trước khi merge (làm sau, không gấp)

**Mục đích:** Nhánh `feature` của bạn có thể có 10 commit be bét kiểu `wip`, `fix typo`, `oops`, `thử lại` — không ai muốn thấy những commit này trong lịch sử của `main`. Squash gộp tất cả lại thành 1-2 commit sạch, có ý nghĩa.

**Cách 1 — Interactive rebase (linh hoạt nhất):**

```bash
git rebase -i HEAD~10    # 10 = số commit muốn gộp, tính từ commit gần nhất
```

Trình editor sẽ mở ra danh sách commit dạng:

```
pick a1b2c3 feat: thêm queryParam state
pick d4e5f6 wip
pick g7h8i9 fix typo
pick j1k2l3 feat: hoàn thiện pagination
```

Đổi `pick` thành `squash` (hoặc `s`) cho các commit muốn gộp _vào commit phía trên nó_:

```
pick a1b2c3 feat: thêm queryParam state
squash d4e5f6 wip
squash g7h8i9 fix typo
pick j1k2l3 feat: hoàn thiện pagination
```

Lưu lại → Git mở tiếp 1 màn hình để bạn viết message chung cho commit đã gộp.

**Cách 2 — Squash merge (đơn giản hơn, làm ở phía main):**

```bash
git checkout main
git merge --squash feature/search-pagination
git commit -m "feat(project): thêm search, filter, pagination cho project list"
```

→ Tất cả thay đổi từ `feature` được gộp thành **1 commit duy nhất** trên `main`, nhánh `feature` giữ nguyên lịch sử chi tiết của nó (không bị ảnh hưởng).

**Ghi chú:** Nhiều nơi làm việc nhóm dùng GitHub/GitLab có sẵn nút **"Squash and merge"** khi merge Pull Request — về bản chất giống Cách 2, không cần làm tay.

---

## Tổng kết nhanh — khi nào dùng gì

| Tình huống                                          | Lệnh                                                                              |
| --------------------------------------------------- | --------------------------------------------------------------------------------- |
| Muốn chia nhỏ commit trong 1 file                   | `git add -p`                                                                      |
| Vừa commit sai message/thiếu file                   | `git commit --amend`                                                              |
| Muốn undo commit nhưng giữ code                     | `git reset --soft HEAD~N`                                                         |
| Cần chuyển nhánh gấp, code đang dở                  | `git stash` / `git stash pop`                                                     |
| Nhánh riêng, muốn lịch sử sạch, sync với main       | `git rebase main`                                                                 |
| Nhánh dùng chung với người khác                     | `git merge main`                                                                  |
| Conflict xuất hiện                                  | Đọc `<<<<<<<` `=======` `>>>>>>>`, sửa, `git add`, `rebase --continue` / `commit` |
| Nhánh nhiều commit lộn xộn trước khi merge vào main | `git rebase -i` (squash) hoặc `git merge --squash`                                |
