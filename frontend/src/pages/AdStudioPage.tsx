import React from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import AdStudioCard from '../components/AdStudioCard';

/**
 * Ad Studio Page - Thu thập link & Lên lịch đăng bài
 * 
 * Layout 2 cột theo phong cách Publer:
 * - Cột trái (70%): Form nhập liệu với 4 sections
 * - Cột phải (30%): Video Preview sticky
 * 
 * Features:
 * - Dán link TikTok/Facebook để fetch video + metadata
 * - Chỉnh sửa caption, tiêu đề, CTA
 * - Chọn thumbnail từ video hoặc upload
 * - Chọn kênh đăng (multi-select với search)
 * - Lịch đăng: Đăng ngay / Hẹn giờ / Tự động
 * - Bình luận tự động (accordion)
 */
const AdStudioPage: React.FC = () => {
  return (
    <>
      <AdStudioCard />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
    </>
  );
};

export default AdStudioPage;
