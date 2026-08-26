import { Mail, UserLock } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/auth';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { animateSlow, baseBackground, baseBorder, baseText, bgSurface } from '../utils/style';
import clsx from 'clsx';
import {Button} from "../components/wrapper/Button";
import ThemeToggle from "../components/ui/ThemeToggle";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    
    const { isAuthenticated, login } = useAuth(); 
    
    useEffect(() => {
        if (isAuthenticated) navigate("/admin");
    }, [isAuthenticated, navigate]);

    const handleLogin = async(e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const res = await authService.login(email, password);
            login(res.access_token);
            toast.success(res.message || "Đăng nhập thành công!");
            navigate("/admin");
        } catch (err) {
            console.error("Failed to login: ", err);
            // Có thể dùng err.message từ backend nếu có, tạm thời để text cứng
            toast.error(err.message || "Email hoặc mật khẩu không chính xác!");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className={clsx(baseBackground, baseText, animateSlow, "relative min-h-screen flex items-center justify-center p-4")}>
            {/* Thêm w-full để card không bị bóp nghẹt trên mobile */}
            <form onSubmit={handleLogin} 
                className={clsx(
                    bgSurface, baseBorder, animateSlow, "border-2 w-full max-w-md p-8 text-center rounded-xl"
            )}>
                
                <p className='text-2xl text-center font-bold mb-6'>
                    Login to manage your website!<br/>
                    <span className="text-primary text-xl font-semibold mt-1 block"> 🗿 My Boss! 🗿</span>
                </p>

                <Input
                    inputType={"email"} 
                    Icon={Mail}
                    label={"Email"}
                    placeHolder={"admin@example.com"}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                
                <div className="mt-4 mb-8">
                    <Input
                        inputType={"text"}
                        Icon={UserLock}
                        label={"Password"}
                        placeHolder={"••••••••"}
                        isPassword={true}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>

                <Button style={clsx("px-4 py-2 rounded-md")}>
                    <button 
                        type="submit" 
                        disabled={loading} // SỬA LỖI 4: Khóa hẳn nút bấm
                        className={clsx("w-full btn-primary", loading && "opacity-60 cursor-not-allowed")}
                    >
                        {loading ? "Authenticating..." : "Log In"}
                    </button>
                </Button>
            </form>
            <div className='absolute top-2 left-2'>
                <ThemeToggle/>
            </div>
        </div>
    );
}