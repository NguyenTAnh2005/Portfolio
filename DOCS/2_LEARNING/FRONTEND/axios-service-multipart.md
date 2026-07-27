## Cách thiết kế axios service cho Timeline

Nguyên tắc: **mỗi hàm service ứng với đúng 1 endpoint**, tham số truyền vào là những gì _người gọi hàm_ (component React) có sẵn — không nhất thiết giống y hệt tham số bên backend.

```js
// FRONTEND/src/services/timeline.js
import axiosInstance from "./axiosConfig";

const ENDPOINT = "/timeline";

// Funct hỗ trợ xử lý khi gọi API endpoint cần nhận MultiPart thay vì JSON
// -> parse class Pydantic thông thường.
// Funct nhận vào là 1 object từ biến useState
export const buildFormData = (data) => {
  // Do multipart nên các thành phần sẽ được gửi từ data của input từng field
  // nên nếu như không thay đổi (ko nhập) - sẽ gửi "" hay null nên nhiệm vụ Func
  // này là phát hiện có những trường nào có dấu hiệu trên sẽ loại bỏ, ko gửi
  // đi gọi API tránh ghi đè dữ liệu.
  // Dù bên backend có làm ntn rồi nhưng việc bảo mật 2 lớp FE BE là không bao giờ thừa

  // 1. Tạo mới Object FormData
  const formData = new FormData();
  for (const key in data) {
    const value = data[key];
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  }
  return formData;
};

// tạo service gồm các func:
export const TimelineService = {
  // POST - nhận đầu vào là FormData (buộc có đầy đủ các field)
  create: async (data) => {
    // eg: data = {title: "abc", desc:"Hi",...}
    const formData = buildFormData(data);
    const response = await axiosInstance.post(`${END_POINT}/`, formData);
    return response;
  },
  // GET - Nhận int là id cần tìm
  get: async (id) => {
    // id: 1
    const response = await axiosInstance.get(`${END_POINT}/${id}`);
    return response;
  },
  // GetAll - Nhận object, axios tự parse -> chuỗi query param
  getAll: async (queryParam) => {
    const response = await axiosInstance.get(`${END_POINT}/`, { queryParam });
    return response;
  },
  // PUT - Nhận vào: id cần sửa, FormData (Optional các field --> helper sẽ giúp bỏ những cái ko đổi)
  update: async (id, data) => {
    const formData = buildFormData(data);
    const response = await axiosInstance.put(`${END_POINT}/${id}`, formData);
    return response;
  },
  // DELETE - Nhận vào là id cần xóa
  delete: async (id) => {
    const response = axiosInstance.delete(`${END_POINT}/${id}`);
    return response;
  },
};
```

- **`id` tách riêng khỏi `data`**: `id` là định danh nằm trên URL (path param), còn `data` là nội dung form (body) — hai thứ khác bản chất nên không nên gộp vào chung 1 object rồi tự bóc tách trong service.
- **`create` vs `update` dùng chung `buildFormData`**: vì cấu trúc field giống hệt nhau (chỉ khác là create thì các field bắt buộc, update thì optional) — tránh lặp code.
- **Không cần tự xử lý `sort_order` rỗng ở đây**: đó là việc của component/form khi submit (ví dụ nếu input rỗng thì đừng đưa key `sort_order` vào object `data` truyền xuống service, thay vì gửi `""`).
- **`getAll(params)`** nhận object rồi để axios tự build query string qua `{ params }` — không cần bạn tự nối chuỗi URL.

## FormData là gì và tại sao "gom 1 cục" rồi gửi?

Đây là chỗ dễ hiểu lầm nhất: **`FormData` KHÔNG phải là gửi 1 object JSON dạng gộp**. Nó là một cấu trúc dữ liệu đặc biệt của trình duyệt, mô phỏng đúng y hệt cách một cái `<form multipart/form-data>` HTML truyền thống gửi dữ liệu — tức là nhiều "phần" (parts) độc lập, mỗi phần có tên riêng.

```js
const formData = new FormData();
formData.append("title", "Learn React");
formData.append("sort_order", "1");
formData.append("img_file", fileObject);
```

Khi bạn `console.log(formData)` sẽ **không** thấy nội dung (vì nó không phải object thường), nhưng khi gửi đi qua network, body thật sự của request trông như thế này (đơn giản hoá):

```
------WebKitFormBoundaryABC123
Content-Disposition: form-data; name="title"

Learn React
------WebKitFormBoundaryABC123
Content-Disposition: form-data; name="sort_order"

1
------WebKitFormBoundaryABC123
Content-Disposition: form-data; name="img_file"; filename="avatar.png"
Content-Type: image/png

<dữ liệu nhị phân của file>
------WebKitFormBoundaryABC123--
```

→ **Mỗi `formData.append(key, value)` = đúng 1 field lẻ**, y hệt như bên FastAPI nhận `title: str = Form(...)`, `img_file: UploadFile = File(...)` — mỗi cái là 1 field lẻ. Bạn không hề "gộp cục" theo nghĩa JSON, mà chỉ đang **đóng gói nhiều field lẻ vào chung 1 cái "phong bì" `FormData`** để trình duyệt gửi đi trong 1 request multipart. Backend nhận về vẫn là các field tách rời như cũ, không có gì thay đổi bản chất.

**Vậy tại sao không viết tay từng dòng `append` như ví dụ trên, mà dùng vòng lặp?**

```js
const buildFormData = (data) => {
  const formData = new FormData();

  for (const key in data) {
    const value = data[key];
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  }

  return formData;
};
```

Giải thích:

- `for (const key in data)`: lặp qua **từng tên field** (key) có trong object `data`. Ví dụ `data = { title: "abc", sort_order: 1 }` thì `key` lần lượt là `"title"`, rồi `"sort_order"`.
- `data[key]`: lấy giá trị tương ứng với key đó — giống hệt `data.title`, nhưng viết bằng biến `key` thay vì gõ chết tên field, để dùng chung cho mọi field.
- Còn lại y hệt bản cũ: nếu có giá trị thật (không `undefined`/`null`) thì mới `append` vào `formData`.

Viết tay `formData.append("title", data.title); formData.append("organization", data.organization); ...` cho 5-6 field thì dài dòng, dễ quên field khi thêm/bớt sau này. Vòng lặp giúp bạn chỉ cần sửa object `data` truyền vào, không phải sửa code build FormData. Đây thuần là tiện lợi code, **không thay đổi việc gửi đi vẫn là từng field lẻ**.

## 2. `axiosInstance.post(url, formData, { headers: {...} })` hoạt động ra sao

`axiosInstance.post(url, data, config)` có 3 tham số:

- `url`: endpoint
- `data`: **body** của request — bình thường bạn gửi object JS thường (`{ name: "abc" }`), axios tự `JSON.stringify` nó và set header `Content-Type: application/json`. Khi bạn gửi `FormData` thay vì object thường, axios (thật ra là trình duyệt qua `XMLHttpRequest`/`fetch` bên dưới) tự hiểu đây là multipart và encode nhị phân đúng chuẩn.
- `config`: cấu hình thêm, trong đó `headers` là nơi bạn override header mặc định.

Về dòng `headers: { "Content-Type": "multipart/form-data" }` thực ra dòng này **hơi thừa và có thể gây lỗi tinh vi**. Lý do:

Multipart request bắt buộc phải có `boundary` trong header, dạng:

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryABC123
```

Cái `boundary` này là chuỗi ngẫu nhiên do trình duyệt tự sinh ra để đánh dấu ranh giới giữa các field (bạn thấy `------WebKitFormBoundary...` trong ví dụ ở mục 1). Nếu bạn tự tay set `Content-Type: multipart/form-data` (thiếu `boundary`), có 2 khả năng:

- Trình duyệt/axios đủ thông minh tự thêm boundary đè lên → vẫn chạy được (thường gặp).
- Một số case bị thiếu boundary → backend không parse được multipart, lỗi 422 khó hiểu.

**Cách an toàn nhất:** không set `Content-Type` tay khi gửi `FormData` — cứ để axios tự nhận diện `data` là instance của `FormData` rồi tự set đúng cả `multipart/form-data` lẫn `boundary`:

```js
create: async (data) => {
  const formData = buildFormData(data);
  const response = await axiosInstance.post(`${ENDPOINT}/`, formData);
  return response;
},
```

Bạn có thể bỏ hẳn object `headers` đi, gọn hơn mà lại an toàn hơn.

## 3. Có nên giữ `if (value !== undefined && value !== null)` không?

Nên giữ, và đúng là nó khớp với logic backend bạn đã viết. Đối chiếu:

- Backend (`parse_field_text_to_pydantic_class`): nếu field là `None` hoặc `""` → **bỏ qua, không set vào Pydantic** → field đó giữ nguyên giá trị cũ trong DB.
- Frontend: nếu field là `undefined`/`null` → **không `append` vào FormData** → field đó sẽ không có mặt trong request → backend nhận được `None` (Form field vắng mặt → `Form(None)` → `None`) → cũng bị bỏ qua tương tự.

→ Hai lớp lọc bổ trợ nhau, không thừa: **frontend lọc để không gửi field thừa lên**, **backend lọc phòng trường hợp có field gửi lên nhưng rỗng `""`** (như bạn note trong file — do Swagger/form luôn gửi `""` chứ không bỏ hẳn field). Với form React tự viết tay (không phải Swagger), bạn kiểm soát được việc có `append` hay không nên ít bị dính case `""`, nhưng vẫn nên giữ điều kiện `undefined/null` để code chủ động, không phụ thuộc hoàn toàn vào backend dọn rác.

Một lưu ý nhỏ: nếu sau này bạn có ô input nào người dùng **cố tình xoá trắng để xoá dữ liệu cũ** (ví dụ muốn xoá hẳn `desc`), thì cách lọc `undefined/null` này sẽ **không cho phép xoá** (vì `""` vẫn bị backend bỏ qua). Hiện tại thiết kế backend của bạn không hỗ trợ "set về rỗng" khi update — đây là giới hạn đã biết (bạn có ghi chú "nếu muốn set none thì phải điền form hơi khác" trong code cũ), không phải bug, chỉ là điều cần nhớ khi thiết kế form update sau này.

## Path param vs Query param

Đây là 2 khái niệm khác hẳn nhau, dễ lẫn:

**Path param** — nằm ngay trong đường dẫn URL, dùng để **xác định 1 tài nguyên cụ thể** (bắt buộc phải có, thiếu là sai URL):

```
GET /timeline/5
              ↑ đây là path param, "5" = id của timeline cần lấy
```

Backend khai báo qua chính path: `@router.get("/{timeline_id}")`. Frontend gọi: `axiosInstance.get(\`${ENDPOINT}/5\`)` — bạn tự nối chuỗi vào URL.

**Query param** — nằm sau dấu `?`, dạng `key=value`, nối nhau bằng `&`, dùng cho **lọc/phân trang/sắp xếp** (thường optional, có giá trị mặc định):

```
GET /timeline/?skip=0&limit=10&sort_by=id&order=asc
               ↑ đây là các query param
```

Backend khai báo bằng `Query(...)` (như trong `get_all` của bạn: `skip: int = Query(0, ...)`). Frontend gọi thì **không tự nối chuỗi tay**, mà đưa object vào `params`, axios tự build:

```js
axiosInstance.get(`${ENDPOINT}/`, {
  params: { skip: 0, limit: 10, sort_by: "id", order: "asc" },
});
// axios tự biến thành: GET /timeline/?skip=0&limit=10&sort_by=id&order=asc
```

→ Quy tắc chọn: cái gì để **xác định "cái nào"** (record nào) → path param. Cái gì để **lọc/điều chỉnh cách trả về** (bao nhiêu, sắp theo gì) → query param.

## 4. Thiết kế state bên FE cho form Create

Trước tiên chỉnh lại 1 từ: bên JS/React, cái bạn lưu trong `useState` là một **object** (JS gọi vậy, không gọi "dict" như Python, cũng không gọi "JSON" — JSON chỉ là _tên định dạng chuỗi_ dùng khi truyền/lưu dữ liệu dạng text, còn khi đang chạy trong code JS thì nó luôn là "object" bình thường).

Cách làm chuẩn:

```jsx
const [formData, setFormData] = useState({
  title: "",
  organization: "",
  desc: "",
  start_end: "",
  sort_order: "",
  img_file: null,   // chưa có ảnh nào thì để null, không phải "None" (đó là từ Python)
});

// Khi user gõ vào 1 ô input text (dùng chung 1 handler cho mọi field text)
const handleChange = (e) => {
  const { name, value } = e.target; // name = "title", value = user gõ gì đó
  setFormData((prev) => ({
    ...prev,       // giữ nguyên các field khác
    [name]: value, // chỉ cập nhật đúng field vừa đổi
  }));
};

// Khi user chọn file ảnh — xử lý riêng vì input file khác input text
const handleFileChange = (e) => {
  setFormData((prev) => ({
    ...prev,
    img_file: e.target.files[0], // lấy file đầu tiên user chọn
  }));
};

// JSX:
<input name="title" value={formData.title} onChange={handleChange} />
<input name="sort_order" value={formData.sort_order} onChange={handleChange} />
<input type="file" onChange={handleFileChange} />
```

Khi submit, gọi thẳng `timelineService.create(formData)` — object này đã đúng shape để đưa vào `buildFormData()` luôn, không cần biến đổi gì thêm. Với **create**, vì mọi field đều bắt buộc, bạn không cần lo phần lọc `undefined/null` (form validate đủ trước khi submit là được) — phần lọc đó quan trọng hơn ở **update**, vì đó mới là chỗ có thể chỉ sửa 1-2 field và để trống phần còn lại.

## 5. Nếu Timeline (hoặc entity khác) KHÔNG có ảnh — nên multipart hay JSON?

Câu này quan trọng, chốt lại nguyên tắc:

> **Có file cần upload → bắt buộc multipart/FormData. Không có file → luôn dùng JSON thường**, y hệt cách bạn đang làm với `info.js`.

Vì bản chất multipart chỉ tồn tại để "cõng" được dữ liệu nhị phân (file) đi cùng text trong 1 request — không có file thì dùng nó chỉ tổ phức tạp hơn JSON vô ích (backend cũng phải viết `Form(...)` cho từng field, thay vì nhận thẳng 1 Pydantic model qua `Body(...)` — đúng như bạn đoán).

Nên nếu sau này bạn làm ví dụ **Achievement** mà không có ảnh, code sẽ trông y hệt `info.js`:

Backend:

```python
@router.put("/{achievement_id}")
def update(achievement_id: int, update_data: AchievementUpdate, db: Session = Depends(...)):
    ...
```

Frontend:

```js
export const achievementService = {
  update: async (id, data) => {
    const response = await axiosInstance.put(`${ENDPOINT}/${id}`, data); // data là object thường, KHÔNG cần FormData
    return response;
  },
};
```

Không `FormData`, không lo header, không cần `buildFormData` — axios thấy `data` là object JS thường thì tự động `JSON.stringify` + set `Content-Type: application/json`. Cái phức tạp (`FormData`, `Form(...)` bên backend) chỉ xuất hiện đúng lúc bạn thật sự có `UploadFile`/`<input type="file">` thôi — coi đây là "trường hợp đặc biệt", còn mặc định luôn là JSON như Info.
