/** @type {import('tailwindcss').Config} */
export default {
  // 1. CƠ CHẾ DARK MODE:
  // tự điều khiển bằng nút bấm (công tắc ThemeToggle), khi nút bấm thêm class "dark" vào thẻ <html>, Tailwind sẽ tự động kích hoạt các màu dark:bg-...
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
    // Viết trong "extend" nghĩa là: "Giữ nguyên các màu mặc định, và cộng thêm bộ màu riêng của tôi vào đây".
    extend: {
      colors: {
        //  MÀU CHÍNH TRANG WEB
        primary: { DEFAULT: '#D98C2B', hover: '#B8701C' },

        light: {
          bg: '#F7F7F6',
          surface: '#FFFFFF',
          text: '#1F1F1D',
          muted: '#6E6E6B'
        },
        dark: {
          bg: '#16171A',
          surface: '#1E1F23',
          text: '#F2F2F0',
          muted: '#93938E'
        },
      },
      // Thiết lập phông chữ 
      fontFamily: {
        sans: ['"Rubik"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      transitionDuration: {fast:'200ms', base:'300ms',slow:'500ms' }
    },
  },
  plugins: [],
}