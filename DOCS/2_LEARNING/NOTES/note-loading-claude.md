## LOADER xịn hơn do claude code

```jsx
import { motion } from "framer-motion";

export const StatusLoading = () => {
  return (
    <div className="p-6 flex flex-col justify-center items-center gap-5">
      {/* Dual-ring spinner: outer ring quay chậm, inner ring quay nhanh ngược chiều */}
      <div className="relative w-14 h-14 flex items-center justify-center">
        <motion.div
          className="absolute inset-0 border-4 border-solid rounded-full dark:border-white/20 border-primary/20 dark:border-t-white border-t-primary"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "linear" }}
        />
        <motion.div
          className="absolute inset-2 border-4 border-solid rounded-full dark:border-white/10 border-primary/10 border-b-primary dark:border-b-white"
          animate={{ rotate: -360 }}
          transition={{ duration: 0.9, repeat: Infinity, ease: "linear" }}
        />
      </div>

      {/* Text với dots nhảy tuần tự thay vì đứng yên */}
      <div className="flex items-center gap-1 text-2xl">
        <motion.span
          initial={{ opacity: 0.4 }}
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
        >
          Waiting to load data
        </motion.span>
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="inline-block"
            animate={{ y: [0, -6, 0] }}
            transition={{
              duration: 0.9,
              repeat: Infinity,
              delay: i * 0.15,
              ease: "easeInOut",
            }}
          >
            .
          </motion.span>
        ))}
      </div>
    </div>
  );
};
```
