/** @type {import('tailwindcss').Config} */
export default {
  // 1. CƠ CHẾ DARK MODE:
  // Tại sao là 'class'? Vì ta muốn tự điều khiển bằng nút bấm (công tắc ThemeToggle).
  // Khi nút bấm thêm class "dark" vào thẻ <html>, Tailwind sẽ tự động kích hoạt các màu dark:bg-...
  // (Nếu để 'media', web sẽ tự đổi màu theo cài đặt sáng/tối của hệ điều hành máy tính/điện thoại).
  darkMode: 'class',

  // 2. MÁY QUÉT MÃ NGUỒN (Content):
  // Đây là nơi bảo Tailwind: "Hãy quét tất cả các file có đuôi .html, .js, .jsx, .ts, .tsx trong thư mục src/".
  // Tác dụng cực lớn: Khi build dự án, Tailwind chỉ giữ lại những class NÀO CÓ DÙNG trong các file này.
  // Class nào không dùng sẽ bị vứt đi -> Giúp file CSS cuối cùng siêu nhẹ (chỉ vài KB).
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],

  theme: {
    // 3. TẠI SAO PHẢI VIẾT TRONG "EXTEND"?
    // "extend" có nghĩa là MỞ RỘNG. 
    // Nếu bạn viết màu sắc thẳng vào "theme", bạn sẽ XÓA SẠCH toàn bộ bảng màu mặc định của Tailwind (red-500, blue-500,... sẽ biến mất).
    // Viết trong "extend" nghĩa là: "Giữ nguyên các màu mặc định, và cộng thêm bộ màu riêng của tôi vào đây".
    extend: {
      colors: {
        // Cách gọi: className="bg-primary hover:bg-primary-hover text-white"
        primary: {
          // cam-##ca3500 blue-#2563eb-hover-1D4ED8   xanh-ngọc-00d2d3-hover-01a3a4
          DEFAULT: '#2563eb',   // Màu gốc
          // 
          hover: '#1D4ED8'      // Màu khi chuột di vào
        },
        // Cách gọi: className="bg-light-bg text-light-text" -> Giao diện Sáng
        light: {
          bg: '#f8f9fa',        // Màu nền tổng thể toàn trang
          surface: '#ffffff',   // Màu nền các khối hộp (Card, Navbar)
          text: '#2d3436',      // Màu chữ chính
          muted: '#636e72'      // Màu chữ phụ (Mô tả, ngày tháng,...)
        },
        // Cách gọi: className="dark:bg-dark-bg dark:text-dark-text" -> Giao diện Tối
        dark: {
          bg: '#111827',
          surface: '#1f2937',
          text: '#f9fafb',
          muted: '#9ca3af'
        },
      },
      // Thiết lập phông chữ mặc định của web là Inter. Cách gọi: className="font-sans"
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}