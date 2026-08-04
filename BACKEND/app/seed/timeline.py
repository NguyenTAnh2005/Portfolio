from app.models.models import TimeLine
from sqlalchemy.orm import Session

def seed_timeline(db: Session):
    timeline_seed_data = [
        {
            "title": "Primary school student",
            "organization": "Cam Quang Primary School",
            "desc": "I studied here from age 6. I started 1st grade later than my classmate. I didn't learn English until 4th grade. I got the 'good student' award all 5 years!",
            "start_end": "2011 - 2016",
            "sort_order": 1,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805458/Portfolio/TimeLines/cam-quang-primary-school_y081lv.jpg",
            "img_public_id": "Portfolio/TimeLines/cam-quang-primary-school_y081lv",
        },
        {
            "title": "Secondary school student",
            "organization": "Nguyen Huu Thai Secondary School",
            "desc": "I studied here from age 11. Not much happened during this time. My English got worse starting in 8th grade. In 9th grade I learned a bit of Pascal, but I didn't take it seriously, and I still knew nothing about computers.",
            "start_end": "2016 - 2020",
            "sort_order": 2,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805459/Portfolio/TimeLines/nguyen-huu-thai-secondary-school_hqdw4f.jpg",
            "img_public_id": "Portfolio/TimeLines/nguyen-huu-thai-secondary-school_hqdw4f",
        },
        {
            "title": "High school student",
            "organization": "Cam Binh High School",
            "desc": "I studied here from age 15. I spent most of my time studying, but my grades were just average. In 11th grade I learned Pascal, but only with pen and paper — I didn't have a laptop to practice on. I got a total score of 24.3 on the National High School Graduation Exam to apply for an IT major.",
            "start_end": "2020 - 2023",
            "sort_order": 3,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805458/Portfolio/TimeLines/cam-binh-high-school_zpq2cx.jpg",
            "img_public_id": "Portfolio/TimeLines/cam-binh-high-school_zpq2cx",
        },
        {
            "title": "The first Part-time job",
            "organization": "GS25",
            "desc": "I had a part-time job at GS25, a convenience store chain from South Korea. I learned a lot there, and it made me value money more. But I only worked there for 6 months during my second year of university, because I had a lot of school projects around that time. The projects weren't hard, but since I had just started learning, I still struggled and couldn't manage the minimum hours per week that the job required.",
            "start_end": "12/2024 - 06/2025",
            "sort_order": 4,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805458/Portfolio/TimeLines/gs25_syxdoy.jpg",
            "img_public_id": "Portfolio/TimeLines/gs25_syxdoy",
        },
        {
            "title": "University student",
            "organization": "Binh Duong University",
            "desc": "I've studied here since age 18, in the IT program. Studying here was very different from before. In 1/2025 I learned HTML and CSS. In 4/2025 I learned basic JS. In 8/2025 I started using Bootstrap CSS. In 9/2025 I started learning React through React.dev, plus TailwindCSS. Right now I'm focusing on Software Engineering.",
            "start_end": "9/2023 - Now",
            "sort_order": 5,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805459/Portfolio/TimeLines/binh-duong-university_vmt2fm.jpg",
            "img_public_id": "Portfolio/TimeLines/binh-duong-university_vmt2fm",
        }
    ]

    for tl in timeline_seed_data:
        db_tl = TimeLine(
            title = tl["title"], organization= tl["organization"],
            desc= tl["desc"], start_end=tl["start_end"], sort_order=tl["sort_order"],
            img_url= tl["img_url"],
            img_public_id=tl["img_public_id"]
        )
        db.add(db_tl)
        
    print(f"⚠️  Added timelines seed data ....... waiting commit .............")


# timeline_seed_data = [
#     {
#         "title": "Primary school student",
#         "organization": "Cam Quang Primary School",
#         "desc": "Tôi học tại đây từ lúc 6 tuổi, nhập học lớp 1 muộn hơn một năm so với các bạn cùng trang lứa. Phải đến tận lớp 4 tôi mới được tiếp cận môn Tiếng Anh. Cả 5 năm học tôi đều đạt danh hiệu học sinh giỏi!",
#         "start_end": "2011 - 2016",
#         "sort_order": 1,
#         "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1784871406/Portfolio/TimeLines/cam-quang-primary-school-logo_vvsfl4.jpg",
#         "img_public_id": "Portfolio/TimeLines/cam-quang-primary-school-logo_vvsfl4",
#     },
#     {
#         "title": "Secondary school student",
#         "organization": "Nguyen Huu Thai Secondary School",
#         "desc": "Tôi học tại đây từ lúc 11 tuổi. Đây là thời kỳ không có quá nhiều biến cố, dù từ lớp 8 trở đi trình độ Tiếng Anh của tôi sụt giảm rõ rệt. Lớp 9 tôi được tiếp cận Pascal nhưng chưa học nghiêm túc, cũng chưa biết gì về máy tính.",
#         "start_end": "2016 - 2020",
#         "sort_order": 2,
#         "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1784871406/Portfolio/TimeLines/nguyen-huu-thai-secondary-school-logo_zrnqyp.jpg",
#         "img_public_id": "Portfolio/TimeLines/nguyen-huu-thai-secondary-school-logo_zrnqyp",
#     },
#     {
#         "title": "High school student",
#         "organization": "Cam Binh High School",
#         "desc": "Tôi học tại đây từ lúc 15 tuổi. Giai đoạn này tôi dành phần lớn thời gian cho việc học, dù kết quả chỉ ở mức trung bình. Năm lớp 11 tôi được tiếp cận Pascal nhưng chỉ học bằng giấy bút, không có laptop để thực hành. Tôi đạt tổng điểm 24,3 trong kỳ thi THPTQG để xét tuyển ngành CNTT.",
#         "start_end": "2020 - 2023",
#         "sort_order": 3,
#         "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1784871406/Portfolio/TimeLines/cam-binh-high-school-logo_s6y2hl.png",
#         "img_public_id": "Portfolio/TimeLines/cam-binh-high-school-logo_s6y2hl",
#     },
#     {
#         "title": "University student",
#         "organization": "Binh Duong University",
#         "desc": "Tôi học tại đây từ lúc 18 tuổi, theo ngành IT. Việc học ở đây khác hẳn so với các cấp trước. Tháng 1/2025 tôi làm quen với HTML, CSS. Tháng 4/2025 tôi tìm hiểu JS cơ bản. Tháng 8/2025 tôi bắt đầu dùng Bootstrap CSS. Tháng 9/2025 tôi tiếp cận React cơ bản qua React.dev và TailwindCSS. Hiện tại tôi đang theo đuổi chuyên ngành Công nghệ phần mềm.",
#         "start_end": "9/2023 - Now",
#         "sort_order": 5,
#         "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1784871406/Portfolio/TimeLines/binh-duong-university-logo_fzlsbc.jpg",
#         "img_public_id": "Portfolio/TimeLines/binh-duong-university-logo_fzlsbc",
#     },
#     {
#         "title": "The first Part-time job",
#         "organization": "GS25",
#         "desc": "Tôi có trải nghiệm đi làm thêm tại cửa hàng tiện lợi GS25 - chuỗi cửa hàng có nguồn gốc từ Hàn Quốc. Tại đây tôi có nhiều trải nghiệm quý giá và cảm thấy trân trọng đồng tiền hơn. Tuy nhiên, tôi chỉ làm được vỏn vẹn 6 tháng trong năm hai đại học, vì thời điểm đó tôi phải làm khá nhiều dự án trên trường. Các dự án đó không khó, nhưng vì mới bắt đầu học nên tôi vẫn còn lúng túng, không thể sắp xếp đủ thời gian tối thiểu mỗi tuần theo yêu cầu.",
#         "start_end": "12/2024 - 06/2025",
#         "sort_order": 4,
#         "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1784871405/Portfolio/TimeLines/gs25-logo_fymimi.jpg",
#         "img_public_id": "Portfolio/TimeLines/gs25-logo_fymimi",
#     }]