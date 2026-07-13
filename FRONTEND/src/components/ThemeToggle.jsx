import { useState, useEffect } from "react";
import { Moon, Sun } from 'lucide-react';
import { motion } from "framer-motion";
function ThemeToggle() {
    // =========================================================================
    // 1. KHỞI TẠO BỘ NHỚ (State + LocalStorage)
    // Dùng mũi tên () => (Lazy Init) để chỉ đọc ổ cứng 1 LẦN DUY NHẤT lúc mở web.
    // Nếu ổ cứng chưa lưu gì thì mặc định lấy 'light'.
    // =========================================================================
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('theme') || 'light';
    });

    // =========================================================================
    // 2. ĐỒNG BỘ HÓA GIAO DIỆN (Side Effect)
    // Mỗi khi biến 'theme' thay đổi, useEffect sẽ chạy để làm 2 việc ngoài luồng:
    // - Sơn lại thẻ <html> của trình duyệt (thêm/xóa class 'dark')
    // - Ghi nhớ vào ổ cứng (localStorage) để lần sau F5 không bị mất
    // =========================================================================
    useEffect(() => {
        const htmlElement = document.documentElement; // Tóm lấy thẻ <html> cao nhất

        if (theme === 'dark') {
            htmlElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }, [theme]); // <-- Chỉ kích hoạt khi 'theme' có sự thay đổi

    // =========================================================================
    // 3. CÔNG TẮC ĐẢO CHIỀU
    // Dùng prevTheme (giá trị trước đó) để lật ngược trạng thái an toàn tuyệt đối
    // =========================================================================
    const toggleTheme = () => {
        setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
    };

    return (
        <div
            onClick={toggleTheme} 
            className="btn-primary rounded-full flex items-center justify-center w-12 h-12 transition-all ease-linear duration-500"
        >
            {theme === 'light' ? (
                <motion.div
                    key={"light"}
                    initial={{opacity:0, x:-25, rotate:-90}}
                    animate={{opacity:1, x: 0, rotate:0}}
                    exit={{opacity:0, x:-25, rotate:-90}}
                    transition={{duration:0.5, ease:"easeInOut"}}

                >
                    <Sun className="text-xl" />
                </motion.div>
            ) : (
                <motion.div
                    key={"dark"}
                    initial={{opacity:0, x:25, rotate:90}}
                    animate={{opacity:1, x:0, rotate:0}}
                    exit={{opacity:0, x:25, rotate:90}}
                    transition={{duration:0.5, ease:"easeInOut"}}
                >
                    <Moon className="text-xl" />
                </motion.div>
            )}
        </div>
    );
}

export default ThemeToggle;