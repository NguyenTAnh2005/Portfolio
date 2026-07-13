-- Xóa dữ liệu và reset luôn cả bộ đếm ID về 1
TRUNCATE TABLE 
    system_configs, 
    blogs, 
    projects, 
    categories, 
    users, 
    roles, 
    myinfos 
RESTART IDENTITY CASCADE;
--TRUNCATE: Xóa sạch sành sanh dữ liệu nhưng giữ lại cấu trúc bảng.
--RESTART IDENTITY: Đưa bộ đếm ID tự động tăng về lại số 1.
--ASCADE: Tự động xử lý các ràng buộc khóa ngoại (ví dụ xóa Category thì không bị kẹt vì Blog).

Select * from Users
select * from Myinfos
Select * from Blogs
select * from Users;