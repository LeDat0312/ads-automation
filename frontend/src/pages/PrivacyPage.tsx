import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="w-full px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Logo UA in circle */}
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">UA</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Updatemetaads</h1>
              <p className="text-sm text-slate-400">Nền tảng tự động hóa Facebook Ads</p>
            </div>
          </div>
          <Link
            to="/"
            className="text-slate-300 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium"
          >
            <span>←</span>
            <span>Quay lại trang chủ</span>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-16">
        <div className="rounded-3xl border border-white/5 bg-slate-900/60 p-6 sm:p-8 md:p-12 shadow-xl shadow-black/40">
          {/* Title */}
          <h1 className="text-4xl font-bold text-white mb-4">Chính sách quyền riêng tư</h1>
          <p className="text-slate-400 text-lg mb-8">Cập nhật lần cuối: {new Date().toLocaleDateString('vi-VN')}</p>

          {/* Introduction */}
          <div className="mb-8">
            <p className="text-slate-300 leading-relaxed text-base">
              Updatemetaads cung cấp nền tảng SaaS, thu thập dữ liệu từ Meta để hiển thị báo cáo và chạy automation. 
              Chúng tôi cam kết bảo vệ quyền riêng tư và dữ liệu của bạn.
            </p>
          </div>

          {/* Section 1: Dữ liệu thu thập */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">1. Dữ liệu thu thập</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>
                Chúng tôi thu thập các loại dữ liệu sau để cung cấp dịch vụ:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <strong className="text-white">Dữ liệu từ Meta API:</strong> Thông tin về chiến dịch quảng cáo, 
                  nhóm quảng cáo, quảng cáo, hiệu suất quảng cáo (chi tiêu, lượt hiển thị, lượt nhấp, chuyển đổi, v.v.)
                </li>
                <li>
                  <strong className="text-white">Thông tin tài khoản:</strong> Tên người dùng, email, 
                  cài đặt tài khoản và tùy chọn người dùng
                </li>
                <li>
                  <strong className="text-white">Token truy cập:</strong> Token Facebook/Meta được lưu trữ an toàn 
                  để kết nối với tài khoản quảng cáo của bạn
                </li>
                <li>
                  <strong className="text-white">Dữ liệu sử dụng:</strong> Log truy cập, thời gian sử dụng dịch vụ, 
                  và các hành động bạn thực hiện trên nền tảng
                </li>
              </ul>
            </div>
          </section>

          {/* Section 2: Cách sử dụng dữ liệu */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">2. Cách sử dụng dữ liệu</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>Chúng tôi sử dụng dữ liệu thu thập được cho các mục đích sau:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Hiển thị báo cáo và phân tích hiệu suất quảng cáo</li>
                <li>Chạy các automation và quy tắc tự động hóa theo cấu hình của bạn</li>
                <li>Cải thiện và phát triển dịch vụ</li>
                <li>Gửi thông báo và cập nhật về dịch vụ (nếu bạn đăng ký nhận)</li>
                <li>Xử lý yêu cầu hỗ trợ và giải quyết vấn đề kỹ thuật</li>
              </ul>
              <p className="mt-4 font-medium text-white">
                ⚠️ Lưu ý quan trọng: Chúng tôi KHÔNG bán, cho thuê, hoặc chia sẻ dữ liệu của bạn với bên thứ ba 
                vì mục đích quảng cáo hoặc marketing.
              </p>
            </div>
          </section>

          {/* Section 3: Cam kết bảo mật và chia sẻ dữ liệu */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">3. Cam kết bảo mật và chia sẻ dữ liệu</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>
                Chúng tôi cam kết chỉ sử dụng dữ liệu của bạn để cung cấp dịch vụ và không chia sẻ với bên thứ ba, 
                trừ các trường hợp sau:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <strong className="text-white">Nhà cung cấp dịch vụ:</strong> Chúng tôi có thể sử dụng các nhà cung cấp 
                  dịch vụ đáng tin cậy (như dịch vụ lưu trữ đám mây) để vận hành nền tảng, nhưng họ chỉ được phép 
                  xử lý dữ liệu theo hướng dẫn của chúng tôi
                </li>
                <li>
                  <strong className="text-white">Yêu cầu pháp lý:</strong> Chúng tôi có thể tiết lộ dữ liệu nếu được 
                  yêu cầu bởi cơ quan pháp luật hoặc để tuân thủ các quy định pháp lý
                </li>
                <li>
                  <strong className="text-white">Bảo vệ quyền lợi:</strong> Chúng tôi có thể tiết lộ thông tin để bảo vệ 
                  quyền, tài sản hoặc an toàn của chúng tôi, người dùng hoặc người khác
                </li>
              </ul>
            </div>
          </section>

          {/* Section 4: Bảo mật & lưu trữ */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">4. Bảo mật & lưu trữ</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>Chúng tôi áp dụng các biện pháp bảo mật sau để bảo vệ dữ liệu của bạn:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Mã hóa dữ liệu trong quá trình truyền (HTTPS/TLS)</li>
                <li>Mã hóa token và thông tin nhạy cảm khi lưu trữ</li>
                <li>Kiểm soát truy cập nghiêm ngặt và xác thực người dùng</li>
                <li>Giám sát và phát hiện các hoạt động bất thường</li>
                <li>Sao lưu dữ liệu định kỳ để đảm bảo tính khả dụng</li>
              </ul>
              <p className="mt-4">
                Dữ liệu được lưu trữ trên các máy chủ an toàn và chỉ được giữ lại trong thời gian cần thiết 
                để cung cấp dịch vụ hoặc theo yêu cầu pháp lý.
              </p>
            </div>
          </section>

          {/* Section 5: Quyền của bạn */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">5. Quyền của bạn</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>Bạn có các quyền sau đối với dữ liệu của mình:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <strong className="text-white">Quyền truy cập:</strong> Bạn có thể xem và xuất dữ liệu của mình 
                  thông qua giao diện nền tảng
                </li>
                <li>
                  <strong className="text-white">Quyền chỉnh sửa:</strong> Bạn có thể cập nhật thông tin tài khoản 
                  và cài đặt của mình
                </li>
                <li>
                  <strong className="text-white">Quyền xóa:</strong> Bạn có thể yêu cầu xóa tài khoản và dữ liệu 
                  của mình (một số dữ liệu có thể được giữ lại để tuân thủ pháp luật)
                </li>
                <li>
                  <strong className="text-white">Quyền ngắt kết nối:</strong> Bạn có thể ngắt kết nối ứng dụng 
                  Updatemetaads khỏi tài khoản Facebook của mình bất cứ lúc nào thông qua 
                  <strong className="text-white"> Facebook Business Settings</strong>
                </li>
                <li>
                  <strong className="text-white">Quyền từ chối:</strong> Bạn có thể từ chối việc thu thập một số 
                  dữ liệu nhất định, nhưng điều này có thể ảnh hưởng đến chức năng của dịch vụ
                </li>
              </ul>
            </div>
          </section>

          {/* Section 6: Thông tin liên hệ */}
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-4">6. Thông tin liên hệ</h2>
            <div className="text-slate-300 leading-relaxed space-y-3">
              <p>
                Nếu bạn có câu hỏi, yêu cầu hoặc khiếu nại về chính sách quyền riêng tư này, 
                vui lòng liên hệ với chúng tôi:
              </p>
              <div className="bg-slate-800/50 rounded-lg p-4 mt-4 border border-slate-700/50">
                <p className="text-white font-medium mb-2">Updatemetaads</p>
                <p className="text-sm">Email: support@updatemetaads.com</p>
                <p className="text-sm mt-1">
                  Thời gian phản hồi: Chúng tôi sẽ phản hồi trong vòng 48 giờ làm việc.
                </p>
              </div>
            </div>
          </section>

          {/* Footer note */}
          <div className="mt-8 pt-6 border-t border-slate-700/50">
            <p className="text-sm text-slate-400 text-center">
              Chúng tôi có thể cập nhật chính sách này theo thời gian. 
              Mọi thay đổi sẽ được thông báo trên trang này.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PrivacyPage;

